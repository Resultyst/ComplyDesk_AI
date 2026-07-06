import json
import urllib.request
import urllib.error
import time
import logging
from app.core import config

logger = logging.getLogger(__name__)

class GroqLLMProvider:
    """Provider for cloud-based inference via Groq API with automatic fallback."""

    def __init__(self) -> None:
        self.api_key = config.GROQ_API_KEY
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.default_model = config.GROQ_MODEL_LOW_SENSITIVITY
        self.fallback_model = config.GROQ_MODEL_FALLBACK

    def generate_response(self, prompt: str) -> dict:
        """Call Groq to generate a response. Tries default model first, falls back on error."""
        if not self.api_key:
            raise ValueError("Groq API Key is not set")

        # Try default model first
        try:
            return self._call_api(self.default_model, prompt)
        except Exception as e:
            logger.warning(f"Groq primary model ({self.default_model}) failed: {e}. Trying fallback ({self.fallback_model}).")
            return self._call_api(self.fallback_model, prompt, is_fallback=True)

    def _call_api(self, model: str, prompt: str, is_fallback: bool = False) -> dict:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a customer support agent at NexaPay."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 512
        }

        start_time = time.time()
        req = urllib.request.Request(
            self.base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as res:
                response_data = json.loads(res.read().decode("utf-8"))
                latency_ms = int((time.time() - start_time) * 1000)
                
                text = response_data["choices"][0]["message"]["content"]
                
                # Estimate cost (approximate: input/output tokens)
                usage = response_data.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                # Let's use generic pricing: $0.15/1M input, $0.60/1M output
                cost = (prompt_tokens * 0.00000015) + (completion_tokens * 0.00000060)

                return {
                    "response_text": text.strip(),
                    "model_used": model,
                    "provider": "groq",
                    "latency_ms": latency_ms,
                    "cost_usd": round(cost, 5),
                    "is_fallback": is_fallback
                }
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            logger.error(f"Groq HTTP error: {e.code} - {error_body}")
            raise RuntimeError(f"Groq API error ({e.code}): {error_body}")
        except Exception as e:
            logger.error(f"Groq connection error: {e}")
            raise e
