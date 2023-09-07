from dataclasses import dataclass
from mediaprobe import MediaProbe

# "error": "A matching value could not be found for the custom dropdown field REI_field_19; Value: 42 bit.\r\n"

COLOR_SPACE_MAP: dict[str, str] = {
    "BT.709": "Rec709",
    "Display P3": "P3-D65",
    "BT.2020": "Rec2020",
    "DCI P3": "DCI-P3"
}

# Resolve does not include the color primaries metadata when using 2.4 gamma
EOTF_MAP: dict [str | None, str] = {
    "BT.470 System M": "2.2 Gamma",
    None: "2.4 Gamma",
    "BT.709": "Rec709",
    "PQ": "PQ"
}

MATRIX_MAP: dict[str, str] = {
    "BT.709": "Rec709",
    "BT.2020 non-constant": "Rec2020"
}

# From Frame Rates table in MetaVault->Setup
FRAMERATE_ENUM: dict[str, int] = {
    "23.976": 10,
    "24": 11,
    "25": 12,
    "29.97": 13,
    "30": 14,
    "48": 15,
    "50": 16,
    "59.94": 17,
    "60": 18
}

@dataclass
class SpecMethod:
    spec: str
    track: str=""
    field: str=""
    probetype: str="simple"
    value: str=""

SPEC_PROBE_MAP: dict[str, tuple[str, str, str]] = {
    "length": ("General", "Duration", "simple"),
    "resolution": ("", "simple", "complex"),
    "dropframe": ("", "simple", "complex"),
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

SPEC_FIELD_MAP: dict[str, str] = {
    "length": "REI_field_21",
    "resolution": "builtin",
    "dropframe": "REI_field_23",
    "color_space": "REI_field_11",
    "eotf": "REI_field_20",
    "matrix": "REI_field_18",
    "chroma_sub": "REI_field_17",
    "frame_rate": "builtin",
    "scan_type": "REI_field_12",
    "video_codec": "builtin",
    "video_profile": "REI_field_10",
    "video_bitrate": "REI_field_15",
    "video_bitdepth": "REI_field_19",
    "video_bitrate_mode": "REI_field_26",
    "audio_bitrate": "REI_field_16",
    "audio_bitdepth": "REI_field_14",
    "audio_bitrate_mode": "REI_field_25",
    "audio_samplerate": "REI_field_22"
}


class SpecInterface:
    def __init__(self, probe: MediaProbe):
        self.probe = probe
        self.specs: list[SpecMethod] = self._methods()

    def _methods(self) -> list[SpecMethod]:
        return [SpecMethod(spec, *SPEC_PROBE_MAP[spec]) for spec in SPEC_PROBE_MAP]

    def _find(self) -> None:
        for method in self.specs:
            if method.probetype == "simple":
                self._simple(method)
            elif method.probetype == "complex":
                self._complex(method)

    def _simple(self, method: SpecMethod) -> None:
        for track in self.probe.fulljson["tracks"]:
            if track["@type"] == method.track:
                value = track.get(method.field)
                if value:
                    method.value = value

    def _complex(self, method: SpecMethod) -> None:
        pass