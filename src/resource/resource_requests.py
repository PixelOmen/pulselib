import json
import requests

from ..errors import ResourceUncaughtError, ResourceNotFoundError, ResourceExistsError

from .. import utils
from ..config import CONFIG


def query(query: dict) -> list[dict]:
    url = f"{CONFIG.RESOURCE_QUERY_URL}/?query={query}"
    r = requests.get(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = json.loads(utils.verify_response(url=url, response=r))
    if not isinstance(body, list):
        err = body.get("error")
        if err:
            debugdict = query if query else {}
            raise ResourceUncaughtError(debugdict, err)
    return body

def get(assetno: str) -> dict:
    url = f"{CONFIG.RESOURCE_URL}/resource_code={str(assetno)}"
    r = requests.get(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = json.loads(utils.verify_response(url=url, response=r))
    err = body.get("error")
    if err:
        if err.startswith("Alternate key not found:"):
            raise ResourceNotFoundError(assetno)
        else:
            raise ResourceUncaughtError(assetno, err)
    return body

def patch(resource_code: str, patchlist: list[dict]) -> None:
    url = f"{CONFIG.RESOURCE_URL}/resource_code={str(resource_code)}"
    r = requests.patch(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=patchlist)
    body = utils.verify_response(url=url, response=r)
    if body:
        jbody = json.loads(body)
        err = jbody.get("error")
        if err:
            if err.startswith("Alternate key not found:"):
                raise ResourceNotFoundError(resource_code)
            else:
                raise ResourceUncaughtError(resource_code, err)

def post(jdict: dict) -> None:
    url = f"{CONFIG.RESOURCE_URL}"
    r = requests.post(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=jdict)
    body = utils.verify_response(url=url, response=r)
    if body:
        jbody = json.loads(body)
        err = jbody.get("error")
        if err:
            if "already exists" in err:
                raise ResourceExistsError(jdict, err)
            else:
                raise ResourceUncaughtError(jdict, err)


def query_qualifications(query: dict | None = None) -> list[dict]:
    """
    This endpoint does not support standard querying.
    It will return all qualifactions regardless of the query.
    Filtering is done in the function itself.
    """
    url = f"{CONFIG.QUALIFICATION_URL}"
    r = requests.get(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = json.loads(utils.verify_response(url=url, response=r))
    if not isinstance(body, list):
        err = body.get("error")
        if err and query is not None:
            raise ResourceUncaughtError(query, err)
    if query is None:
        return body
    filtered = []
    for qual in body:
        for key, value in query.items():
            if qual.get(key) == value:
                filtered.append(qual)
    return filtered

def get_qualification(qual_no: str) -> dict:
    url = f"{CONFIG.QUALIFICATION_URL}/qualification_no={str(qual_no)}"
    r = requests.get(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = json.loads(utils.verify_response(url=url, response=r))
    err = body.get("error")
    if err:
        if err.startswith("Alternate key not found:"):
            raise ResourceNotFoundError(qual_no)
        else:
            raise ResourceUncaughtError(qual_no, err)
    return body

def post_qualification(jdict: dict) -> None:
    url = f"{CONFIG.QUALIFICATION_URL}"
    r = requests.post(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=jdict)
    body = utils.verify_response(url=url, response=r)
    if body:
        jbody = json.loads(body)
        err = jbody.get("error")
        if err:
            raise ResourceUncaughtError(jdict, err)

def add_qual_to_resource(res_code: str, qual_no: str) -> None:
    jdict = [{
        "resource_code": res_code,
        "qualification_no": qual_no
    }]
    url = f"{CONFIG.RESOURCE_URL}/resource_code={res_code}/sch_resource_qual"
    r = requests.post(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=jdict)
    body = utils.verify_response(url=url, response=r)
    if body:
        jbody = json.loads(body)
        err = jbody.get("error")
        if err:
            raise ResourceUncaughtError(res_code, err)

def get_group_resources(group_code: str) -> list[dict]:
    url = f"{CONFIG.SCHGROUP_URL}/group_code={group_code}/sch_group_resource"
    r = requests.get(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = json.loads(utils.verify_response(url=url, response=r))
    if not isinstance(body, list):
        err = body.get("error")
        if err:
            raise ResourceUncaughtError(f"{group_code}", err)
    return body
        
def post_resource_to_group(group_code: str, resource_code: str, isdefault: bool = True) -> None:
    isdefault_str = "Y" if isdefault else "N"
    payload = [{
        "group_code": group_code,
        "default_group": isdefault_str,
        "resource_code": {
            "resource_code": resource_code
        }
    }]
    url = f"{CONFIG.SCHGROUP_URL}/group_code={group_code}/sch_group_resource"
    r = requests.post(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD), json=payload)
    body = utils.verify_response(url=url, response=r)
    if body:
        jbody = json.loads(body)
        err = jbody.get("error")
        if err:
            raise ResourceUncaughtError(f"{group_code}", err)