import json
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "sample_data"
_AUDIT_RECORDS: list[dict] = []


def _load_audit_records() -> list[dict]:
    """Load audit records from JSON file (cached in memory)."""
    global _AUDIT_RECORDS
    if not _AUDIT_RECORDS:
        with open(_DATA_DIR / "audit_log.json", "r") as f:
            _AUDIT_RECORDS = json.load(f)
    return _AUDIT_RECORDS


def get_all_audit_records() -> list[dict]:
    """Return all audit records."""
    return _load_audit_records()


def add_audit_record(record: dict) -> None:
    """Append a new audit record to the in-memory list."""
    records = _load_audit_records()
    records.append(record)
