from pathlib import Path
from typing import TYPE_CHECKING
from dataclasses import dataclass, field

import tclib3
import mediaprobe
from mediaprobe import MediaProbe
from rosettapath import RosettaPath

from .assetfieldmaps import ASSET_FIELD_MAPS

if TYPE_CHECKING:
    from ..fieldmaps import SimpleFieldMap

    

@dataclass
class SpecInfo:
    name: str
    minfo_track: str=""
    minfo_field: str=""
    probetype: str="simple"
    minfo_value: str|bool=""
    mpulse_value: str|bool=""
    mapping: "SimpleFieldMap"=field(init=False)
    outputdict: dict[str, str]=field(default_factory=dict)
    found: bool=False

    def __post_init__(self) -> None:
        self.mapping = ASSET_FIELD_MAPS[self.name]

    def patch_op(self) -> dict:
        return self.mapping.patch_op(self._format(self.mpulse_value))

    def makejdict(self) -> dict:
        return self.mapping.makejdict(self._format(self.mpulse_value))

    def _format(self, value: str | bool) -> str | bool:
        if not value:
            return value
        if self.name == "video_bitrate" or self.name == "audio_bitrate":
            return mediaprobe.helpers.format_size(int(value), returnbits=True, returnrate=True)
        return value

BITDEPTH_DICT: dict[str, str] = {
    "8": "8 bit",
    "10": "10 bit",
    "12": "12 bit",
    "16": "16 bit",
    "24": "24 bit",
    "32": "32 bit"
}

AUDIO_SAMPLERATE_DICT: dict[str, str] = {
    "16000": "16000 Hz",
    "32000": "32000 Hz",
    "44100": "44100 Hz",
    "48000": "48000 Hz",
    "96000": "96000 Hz",
    "192000": "192000 Hz"
}

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
    "video_bitrate_mode": ("Video", "BitRate_Mode"),
    "audio_codec": ("Audio", "Format"),
    "audio_bitrate": ("Audio", "BitRate"),
    "audio_bitrate_mode": ("Audio", "BitRate_Mode"),
}

