import json
import requests

from ... import utils
from ...config import CONFIG
from ...errors import SessionNotFoundError, SessionUncaughtError


def query(query: dict) -> list[dict]:
    url = f"{CONFIG.ASSET_SESSION_QUERY_URL}/?query={query}"
    r = requests.get(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = json.loads(utils.verify_response(url=url, response=r))
    if not isinstance(body, list):
        err = body.get("error")
        if err:
            raise SessionUncaughtError(query, err)
    return body

def get(session_no: str) -> dict:
    url = f"{CONFIG.ASSET_SESSION_URL}/session_no={session_no}"
    r = requests.get(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = json.loads(utils.verify_response(url=url, response=r))
    err = body.get("error")
    if err:
        if err.startswith("Alternate key not found:"):
            raise SessionNotFoundError(session_no)
        else:
            raise SessionUncaughtError(session_no, err)
    return body

def post(payload: dict) -> None:
    url = f"{CONFIG.ASSET_SESSION_URL}"
    r = requests.post(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=payload)
    body = utils.verify_response(url=url, response=r)
    if body:
        jbody = json.loads(body)
        err = jbody.get("error")
        if err:
            raise SessionUncaughtError(payload, err)
        
def patch(session_no: str, updatelist: list[dict]) -> None:
    url = f"{CONFIG.ASSET_SESSION_URL}/session_no={session_no}"
    r = requests.patch(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=updatelist)
    body = utils.verify_response(url=url, response=r)
    if body:
        jbody = json.loads(body)
        err = jbody.get("error")
        if err:
            raise SessionUncaughtError(session_no, err)

def post_issues(session_no: str, issues: list[dict]) -> None:
    url = f"{CONFIG.ASSET_SESSION_URL}/session_no={session_no}/im_session_issue"
    r = requests.post(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=issues)
    body = utils.verify_response(url=url, response=r)
    if body:
        jbody = json.loads(body)
        err = jbody.get("error")
        if err:
            raise SessionUncaughtError(session_no, err)