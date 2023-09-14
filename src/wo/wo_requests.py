import json
import requests

from . import WorkOrder
from .. import utils
from ..config import CONFIG

class WorkOrderNotFoundError(Exception):
    def __init__(self, wo_num: int):
        super().__init__(f"wo_requests: Workorder not found: {wo_num}")

class WorkOrderUnknownError(Exception):
    def __init__(self, wo_num: int, err: str):
        super().__init__(f"wo_requests: Unknown error - {wo_num} - {err}")


def gen_query(wo_num: str) -> str:
    return json.dumps({
        "wo_no_seq": wo_num
    })

def make_list_query(query: str) -> list[WorkOrder]:
    fullurl = f"{CONFIG.WO_QUERY_URL}/?query={query}"
    res = requests.get(url=fullurl, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = utils.verify_response(url=fullurl, response=res)
    jbody = json.loads(body)
    return [WorkOrder(jdict) for jdict in jbody]

def get(wo_num: int) -> dict:
    url = f"{CONFIG.WO_URL}/wo_no_seq={str(wo_num)}"
    r = requests.get(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = json.loads(utils.verify_response(url=url, response=r))
    err = body.get("error")
    if err:
        if err.startswith("Alternate key not found:"):
            raise WorkOrderNotFoundError(wo_num)
        else:
            raise WorkOrderUnknownError(wo_num, err)
    return body