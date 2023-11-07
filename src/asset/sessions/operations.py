from datetime import datetime, timedelta

from . import session_requests
from .assetsessionmaps import (
    ASSET_SESSION_MAPS,
    SESSION_ISSUE_MAPS
)


def _strip_asset_info(sessiondict: dict) -> dict:
    new_dict = {}
    for k,v in sessiondict.items():
        if (not k == "session_no" and
            not k.startswith("lib_master") and 
            not k.startswith("master_")):
            new_dict[k] = v
    return new_dict

def _format_session_copy(sessiondict: dict, target_asset: str) -> dict:
    new_dict = _strip_asset_info(sessiondict)
    new_dict["keystring"]["keystring"] = target_asset
    new_dict["keystring"]["master_no"] = target_asset
    new_dict["parent_keystring"] = f"11032:{target_asset}"
    return new_dict

def _is_recent_session(sessiondict: dict) -> bool:
    date_added = sessiondict.get("date_added")
    if date_added is None:
        session_no = sessiondict["session_no"]["session_no"]
        raise ValueError(f"Session has no date_added field: {session_no}")
    session_time = datetime.strptime(date_added, "%Y-%m-%dT%H:%M:%S")
    now = datetime.now()
    diff_minus = now - timedelta(minutes=2)
    diff_plus = now + timedelta(minutes=2)
    return diff_minus <= session_time <= diff_plus

def _copy_session_wout_issues(source_session: str, target_asset: str) -> tuple[str, list[dict]]:
    """ Returns tuple of new session no and list of issues """
    source_dict = session_requests.get(source_session)
    issues = ASSET_SESSION_MAPS["issues"].read(source_dict)
    if issues is None:
        issues = []
    else:
        del source_dict[ASSET_SESSION_MAPS["issues"].keys]

    new_dict = _format_session_copy(source_dict, target_asset)
    session_requests.post(new_dict)

    target_sessions = session_requests.query({"keystring": target_asset})
    if not target_sessions:
        raise RuntimeError(f"Session copy to target asset failed, no sessions: {target_asset}")
    recent_sessions = [session for session in target_sessions if _is_recent_session(session)]
    if not recent_sessions:
        raise RuntimeError(f"Session copy to target asset failed, no recent sessions: {target_asset}")
    
    most_recent = recent_sessions[0]
    for session in recent_sessions:
        if session["date_added"] > most_recent["date_added"]:
            most_recent = session
    most_recent_no = most_recent["session_no"]["session_no"]
    return (most_recent_no, issues)

def _replace_session_in_issues(issues: list[dict], new_session_no: str) -> None:
    if not issues:
        return
    for issue in issues:
        if issue.get("session_issue_no") is not None:
            del issue["session_issue_no"]
        issue["session_no"] = new_session_no

def _gen_tc_events(tcs: list[tuple[str, str]]) -> list[dict]:
    events = []
    event_type_key = SESSION_ISSUE_MAPS["event_type"].keys
    tc_in_key = SESSION_ISSUE_MAPS["tc_in"].keys
    tc_out_key = SESSION_ISSUE_MAPS["tc_out"].keys
    for tc in tcs:
        events.append({
            event_type_key: "EVENT",
            tc_in_key: tc[0],
            tc_out_key: tc[1],
        })
    return events


def copy_session(source_session: str, target_asset: str) -> str:
    """ Returns new session no """
    new_session_no, issues = _copy_session_wout_issues(source_session, target_asset)
    _replace_session_in_issues(issues, new_session_no)
    session_requests.post_issues(new_session_no, issues)
    return new_session_no


def patch_po(session_no: str, po_num: str) -> None:
    patch = [{
        "op": "replace",
        "path": ASSET_SESSION_MAPS["po"].keys,
        "value": po_num
    }]
    session_requests.patch(session_no, patch)


def patch_tc_events(session_no: str, tcs: list[tuple[str, str]]) -> None:
    events = _gen_tc_events(tcs)
    session_requests.post_issues(session_no, events)