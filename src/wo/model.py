from typing import Any

from ..asset import Asset, asset_requests
from .wofieldmaps import WO_FIELD_MAPS
from .mosources import MOSOURCES_FIELD_MAPS, MOSource

class WorkOrder:
    def __init__(self, jdict: dict) -> None:
        self.jdict = jdict
        self.fieldmaps = WO_FIELD_MAPS
        self.sources = self._get_sources()
        self.assets = self._get_assets()

    def find(self, key: str) -> Any:
        return self.fieldmaps[key].read(self.jdict)
    
    def _get_sources(self) -> list[MOSource]:
        asset_dicts: list[dict] | None = self.jdict.get("mo_source")
        if not asset_dicts:
            return []
        return [MOSource(adict) for adict in asset_dicts]

    def _get_assets(self) -> list[Asset]:
        assets = []
        for source in self.sources:
            source_no = source.find("source_no")
            if source_no:
                jdict = asset_requests.get(int(source_no))
                assets.append(Asset(jdict))
        return assets
