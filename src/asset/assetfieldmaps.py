from ..fieldmaps import SimpleFieldMap, FieldTypeEnum

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