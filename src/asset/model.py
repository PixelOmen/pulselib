from pathlib import Path
from typing import Any, TYPE_CHECKING

from . import asset_requests
from .probe import get_mediainfo
from .specinterface import SpecInterface
from .assetfieldmaps import ASSET_FIELD_MAPS, NEW_ASSET_TEMPLATE

if TYPE_CHECKING:
    from mediaprobe import MediaProbe

class AssetPathNotFoundError(LookupError):
    def __init__(self, origin: str) -> None:
        super().__init__(f"{origin}: unable to get filepath and/or filename")

class AssetNotFoundError(LookupError):
    def __init__(self, id: dict | str) -> None:
        super().__init__(f"Asset not found: {id}")

class AssetExistsError(Exception):
    def __init__(self, path: str) -> None:
        super().__init__(f"Asset already exists: {path}")

class MultipleAssetsFoundError(Exception):
    def __init__(self, query: dict) -> None:
        super().__init__(f"Multiple assets found: {query}")


class Asset:
    def __init__(self, jdict: dict, specinterface: SpecInterface=...) -> None:
        self.jdict = jdict
        self.specinterface = SpecInterface("") if specinterface is ... else specinterface
        self.assetno: str | None = ASSET_FIELD_MAPS["assetno"].read(self.jdict)
        self.probe: MediaProbe | None = None
        self._wasprobed = False
        self._file_exists: bool | None = None

    @classmethod
    def from_interface(cls, specinterface: SpecInterface) -> "Asset":
        jdict = {}
        mpulse_path = Path(specinterface.mpulse_path)
        filename_key = ASSET_FIELD_MAPS["filename"].keys[0]
        filepath_ley = ASSET_FIELD_MAPS["filepath"].keys[0]
        jdict[filename_key] = mpulse_path.name
        jdict[filepath_ley] = str(mpulse_path.parent)
        return cls(jdict, specinterface)

    def refresh(self) -> None:
        if self.assetno:
            self.jdict = asset_requests.get(self.assetno)
        else:
            results = self.get_asset()
            if not results:
                raise AssetNotFoundError(f"Attemped to refresh non-existent asset: {self.specinterface.mpulse_path}")
            self.jdict = results
            assetno = ASSET_FIELD_MAPS["assetno"].read(results)
            if not assetno:
                raise LookupError(f"Unable to get assetno: {self.specinterface.mpulse_path}")
            self.assetno = assetno

    def file_exists(self, retry: bool=False) -> bool:
        if not retry and self._file_exists is not None:
            return self._file_exists
        if self.specinterface.mpulse_path:
            path = Path(self.specinterface.mpulse_path)
        else:
            path = self._get_path()
        if not path:
            return False
        try:
            get_mediainfo(str(path))
        except FileNotFoundError:
            self._file_exists = False
            return False
        self._file_exists = True
        return True

    def find_key(self, key: str) -> Any:
        return ASSET_FIELD_MAPS[key].read(self.jdict)

    def probefile(self) -> None:
        if not self.specinterface.mpulse_path:
            filepath = self._get_path()
            if not filepath:
                raise AssetPathNotFoundError("Asset.probe")
            self.specinterface.mpulse_path = str(filepath)
        self.probe = get_mediainfo(self.specinterface.mpulse_path)
        self.specinterface.probefile(self.probe)
        self._wasprobed = True
        self._file_exists = True

    def patch(self) -> None:
        if not self.assetno:
            raise RuntimeError(f"Attemped to patch asset w/o assetno: {self.specinterface.mpulse_path}")
        if not self._wasprobed:
            self.probefile()
        patches = []
        for specinfo in self.specinterface.all:
            patches.append(specinfo.patch_op())
        if patches:
            asset_requests.patch(self.assetno, patches)

    def post_new(self) -> None:
        if self.assetno:
            raise AssetExistsError(f"Attemped to create existing asset: Assetno: {self.assetno} - {self.specinterface.mpulse_path}")
        else:
            exists = self.get_asset()
            if exists:
                assetno = ASSET_FIELD_MAPS["assetno"].read(exists)
                raise AssetExistsError(f"Attemped to create existing asset: Assetno: {assetno} - {self.specinterface.mpulse_path}")
            
        if not self._wasprobed:
            self.probefile()

        jdict = {}
        for specinfo in self.specinterface.all:
            jdict.update(specinfo.makejdict())
        jdict.update(NEW_ASSET_TEMPLATE)

        fullpath = Path(self.specinterface.mpulse_path)
        filename_key = ASSET_FIELD_MAPS["filename"].keys
        filepath_key = ASSET_FIELD_MAPS["filepath"].keys
        desc_key = ASSET_FIELD_MAPS["asset_desc"].keys
        jdict[filename_key] = fullpath.name
        jdict[filepath_key] = str(fullpath.parent)
        jdict[desc_key] = fullpath.name

        asset_requests.post(jdict, self.specinterface.mpulse_path)

    def get_asset(self) -> dict:
        filename_key = ASSET_FIELD_MAPS["filename"].keys
        filepath_key = ASSET_FIELD_MAPS["filepath"].keys
        if self.specinterface.mpulse_path:
            mpulse_path = Path(self.specinterface.mpulse_path)
            filename = mpulse_path.name
            filepath = str(mpulse_path.parent)
            query = {filename_key: filename, filepath_key: filepath}
        else:
            fullpath = self._get_path()
            if not fullpath:
                raise AssetPathNotFoundError(f"Asset._find_asset: {self.assetno} - {self.specinterface.mpulse_path}")
            query = {filename_key: fullpath.name, filepath_key: str(fullpath.parent)}

        results = asset_requests.query(query)
        if len(results) > 1:
            raise MultipleAssetsFoundError(query)
        elif len(results) < 1:
            return {}
        return results[0]            

    def _get_path(self) -> Path | None:
        try:
            filename = ASSET_FIELD_MAPS["filename"].read(self.jdict)
            filepath = ASSET_FIELD_MAPS["filepath"].read(self.jdict)
        except KeyError:
            return None
        if not filename or not filepath:
            return None
        return Path(filepath) / filename