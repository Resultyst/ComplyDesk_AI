import urllib.request
import logging
from app.core import config

logger = logging.getLogger(__name__)

def check_hindsight_health() -> str:
    """Check connectivity to Hindsight Cloud."""
    if not config.HINDSIGHT_API_KEY:
        return "unavailable"
    try:
        # Simple health check endpoint or root endpoint of Hindsight Cloud
        req = urllib.request.Request(
            config.HINDSIGHT_BASE_URL,
            method="GET",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=1.0) as res:
            if res.status in (200, 404):  # Hindsight cloud returns 200 or 404 on root depending on config
                return "healthy"
            return "degraded"
    except Exception:
        return "unavailable"

def check_groq_health() -> str:
    """Check config status of Groq."""
    if not config.GROQ_API_KEY:
        return "unavailable"
    # To check connection without wasting tokens, we verify config and connectivity
    try:
        req = urllib.request.Request(
            "https://api.groq.com",
            method="GET",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=1.0) as res:
            return "healthy"
    except Exception:
        return "unavailable"

def check_ollama_health() -> str:
    """Check connectivity to local Ollama server and verify loaded models."""
    import json
    try:
        req = urllib.request.Request(
            f"{config.OLLAMA_BASE_URL}/api/tags",
            method="GET"
        )
        with urllib.request.urlopen(req, timeout=1.5) as res:
            data = json.loads(res.read().decode())
            if "models" in data:
                return "healthy"
            return "degraded"
    except Exception:
        return "unavailable"

def get_health_status() -> dict:
    """Compile a full provider health snapshot."""
    return {
        "hindsight": check_hindsight_health(),
        "groq": check_groq_health(),
        "ollama": check_ollama_health()
    }
