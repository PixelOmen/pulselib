from ..fieldmaps import SimpleFieldMap, FieldTypeEnum

WO_FIELD_MAPS = {
    "wo_no": SimpleFieldMap("wo_no", FieldTypeEnum.DICT, ["wo_no_seq", "wo_no_seq"]),
    "wo_po": SimpleFieldMap("wo_po", FieldTypeEnum.STRING, "po"),
}