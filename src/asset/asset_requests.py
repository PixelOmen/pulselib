import requests
from mediaprobe import MediaProbe
from json import JSONDecodeError

from ..config import CONFIG

def get_mediainfo(file: str, port: int=80):
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