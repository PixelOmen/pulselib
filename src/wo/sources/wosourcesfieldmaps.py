from ...fieldmaps import SimpleFieldMap, FieldTypeEnum

WOSOURCES_FIELD_MAPS = {
    "wo_no": SimpleFieldMap("wo_no", FieldTypeEnum.DICT, ["wo_no_seq", "wo_no_seq"]),
    "seq_no": SimpleFieldMap("source_no", FieldTypeEnum.STRING, "dsp_seq"),
    "source_no": SimpleFieldMap("source_no", FieldTypeEnum.DICT, ["source_no", "source_no"]),
    "asset_no": SimpleFieldMap("asset_no", FieldTypeEnum.DICT, ["master_no", "master_no"]),
    "filepath": SimpleFieldMap("filepath", FieldTypeEnum.STRING, "WOS_field_1"),
    "filename": SimpleFieldMap("filename", FieldTypeEnum.STRING, "WOS_field_2"),
    "created": SimpleFieldMap("created", FieldTypeEnum.CHECKMARK, "WOS_field_3")
}