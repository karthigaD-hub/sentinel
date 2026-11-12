import logging
import time
from dataclasses import dataclass

import httpx

from app.core.config import settings
from app.llm.types import LLMError, LLMGeneration

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OllamaHealth:
    reachable: bool
    model_available: bool
    installed_models: list[str]
    error: str | None


def model_matches(configured: str, installed: str) -> bool:
    if configured == installed:
        return True
    return ":" not in configured and installed == f"{configured}:latest"


def _describe(exc: Exception) -> str:
    return exc.__class__.__name__


class OllamaClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def health(self, model: str) -> OllamaHealth:
        try:
            async with httpx.AsyncClient(timeout=settings.llm_health_timeout_seconds) as client:
                response = await client.get(f"{self.base_url}/api/tags")
        except httpx.HTTPError as exc:
            return OllamaHealth(False, False, [], f"Ollama is not reachable at {self.base_url} ({_describe(exc)})")
        if response.status_code != 200:
            return OllamaHealth(True, False, [], f"Ollama /api/tags returned HTTP {response.status_code}")
        try:
            data = response.json()
        except ValueError:
            return OllamaHealth(True, False, [], "Ollama /api/tags returned a non-JSON body")
        models = data.get("models") if isinstance(data, dict) else None
        if not isinstance(models, list):
            return OllamaHealth(True, False, [], "Ollama /api/tags response has no model list")
        installed = [item["name"] for item in models if isinstance(item, dict) and isinstance(item.get("name"), str)]
        available = any(model_matches(model, name) for name in installed)
        error = None if available else f"Model '{model}' is not installed in Ollama"
        return OllamaHealth(True, available, installed, error)

    async def chat(self, model: str, system_prompt: str, user_message: str) -> LLMGeneration:
        payload = {
            "model": model,
            "stream": False,
            "keep_alive": settings.llm_keep_alive,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "options": {
                "temperature": settings.llm_temperature,
                "num_ctx": settings.llm_context_window,
                "num_predict": settings.llm_max_output_tokens,
            },
        }
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(settings.llm_timeout_seconds)) as client:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
        except httpx.TimeoutException as exc:
            raise LLMError("llm_timeout", f"Ollama did not respond within {settings.llm_timeout_seconds:.0f} seconds") from exc
        except httpx.HTTPError as exc:
            raise LLMError("llm_unavailable", f"Ollama is not reachable at {self.base_url} ({_describe(exc)})") from exc

        if response.status_code == 404:
            raise LLMError("llm_model_missing", f"Model '{model}' is not installed in Ollama")
        if response.status_code != 200:
            raise LLMError("llm_error", f"Ollama returned HTTP {response.status_code}")

        try:
            data = response.json()
        except ValueError as exc:
            raise LLMError("llm_malformed_response", "Ollama returned a body that is not valid JSON") from exc
        message = data.get("message") if isinstance(data, dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str):
            raise LLMError("llm_malformed_response", "Ollama response has no message content")
        text = content.strip()
        duration_ms = round((time.perf_counter() - started) * 1000, 1)
        if not text:
            raise LLMError("llm_empty_response", "Ollama returned an empty answer")

        prompt_tokens = data.get("prompt_eval_count")
        completion_tokens = data.get("eval_count")
        truncated = data.get("done_reason") == "length"
        logger.info(
            "ollama chat model=%s duration_ms=%.1f prompt_tokens=%s completion_tokens=%s truncated=%s",
            model, duration_ms, prompt_tokens, completion_tokens, truncated,
        )
        return LLMGeneration(
            text=text,
            model=model,
            truncated=truncated,
            prompt_tokens=prompt_tokens if isinstance(prompt_tokens, int) else None,
            completion_tokens=completion_tokens if isinstance(completion_tokens, int) else None,
            duration_ms=duration_ms,
        )
