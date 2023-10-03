from pathlib import Path
from typing import Any, TYPE_CHECKING

from ..errors import (
    AssetExistsError,
    AssetPathNotFoundError,
    AssetRefreshError,
    MultipleAssetsFoundError
)

from .probe import get_mediainfo
from . import asset_requests, audio
from .specinterface import SpecInterface
from .assetfieldmaps import ASSET_FIELD_MAPS, NEW_ASSET_TEMPLATE

if TYPE_CHECKING:
    from mediaprobe import MediaProbe

class Asset:
    @staticmethod
    def _set_path_from_interface(jdict: dict, interface: SpecInterface) -> None:
        path = Path(interface.path)
        filename_key = ASSET_FIELD_MAPS["filename"].keys[0]
        filepath_key = ASSET_FIELD_MAPS["filepath"].keys[0]
        jdict[filename_key] = path.name
        jdict[filepath_key] = str(path.parent)

    @classmethod
    def from_interface(cls, specinterface: SpecInterface) -> "Asset":
        jdict = {}
        cls._set_path_from_interface(jdict, specinterface)
        return cls(jdict, specinterface)
    
    def __init__(self, jdict: dict, specinterface: SpecInterface=...) -> None:
        self.jdict = jdict
        self.specinterface = SpecInterface("") if specinterface is ... else specinterface
        self.assetno: str | None = ASSET_FIELD_MAPS["assetno"].read(self.jdict)
        self.probe: MediaProbe | None = None
        self.wo_seq: int | None = None
        self._wasprobed = False
        self._file_exists: bool | None = None

    def set_path(self, path: str) -> None:
        self.specinterface.set_path(path)
        self._set_path_from_interface(self.jdict, self.specinterface)

    def get_path(self) -> Path | None:
        if self.specinterface.path:
            return Path(self.specinterface.path)
        else:
            return self._get_path()

    def refresh(self) -> None:
        if self.assetno:
            self.jdict = asset_requests.get(self.assetno)
        else:
            results = self.get_asset()
            if not results:
                raise AssetRefreshError(self.specinterface.path)
            self.jdict = results
            assetno = ASSET_FIELD_MAPS["assetno"].read(results)
            if not assetno:
                raise LookupError(f"Unable to get assetno: {self.specinterface.path}")
            self.assetno = assetno

    def file_exists(self, retry: bool=False) -> bool:
        if not retry and self._file_exists is not None:
            return self._file_exists
        if self.specinterface.path:
            path = Path(self.specinterface.path)
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
        if not self.specinterface.path:
            filepath = self._get_path()
            if not filepath:
                raise AssetPathNotFoundError("Asset.probe")
            self.specinterface.set_path(str(filepath))
        self.probe = get_mediainfo(self.specinterface.path)
        self.specinterface.probefile(self.probe)
        self._wasprobed = True
        self._file_exists = True

    def patch(self) -> None:
        if not self.assetno:
            raise RuntimeError(f"Attemped to patch asset w/o assetno: {self.specinterface.path}")
        if not self._wasprobed:
            self.probefile()
        asset_requests.patch(self.assetno, self.specinterface.patch_ops())

    def post_new(self, audiolayout: bool=True) -> None:
        if self.assetno:
            raise AssetExistsError(f"Assetno: {self.assetno} - {self.specinterface.path}")
        else:
            exists = self.get_asset()
            if exists:
                assetno = ASSET_FIELD_MAPS["assetno"].read(exists)
                raise AssetExistsError(f"Assetno: {assetno} - {self.specinterface.path}")
            
        if not self._wasprobed:
            self.probefile()

        jdict = self.specinterface.makejdict()
        jdict.update(NEW_ASSET_TEMPLATE)

        fullpath = Path(self.specinterface.path)
        jdict.update(ASSET_FIELD_MAPS["filename"].makejdict(fullpath.name))
        jdict.update(ASSET_FIELD_MAPS["filepath"].makejdict(str(fullpath.parent)))
        jdict.update(ASSET_FIELD_MAPS["asset_desc"].makejdict(fullpath.name[:60]))

        asset_requests.post(jdict, self.specinterface.path)

        if audiolayout:
            self._audio()

    def get_asset(self) -> dict:
        filename_key = ASSET_FIELD_MAPS["filename"].keys
        filepath_key = ASSET_FIELD_MAPS["filepath"].keys
        if self.specinterface.path:
            mpulse_path = Path(self.specinterface.path)
            filename = mpulse_path.name
            filepath = str(mpulse_path.parent)
            query = {filename_key: filename, filepath_key: filepath}
        else:
            fullpath = self._get_path()
            if not fullpath:
                raise AssetPathNotFoundError(f"Asset._find_asset: {self.assetno} - {self.specinterface.path}")
            query = {filename_key: fullpath.name, filepath_key: str(fullpath.parent)}

        results = asset_requests.query(query)
        if len(results) > 1:
            raise MultipleAssetsFoundError(query, results)
        elif len(results) < 1:
            return {}
        return results[0]
    
    def _audio(self) -> None:
        self.refresh()
        if not self.assetno:
            raise AssetRefreshError(f"Asset._audio: Unable to get assetno after refresh: {self.specinterface.path}")
        if not self.probe:
            raise AssetRefreshError(f"Asset._audio: Unable to get probe after refresh: {self.specinterface.path}")
        audiolayout = audio.asset_audio_dict(self.assetno, self.probe)
        asset_requests.post_audio(self.assetno, audiolayout)

    def _get_path(self) -> Path | None:
        try:
            filename = ASSET_FIELD_MAPS["filename"].read(self.jdict)
            filepath = ASSET_FIELD_MAPS["filepath"].read(self.jdict)
        except KeyError:
            return None
        if not filename or not filepath:
            return None
        return Path(filepath) / filename