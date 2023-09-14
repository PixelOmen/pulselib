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
    err = resjson.get("error")
    if err:
        if err.startswith("Not a valid file path:"):
            raise FileNotFoundError(err)
        else:
            raise LookupError(err)
    mi = resjson["output"]["mediainfo"]
    return MediaProbe(file, jsondict=mi)