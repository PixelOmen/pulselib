from ...fieldmaps import SimpleFieldMap, FieldTypeEnum

ASSET_SESSION_MAPS = {
    "issues": SimpleFieldMap("issues", FieldTypeEnum.LIST, "im_session_issue"),
    "po": SimpleFieldMap("po", FieldTypeEnum.STRING, "REIQC_field_44")
}

SESSION_ISSUE_MAPS = {
    "event_type": SimpleFieldMap("event_type", FieldTypeEnum.STRING, "REIQCISS_field_2"),
    "tc_in": SimpleFieldMap("tc_in", FieldTypeEnum.STRING, "time_code_in"),
    "tc_out": SimpleFieldMap("tc_out", FieldTypeEnum.STRING, "time_code_out"),
}