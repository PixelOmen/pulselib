import json
import requests
from typing import Any

from . import Transaction
from .. import utils, PhaseEnum
from ..config import CONFIG

def gen_query(daterange: tuple[str, str]=...) -> str:
    if daterange is ...:
        daterange = (utils.today(), utils.today())
    queryparams = {
        "trx_begin_dt": {
            "$range": list(daterange)
        },
        "resource_desc": {
            "$ne": "|NULL|"
        },
        "job_desc": {
            "$ne": "|NULL|"
        },
        "phase_code": {
            "$ne": "VOID"
        }
    }
    return json.dumps(queryparams, indent=0)

def gen_resultcolumns() -> str:
    return json.dumps({
        "L": [
            "wo_no_seq",
            "resource_desc",
            "trx_begin_dt",
            "trx_end_dt",
            "row_display",
            "customer_name",
            "note_no_text",
            "group_desc",
            "job_desc",
            "wo_job_no",
            "wo_desc",
            "WO_field_2",
            "wo_type_no",
            "wo_begin_dt",
            "job_table1_no",
            "phase_code",
            "user_added"
        ]
    })

def gen_listquery_url(query: str, resultcolumns: str) -> str:
    return f"{CONFIG.TRX_QUERY_URL}/?query={query}&resultColumns={resultcolumns}"

def list_query(query: str, resultcolumns: str) -> Any:
    fullurl = gen_listquery_url(query, resultcolumns)
    res = requests.get(url=fullurl, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = utils.verify_response(url=fullurl, response=res)
    return json.loads(body)

def by_date(daterange: tuple[str, str]=...,
            onhold: bool=True, invoiced: bool=True, proposed: bool=True, raw: bool=False) -> list[Transaction]:
    query = gen_query(daterange)
    resultcolumns = gen_resultcolumns()
    response = list_query(query, resultcolumns)
    if raw:
        return response
    trx = [Transaction.from_dict(d) for d in response]
    if onhold and invoiced:
        return trx
    
    filteredtrx = []
    for t in trx:
        if not onhold and t.phase_code == PhaseEnum.hold.code:
            continue
        if not invoiced and t.phase_code == PhaseEnum.invoiced.code:
            continue
        if not proposed and t.phase_code == PhaseEnum.proposed.code:
            continue
        filteredtrx.append(t)        
    return filteredtrx