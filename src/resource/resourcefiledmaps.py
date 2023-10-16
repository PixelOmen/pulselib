from ..fieldmaps import SimpleFieldMap, FieldTypeEnum

LINGUIST_TEMPLATE = {
    "default_group_code": {
        "default_group_code": "LINGS",
        "external_key": None,
        "group_code": "LINGS",
        "group_desc": "Linguists"
    }
}

LINGUIST_MAPS = {
    "name": SimpleFieldMap("name", FieldTypeEnum.STRING, "resource_desc"),
    "email": SimpleFieldMap("email", FieldTypeEnum.STRING, "email_address"),
    "transrate": SimpleFieldMap("transrate", FieldTypeEnum.STRING, "A_field_1"),
    "qcrate": SimpleFieldMap("qcrate", FieldTypeEnum.STRING, "A_field_2"),
    "note": SimpleFieldMap("note", FieldTypeEnum.STRING, "note_no_text"),
    "feedback": SimpleFieldMap("feedback", FieldTypeEnum.STRING, "A_field_82_text"),
}