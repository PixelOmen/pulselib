from typing import Any
from pathlib import Path

from ...asset import Asset, SpecInterface

from .wosourcesfieldmaps import WOSOURCES_FIELD_MAPS

class WOSource:
    def __init__(self, jdict: dict) -> None:
        self.jdict = jdict
        self.fieldmaps = WOSOURCES_FIELD_MAPS
        self.seq_no: str = self.find_key("seq_no")
        self.source_no: str = self.find_key("source_no")
        self.fullpath: str = self.find_key("fullpath")
        self.asset_no: str = self.find_key("asset_no")
        self.created: bool = self.find_key("created")
        if self.fullpath is not None:
            self.fullpath = self.fullpath.replace("\"", "")

    def find_key(self, key: str) -> Any:
        return self.fieldmaps[key].read(self.jdict)

    def new_asset(self) -> Asset:
        if not self.fullpath:
            raise LookupError(f"Unable to get path from wosource: {self.source_no}")
        if not self.created:
            raise ValueError(f"Source {self.source_no} has not been created")
        specinterface = SpecInterface(self.fullpath)
        return Asset.from_interface(specinterface)

    def patch_op(self, assetno: str) -> dict:
        return self.fieldmaps["asset_no"].patch_op(assetno)