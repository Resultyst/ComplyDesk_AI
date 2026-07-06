import json
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "sample_data"
_TICKETS: list[dict] = []


def _load_tickets() -> list[dict]:
    """Load tickets from JSON file (cached in memory)."""
    global _TICKETS
    if not _TICKETS:
        with open(_DATA_DIR / "historical_tickets.json", "r") as f:
            _TICKETS = json.load(f)
    return _TICKETS


def get_all_tickets() -> list[dict]:
    """Return all tickets."""
    return _load_tickets()


def get_tickets_by_customer(customer_id: str) -> list[dict]:
    """Return tickets for a specific customer."""
    tickets = _load_tickets()
    return [t for t in tickets if t["customer_id"] == customer_id]
