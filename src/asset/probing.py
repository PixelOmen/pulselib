from pathlib import Path
from typing import TYPE_CHECKING
from dataclasses import dataclass, field

import tclib3

from .assetfieldmaps import ASSET_MAPS

if TYPE_CHECKING:
    from mediaprobe import MediaProbe
    from ..fieldmaps import SimpleFieldMap

@dataclass
class SpecInfo:
    spec: str
    minfo_track: str=""
    minfo_field: str=""
    probetype: str="simple"
    minfo_value: str|bool=""
    mpulse_value: str|bool=""
    mapping: "SimpleFieldMap"=field(init=False)
    outputdict: dict[str, str]=field(default_factory=dict)
    found: bool=False

    def __post_init__(self) -> None:
        self.mapping = ASSET_MAPS[self.spec]

    def patch_op(self) -> dict:
        return self.mapping.patch_op(self.mpulse_value)


COLOR_SPACE_DICT: dict[str, str] = {
    "BT.709": "Rec709",
    "Display P3": "P3-D65",
    "BT.2020": "Rec2020",
    "DCI P3": "DCI-P3"
}

# Resolve does not include the color primaries metadata when using 2.4 gamma
EOTF_DICT: dict [str | None, str] = {
    "BT.470 System M": "2.2 Gamma",
    "SMPTE 428M": "2.6 Gamma",
    "BT.709": "Rec709",
    "PQ": "PQ"
}

MATRIX_DICT: dict[str, str] = {
    "BT.709": "Rec709",
    "BT.2020 non-constant": "Rec2020"
}


SPEC_PROBE_MAP_SIMPLE: dict[str, tuple[str, str]] = {
    "chroma_sub": ("Video", "ChromaSubsampling"),
    "frame_rate": ("Video", "FrameRate"),
    "scan_type": ("Video", "ScanType"),
    "video_codec": ("Video", "Format"),
    "video_profile": ("Video", "Format_Profile"),
    "video_bitrate": ("Video", "BitRate"),
    "video_bitdepth": ("Video", "BitDepth"),
    "video_bitrate_mode": ("Video", "BitRate_Mode"),
    "audio_codec": ("Audio", "Format"),
    "audio_bitrate": ("Audio", "BitRate"),
    "audio_bitdepth": ("Audio", "BitDepth"),
    "audio_bitrate_mode": ("Audio", "BitRate_Mode"),
    "audio_samplerate": ("Audio", "SamplingRate"),
}

SPEC_PROBE_MAP_DICT: dict[str, tuple[str, str, dict]] = {
    "color_space": ("Video", "colour_primaries", COLOR_SPACE_DICT),
    "eotf": ("Video", "transfer_characteristics", EOTF_DICT),
    "matrix": ("Video", "matrix_coefficients", MATRIX_DICT),
}

SPEC_PROBE_MAP_COMPLEX: list[str] = [
    "container",
    "length",
    "resolution",
    "dropframe"
]

# May need to add handling for this error:
# "error": "A matching value could not be found for the custom dropdown field REI_field_19; Value: 42 bit.\r\n"
class SpecInterface:
    def __init__(self, probe: "MediaProbe"):
        self.probe = probe
        self.all: list[SpecInfo] = self._create_specinfo()
        self.found: list[SpecInfo] = []
        self.notfound: list[SpecInfo] = []
        self._find()

    def patch_ops(self) -> list[dict]:
        return [method.patch_op() for method in self.found]

    def _create_specinfo(self) -> list[SpecInfo]:
        simple = [SpecInfo(spec, *SPEC_PROBE_MAP_SIMPLE[spec], probetype="simple") for spec in SPEC_PROBE_MAP_SIMPLE]
        complex = [SpecInfo(spec, probetype="complex") for spec in SPEC_PROBE_MAP_COMPLEX]
        maps = []
        for spec in SPEC_PROBE_MAP_DICT:
            args = SPEC_PROBE_MAP_DICT[spec][:-1]
            outputdict = SPEC_PROBE_MAP_DICT[spec][-1]
            maps.append(SpecInfo(spec, *args, probetype="dict", outputdict=outputdict))
        return simple + maps + complex

    def _add_found(self, method: SpecInfo) -> None:
        method.found = True
        self.found.append(method)

    def _add_notfound(self, method: SpecInfo) -> None:
        self.notfound.append(method)

    def _find(self) -> None:
        for method in self.all:
            if method.probetype == "simple":
                self._simple_lookup(method)
            elif method.probetype == "dict":
                self._dict_lookup(method)
            elif method.probetype == "complex":
                self._complex_lookup(method)

    def _simple_lookup(self, method: SpecInfo) -> None:
        for track in self.probe.fulljson["tracks"]:
            if track["@type"] == method.minfo_track:
                value = track.get(method.minfo_field)
                if value:
                    method.minfo_value = value
                    method.mpulse_value = value
                    self._add_found(method)
                else:
                    self._add_notfound(method)
                break

    def _dict_lookup(self, method: SpecInfo) -> None:
        self._simple_lookup(method)
        if method.found:
            if not isinstance(method.mpulse_value, str):
                return
            mpulse_value = method.outputdict.get(method.mpulse_value)
            if mpulse_value is None:
                return
            method.mpulse_value = mpulse_value

    def _complex_lookup(self, method: SpecInfo) -> None:
        match method.spec:
            case "container":
                self._container_spec(method)
            case "length":
                self._length_spec(method)
            case "resolution":
                self._resolution_spec(method)
            case "dropframe":
                self._dropframe_spec(method)
            case _:
                raise NotImplementedError(f"SpecInterface._complex: {method.spec}")

    def _is_df(self) -> bool:
        start_tc = self.probe.start_tc()
        if not start_tc:
            return False
        if ";" in start_tc:
            return True
        return False

    def _container_spec(self, method: SpecInfo) -> None:
        method.mpulse_value = Path(self.probe.filepath).suffix[1:].upper()
        for track in self.probe.fulljson["tracks"]:
            if track["@type"] == "General":
                method.minfo_value = track.get("Format", "")
                break
        self._add_found(method)
            
    def _length_spec(self, method: SpecInfo) -> None:
        duration = self.probe.duration()
        if not duration:
            self._add_notfound(method)
            return
        
        method.minfo_value = duration

        fps_str = self.probe.fps()
        if not fps_str:
            method.mpulse_value = duration
            self._add_found(method)
            return
        
        fps_int = round(float(fps_str))
        hrminsec = [0, 0, float(duration)]
        frames = tclib3.ms_to_frames(hrminsec, fps_int, True)
        method.mpulse_value = tclib3.frames_to_tc(frames-1, fps_int, self._is_df())
        self._add_found(method)

    def _resolution_spec(self, method: SpecInfo) -> None:
        resolution_str = self.probe.resolution(asint=False)
        if resolution_str is None:
            self._add_notfound(method)
            return
        method.minfo_value = f"{resolution_str[0]},{resolution_str[1]}"
        method.mpulse_value = f"{resolution_str[0]} x {resolution_str[1]}"
        self._add_found(method)

    def _dropframe_spec(self, method: SpecInfo) -> None:
        is_df = self._is_df()
        method.minfo_value = is_df
        method.mpulse_value = is_df
        self._add_found(method)