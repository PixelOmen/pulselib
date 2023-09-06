from . import sessions

# "error": "A matching value could not be found for the custom dropdown field REI_field_19; Value: 42 bit.\r\n"

COLOR_SPACE_MAP: dict[str, str] = {
    "BT.709": "Rec709",
    "Display P3": "P3-D65",
    "BT.2020": "Rec2020",
    "DCI P3": "DCI-P3"
}

BITRATE_MODE_MODE_MAP: dict[str, str] = {
    "VBR": "Variable",
    "CBR": "Constant"
}

FRAMERATE_ENUM = {

}

SPEC_FIELD_MAP: dict[str, str] = {
    "length": "REI_field_21",
    "resolution": "builtin",
    "video_codec": "builtin",
    "video_profile": "REI_field_10",
    "color_space": "REI_field_11",
    "eotf": "REI_field_20",
    "matrix_coefficients": "REI_field_18",
    "chroma_subsampling": "REI_field_17",
    "scan_type": "REI_field_12",
    "frame_rate": "builtin",
    "video_bitrate": "REI_field_15",
    "bitrate_mode": "builtin",
    "video_bitdepth": "REI_field_19",
    "audio_bitrate": "REI_field_16",
    "audio_bitdepth": "REI_field_14",
    "audio_samplerate": "REI_field_22"
}

PROBE_SPEC_MAP: dict[str, tuple[str, str]] = {
    "video_codec": ("Video", "Format"),
    "video_profile": ("Video", "Format_Profile"),
    "video_bitrate": ("Video", "BitRate_Mode")
}

PROBE_COMPLEX = [
    "length",
    "resolution",
    "color_space",
    "eotf",
    "matrix_coefficients",
]