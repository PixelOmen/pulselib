from typing import Any

from ..asset import Asset, asset_requests

from . import wo_requests
from .sources import WOSource
from .wofieldmaps import WO_FIELD_MAPS

class WorkOrder:
    def __init__(self, jdict: dict) -> None:
        self.jdict = jdict
        self.fieldmaps = WO_FIELD_MAPS
        self.wo_no: str = self.find_key("wo_no")
        self.sources = self._get_sources()
        self.assets: list[Asset] = []
        self._assetspulled = False

    def refresh(self) -> None:
        self.jdict = wo_requests.get(self.wo_no)
        self.sources = self._get_sources()
        if self._assetspulled:
            self.pull_assets(refresh=True)

    def find_key(self, key: str) -> Any:
        return self.fieldmaps[key].read(self.jdict)
    
    def pull_assets(self, refresh: bool=False) -> None:
        if refresh:
            self._assetspulled = False
        elif self._assetspulled:
            return
        assets = []
        for source in self.sources:
            source_no = source.find_key("source_no")
            if source_no:
                jdict = asset_requests.get(source_no)
                assets.append(Asset(jdict))
        self.assets = assets
        self._assetspulled = True

    # -----------  Not correct, need to fix -----------
    # def make_asset(self, source_no: str) -> str:
    #     for source in self.sources:
    #         if source.find("source_no") == source_no:
    #             asset = source.make_asset()
    #             asset.post_new()
    #             self.refresh()
    #     raise ValueError(f"Unable to find source: {source_no}")
    
    def _get_sources(self) -> list[WOSource]:
        asset_dicts: list[dict] | None = self.jdict.get("mo_source")
        if not asset_dicts:
            return []
        return [WOSource(adict) for adict in asset_dicts]