from app.core.config import settings


class LLMService:
    def __init__(self) -> None:
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self.api_key = settings.llm_api_key

    @property
    def available(self) -> bool:
        return bool(self.provider and self.model and self.api_key)

    def answer(self, prompt: str, context: str = "") -> str:
        if not self.available:
            raise RuntimeError("LLM provider is not configured. Set LLM_PROVIDER, LLM_MODEL, and LLM_API_KEY.")

        if self.provider.lower() == "openai":
            return self._call_openai(prompt, context)
        raise RuntimeError(f"Unsupported LLM provider: {self.provider}")

    def _call_openai(self, prompt: str, context: str) -> str:
        import httpx

        system_prompt = (
            "You are Q-Sentinel, an AI cybersecurity assistant. "
            "Answer questions about detected attacks, detection reasoning, SHAP explanations, "
            "MITRE ATT&CK techniques, CVEs, OWASP guidance, and defensive actions. "
            "Only use the provided context. If the context is insufficient, state: "
            "'Insufficient retrieved evidence.'"
        )
        user_content = f"Context:\n{context}\n\nQuestion:\n{prompt}" if context else prompt

        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                "temperature": 0.3,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


llm_service = LLMService()
