import json
from pathlib import Path
from typing import Optional

_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "sample_data"
_CUSTOMERS: list[dict] = []


def _load_customers() -> list[dict]:
    """Load customers from JSON file (cached in memory)."""
    global _CUSTOMERS
    if not _CUSTOMERS:
        with open(_DATA_DIR / "customers.json", "r") as f:
            _CUSTOMERS = json.load(f)
    return _CUSTOMERS


def get_all_customers() -> list[dict]:
    """Return all customers."""
    return _load_customers()


def get_customer_by_id(customer_id: str) -> Optional[dict]:
    """Return a single customer by ID, or None if not found."""
    customers = _load_customers()
    for customer in customers:
        if customer["customer_id"] == customer_id:
            return customer
    return None
