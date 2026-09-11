"""Executable agent used by the French V2 teaching deck.

Each function corresponds to one concept in the presentation: model proposal,
controlled execution, observation, evidence gate, and orchestration loop.
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agent import LLMClient, MockLLM, SYSTEM_PROMPT
from src.models import AssistantTurn, ToolCall, TraceEntry
from src.safety import execute_checked, inspect_evidence
from src.tools import TOOL_SCHEMAS, reset_operations


Message = dict[str, object]


@dataclass
class AgentState:
    """Everything required to continue one agent run."""

    question: str
    messages: list[Message]
    trace: list[TraceEntry] = field(default_factory=list)
    seen_calls: set[str] = field(default_factory=set)


def create_state(question: str) -> AgentState:
    """Create the initial conversation and an empty execution trace."""
    return AgentState(
        question=question,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
    )


def ask_model(state: AgentState, client: LLMClient) -> AssistantTurn:
    """Give the history and tool contracts to the selected model."""
    return client.complete(state.messages, TOOL_SCHEMAS)


def make_trace(
    state: AgentState, call: ToolCall, result, started: float
) -> TraceEntry:
    """Build one observable trace entry from the executed proposal."""
    return TraceEntry(
        step=len(state.trace) + 1,
        call_id=call.id,
        tool=call.name,
        arguments=call.arguments,
        status="success" if result.ok else "error",
        result=result.data,
        error=None if result.ok else result.error["message"],
        latency_ms=(time.perf_counter() - started) * 1000,
    )


def execute_and_observe(state: AgentState, call: ToolCall) -> bool:
    """Validate one proposal, execute it, trace it, and add its result."""
    signature = json.dumps(
        {"name": call.name, "arguments": call.arguments}, sort_keys=True
    )
    if signature in state.seen_calls:
        raise RuntimeError("Repeated tool call blocked")
    state.seen_calls.add(signature)

    started = time.perf_counter()
    result = execute_checked(call, state.trace, state.question)
    state.trace.append(make_trace(state, call, result, started))
    state.messages.append(
        {
            "role": "tool",
            "tool_call_id": call.id,
            "name": call.name,
            "content": result.model_dump_json(),
        }
    )
    return result.ok


def finish(state: AgentState, answer: str) -> dict:
    """Release the answer only when the trace contains the required evidence."""
    evidence = inspect_evidence(state.trace, state.question)
    if evidence["missing"]:
        return {"status": "blocked", "reason": evidence["missing"]}
    if evidence["human_required"] and not evidence["human_approved"]:
        return {"status": "review_required"}
    return {"status": "approved", "answer": answer}


def run_agent(question: str, client: LLMClient, max_turns: int = 8) -> dict:
    """Repeat proposal and observation until an answer or controlled stop."""
    state = create_state(question)
    for _ in range(max_turns):
        turn = ask_model(state, client)
        if not turn.tool_calls:
            return {**finish(state, turn.content or "No answer"), "trace": state.trace}

        state.messages.append(
            {
                "role": "assistant",
                "content": turn.content,
                "tool_calls": [call.model_dump() for call in turn.tool_calls],
            }
        )
        for call in turn.tool_calls:
            if not execute_and_observe(state, call):
                return {"status": "blocked", "trace": state.trace}

    return {"status": "blocked", "reason": "turn_limit", "trace": state.trace}


def demo() -> dict:
    """Run the complete synthetic incident without an external API."""
    reset_operations()
    return run_agent("Investigue l'alerte KCARE-ADJ-01.", MockLLM())


if __name__ == "__main__":
    run = demo()
    print("STATUS:", run["status"])
    print("TOOLS:", " -> ".join(entry.tool for entry in run["trace"]))
