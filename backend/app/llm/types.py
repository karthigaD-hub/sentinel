from dataclasses import dataclass


class LLMError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class LLMGeneration:
    text: str
    model: str
    truncated: bool
    prompt_tokens: int | None
    completion_tokens: int | None
    duration_ms: float
