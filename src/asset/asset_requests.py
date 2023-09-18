import json
import requests

from .. import utils
from ..config import CONFIG

class AssetNotFoundError(Exception):
    def __init__(self, assetno: str):
        super().__init__(f"asset_requests: Asset not found: {assetno}")

class AssetUnknownError(Exception):
    def __init__(self, assetid: str | dict, err: str):
        super().__init__(f"asset_requests: Unknown error - {assetid} - {err}")


def query(query: dict) -> list[dict]:
    url = f"{CONFIG.ASSET_QUERY_URL}/?query={query}"
    r = requests.get(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = json.loads(utils.verify_response(url=url, response=r))
    if not isinstance(body, list):
        err = body.get("error")
        if err:
            raise AssetUnknownError(query, err)
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
            raise AssetUnknownError(assetno, err)
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
                raise AssetUnknownError(assetno, err)

def post(jdict: dict, filename: str) -> None:
    url = f"{CONFIG.ASSET_URL}"
    r = requests.post(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=jdict)
    body = utils.verify_response(url=url, response=r)
    if body:
        jbody = json.loads(body)
        err = jbody.get("error")
        if err:
            raise AssetUnknownError(filename, err)
        