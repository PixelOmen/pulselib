from typing import Any
from pathlib import Path

from ...asset import Asset, SpecInterface

from .wosourcesfieldmaps import WOSOURCES_FIELD_MAPS

class WOSource:
    def __init__(self, jdict: dict) -> None:
        self.jdict = jdict
        self.fieldmaps = WOSOURCES_FIELD_MAPS
        self.source_no: str = self.find("source_no")
        self.asset_no: str = self.find("asset_no")
        self.filepath: str = self.find("filepath")
        self.filename: str = self.find("filename")
        self.created: bool = self.find("created")

    def find(self, key: str) -> Any:
        return self.fieldmaps[key].read(self.jdict)

    def make_asset(self) -> Asset:
        if not self.filepath or not self.filename:
            raise LookupError(f"Unable to get filepath and/or filename from source: {self.asset_no}")
        if not self.created:
            raise ValueError(f"Source {self.asset_no} has not been created")
        full_path = Path(self.filepath) / self.filename
        specinterface = SpecInterface(str(full_path))
        return Asset.from_interface(specinterface)