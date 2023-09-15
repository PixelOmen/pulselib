from typing import Any

from .mosourcesfieldmaps import MOSOURCES_FIELD_MAPS

class MOSource:
    def __init__(self, jdict: dict) -> None:
        self.jdict = jdict
        self.fieldmaps = MOSOURCES_FIELD_MAPS

    def find(self, key: str) -> Any:
        return self.fieldmaps[key].read(self.jdict)