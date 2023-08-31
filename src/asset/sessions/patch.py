import json
import requests

from ... import utils
from ...config import CONFIG

def patch_po(session_num: str, po_num: str) -> None:
    patch_url = f"{CONFIG.ASSET_SESSION_URL}/session_no={session_num}"
    patch = [{
        "op": "replace",
        "path": "REIQC_field_44",
        "value": po_num
    }]
    res = requests.patch(url=patch_url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=patch)
    utils.verify_response(url=patch_url, response=res)
    if res.text != "":
        jbody = json.loads(res.text)
        raise LookupError(jbody["error"])