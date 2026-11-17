import functools

import httpx
import pytest

from app.core.config import settings
from app.llm import ollama_client
from app.llm.ollama_client import OllamaClient, model_matches


def _install_transport(monkeypatch, handler):
    transport = httpx.MockTransport(handler)
    real_client = httpx.AsyncClient
    monkeypatch.setattr(ollama_client.httpx, "AsyncClient", functools.partial(real_client, transport=transport))


def _chat_ok(content: str, **extra) -> dict:
    body = {"message": {"role": "assistant", "content": content}, "done": True, "prompt_eval_count": 42, "eval_count": 7}
    body.update(extra)
    return body


def test_model_matches_accepts_latest_tag_for_untagged_name():
    assert model_matches("llama3.1", "llama3.1:latest")
    assert model_matches("llama3.1:8b", "llama3.1:8b")
    assert not model_matches("llama3.1:8b", "llama3.1:70b")
    assert not model_matches("llama3.1", "llama3.1:8b")


@pytest.mark.asyncio
async def test_health_reports_model_available_when_tag_listed(monkeypatch):
    _install_transport(monkeypatch, lambda req: httpx.Response(200, json={"models": [{"name": "llama3.1:latest"}]}))
    health = await OllamaClient("http://ollama.test").health("llama3.1")
    assert health.reachable and health.model_available
    assert health.installed_models == ["llama3.1:latest"]
    assert health.error is None


@pytest.mark.asyncio
async def test_health_reports_missing_model(monkeypatch):
    _install_transport(monkeypatch, lambda req: httpx.Response(200, json={"models": [{"name": "mistral:latest"}]}))
    health = await OllamaClient("http://ollama.test").health("llama3.1")
    assert health.reachable and not health.model_available
    assert "not installed" in health.error


@pytest.mark.asyncio
async def test_health_reports_unreachable(monkeypatch):
    def handler(request):
        raise httpx.ConnectError("refused", request=request)

    _install_transport(monkeypatch, handler)
    health = await OllamaClient("http://ollama.test").health("llama3.1")
    assert not health.reachable and not health.model_available
    assert "not reachable" in health.error


@pytest.mark.asyncio
async def test_health_rejects_malformed_tags_body(monkeypatch):
    _install_transport(monkeypatch, lambda req: httpx.Response(200, content=b"<html>proxy</html>"))
    health = await OllamaClient("http://ollama.test").health("llama3.1")
    assert health.reachable and not health.model_available


@pytest.mark.asyncio
async def test_chat_returns_text_and_token_counts(monkeypatch):
    _install_transport(monkeypatch, lambda req: httpx.Response(200, json=_chat_ok("  Brute force is T1110.  ")))
    result = await OllamaClient("http://ollama.test").chat("llama3.1", "sys", "user")
    assert result.text == "Brute force is T1110."
    assert result.prompt_tokens == 42
    assert result.completion_tokens == 7
    assert result.truncated is False


@pytest.mark.asyncio
async def test_chat_flags_truncated_output(monkeypatch):
    _install_transport(monkeypatch, lambda req: httpx.Response(200, json=_chat_ok("partial", done_reason="length")))
    result = await OllamaClient("http://ollama.test").chat("llama3.1", "sys", "user")
    assert result.truncated is True


@pytest.mark.asyncio
async def test_chat_sends_non_streaming_request_with_limits(monkeypatch):
    seen = {}

    def handler(request):
        seen["body"] = request.read()
        return httpx.Response(200, json=_chat_ok("ok"))

    _install_transport(monkeypatch, handler)
    await OllamaClient("http://ollama.test").chat("llama3.1", "sys", "user")
    assert b'"stream":false' in seen["body"].replace(b" ", b"")
    assert str(settings.llm_max_output_tokens).encode() in seen["body"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response_factory, code",
    [
        (lambda req: httpx.Response(200, content=b"{not json"), "llm_malformed_response"),
        (lambda req: httpx.Response(200, json={"done": True}), "llm_malformed_response"),
        (lambda req: httpx.Response(200, json=_chat_ok("   ")), "llm_empty_response"),
        (lambda req: httpx.Response(404, json={"error": "model not found"}), "llm_model_missing"),
        (lambda req: httpx.Response(500, json={"error": "boom"}), "llm_error"),
    ],
)
async def test_chat_maps_bad_responses_to_error_codes(monkeypatch, response_factory, code):
    _install_transport(monkeypatch, response_factory)
    from app.llm.types import LLMError

    with pytest.raises(LLMError) as exc:
        await OllamaClient("http://ollama.test").chat("llama3.1", "sys", "user")
    assert exc.value.code == code


@pytest.mark.asyncio
async def test_chat_maps_timeout(monkeypatch):
    def handler(request):
        raise httpx.ReadTimeout("slow", request=request)

    _install_transport(monkeypatch, handler)
    from app.llm.types import LLMError

    with pytest.raises(LLMError) as exc:
        await OllamaClient("http://ollama.test").chat("llama3.1", "sys", "user")
    assert exc.value.code == "llm_timeout"


@pytest.mark.asyncio
async def test_chat_maps_unreachable(monkeypatch):
    def handler(request):
        raise httpx.ConnectError("refused", request=request)

    _install_transport(monkeypatch, handler)
    from app.llm.types import LLMError

    with pytest.raises(LLMError) as exc:
        await OllamaClient("http://ollama.test").chat("llama3.1", "sys", "user")
    assert exc.value.code == "llm_unavailable"
