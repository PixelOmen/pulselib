from typing import Any

from ..asset import Asset
from .wofieldmaps import WO_FIELD_MAPS

class WorkOrder:
    def __init__(self, jdict: dict) -> None:
        self.jdict = jdict
        self.fieldmaps = WO_FIELD_MAPS
        self.assets = self._get_assets()

    def find(self, key: str) -> Any:
        return self.fieldmaps[key].read(self.jdict)
    
    def _get_assets(self) -> list[Asset]:
        asset_dicts: list[dict] | None = self.jdict.get("mo_source")
        if not asset_dicts:
            return []
        return [Asset(adict) for adict in asset_dicts]
