import json
from datetime import datetime
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .trx import Transaction
    from requests import Response

def print_json(jdict_or_list: Any) -> None:
    jstr = json.dumps(jdict_or_list, indent=4, sort_keys=True)
    print(jstr)

def print_transactions(trxlist: list["Transaction"]) -> None:
    combined = [trx.jdict for trx in trxlist]
    jstr = json.dumps(combined, indent=4, sort_keys=True)
    print(jstr)

def verify_response(url: str, response: "Response") -> str:
    if not response.text:
        print("HTTP Response did not contain a body.")
        print(f"URL: {url}")
        exit()
    return response.text.encode('utf-8').decode('utf-8')

def today() -> str:
    return datetime.now().strftime('%Y-%m-%d')