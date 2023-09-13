from pathlib import Path

from .specinterface import SpecInterface
from .asset_requests import get_mediainfo
from .assetfieldmaps import ASSET_FIELD_MAPS


class Asset:
    @classmethod
    def from_interface(cls, specinterface: SpecInterface) -> "Asset":
        jdict = {}
        mpulse_path = Path(specinterface.mpulse_path)
        filename_key = ASSET_FIELD_MAPS["filename"].keys[0]
        storage_path_key = ASSET_FIELD_MAPS["storage_path"].keys[0]
        jdict[filename_key] = mpulse_path.name
        jdict[storage_path_key] = str(mpulse_path.parent)
        return cls(jdict, specinterface)
    
    def __init__(self, jdict: dict, specinterface: SpecInterface=...) -> None:
        self.jdict = jdict
        self.specinterface = specinterface if specinterface is not ... else None

    def init_interface(self) -> None:
        if self.specinterface:
            return
        filepath = self._get_path()
        if not filepath:
            raise LookupError("Asset._init_interface: unable to get filepath and/or storage_path")
        info = get_mediainfo(str(filepath))
        self.specinterface = SpecInterface(str(filepath), info)

    def _get_path(self) -> Path | None:
        filename = ASSET_FIELD_MAPS["filename"].read(self.jdict)
        storage_path = ASSET_FIELD_MAPS["storage_path"].read(self.jdict)
        if not filename or not storage_path:
            return None
        return Path(storage_path) / filename

