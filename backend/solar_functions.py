"""Solar agent tools. Results go to one place (save_result), so swapping the
file for GHL, a sheet or a database later means changing only this file.

lead_id and phone are added by the server, never by the model.
"""
import json
import threading
from datetime import datetime, timezone
from pathlib import Path

RESULTS_FILE = Path("call_results.jsonl")
DNC_FILE = Path("do_not_call.txt")
_lock = threading.Lock()


def save_result(lead_id: str, kind: str, data: dict) -> None:
    record = {
        "time": datetime.now(timezone.utc).isoformat(),
        "lead_id": lead_id,
        "type": kind,
        **data,
    }
    with _lock, RESULTS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def is_do_not_call(phone: str) -> bool:
    if not DNC_FILE.exists():
        return False
    with _lock:
        numbers = {line.strip() for line in DNC_FILE.read_text(encoding="utf-8").splitlines()}
    return phone in numbers


def save_qualification(
    owns_property: str = "",
    monthly_bill: str = "",
    roof_type: str = "",
    location: str = "",
    timeline: str = "",
    wants_financing: str = "",
    interest_level: str = "",
    notes: str = "",
    lead_id: str = "",
    phone: str = "",
) -> dict:
    save_result(lead_id, "qualification", {
        "owns_property": owns_property,
        "monthly_bill": monthly_bill,
        "roof_type": roof_type,
        "location": location,
        "timeline": timeline,
        "wants_financing": wants_financing,
        "interest_level": interest_level,
        "notes": notes,
    })
    return {"status": "saved"}


def request_callback(
    preferred_time: str = "",
    reason: str = "",
    lead_id: str = "",
    phone: str = "",
) -> dict:
    save_result(lead_id, "callback", {"preferred_time": preferred_time, "reason": reason})
    return {"status": "noted", "message": "A team member will follow up."}


def mark_do_not_call(reason: str = "", lead_id: str = "", phone: str = "") -> dict:
    if phone:
        with _lock, DNC_FILE.open("a", encoding="utf-8") as f:
            f.write(phone + "\n")
    save_result(lead_id, "do_not_call", {"reason": reason})
    return {"status": "done", "message": "This number will not be called again."}


FUNCTION_MAP = {
    "save_qualification": save_qualification,
    "request_callback": request_callback,
    "mark_do_not_call": mark_do_not_call,
}