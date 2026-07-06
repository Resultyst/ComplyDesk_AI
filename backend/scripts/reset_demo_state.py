import os
import json
import urllib.request
import urllib.error
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("reset_demo_state")

# 1. Resolve paths
BACKEND_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DATA_DIR = BACKEND_DIR.parent / "sample_data"
ENV_PATH = BACKEND_DIR / ".env"

# 2. Load .env variables manually to be self-contained
if ENV_PATH.exists():
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()
else:
    logger.warning(f".env file not found at {ENV_PATH}. Falling back to default environment variables.")

HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY", "")
HINDSIGHT_BASE_URL = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")
HINDSIGHT_NAMESPACE = os.getenv("HINDSIGHT_NAMESPACE", "complydesk-fintech")

CUSTOMER_IDS = ["CUST-001", "CUST-002", "CUST-003", "CUST-004"]

def reset_hindsight_memories():
    """Wipes cloud memories for all demo customers and reseeds them with canonical preferences."""
    if not HINDSIGHT_API_KEY:
        logger.info("No HINDSIGHT_API_KEY configured. Skipping cloud memory reset.")
        return

    # Load canonical seed memory data
    seed_file = SAMPLE_DATA_DIR / "memory_seed.json"
    if not seed_file.exists():
        logger.error(f"memory_seed.json not found at {seed_file}. Cannot reseed Hindsight.")
        return

    with open(seed_file, "r", encoding="utf-8") as f:
        seed_data = json.load(f)

    for cid in CUSTOMER_IDS:
        bank_id = f"{HINDSIGHT_NAMESPACE}-{cid}".lower()
        
        # A. Delete all existing memories in the bank
        delete_url = f"{HINDSIGHT_BASE_URL}/v1/default/banks/{bank_id}/memories"
        logger.info(f"Wiping cloud memories in bank {bank_id}...")
        try:
            req = urllib.request.Request(
                delete_url,
                method="DELETE",
                headers={
                    "Authorization": f"Bearer {HINDSIGHT_API_KEY}",
                    "User-Agent": "Mozilla/5.0"
                }
            )
            with urllib.request.urlopen(req, timeout=10) as res:
                logger.info(f"Successfully wiped cloud memories for bank {bank_id}.")
        except urllib.error.HTTPError as e:
            # If bank doesn't exist, it might return 404 which is fine
            if e.code == 404:
                logger.info(f"Cloud bank {bank_id} did not exist yet. Safe to seed.")
            else:
                logger.warning(f"Failed to delete bank {bank_id} memories: {e.code} - {e.read().decode()}")
        except Exception as e:
            logger.warning(f"Connection failure deleting bank {bank_id}: {e}")

        # B. Reseed memories if present in seed file
        customer_seeds = seed_data.get(cid, [])
        if not customer_seeds:
            continue

        logger.info(f"Reseeding {len(customer_seeds)} items to cloud bank {bank_id}...")
        retain_url = f"{HINDSIGHT_BASE_URL}/v1/default/banks/{bank_id}/memories"
        
        # Format the items list with normalized categories
        category_map = {
            "customer_preference": "customer_preference",
            "support_history": "support_history",
            "compliance_context": "account_context",
            "escalation_context": "risk_context",
        }
        items = []
        for seed in customer_seeds:
            normalized_key = category_map.get(seed["key"].lower().strip(), seed["key"])
            items.append({
                "content": seed["value"],
                "context": normalized_key,
                "timestamp": seed["timestamp"]
            })
        
        payload = {"items": items}

        try:
            req = urllib.request.Request(
                retain_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {HINDSIGHT_API_KEY}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as res:
                logger.info(f"Successfully reseeded bank {bank_id} (Cloud status: {res.status}).")
        except Exception as e:
            logger.error(f"Failed to reseed bank {bank_id}: {e}")

def reset_local_audit_logs():
    """Restores audit_log.json on disk to the canonical 10 NexaPay support history records."""
    audit_file = SAMPLE_DATA_DIR / "audit_log.json"
    logger.info(f"Resetting local audit logs at {audit_file}...")

    canonical_audit = [
        {
            "audit_id": "AUD-001",
            "timestamp": "2026-06-18T10:15:00Z",
            "ticket_id": "TKT-SUR-001",
            "customer_id": "CUST-001",
            "sensitivity": "high",
            "model_selected": "Ollama/llama3",
            "routing_reason": "High-sensitivity ticket containing compliance risks routed to local Ollama hardware. [Compliance: True] [Budget: False] [Health: Groq=healthy, Ollama=healthy, Hindsight=healthy] | Memory: hindsight (recalled=2) | Cost saved: $0.05000 (baseline: $0.05000, actual: $0.00000)",
            "memory_used": True,
            "latency_ms": 850,
            "estimated_cost_usd": 0.0
        },
        {
            "audit_id": "AUD-002",
            "timestamp": "2026-06-26T12:40:00Z",
            "ticket_id": "TKT-SUR-002",
            "customer_id": "CUST-001",
            "sensitivity": "medium",
            "model_selected": "Ollama/llama3",
            "routing_reason": "Medium-sensitivity ticket containing PII/finance details routed to local Ollama hardware. [Compliance: True] [Budget: False] [Health: Groq=healthy, Ollama=healthy, Hindsight=healthy] | Memory: hindsight (recalled=2) | Cost saved: $0.05000 (baseline: $0.05000, actual: $0.00000)",
            "memory_used": True,
            "latency_ms": 620,
            "estimated_cost_usd": 0.0
        },
        {
            "audit_id": "AUD-003",
            "timestamp": "2026-07-02T09:20:00Z",
            "ticket_id": "TKT-SUR-003",
            "customer_id": "CUST-001",
            "sensitivity": "medium",
            "model_selected": "Ollama/llama3",
            "routing_reason": "Medium-sensitivity ticket containing PII/finance details routed to local Ollama hardware. [Compliance: True] [Budget: False] [Health: Groq=healthy, Ollama=healthy, Hindsight=healthy] | Memory: hindsight (recalled=2) | Cost saved: $0.05000 (baseline: $0.05000, actual: $0.00000)",
            "memory_used": True,
            "latency_ms": 620,
            "estimated_cost_usd": 0.0
        },
        {
            "audit_id": "AUD-004",
            "timestamp": "2026-06-20T08:30:00Z",
            "ticket_id": "TKT-NAR-001",
            "customer_id": "CUST-002",
            "sensitivity": "low",
            "model_selected": "Groq/openai/gpt-oss-120b",
            "routing_reason": "Low-sensitivity ticket routed to cost-optimized Groq cloud model. [Compliance: False] [Budget: True] [Health: Groq=healthy, Ollama=healthy, Hindsight=healthy] | Memory: hindsight (recalled=2) | Cost saved: $0.00000 (baseline: $0.00300, actual: $0.00300)",
            "memory_used": True,
            "latency_ms": 340,
            "estimated_cost_usd": 0.003
        },
        {
            "audit_id": "AUD-005",
            "timestamp": "2026-06-29T15:05:00Z",
            "ticket_id": "TKT-NAR-002",
            "customer_id": "CUST-002",
            "sensitivity": "low",
            "model_selected": "Groq/openai/gpt-oss-120b",
            "routing_reason": "Low-sensitivity ticket routed to cost-optimized Groq cloud model. [Compliance: False] [Budget: True] [Health: Groq=healthy, Ollama=healthy, Hindsight=healthy] | Memory: hindsight (recalled=2) | Cost saved: $0.00000 (baseline: $0.00300, actual: $0.00300)",
            "memory_used": True,
            "latency_ms": 340,
            "estimated_cost_usd": 0.003
        },
        {
            "audit_id": "AUD-006",
            "timestamp": "2026-07-03T18:10:00Z",
            "ticket_id": "TKT-NAR-003",
            "customer_id": "CUST-002",
            "sensitivity": "medium",
            "model_selected": "Ollama/llama3",
            "routing_reason": "Medium-sensitivity ticket containing PII/finance details routed to local Ollama hardware. [Compliance: True] [Budget: False] [Health: Groq=healthy, Ollama=healthy, Hindsight=healthy] | Memory: hindsight (recalled=2) | Cost saved: $0.05000 (baseline: $0.05000, actual: $0.00000)",
            "memory_used": True,
            "latency_ms": 620,
            "estimated_cost_usd": 0.0
        },
        {
            "audit_id": "AUD-007",
            "timestamp": "2026-06-17T11:25:00Z",
            "ticket_id": "TKT-SAN-001",
            "customer_id": "CUST-003",
            "sensitivity": "medium",
            "model_selected": "Ollama/llama3",
            "routing_reason": "Medium-sensitivity ticket containing PII/finance details routed to local Ollama hardware. [Compliance: True] [Budget: False] [Health: Groq=healthy, Ollama=healthy, Hindsight=healthy] | Memory: hindsight (recalled=2) | Cost saved: $0.05000 (baseline: $0.05000, actual: $0.00000)",
            "memory_used": True,
            "latency_ms": 620,
            "estimated_cost_usd": 0.0
        },
        {
            "audit_id": "AUD-008",
            "timestamp": "2026-07-04T10:00:00Z",
            "ticket_id": "TKT-SAN-003",
            "customer_id": "CUST-003",
            "sensitivity": "high",
            "model_selected": "Ollama/llama3",
            "routing_reason": "High-sensitivity ticket containing compliance risks routed to local Ollama hardware. [Compliance: True] [Budget: False] [Health: Groq=healthy, Ollama=healthy, Hindsight=healthy] | Memory: hindsight (recalled=2) | Cost saved: $0.05000 (baseline: $0.05000, actual: $0.00000)",
            "memory_used": True,
            "latency_ms": 850,
            "estimated_cost_usd": 0.0
        },
        {
            "audit_id": "AUD-009",
            "timestamp": "2026-06-16T09:45:00Z",
            "ticket_id": "TKT-KUM-001",
            "customer_id": "CUST-004",
            "sensitivity": "high",
            "model_selected": "Ollama/llama3",
            "routing_reason": "High-sensitivity ticket containing compliance risks routed to local Ollama hardware. [Compliance: True] [Budget: False] [Health: Groq=healthy, Ollama=healthy, Hindsight=healthy] | Memory: hindsight (recalled=2) | Cost saved: $0.05000 (baseline: $0.05000, actual: $0.00000)",
            "memory_used": True,
            "latency_ms": 850,
            "estimated_cost_usd": 0.0
        },
        {
            "audit_id": "AUD-010",
            "timestamp": "2026-07-01T17:40:00Z",
            "ticket_id": "TKT-KUM-003",
            "customer_id": "CUST-004",
            "sensitivity": "high",
            "model_selected": "Ollama/llama3",
            "routing_reason": "High-sensitivity ticket containing compliance risks routed to local Ollama hardware. [Compliance: True] [Budget: False] [Health: Groq=healthy, Ollama=healthy, Hindsight=healthy] | Memory: hindsight (recalled=2) | Cost saved: $0.05000 (baseline: $0.05000, actual: $0.00000)",
            "memory_used": True,
            "latency_ms": 850,
            "estimated_cost_usd": 0.0
        }
    ]

    try:
        with open(audit_file, "w", encoding="utf-8") as f:
            json.dump(canonical_audit, f, indent=2)
        logger.info("Successfully reset audit logs file on disk.")
    except Exception as e:
        logger.error(f"Failed to reset audit logs file: {e}")

if __name__ == "__main__":
    logger.info("=== STARTING CANONICAL DEMO RESET & RESEED WORKFLOW ===")
    reset_hindsight_memories()
    reset_local_audit_logs()
    logger.info("=== CANONICAL RESET & RESEED COMPLETE! Please restart the backend server. ===")
