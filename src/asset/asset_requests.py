import json
import requests

from .. import utils
from ..asset import Asset
from ..config import CONFIG


def get(assetno: int) -> Asset:
    url = f"{CONFIG.ASSET_URL}/master_no={str(assetno)}"
    r = requests.get(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = utils.verify_response(url=url, response=r)
    return Asset(json.loads(body))

def patch(url: str, json: list[dict]) -> requests.Response:
    r = requests.patch(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=json)
    return r