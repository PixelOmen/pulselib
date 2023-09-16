from typing import Any
from pathlib import Path

from ...asset import Asset, SpecInterface

from .wosourcesfieldmaps import WOSOURCES_FIELD_MAPS

class WOSource:
    def __init__(self, jdict: dict) -> None:
        self.jdict = jdict
        self.fieldmaps = WOSOURCES_FIELD_MAPS
        self.source_no: str = self.find_key("source_no")
        self.asset_no: str = self.find_key("asset_no")
        self.filepath: str = self.find_key("filepath")
        self.filename: str = self.find_key("filename")
        self.created: bool = self.find_key("created")

    def find_key(self, key: str) -> Any:
        return self.fieldmaps[key].read(self.jdict)

    def make_asset(self) -> Asset:
        if not self.filepath or not self.filename:
            raise LookupError(f"Unable to get filepath and/or filename from wosource: {self.source_no}")
        if not self.created:
            raise ValueError(f"Source {self.source_no} has not been created")
        full_path = Path(self.filepath) / self.filename
        specinterface = SpecInterface(str(full_path))
        return Asset.from_interface(specinterface)