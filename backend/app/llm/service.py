from app.core.config import settings


class LLMService:
    def __init__(self) -> None:
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self.api_key = settings.llm_api_key
        self.base_url = settings.llm_base_url

    @property
    def available(self) -> bool:
        if not self.provider or not self.model:
            return False
        provider = self.provider.lower()
        if provider == "ollama":
            return True
        return bool(self.api_key)

    def answer(self, prompt: str, context: str = "") -> str:
        if not self.available:
            raise RuntimeError("LLM provider is not configured. Set LLM_PROVIDER, LLM_MODEL, and LLM_API_KEY.")

        provider = self.provider.lower()
        if provider == "openai":
            return self._call_openai(prompt, context)
        if provider == "ollama":
            return self._call_ollama(prompt, context)
        raise RuntimeError(f"Unsupported LLM provider: {self.provider}")

    def _system_prompt(self) -> str:
        return (
            "You are Q-Sentinel, an AI cybersecurity assistant. "
            "Answer questions about detected attacks, detection reasoning, SHAP explanations, "
            "MITRE ATT&CK techniques, CVEs, OWASP guidance, and defensive actions. "
            "Only use the provided context. If the context is insufficient, state: "
            "'Insufficient retrieved evidence.'"
        )

    def _call_openai(self, prompt: str, context: str) -> str:
        import httpx

        user_content = f"Context:\n{context}\n\nQuestion:\n{prompt}" if context else prompt
        base = self.base_url or "https://api.openai.com/v1"
        response = httpx.post(
            f"{base.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self._system_prompt()},
                    {"role": "user", "content": user_content},
                ],
                "temperature": 0.3,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _call_ollama(self, prompt: str, context: str) -> str:
        import httpx

        user_content = f"Context:\n{context}\n\nQuestion:\n{prompt}" if context else prompt
        base = self.base_url or "http://localhost:11434"
        response = httpx.post(
            f"{base.rstrip('/')}/api/chat",
            headers={"Content-Type": "application/json"},
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self._system_prompt()},
                    {"role": "user", "content": user_content},
                ],
                "stream": False,
                "options": {"temperature": 0.3},
            },
            timeout=120.0,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "") or data.get("response", "")


llm_service = LLMService()
