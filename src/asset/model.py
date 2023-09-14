from pathlib import Path
from typing import Any, TYPE_CHECKING

from . import asset_requests
from .probe import get_mediainfo
from .specinterface import SpecInterface
from .assetfieldmaps import ASSET_FIELD_MAPS

if TYPE_CHECKING:
    from mediaprobe import MediaProbe

class PathNotFoundError(LookupError):
    def __init__(self, origin: str) -> None:
        super().__init__(f"{origin}: unable to get filepath and/or storage_path")


class Asset:
    def __init__(self, jdict: dict, specinterface: SpecInterface=...) -> None:
        self.jdict = jdict
        self.specinterface = SpecInterface("") if specinterface is ... else specinterface
        self.probe: MediaProbe | None = None
        self._wasprobed = False
        self._file_exists: bool | None = None

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

    def file_exists(self, retry: bool=False) -> bool:
        if not retry and self._file_exists is not None:
            return self._file_exists
        path = self._get_path()
        if not path:
            return False
        try:
            get_mediainfo(str(path))
        except LookupError:
            self._file_exists = False
            return False
        self._file_exists = True
        return True

    def find(self, key: str) -> Any:
        return ASSET_FIELD_MAPS[key].read(self.jdict)

    def probefile(self) -> None:
        if not self.specinterface.mpulse_path:
            filepath = self._get_path()
            if not filepath:
                raise PathNotFoundError("Asset.probe")
            self.specinterface.mpulse_path = str(filepath)
        self.probe = get_mediainfo(self.specinterface.mpulse_path)
        self.specinterface.probefile(self.probe)
        self._wasprobed = True
        self._file_exists = True

    def patch(self) -> None:
        if not self._wasprobed:
            self.probefile()
        assetno = ASSET_FIELD_MAPS["assetno"].read(self.jdict)
        if not assetno:
            raise LookupError("Asset.patch: unable to get assetno")
        patches = []
        for method in self.specinterface.found:
            patches.append(method.patch_op())
        if patches:
            asset_requests.patch(int(assetno), patches)

    def _get_path(self) -> Path | None:
        filename = ASSET_FIELD_MAPS["filename"].read(self.jdict)
        storage_path = ASSET_FIELD_MAPS["storage_path"].read(self.jdict)
        if not filename or not storage_path:
            return None
        return Path(storage_path) / filename