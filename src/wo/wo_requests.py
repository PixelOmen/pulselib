import json
import requests

from . import WorkOrder
from .. import utils
from ..config import CONFIG

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

def get_wo(wo_num: str) -> WorkOrder:
    fullurl = f"{CONFIG.WO_URL}/wo_no_seq={wo_num}"
    res = requests.get(url=fullurl, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = utils.verify_response(url=fullurl, response=res)
    return WorkOrder(json.loads(body))