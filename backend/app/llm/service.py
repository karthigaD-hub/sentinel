import logging
import time

import httpx

from app.core.config import settings
from app.llm.ollama_client import OllamaClient, OllamaHealth
from app.llm.types import LLMError, LLMGeneration

logger = logging.getLogger(__name__)

DEFAULT_OLLAMA_URL = "http://localhost:11434"


class LLMService:
    def __init__(self) -> None:
        self.provider = settings.llm_provider.lower()
        self.model = settings.llm_model
        self.api_key = settings.llm_api_key
        self.base_url = settings.llm_base_url

    @property
    def configured(self) -> bool:
        if not self.provider or not self.model:
            return False
        if self.provider == "ollama":
            return True
        return self.provider == "openai" and bool(self.api_key)

    def _ollama(self) -> OllamaClient:
        return OllamaClient(self.base_url or DEFAULT_OLLAMA_URL)

    async def health(self) -> dict:
        if self.provider != "ollama":
            return {"provider": self.provider, "configured": self.configured, "reachable": None, "model_available": None, "error": None}
        result: OllamaHealth = await self._ollama().health(self.model)
        return {
            "provider": "ollama",
            "configured": self.configured,
            "base_url": self.base_url or DEFAULT_OLLAMA_URL,
            "model": self.model,
            "reachable": result.reachable,
            "model_available": result.model_available,
            "installed_models": result.installed_models,
            "error": result.error,
        }

    async def generate(self, system_prompt: str, user_message: str) -> LLMGeneration:
        if not self.configured:
            raise LLMError("llm_not_configured", "The language model is not configured")
        if self.provider == "ollama":
            return await self._ollama().chat(self.model, system_prompt, user_message)
        return await self._openai(system_prompt, user_message)

    async def _openai(self, system_prompt: str, user_message: str) -> LLMGeneration:
        base = self.base_url or "https://api.openai.com/v1"
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(settings.llm_timeout_seconds)) as client:
                response = await client.post(
                    f"{base.rstrip('/')}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message},
                        ],
                        "temperature": settings.llm_temperature,
                        "max_tokens": settings.llm_max_output_tokens,
                    },
                )
        except httpx.TimeoutException as exc:
            raise LLMError("llm_timeout", "The OpenAI request timed out") from exc
        except httpx.HTTPError as exc:
            raise LLMError("llm_unavailable", "The OpenAI request failed") from exc
        if response.status_code != 200:
            raise LLMError("llm_error", f"OpenAI returned HTTP {response.status_code}")
        try:
            data = response.json()
            choice = data["choices"][0]
            text = str(choice["message"]["content"]).strip()
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise LLMError("llm_malformed_response", "OpenAI response has an unexpected shape") from exc
        if not text:
            raise LLMError("llm_empty_response", "OpenAI returned an empty answer")
        usage = data.get("usage") or {}
        return LLMGeneration(
            text=text,
            model=self.model,
            truncated=choice.get("finish_reason") == "length",
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            duration_ms=round((time.perf_counter() - started) * 1000, 1),
        )


llm_service = LLMService()
