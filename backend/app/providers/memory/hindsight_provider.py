import json
import urllib.request
import urllib.error
import logging
from typing import Any
from app.services.memory_provider import BaseMemoryProvider, LocalMemoryProvider
from app.schemas.customer import MemoryItem
from app.utils import utc_now
from app.core import config

logger = logging.getLogger(__name__)

class HindsightMemoryProvider(BaseMemoryProvider):
    """Real integration provider for Hindsight Cloud with local fallback capability."""

    def __init__(self) -> None:
        self.api_key = config.HINDSIGHT_API_KEY
        self.base_url = config.HINDSIGHT_BASE_URL
        self.namespace = config.HINDSIGHT_NAMESPACE
        self.local_provider = LocalMemoryProvider()
        self.last_used_source = "local_fallback"

    def get_memory_items(self, customer_id: str) -> list[MemoryItem]:
        self.last_used_source = "local_fallback"
        if not self.api_key:
            logger.info("Hindsight API key not set, using local memory fallback.")
            return self.local_provider.get_memory_items(customer_id)

        bank_id = f"{self.namespace}-{customer_id}".lower()
        url = f"{self.base_url}/v1/default/banks/{bank_id}/memories/recall"
        payload = {
            "query": "Retrieve all customer profile facts, prior transaction disputes, compliance and KYC verification history.",
            "num_results": 10
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as res:
                response_data = json.loads(res.read().decode("utf-8"))
                results = response_data.get("results", [])
                
                if not results:
                    logger.info(f"Hindsight returned empty results for bank {bank_id}, falling back to local memory.")
                    return self.local_provider.get_memory_items(customer_id)
                
                # Convert Hindsight recall results to MemoryItem schema
                memory_items = []
                for item in results:
                    memory_items.append(
                        MemoryItem(
                            key=item.get("context") or "general",
                            value=item.get("text") or "",
                            source="hindsight",
                            timestamp=item.get("mentioned_at") or utc_now()
                        )
                    )
                self.last_used_source = "hindsight"
                return memory_items

        except Exception as e:
            logger.warning(f"Failed to query Hindsight cloud for {bank_id} ({e}). Falling back to local memory.")
            return self.local_provider.get_memory_items(customer_id)

    def append_memory_item(self, customer_id: str, key: str, value: str, source: str) -> None:
        # 1. Sync locally first for continuous demo coherence
        self.local_provider.append_memory_item(customer_id, key, value, source)

        if not self.api_key:
            logger.info("Hindsight API key not set, skipped cloud storage.")
            return

        bank_id = f"{self.namespace}-{customer_id}".lower()
        url = f"{self.base_url}/v1/default/banks/{bank_id}/memories"
        payload = {
            "items": [
                {
                    "content": value,
                    "context": key,
                    "timestamp": utc_now()
                }
            ]
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as res:
                if res.status in (200, 201):
                    logger.info(f"Successfully retained new memory fact in Hindsight bank {bank_id}.")
                else:
                    logger.warning(f"Hindsight returned status {res.status} when retaining memory.")
        except Exception as e:
            logger.warning(f"Failed to append memory to Hindsight bank {bank_id} ({e}).")
