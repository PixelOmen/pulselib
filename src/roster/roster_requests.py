import json
import requests

from .. import utils
from ..config import CONFIG
from ..errors import RosterUncaughtError

from .model import RosterTimeOff
from .rosterfieldmaps import ROSTER_CODES

def query(query: dict) -> list[dict]:
    url = f"{CONFIG.ROSTER_QUERY_URL}/?query={query}"
    r = requests.get(url=url, auth=(CONFIG.USERNAME, CONFIG.PASSWORD))
    body = json.loads(utils.verify_response(url=url, response=r))
    if not isinstance(body, list):
        err = body.get("error")
        if err:
            raise RosterUncaughtError(query, err)
    return body

def by_date(daterange: tuple[str, str] | None = None, maintenance_only: bool=True) -> list[RosterTimeOff]:
    query_params = {}
    if daterange is None:
        daterange = (utils.today(), utils.today())
    query_params["trx_begin_dt"] = {"$range": list(daterange)}
    if maintenance_only:
        query_params["time_off_type_no"] = "6"
    jdict_list = query(query_params)
    if jdict_list:
        return [RosterTimeOff(jdict) for jdict in jdict_list]
    else:
        return []