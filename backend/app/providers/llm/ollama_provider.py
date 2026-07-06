import json
import urllib.request
import urllib.error
import time
import logging
from app.core import config

logger = logging.getLogger(__name__)

class OllamaLLMProvider:
    """Provider for local compliant LLM inference via Ollama API."""

    def __init__(self) -> None:
        self.base_url = config.OLLAMA_BASE_URL
        self.primary_model = config.OLLAMA_MODEL_PRIMARY
        self.fallback_model = config.OLLAMA_MODEL_FALLBACK

    def generate_response(self, prompt: str) -> dict:
        """Generate response via local Ollama. Falls back if primary model fails."""
        try:
            return self._call_api(self.primary_model, prompt)
        except Exception as e:
            logger.warning(f"Ollama primary model ({self.primary_model}) failed: {e}. Trying fallback ({self.fallback_model}).")
            if self.primary_model != self.fallback_model:
                try:
                    return self._call_api(self.fallback_model, prompt, is_fallback=True)
                except Exception as inner_e:
                    logger.error(f"Ollama fallback model also failed: {inner_e}")
                    raise inner_e
            else:
                raise e

    def _resolve_model(self, target_model: str) -> str:
        """Dynamically match target model name against installed local Ollama models."""
        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/tags",
                method="GET"
            )
            with urllib.request.urlopen(req, timeout=2.0) as res:
                data = json.loads(res.read().decode("utf-8"))
                installed_models = [m["name"] for m in data.get("models", [])]
                
                if not installed_models:
                    logger.warning("No models found in Ollama local tag list.")
                    return target_model

                # 1. Exact match
                if target_model in installed_models:
                    return target_model

                # 2. Substring/Prefix matching (e.g. 'llama3' -> 'llama3:8b')
                for model in installed_models:
                    if target_model.lower() in model.lower() or model.lower() in target_model.lower():
                        logger.info(f"Resolved model '{target_model}' to installed '{model}'")
                        return model

                # 3. Default to the first installed model as fallback
                logger.warning(f"Configured model '{target_model}' not installed. Defaulting to first available '{installed_models[0]}'")
                return installed_models[0]
        except Exception as e:
            logger.warning(f"Could not contact Ollama /api/tags to resolve model: {e}")
            return target_model

    def _call_api(self, model: str, prompt: str, is_fallback: bool = False) -> dict:
        resolved_model = self._resolve_model(model)
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": resolved_model,
            "prompt": prompt,
            "options": {
                "temperature": 0.3
            },
            "stream": False
        }

        start_time = time.time()
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as res:
                response_data = json.loads(res.read().decode("utf-8"))
                latency_ms = int((time.time() - start_time) * 1000)
                
                text = response_data.get("response", "")
                
                return {
                    "response_text": text.strip(),
                    "model_used": resolved_model,
                    "provider": "ollama",
                    "latency_ms": latency_ms,
                    "cost_usd": 0.0,  # Local Ollama is free
                    "is_fallback": is_fallback
                }
        except Exception as e:
            logger.error(f"Failed to generate response on local Ollama at {url} using {resolved_model} ({e})")
            raise e
