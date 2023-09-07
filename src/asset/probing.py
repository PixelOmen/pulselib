from dataclasses import dataclass
from mediaprobe import MediaAttributes

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
class ProbeMethod:
    spec: str
    track: str=""
    field: str=""
    probetype: str="simple"

SPEC_PROBE_MAP: dict[str, ProbeMethod] = {
    "length": ProbeMethod("length", "General", "Duration"),
    "resolution": ProbeMethod("resolution", probetype="complex"),
    "dropframe": ProbeMethod("dropframe", probetype="complex"),
    "color_space": ProbeMethod("color_space", "Video", "colour_primaries"),
    "eotf": ProbeMethod("eotf", "Video", "transfer_characteristics"),
    "matrix": ProbeMethod("matrix", "Video", "matrix_coefficients"),
    "chroma_sub": ProbeMethod("chroma_sub", "Video", "ChromaSubsampling"),
    "frame_rate": ProbeMethod("frame_rate", "Video", "FrameRate"),
    "scan_type": ProbeMethod("scan_type", "Video", "ScanType"),
    "video_codec": ProbeMethod("video_codec", "Video", "Format"),
    "video_profile": ProbeMethod("video_profile", "Video", "Format_Profile"),
    "video_bitrate": ProbeMethod("video_bitrate", "Video", "BitRate"),
    "video_bitdepth": ProbeMethod("video_bitdepth", "Video", "BitDepth"),
    "video_bitrate_mode": ProbeMethod("video_bitrate_mode", "Video", "BitRate_Mode"),
    "audio_bitrate": ProbeMethod("audio_bitrate", "Audio", "BitRate"),
    "audio_bitdepth": ProbeMethod("audio_bitdepth", "Audio", "BitDepth"),
    "audio_bitrate_mode": ProbeMethod("audio_bitrate_mode", "Audio", "BitRate_Mode"),
    "audio_samplerate": ProbeMethod("audio_samplerate", "Audio", "SamplingRate")
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