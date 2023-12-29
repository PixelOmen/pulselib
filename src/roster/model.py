from .rosterfieldmaps import ROSTER_FIELD_MAPS

class RosterTimeOff:
    def __init__(self, jdict: dict):
        self.jdict = jdict
        self.name = ROSTER_FIELD_MAPS["resource"].read(jdict)
        self.code = ROSTER_FIELD_MAPS["code"].read(jdict)
        self.group = ROSTER_FIELD_MAPS["group"].read(jdict)
        self.group_code = ROSTER_FIELD_MAPS["group_code"].read(jdict)
        self.start = ROSTER_FIELD_MAPS["start"].read(jdict)
        self.end = ROSTER_FIELD_MAPS["end"].read(jdict)
        self.trx_no = ROSTER_FIELD_MAPS["trx_no"].read(jdict)
        self.time_off_type = ROSTER_FIELD_MAPS["time_off_type"].read(jdict)
        self.time_off_type_no = ROSTER_FIELD_MAPS["time_off_type_no"].read(jdict)