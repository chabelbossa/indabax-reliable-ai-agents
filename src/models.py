from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ClinicStatusInput(StrictModel):
    clinic_id: str = Field(pattern=r"^KCARE-[A-Z]{3}-\d{2}$")


class SOPSearchInput(StrictModel):
    query: str = Field(min_length=3, max_length=200)


class ExcursionRiskInput(StrictModel):
    clinic_id: str = Field(pattern=r"^KCARE-[A-Z]{3}-\d{2}$")
    temperature_c: float = Field(ge=-30, le=40)
    duration_minutes: int = Field(ge=0, le=1440)
    sensor_status: Literal["OK", "OFFLINE"] = "OK"


class IncidentInput(StrictModel):
    clinic_id: str = Field(pattern=r"^KCARE-[A-Z]{3}-\d{2}$")
    severity: Literal["HIGH", "CRITICAL", "UNKNOWN"]
    summary: str = Field(min_length=10, max_length=300)


class HumanReviewInput(StrictModel):
    incident_id: str = Field(pattern=r"^INC-\d{3}$")
    proposed_action: Literal[
        "CONTINUE_MONITORING",
        "QUARANTINE_STOCK",
        "QUARANTINE_AND_TRANSFER",
        "MANUAL_INSPECTION",
    ]
    question: str = Field(min_length=10, max_length=300)


class ToolCall(StrictModel):
    id: str
    name: str
    arguments: dict[str, Any]
    thought_signature: bytes | None = None


class AssistantTurn(StrictModel):
    content: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)


class ToolResult(StrictModel):
    ok: bool
    data: Any = None
    error: dict[str, str] | None = None


class TraceEntry(StrictModel):
    step: int = Field(default=1, ge=1)
    call_id: str = "unknown"
    tool: str
    arguments: dict[str, Any]
    status: Literal["success", "error"]
    result: Any = None
    error: str | None = None
    latency_ms: float = Field(ge=0)


class AgentRun(StrictModel):
    run_id: str = "RUN-UNKNOWN"
    answer: str
    trace: list[TraceEntry] = Field(default_factory=list)
    mode: Literal["gemini", "mock"]
    outcome: Literal["completed", "escalated", "failed", "stopped"] = "completed"
    safety_status: Literal["safe", "human_approved", "review_required", "blocked"] = "safe"
