from typing import Any
from dataclasses import dataclass

from ..errors import AssetExistsError
from ..asset import Asset, asset_requests

from . import wo_requests
from .sources import WOSource
from .wofieldmaps import WO_FIELD_MAPS

@dataclass
class UpdateResults:
    updated: list[str]
    errors: list[str]

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
            if source.asset_no:
                jdict = asset_requests.get(source.asset_no)
                assets.append(Asset(jdict))
        self.assets = assets
        self._assetspulled = True

    def sources_ready(self) -> list[WOSource]:
        ready_to_create: list[WOSource] = []
        for source in self.sources:
            if source.created and not source.asset_no and source.fullpath:
                ready_to_create.append(source)
        return ready_to_create

    def make_asset(self, seq_no: int, use_existing: bool=True, force: bool=False) -> str:
        for source in self.sources:
            if source.seq_no != seq_no:
                continue
            asset = source.new_asset(force=force)
            try:
                asset.post_new()
            except AssetExistsError as e:
                if not use_existing:
                    raise e
            asset.refresh()
            asset.wo_seq = source.seq_no
            self.assets.append(asset)
            if not asset.assetno:
                msg = f"Workorder.make_asset: Asset did not receive assetno, source: {seq_no}"
                raise RuntimeError(msg)
            return asset.assetno
        raise ValueError(f"Workorder.make_asset: Unable to find source: {seq_no}")

    def sources_to_assets(self) -> None:
        ready = self.sources_ready()
        for source in ready:
            self.make_asset(source.seq_no)

    def update_sources(self) -> UpdateResults:
        updated = []
        errors = []
        for asset in self.assets:
            if not asset.wo_seq:
                continue
            for source in self.sources:
                if source.seq_no != asset.wo_seq:
                    continue
                try:
                    if not asset.assetno:
                        msg = f"Workorder.update_sources: Asset has no assetno: {asset.specinterface.path}"
                        raise RuntimeError(msg)
                    wo_requests.patch_source(self.wo_no, source.seq_no, source.patch_op(asset.assetno))
                except Exception as e:
                    errors.append(f"{type(e).__name__}: {e}")
                else:
                    updated.append(asset.specinterface.path)
                finally:
                    break
        return UpdateResults(updated, errors)
    
    def _get_sources(self) -> list[WOSource]:
        asset_dicts: list[dict] | None = self.jdict.get("mo_source")
        if not asset_dicts:
            return []
        return [WOSource(adict) for adict in asset_dicts]