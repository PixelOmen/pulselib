from typing import TYPE_CHECKING
from dataclasses import dataclass

import tclib3

if TYPE_CHECKING:
    from mediaprobe import MediaProbe


@dataclass
class SpecInfo:
    spec: str
    track: str=""
    field: str=""
    probetype: str="simple"
    minfo_value: str=""
    mpulse_value: str=""


COLOR_SPACE_MAP: dict[str, str] = {
    "BT.709": "Rec709",
    "Display P3": "P3-D65",
    "BT.2020": "Rec2020",
    "DCI P3": "DCI-P3"
}

# Resolve does not include the color primaries metadata when using 2.4 gamma
EOTF_MAP: dict [str | None, str] = {
    "BT.470 System M": "2.2 Gamma",
    "SMPTE 428M": "2.6 Gamma",
    "BT.709": "Rec709",
    "PQ": "PQ"
}

MATRIX_MAP: dict[str, str] = {
    "BT.709": "Rec709",
    "BT.2020 non-constant": "Rec2020"
}

SPEC_PROBE_MAP_SIMPLE: dict[str, tuple[str, str, str]] = {
    "color_space": ("Video", "colour_primaries", "simple"),
    "eotf": ("Video", "transfer_characteristics", "simple"),
    "matrix": ("Video", "matrix_coefficients", "simple"),
    "chroma_sub": ("Video", "ChromaSubsampling", "simple"),
    "frame_rate": ("Video", "FrameRate", "simple"),
    "scan_type": ("Video", "ScanType", "simple"),
    "video_codec": ("Video", "Format", "simple"),
    "video_profile": ("Video", "Format_Profile", "simple"),
    "video_bitrate": ("Video", "BitRate", "simple"),
    "video_bitdepth": ("Video", "BitDepth", "simple"),
    "video_bitrate_mode": ("Video", "BitRate_Mode", "simple"),
    "audio_bitrate": ("Audio", "BitRate", "simple"),
    "audio_bitdepth": ("Audio", "BitDepth", "simple"),
    "audio_bitrate_mode": ("Audio", "BitRate_Mode", "simple"),
    "audio_samplerate": ("Audio", "SamplingRate", "simple")
}

SPEC_PROBE_MAP_COMPLEX: list[str] = [
    "length",
    "resolution",
    "dropframe"
]


# "error": "A matching value could not be found for the custom dropdown field REI_field_19; Value: 42 bit.\r\n"
class SpecInterface:
    def __init__(self, probe: "MediaProbe"):
        self.probe = probe
        self.all: list[SpecInfo] = self._create_specinfo()
        self.found: list[SpecInfo] = []
        self.notfound: list[SpecInfo] = []
        self._find()

    def _create_specinfo(self) -> list[SpecInfo]:
        simple = [SpecInfo(spec, *SPEC_PROBE_MAP_SIMPLE[spec]) for spec in SPEC_PROBE_MAP_SIMPLE]
        complex = [SpecInfo(spec, probetype="complex") for spec in SPEC_PROBE_MAP_COMPLEX]
        return simple + complex

    def _add_found(self, method: SpecInfo) -> None:
        self.found.append(method)

    def _add_notfound(self, method: SpecInfo) -> None:
        self.notfound.append(method)

    def _find(self) -> None:
        for method in self.all:
            if method.probetype == "simple":
                self._simple(method)
            elif method.probetype == "complex":
                self._complex(method)

    def _simple(self, method: SpecInfo) -> None:
        for track in self.probe.fulljson["tracks"]:
            if track["@type"] == method.track:
                value = track.get(method.field)
                if value:
                    method.minfo_value = value
                    self._add_found(method)
                else:
                    self._add_notfound(method)
                break

    def _complex(self, method: SpecInfo) -> None:
        match method.spec:
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
        method.minfo_value = "True" if is_df else ""
        method.mpulse_value = "Y" if is_df else "N"
        self._add_found(method)