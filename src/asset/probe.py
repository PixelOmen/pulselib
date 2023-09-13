import json
import requests
from urllib import error

from mediaprobe import MediaProbe

from ..config import CONFIG

def get_mediainfo(file: str) -> MediaProbe:
    res = requests.post(url=CONFIG.MEDIAINFO_URL, json={"path": file})
    try:
        resjson = res.json()
    except json.JSONDecodeError:
        raise error.URLError(f"Invalid JSON response from MediaInfo endpoint. Check URL and PORT: {CONFIG.MEDIAINFO_URL}\n{res.text}", file)
    if resjson["error"]:
        raise LookupError(resjson["error"])
    mi = resjson["output"]["mediainfo"]
    return MediaProbe(file, jsondict=mi)