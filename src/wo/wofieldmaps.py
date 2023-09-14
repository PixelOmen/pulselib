from ..fieldmaps import SimpleFieldMap, FieldTypeEnum

WO_FIELD_MAPS = {
    "wo_num": SimpleFieldMap("wo_num", FieldTypeEnum.DICT, ["wo_no_seq", "wo_no_seq"]),
    "wo_po": SimpleFieldMap("wo_po", FieldTypeEnum.STRING, "po"),
}