SPEC_PROBE_MAP_DICT: dict[str, tuple[str, str, dict]] = {
    "color_space": ("Video", "colour_primaries", COLOR_SPACE_DICT),
    "eotf": ("Video", "transfer_characteristics", EOTF_DICT),
    "matrix": ("Video", "matrix_coefficients", MATRIX_DICT),
    "video_bitdepth": ("Video", "BitDepth", BITDEPTH_DICT),
    "audio_bitdepth": ("Audio", "BitDepth", BITDEPTH_DICT),
    "audio_samplerate": ("Audio", "SamplingRate", AUDIO_SAMPLERATE_DICT)
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
    def __init__(self, path: str):
        self.path: str
        self.set_path(path)
        self.all: list[SpecInfo] = self._create_specinfo()
        self.found: list[SpecInfo] = []
        self.notfound: list[SpecInfo] = []
        self._isprobed = False

    @property
    def isprobed(self) -> bool:
        return self._isprobed

    def set_path(self, path: str) -> None:
        if not path:
            self.path = ""
            return
        self.path = RosettaPath(path.replace("\"", "")).linux_path()

    def probefile(self, probe: "MediaProbe") -> None:
        for method in self.all:
            if method.probetype == "simple":
                self._simple_lookup(method, probe)
            elif method.probetype == "dict":
                self._dict_lookup(method, probe)
            elif method.probetype == "complex":
                self._complex_lookup(method, probe)
        assert len(self.all) == len(self.found) + len(self.notfound)
        self._isprobed = True

    def get_spec(self, spec: str) -> SpecInfo | None:
        if not self.isprobed:
            raise RuntimeError("SpecInterface.get_spec: probe() must be called before get_spec()")
        for specinfo in self.all:
            if specinfo.name.lower() == spec.lower():
                return specinfo

    def patch_ops(self) -> list[dict]:
        if not self.isprobed:
            raise RuntimeError("SpecInterface.patch_ops: probe() must be called before patch_ops()")
        return [method.patch_op() for method in self.found]

    def _create_specinfo(self) -> list[SpecInfo]:
        simple_map = [SpecInfo(spec, *SPEC_PROBE_MAP_SIMPLE[spec], probetype="simple") for spec in SPEC_PROBE_MAP_SIMPLE]
        complex_map = [SpecInfo(spec, probetype="complex") for spec in SPEC_PROBE_MAP_COMPLEX]
        all_maps = simple_map + complex_map
        for spec in SPEC_PROBE_MAP_DICT:
            args = SPEC_PROBE_MAP_DICT[spec][:-1]
            outputdict = SPEC_PROBE_MAP_DICT[spec][-1]
            all_maps.append(SpecInfo(spec, *args, probetype="dict", outputdict=outputdict))
        return all_maps

    def _add_found(self, method: SpecInfo) -> None:
        method.found = True
        self.found.append(method)

    def _add_notfound(self, method: SpecInfo) -> None:
        self.notfound.append(method)

    def _simple_lookup(self, method: SpecInfo, probe: "MediaProbe") -> None:
        for track in probe.fulljson["tracks"]:
            if track["@type"] == method.minfo_track:
                value = track.get(method.minfo_field)
                if value:
                    method.minfo_value = value
                    method.mpulse_value = value
                    method.found = True
                    self._add_found(method)
                else:
                    self._add_notfound(method)
                return
        self._add_notfound(method)

    def _dict_lookup(self, method: SpecInfo, probe: "MediaProbe") -> None:
        self._simple_lookup(method, probe)
        if method.found:
            if not isinstance(method.mpulse_value, str):
                return
            mpulse_value = method.outputdict.get(method.mpulse_value)
            if mpulse_value is None:
                return
            method.mpulse_value = mpulse_value

    def _complex_lookup(self, method: SpecInfo, probe: "MediaProbe") -> None:
        match method.name:
            case "container":
                self._container_spec(method, probe)
            case "length":
                self._length_spec(method, probe)
            case "resolution":
                self._resolution_spec(method, probe)
            case "dropframe":
                self._dropframe_spec(method, probe)
            case _:
                raise NotImplementedError(f"SpecInterface._complex: {method.name}")

    def _is_df(self, probe: "MediaProbe") -> bool:
        start_tc = probe.start_tc()
        if not start_tc:
            return False
        if ";" in start_tc:
            return True
        return False

    def _container_spec(self, method: SpecInfo, probe: "MediaProbe") -> None:
        method.mpulse_value = Path(probe.filepath).suffix[1:].upper()
        for track in probe.fulljson["tracks"]:
            if track["@type"] == "General":
                method.minfo_value = track.get("Format", "")
                break
        self._add_found(method)
            
    def _length_spec(self, method: SpecInfo, probe: "MediaProbe") -> None:
        duration = probe.duration()
        if not duration:
            self._add_notfound(method)
            return
        
        method.minfo_value = duration

        fps_str = probe.fps()
        if not fps_str:
            method.mpulse_value = duration
            self._add_found(method)
            return
        
        fps_int = round(float(fps_str))
        hrminsec = [0, 0, float(duration)]
        frames = tclib3.ms_to_frames(hrminsec, fps_int, hrminsec=True)
        method.mpulse_value = tclib3.frames_to_tc(frames-1, fps_int, self._is_df(probe))
        self._add_found(method)

    def _resolution_spec(self, method: SpecInfo, probe: "MediaProbe") -> None:
        resolution_str = probe.resolution(asint=False)
        if resolution_str is None:
            self._add_notfound(method)
            return
        method.minfo_value = f"{resolution_str[0]},{resolution_str[1]}"
        method.mpulse_value = f"{resolution_str[0]} x {resolution_str[1]}"
        self._add_found(method)

    def _dropframe_spec(self, method: SpecInfo, probe: "MediaProbe") -> None:
        is_df = self._is_df(probe)
        method.minfo_value = is_df
        method.mpulse_value = is_df
        self._add_found(method)