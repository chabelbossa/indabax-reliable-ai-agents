from __future__ import annotations

import hashlib
import json
import os
import re
import time
from typing import Any, Protocol

from .models import AgentRun, AssistantTurn, ToolCall, TraceEntry
from .tools import TOOL_SCHEMAS, execute_tool
from .safety import execute_checked, inspect_evidence


Message = dict[str, Any]


SYSTEM_PROMPT = """You are KoraCare's cold-chain incident copilot.
Use the provided tools; never invent telemetry, procedures, incidents, or human decisions.
For an incident investigation, inspect the clinic, consult the SOP, assess risk, and create
an incident when severity is HIGH, CRITICAL, or UNKNOWN. A risky case is not resolved until
request_human_review records an explicit operator decision. Never claim vaccine stock is safe
when telemetry is missing. Keep the final operational summary concise."""


class LLMClient(Protocol):
    mode: str

    def complete(self, messages: list[Message], tools: list[dict]) -> AssistantTurn: ...


class LLMProviderError(RuntimeError):
    """Expected live-provider failure that should not crash the workshop."""


class MockLLM:
    """Deterministic incident workflow that keeps the complete lab runnable offline."""

    mode = "mock"

    def complete(self, messages: list[Message], tools: list[dict]) -> AssistantTurn:
        last = messages[-1]
        if last["role"] == "user":
            return AssistantTurn(tool_calls=[self._first_call(last["content"])])

        if last["role"] != "tool":
            return AssistantTurn(content="I could not continue the incident workflow.")

        payload = json.loads(last["content"])
        if not payload["ok"]:
            return AssistantTurn(content=f"Controlled stop: {payload['error']['message']}")

        original = next(message["content"] for message in messages if message["role"] == "user")
        if last["name"] == "get_clinic_status":
            status = payload["data"]
            if any(phrase in original.casefold() for phrase in ("status only", "statut uniquement")):
                return AssistantTurn(
                    content=(
                        f"{status['clinic_id']}: {status['temperature_c']}°C, "
                        f"sensor {status['sensor_status']}."
                    )
                )
            if status["sensor_status"] == "OFFLINE":
                query = "capteur hors ligne télémétrie"
            elif 2 <= status["temperature_c"] <= 8:
                query = "plage normale de conservation"
            else:
                query = "température excursion critique"
            return AssistantTurn(
                tool_calls=[
                    ToolCall(
                        id="mock-sop-2",
                        name="search_cold_chain_sop",
                        arguments={"query": query},
                    )
                ]
            )

        if last["name"] == "search_cold_chain_sop":
            status = self._latest_tool_data(messages, "get_clinic_status")
            if status is None:
                return AssistantTurn(content=payload["data"]["guidance"])
            return AssistantTurn(
                tool_calls=[
                    ToolCall(
                        id="mock-risk-3",
                        name="assess_excursion_risk",
                        arguments={
                            "clinic_id": status["clinic_id"],
                            "temperature_c": status["temperature_c"],
                            "duration_minutes": status["excursion_minutes"],
                            "sensor_status": status["sensor_status"],
                        },
                    )
                ]
            )

        if last["name"] == "assess_excursion_risk":
            risk = payload["data"]
            if not risk["human_review_required"]:
                return AssistantTurn(
                    content=(
                        f"{risk['clinic_id']} is within the monitored range. "
                        f"Decision: {risk['recommended_action']}."
                    )
                )
            return AssistantTurn(
                tool_calls=[
                    ToolCall(
                        id="mock-incident-4",
                        name="create_incident",
                        arguments={
                            "clinic_id": risk["clinic_id"],
                            "severity": risk["severity"],
                            "summary": (
                                f"Cold-chain alert assessed as {risk['severity']}. "
                                f"{risk['reason']}"
                            ),
                        },
                    )
                ]
            )

        if last["name"] == "create_incident":
            incident = payload["data"]
            risk = self._latest_tool_data(messages, "assess_excursion_risk")
            return AssistantTurn(
                tool_calls=[
                    ToolCall(
                        id="mock-human-5",
                        name="request_human_review",
                        arguments={
                            "incident_id": incident["incident_id"],
                            "proposed_action": risk["recommended_action"],
                            "question": (
                                f"Approve {risk['recommended_action']} for "
                                f"{incident['clinic_id']}?"
                            ),
                        },
                    )
                ]
            )

        if last["name"] == "request_human_review":
            review = payload["data"]
            incident = self._latest_tool_data(messages, "create_incident")
            return AssistantTurn(
                content=(
                    f"Incident {incident['incident_id']} escalated. Human decision: "
                    f"{review['decision']}: {review['approved_action']}."
                )
            )

        return AssistantTurn(content="The requested operation is complete.")

    @staticmethod
    def _first_call(question: str) -> ToolCall:
        normalized = question.casefold()
        clinic_match = re.search(r"kcare-[a-z]{3}-\d{2}", normalized)
        if any(word in normalized for word in ("sop", "procedure", "procédure")) and not clinic_match:
            return ToolCall(
                id="mock-sop-1",
                name="search_cold_chain_sop",
                arguments={"query": question},
            )
        clinic_id = clinic_match.group(0).upper() if clinic_match else "KCARE-XXX-99"
        return ToolCall(
            id="mock-status-1",
            name="get_clinic_status",
            arguments={"clinic_id": clinic_id},
        )

    @staticmethod
    def _latest_tool_data(messages: list[Message], name: str) -> dict | None:
        for message in reversed(messages):
            if message["role"] == "tool" and message["name"] == name:
                payload = json.loads(message["content"])
                return payload["data"] if payload["ok"] else None
        return None


