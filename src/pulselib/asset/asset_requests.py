import json
import requests

from ..errors import AssetNotFoundError, AssetUncaughtError, AssetAudioUncaughtError

from .. import utils
from ..config import CONFIG


def query(query: dict) -> list[dict]:
    url = f"{CONFIG.ASSET_QUERY_URL}/?query={query}"
    r = requests.get(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = json.loads(utils.verify_response(url=url, response=r))
    if not isinstance(body, list):
        err = body.get("error")
        if err:
            raise AssetUncaughtError(query, err)
    return body

def get(assetno: str) -> dict:
    url = f"{CONFIG.ASSET_URL}/master_no={str(assetno)}"
    r = requests.get(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = json.loads(utils.verify_response(url=url, response=r))
    err = body.get("error")
    if err:
        if err.startswith("Alternate key not found:"):
            raise AssetNotFoundError(assetno)
        else:
            raise AssetUncaughtError(assetno, err)
    return body

def patch(assetno: str, patchlist: list[dict]) -> None:
    url = f"{CONFIG.ASSET_URL}/master_no={str(assetno)}"
    r = requests.patch(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=patchlist)
    body = utils.verify_response(url=url, response=r)
    if body:
        jbody = json.loads(body)
        err = jbody.get("error")
        if err:
            if err.startswith("Alternate key not found:"):
                raise AssetNotFoundError(assetno)
            else:
                raise AssetUncaughtError(assetno, err)

def post(jdict: dict, filename: str) -> None:
    url = f"{CONFIG.ASSET_URL}"
    r = requests.post(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=jdict)
    body = utils.verify_response(url=url, response=r)
    if body:
        jbody = json.loads(body)
        err = jbody.get("error")
        if err:
            raise AssetUncaughtError(filename, err)

def get_audio(asset_no: str) -> list[dict]:
    url = f"{CONFIG.ASSET_URL}/master_no={str(asset_no)}/lib_master_audio"
    r = requests.get(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = json.loads(utils.verify_response(url=url, response=r))
    if not isinstance(body, list):
        err = body.get("error")
        if err:
            raise AssetAudioUncaughtError(asset_no, err)
    return body

def post_audio(asset_no: str, info: list[dict]) -> None:
    url = f"{CONFIG.ASSET_URL}/master_no={str(asset_no)}/lib_master_audio"
    r = requests.post(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=info)
    body = utils.verify_response(url=url, response=r)
    if body:
        jbody = json.loads(body)
        err = jbody.get("error")
        if err:
            raise AssetAudioUncaughtError(asset_no, err)

def patch_audio(asset_no: str, audio_list_no: str, patchlist: list[dict]) -> None:
    url = f"{CONFIG.ASSET_URL}/master_no={str(asset_no)}/lib_master_audio/audio_channel_no={str(audio_list_no)}"
    r = requests.patch(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=patchlist)
    body = utils.verify_response(url=url, response=r)
    if body:
        jbody = json.loads(body)
        err = jbody.get("error")
        if err:
            raise AssetAudioUncaughtError(asset_no, err)