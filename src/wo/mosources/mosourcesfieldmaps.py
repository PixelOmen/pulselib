from ...fieldmaps import SimpleFieldMap, FieldTypeEnum

MOSOURCES_FIELD_MAPS = {
    "source_no": SimpleFieldMap("source_no", FieldTypeEnum.DICT, ["master_no", "master_no"])
}