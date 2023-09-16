from ..fieldmaps import SimpleFieldMap, FieldTypeEnum

NEW_ASSET_TEMPLATE = {
    "asset_type_no": {
        "asset_type_no": 2,
    }
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

RESOLUTION_ENUM: dict[str, int] = {
    "4096 x 2160": 1,
    "3840 x 2160": 2,
    "2048 x 1080": 3,
    "1920 x 1080": 4,
    "1280 x 720": 5,
    "720 x 486": 6,
    "720 x 576": 7,
    "4096 x 3112": 8,
    "4096 x 3120": 9
}


ASSET_FIELD_MAPS = {
    "assetno": SimpleFieldMap("assetno", FieldTypeEnum.DICT, ["master_no", "master_no"]),
    "asset_desc": SimpleFieldMap("asset_desc", FieldTypeEnum.STRING, "master_desc"),
    "filename": SimpleFieldMap("filename", FieldTypeEnum.STRING, "REI_field_9"),
    "filepath": SimpleFieldMap("filepath", FieldTypeEnum.STRING, "REI_field_29"),
    "container": SimpleFieldMap("container", FieldTypeEnum.STRING, "REI_field_28"),
    "length": SimpleFieldMap("length", FieldTypeEnum.STRING, "REI_field_21"),
    "resolution": SimpleFieldMap("resolution", FieldTypeEnum.MPULSE_ENUM, ["format_size_no", "format_size_desc"], enumdict=RESOLUTION_ENUM),
    "dropframe": SimpleFieldMap("dropframe", FieldTypeEnum.CHECKMARK, "REI_field_23"),
    "color_space": SimpleFieldMap("color_space", FieldTypeEnum.STRING, "REI_field_11"),
    "eotf": SimpleFieldMap("eotf", FieldTypeEnum.STRING, "REI_field_20"),
    "matrix": SimpleFieldMap("matrix", FieldTypeEnum.STRING, "REI_field_18"),
    "chroma_sub": SimpleFieldMap("chroma_sub", FieldTypeEnum.STRING, "REI_field_17"),
    "frame_rate": SimpleFieldMap("frame_rate", FieldTypeEnum.MPULSE_ENUM, ["frame_rate_no", "frame_rate_desc"], enumdict=FRAMERATE_ENUM),
    "scan_type": SimpleFieldMap("scan_type", FieldTypeEnum.STRING, "REI_field_12"),
    "video_codec": SimpleFieldMap("video_codec", FieldTypeEnum.STRING, "REI_field_24"),
    "video_profile": SimpleFieldMap("video_profile", FieldTypeEnum.STRING, "REI_field_10"),
    "video_bitrate": SimpleFieldMap("video_bitrate", FieldTypeEnum.STRING, "REI_field_15"),
    "video_bitdepth": SimpleFieldMap("video_bitdepth", FieldTypeEnum.STRING, "REI_field_19"),
    "video_bitrate_mode": SimpleFieldMap("video_bitrate_mode", FieldTypeEnum.STRING, "REI_field_26"),
    "audio_codec": SimpleFieldMap("audio_codec", FieldTypeEnum.STRING, "REI_field_27"),
    "audio_bitrate": SimpleFieldMap("audio_bitrate", FieldTypeEnum.STRING, "REI_field_16"),
    "audio_bitdepth": SimpleFieldMap("audio_bitdepth", FieldTypeEnum.STRING, "REI_field_14"),
    "audio_bitrate_mode": SimpleFieldMap("audio_bitrate_mode", FieldTypeEnum.STRING, "REI_field_25"),
    "audio_samplerate": SimpleFieldMap("audio_samplerate", FieldTypeEnum.STRING, "REI_field_22")
}