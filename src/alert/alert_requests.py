import json
import requests
from datetime import datetime

from .. import utils
from ..config import CONFIG

class AlertUnknownError(Exception):
    def __init__(self, err: str):
        super().__init__(f"alert_requests: Unknown error - {err}")

def post(jdict: dict) -> None:
    url = f"{CONFIG.ALERT_URL}"
    r = requests.post(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=jdict)
    body = utils.verify_response(url=url, response=r)
    if body:
        jbody = json.loads(body)
        err = jbody.get("error")
        if err:
            raise AlertUnknownError(err)

def simple_alert(to_user: str, note: str, from_user: str=..., date: str=...) -> None:
    if date is ...:
        date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    if from_user is ...:
        from_user = to_user
    jdict = {
        "from_user_id": {
            "from_user_id": from_user
        },
        "to_user_id": {
            "to_user_id": to_user
        },
        "send_date": date,
        "note_text": note
    }
    post(jdict)