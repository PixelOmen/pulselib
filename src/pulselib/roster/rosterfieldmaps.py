from ..fieldmaps import SimpleFieldMap, FieldTypeEnum

ROSTER_CODES = {
    "Maintenance": 6
}

ROSTER_FIELD_MAPS = {
    "resource": SimpleFieldMap("resource", FieldTypeEnum.STRING, "resource_desc"),
    "code": SimpleFieldMap("code", FieldTypeEnum.DICT, ["resource_code", "resource_code"]),
    "group": SimpleFieldMap("group", FieldTypeEnum.STRING, "group_desc"),
    "group_code": SimpleFieldMap("group_code", FieldTypeEnum.DICT, ["group_code", "group_code"]),
    "start": SimpleFieldMap("start", FieldTypeEnum.STRING, "trx_begin_dt"),
    "end": SimpleFieldMap("end", FieldTypeEnum.STRING, "trx_end_dt"),
    "trx_no": SimpleFieldMap("trx_no", FieldTypeEnum.DICT, ["trx_no", "trx_no"]),
    "time_off_type": SimpleFieldMap("time_off_type", FieldTypeEnum.DICT, ["time_off_type_no", "time_off_type_desc"]),
    "time_off_type_no": SimpleFieldMap("time_off_type_no", FieldTypeEnum.DICT, ["time_off_type_no", "time_off_type_no"])
}