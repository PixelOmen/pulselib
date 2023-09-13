from typing import Any
from pathlib import Path

from .probe import get_mediainfo
from .specinterface import SpecInterface
from .assetfieldmaps import ASSET_FIELD_MAPS


class Asset:
    def __init__(self, jdict: dict, specinterface: SpecInterface=...) -> None:
        self.jdict = jdict
        self.specinterface = SpecInterface("") if specinterface is ... else specinterface

    @classmethod
    def from_interface(cls, specinterface: SpecInterface) -> "Asset":
        jdict = {}
        mpulse_path = Path(specinterface.mpulse_path)
        filename_key = ASSET_FIELD_MAPS["filename"].keys[0]
        storage_path_key = ASSET_FIELD_MAPS["storage_path"].keys[0]
        jdict[filename_key] = mpulse_path.name
        jdict[storage_path_key] = str(mpulse_path.parent)
        return cls(jdict, specinterface)

    def asset_exists(self) -> bool:
        if ASSET_FIELD_MAPS["assetno"].read(self.jdict):
            return True
        return False

    def file_exists(self) -> bool:
        path = self._get_path()
        if not path:
            return False
        try:
            get_mediainfo(str(path))
        except LookupError:
            return False
        return True

    def find(self, key: str) -> Any:
        return ASSET_FIELD_MAPS[key].read(self.jdict)

    def probe(self, port: int=80) -> None:
        if not self.specinterface.mpulse_path:
            filepath = self._get_path()
            if not filepath:
                raise LookupError("Asset.probe: unable to get filepath and/or storage_path")
            self.specinterface.mpulse_path = str(filepath)
        probe = get_mediainfo(self.specinterface.mpulse_path)
        self.specinterface.probe(probe)

    def _get_path(self) -> Path | None:
        filename = ASSET_FIELD_MAPS["filename"].read(self.jdict)
        storage_path = ASSET_FIELD_MAPS["storage_path"].read(self.jdict)
        if not filename or not storage_path:
            return None
        return Path(storage_path) / filename

