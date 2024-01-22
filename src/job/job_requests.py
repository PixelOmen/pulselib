import json
import requests

from ..errors import (
    JobNotFoundError,
    JobUncaughtError
)

from .. import utils
from ..config import CONFIG


def gen_query(wo_num: str) -> str:
    return json.dumps({
        "job_no": wo_num
    })

def query(query: dict) -> list[dict]:
    url = f"{CONFIG.JOB_QUERY_URL}/?query={query}"
    r = requests.get(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = json.loads(utils.verify_response(url=url, response=r))
    if not isinstance(body, list):
        err = body.get("error")
        if err:
            raise JobUncaughtError(query, err)
    return body
        

def get(job_num: str) -> dict:
    url = f"{CONFIG.JOB_URL}/job_no={str(job_num)}"
    r = requests.get(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = json.loads(utils.verify_response(url=url, response=r))
    err = body.get("error")
    if err:
        if err.startswith("Alternate key not found:"):
            raise JobNotFoundError(job_num)
        else:
            raise JobUncaughtError(job_num, err)
    return body

def get_project_manager_desc(sale_office_no: str) -> str:
    url = f"{CONFIG.SALES_OFFICE_URL}/sale_office_no={sale_office_no}"
    r = requests.get(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = json.loads(utils.verify_response(url=url, response=r))
    err = body.get("error")
    if err:
        raise JobUncaughtError(sale_office_no, err)
    return body["sale_office_desc"]