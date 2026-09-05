from google.genai import errors, types

from src.gemini_client import GeminiLLM
from src.agent import run_agent
from src.tools import TOOL_SCHEMAS
import httpx
import pytest
from src.agent import LLMProviderError


class FakeModels:
    def __init__(self, response):
        self.response = response
        self.request = None

    def generate_content(self, **kwargs):
        self.request = kwargs
        if isinstance(self.response, Exception):
            raise self.response
        if isinstance(self.response, list):
            return self.response.pop(0)
        return self.response


class FakeClient:
    def __init__(self, response):
        self.models = FakeModels(response)


def response_with_function_call():
    part = types.Part.from_function_call(
        name="get_clinic_status", args={"clinic_id": "KCARE-OUI-02"}
    )
    part.thought_signature = b"signature"
    content = types.Content(role="model", parts=[part])
    candidate = types.Candidate(content=content)
    return types.GenerateContentResponse(candidates=[candidate])


def response_with_text(text: str):
    content = types.Content(role="model", parts=[types.Part.from_text(text=text)])
    return types.GenerateContentResponse(candidates=[types.Candidate(content=content)])


def test_gemini_adapter_normalizes_function_call() -> None:
    fake = FakeClient(response_with_function_call())
    llm = GeminiLLM(api_key="unused", client=fake)
    turn = llm.complete([{"role": "user", "content": "Check KCARE-OUI-02"}], TOOL_SCHEMAS)
    assert turn.tool_calls[0].name == "get_clinic_status"
    assert turn.tool_calls[0].arguments["clinic_id"] == "KCARE-OUI-02"
    assert turn.tool_calls[0].thought_signature == b"signature"
    assert fake.models.request["model"] == "gemini-3.7-flash"


def test_gemini_adapter_preserves_function_call_signature() -> None:
    content = GeminiLLM._to_content(
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "name": "get_clinic_status",
                    "arguments": {"clinic_id": "KCARE-OUI-02"},
                    "thought_signature": b"signature",
                }
            ],
        }
    )
    assert content.role == "model"
    assert content.parts[0].thought_signature == b"signature"


def test_gemini_adapter_runs_through_agent_loop() -> None:
    fake = FakeClient(
        [
            response_with_function_call(),
            response_with_text("KCARE-OUI-02 telemetry retrieved."),
        ]
    )
    run = run_agent(
        "Status only for KCARE-OUI-02.",
        GeminiLLM(api_key="unused", client=fake),
    )
    assert run.mode == "gemini"
    assert run.answer == "KCARE-OUI-02 telemetry retrieved."
    assert run.trace[0].result["temperature_c"] == 5.4


def test_gemini_rate_limit_stops_agent_cleanly() -> None:
    failure = errors.ClientError(
        429,
        {"error": {"code": 429, "message": "quota reached", "status": "RESOURCE_EXHAUSTED"}},
    )
    run = run_agent(
        "Status only for KCARE-OUI-02.",
        GeminiLLM(api_key="unused", client=FakeClient(failure)),
    )
    assert run.mode == "gemini"
    assert run.trace == []
    assert "quota or rate limit reached" in run.answer
    assert "switch explicitly to mock mode" in run.answer


@pytest.mark.parametrize("response", [types.GenerateContentResponse(candidates=[]), httpx.ReadTimeout("secret URL must not be exposed")])
def test_empty_or_network_response_is_sanitized(response):
    llm = GeminiLLM(api_key="unused", client=FakeClient(response))
    with pytest.raises(LLMProviderError) as failure:
        llm.complete([{"role": "user", "content": "Hello"}], TOOL_SCHEMAS)
    assert "secret" not in str(failure.value)
