import json
import requests
from datetime import datetime

from ..errors import AlertUncaughtError

from .. import utils
from ..config import CONFIG


def post(jdict: dict) -> None:
    url = f"{CONFIG.ALERT_URL}"
    r = requests.post(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=jdict)
    body = utils.verify_response(url=url, response=r)
    if body:
        jbody = json.loads(body)
        err = jbody.get("error")
        if err:
            raise AlertUncaughtError(err)

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