from ..fieldmaps import SimpleFieldMap, FieldTypeEnum

LINGUIST_TEMPLATE = {
    "resource_type_no": 7,
    "labor": "Y"
}

RESOURCE_MAPS = {
    "name": SimpleFieldMap("name", FieldTypeEnum.DICT, ["resource_code", "resource_desc"]),
    "email": SimpleFieldMap("email", FieldTypeEnum.STRING, "email_address"),
    "transrate": SimpleFieldMap("transrate", FieldTypeEnum.STRING, "A_field_1"),
    "qcrate": SimpleFieldMap("qcrate", FieldTypeEnum.STRING, "A_field_2"),
    "notes": SimpleFieldMap("notes", FieldTypeEnum.STRING, "note_no_text"),
    "feedback": SimpleFieldMap("feedback", FieldTypeEnum.STRING, "A_field_82_text"),
    "location": SimpleFieldMap("location", FieldTypeEnum.STRING, "A_field_3"),
    "phone": SimpleFieldMap("phone", FieldTypeEnum.STRING, "A_field_7"),
    "type": SimpleFieldMap("type", FieldTypeEnum.DICT, ["resource_type_no", "resource_type_desc"])
}