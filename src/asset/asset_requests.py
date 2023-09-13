import requests
from typing import TYPE_CHECKING
from json import JSONDecodeError

from mediaprobe import MediaProbe

from ..config import CONFIG

if TYPE_CHECKING:
    from ..asset import Asset

def get_mediainfo(file: str, port: int=80) -> MediaProbe:
    url = CONFIG.MEDIAINFO_URL.replace("PORT", str(port))
    res = requests.post(url=url, json={"path": file})
    try:
        resjson = res.json()
    except JSONDecodeError:
        raise LookupError(f"Invalid JSON response from MediaInfo endpoint. Check URL and PORT: {url}\n{res.text}")
    if resjson["error"]:
        raise LookupError(resjson["error"])
    mi = resjson["output"]["mediainfo"]
    return MediaProbe(file, jsondict=mi)

def patch(url: str, json: list[dict]) -> requests.Response:
    r = requests.patch(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=json)
    return r