import json
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "sample_data"
_MEMORIES: dict[str, list[dict]] = {}


def _load_memories() -> dict[str, list[dict]]:
    """Load customer memories from JSON file (cached in memory)."""
    global _MEMORIES
    if not _MEMORIES:
        with open(_DATA_DIR / "memory_seed.json", "r") as f:
            _MEMORIES = json.load(f)
    return _MEMORIES


def get_memories_by_customer(customer_id: str) -> list[dict]:
    """Get memories for a specific customer."""
    memories = _load_memories()
    return memories.get(customer_id, [])


def add_memory_item(customer_id: str, item: dict) -> None:
    """Add a new memory item for a customer."""
    memories = _load_memories()
    if customer_id not in memories:
        memories[customer_id] = []
    memories[customer_id].append(item)