def run_agent(question: str, client: LLMClient, max_turns: int = 8) -> AgentRun:
    run_id = "RUN-" + hashlib.sha256(question.encode("utf-8")).hexdigest()[:8].upper()
    messages: list[Message] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    trace: list[TraceEntry] = []
    seen_calls: set[str] = set()

    for _ in range(max_turns):
        try:
            turn = client.complete(messages, TOOL_SCHEMAS)
        except LLMProviderError as exc:
            return _finish(
                run_id,
                f"Live model request failed ({exc}). Retry shortly or switch explicitly to mock mode.",
                trace,
                client.mode,
                forced_outcome="failed",
            )
        if not turn.tool_calls:
            return _finish(run_id, turn.content or "No answer returned.", trace, client.mode, question=question)

        messages.append(
            {
                "role": "assistant",
                "content": turn.content,
                "tool_calls": [call.model_dump() for call in turn.tool_calls],
            }
        )
        for call in turn.tool_calls:
            call_signature = json.dumps(
                {"name": call.name, "arguments": call.arguments}, sort_keys=True
            )
            if call_signature in seen_calls:
                return _finish(
                    run_id,
                    "Stopped safely because the model repeated the same tool call.",
                    trace,
                    client.mode,
                    forced_outcome="stopped",
                )
            seen_calls.add(call_signature)
            started = time.perf_counter()
            result = execute_checked(call, trace, question)
            latency_ms = (time.perf_counter() - started) * 1000
            trace.append(
                TraceEntry(
                    step=len(trace) + 1,
                    call_id=call.id,
                    tool=call.name,
                    arguments=call.arguments,
                    status="success" if result.ok else "error",
                    result=result.data,
                    error=None if result.ok else result.error["message"],
                    latency_ms=latency_ms,
                )
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": call.name,
                    "content": result.model_dump_json(),
                }
            )
            if not result.ok:
                return _finish(
                    run_id,
                    f"Controlled stop: {result.error['message']}",
                    trace,
                    client.mode,
                    forced_outcome="failed",
                )

    return _finish(
        run_id,
        f"Stopped safely after {max_turns} turns.",
        trace,
        client.mode,
        forced_outcome="stopped",
    )


def _finish(
    run_id: str,
    answer: str,
    trace: list[TraceEntry],
    mode: str,
    forced_outcome: str | None = None,
    question: str = "",
) -> AgentRun:
    if forced_outcome:
        return AgentRun(run_id=run_id, answer=answer, trace=trace, mode=mode,
                        outcome=forced_outcome, safety_status="blocked")
    evidence = inspect_evidence(trace, question)
    if evidence["missing"]:
        return AgentRun(run_id=run_id, answer=evidence["missing"], trace=trace, mode=mode,
                        outcome="stopped", safety_status="blocked")
    human_approved = evidence["human_approved"]
    if evidence["human_required"] and not human_approved:
        return AgentRun(
            run_id=run_id,
            answer="Safety gate: this incident still requires explicit human review.",
            trace=trace,
            mode=mode,
            outcome="stopped",
            safety_status="review_required",
        )
    if human_approved:
        return AgentRun(
            run_id=run_id,
            answer=answer,
            trace=trace,
            mode=mode,
            outcome="escalated",
            safety_status="human_approved",
        )
    return AgentRun(
        run_id=run_id,
        answer=answer,
        trace=trace,
        mode=mode,
        outcome="completed",
        safety_status="safe",
    )


def make_client(mode: str | None = None) -> LLMClient:
    selected = (mode or os.getenv("LLM_MODE", "mock")).casefold()
    if selected == "mock":
        return MockLLM()
    if selected == "gemini":
        from .gemini_client import GeminiLLM

        return GeminiLLM()
    raise ValueError("LLM_MODE must be 'mock' or 'gemini'")
