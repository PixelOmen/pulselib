import json
import requests

from ..errors import (
    WorkOrderNotFoundError,
    WorkOrderUncaughtError
)

from .. import utils
from ..config import CONFIG


def gen_query(wo_num: str) -> str:
    return json.dumps({
        "wo_no_seq": wo_num
    })

def query(query: dict) -> list[dict]:
    url = f"{CONFIG.WO_QUERY_URL}/?query={query}"
    r = requests.get(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = json.loads(utils.verify_response(url=url, response=r))
    body = json.loads(utils.verify_response(url=url, response=r))
    if not isinstance(body, list):
        err = body.get("error")
        if err:
            raise WorkOrderUncaughtError(query, err)
    return body
        

def get(wo_num: str) -> dict:
    url = f"{CONFIG.WO_URL}/wo_no_seq={str(wo_num)}"
    r = requests.get(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = json.loads(utils.verify_response(url=url, response=r))
    err = body.get("error")
    if err:
        if err.startswith("Alternate key not found:"):
            raise WorkOrderNotFoundError(wo_num)
        else:
            raise WorkOrderUncaughtError(wo_num, err)
    return body

def patch(wo_no: str, patchlist: list[dict]) -> None:
    url = f"{CONFIG.WO_URL}/wo_no_seq={str(wo_no)}"
    r = requests.patch(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=patchlist)
    body = utils.verify_response(url=url, response=r)
    if body:
        jbody = json.loads(body)
        err = jbody.get("error")
        if err:
            if err.startswith("Alternate key not found:"):
                raise WorkOrderNotFoundError(wo_no)
            else:
                raise WorkOrderUncaughtError(wo_no, err)

def patch_source(wo_no: str, seq_no: int, patchlist: list[dict]) -> None:
    url = f"{CONFIG.WO_URL}/wo_no_seq={str(wo_no)}/mo_source/dsp_seq={str(seq_no)}"
    r = requests.patch(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=patchlist)
    body = utils.verify_response(url=url, response=r)
    if body:
        jbody = json.loads(body)
        err = jbody.get("error")
        if err:
            if err.startswith("Alternate key not found:"):
                raise WorkOrderNotFoundError(wo_no)
            else:
                raise WorkOrderUncaughtError(wo_no, err)