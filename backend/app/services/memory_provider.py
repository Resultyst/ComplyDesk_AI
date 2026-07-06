from abc import ABC, abstractmethod
from typing import Any
from app.repositories import memory_repo
from app.schemas.customer import MemoryItem
from app.utils import utc_now


class BaseMemoryProvider(ABC):
    """Abstract base class for customer memory systems (e.g. Local vs Hindsight)."""

    @abstractmethod
    def get_memory_items(self, customer_id: str) -> list[MemoryItem]:
        """Retrieve memory items for a customer."""
        pass

    @abstractmethod
    def append_memory_item(self, customer_id: str, key: str, value: str, source: str) -> None:
        """Store a new memory item for a customer."""
        pass


class LocalMemoryProvider(BaseMemoryProvider):
    """Local, in-memory/JSON-backed implementation of customer memory provider."""

    def get_memory_items(self, customer_id: str) -> list[MemoryItem]:
        raw_items = memory_repo.get_memories_by_customer(customer_id)
        return [MemoryItem(**item) for item in raw_items]

    def append_memory_item(self, customer_id: str, key: str, value: str, source: str) -> None:
        new_item = {
            "key": key,
            "value": value,
            "source": source,
            "timestamp": utc_now()
        }
        memory_repo.add_memory_item(customer_id, new_item)


# Global provider instance to be resolved later or overridden
_PROVIDER: BaseMemoryProvider = None


def get_memory_provider() -> BaseMemoryProvider:
    """Dependency resolver for the active memory provider."""
    global _PROVIDER
    if _PROVIDER is None:
        try:
            from app.providers.memory.hindsight_provider import HindsightMemoryProvider
            _PROVIDER = HindsightMemoryProvider()
        except ImportError:
            _PROVIDER = LocalMemoryProvider()
    return _PROVIDER


def set_memory_provider(provider: BaseMemoryProvider) -> None:
    """Allows runtime configuration of the active memory provider (e.g. Hindsight override)."""
    global _PROVIDER
    _PROVIDER = provider
