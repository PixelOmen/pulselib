import json
import requests

from .. import utils
from .. import USERNAME, PASSWORD

TRX_URL = "http://xytechapp01:11000/api/v1/database/REI_LIVE/JmWorkOrderList"

def gen_query(wo_num: str) -> str:
    return json.dumps({
        "wo_no_seq": wo_num
    })

def make_list_query(query: str) -> list[dict]:
    fullurl = f"{TRX_URL}/?query={query}"
    res = requests.get(url=fullurl, auth=(USERNAME, PASSWORD))
    body = utils.verify_response(url=fullurl, response=res)
    jbody = json.loads(body)
    return jbody

def by_num(wo_num: str) -> list[dict]:
    query = gen_query(wo_num)
    return make_list_query(query)