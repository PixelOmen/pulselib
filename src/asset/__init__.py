from dataclasses import dataclass

from . import sessions

# "error": "A matching value could not be found for the custom dropdown field REI_field_19; Value: 42 bit.\r\n"

@dataclass
class ProbeMethod:
    spec: str
    track: str=""
    field: str=""
    probetype: str="simple"

COLOR_SPACE_MAP: dict[str, str] = {
    "BT.709": "Rec709",
    "Display P3": "P3-D65",
    "BT.2020": "Rec2020",
    "DCI P3": "DCI-P3"
}

EOTF_MAP: dict [str, str] = {
    "BT.470 System M": "2.2 Gamma",
    "BT.709": "Rec709",
}

BITRATE_MODE_MODE_MAP: dict[str, str] = {
    "VBR": "Variable",
    "CBR": "Constant"
}

FRAMERATE_ENUM = {

}

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
    "video_bitrate": ProbeMethod("video_bitrate", "Video", "BitRate_Mode"),
    "video_bitdepth": ProbeMethod("video_bitdepth", "Video", "BitDepth"),
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
    "bitrate_mode": "builtin",
    "audio_bitrate": "REI_field_16",
    "audio_bitdepth": "REI_field_14",
    "audio_samplerate": "REI_field_22"
}