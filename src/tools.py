from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from .models import (
    ClinicStatusInput,
    ExcursionRiskInput,
    HumanReviewInput,
    IncidentInput,
    SOPSearchInput,
    ToolResult,
)


CLINICS_PATH = Path(__file__).resolve().parents[1] / "data" / "clinics.json"
SOP_PATH = Path(__file__).resolve().parents[1] / "data" / "cold_chain_sop.json"
INCIDENTS: list[dict] = []
HUMAN_REVIEWS: list[dict] = []


def get_clinic_status(arguments: dict) -> ToolResult:
    """Return the latest synthetic cold-chain telemetry for one clinic."""
    try:
        values = ClinicStatusInput.model_validate(arguments)
        clinics = json.loads(CLINICS_PATH.read_text(encoding="utf-8"))
        clinic = next(
            (record for record in clinics if record["clinic_id"] == values.clinic_id),
            None,
        )
        if clinic is None:
            return ToolResult(
                ok=False,
                error={"type": "ClinicNotFound", "message": f"Unknown clinic: {values.clinic_id}"},
            )
        return ToolResult(ok=True, data=clinic)
    except Exception as exc:
        return ToolResult(ok=False, error={"type": type(exc).__name__, "message": str(exc)})


def search_cold_chain_sop(arguments: dict) -> ToolResult:
    """Search a tiny, auditable cold-chain procedure library."""
    try:
        values = SOPSearchInput.model_validate(arguments)
        query = values.query.casefold()
        records = json.loads(SOP_PATH.read_text(encoding="utf-8"))
        match = next(
            (
                record
                for record in records
                if any(keyword.casefold() in query for keyword in record["keywords"])
            ),
            None,
        )
        if match is None:
            return ToolResult(
                ok=False,
                error={"type": "SOPNotFound", "message": "No matching cold-chain procedure was found."},
            )
        return ToolResult(ok=True, data=match)
    except Exception as exc:
        return ToolResult(ok=False, error={"type": type(exc).__name__, "message": str(exc)})


def assess_excursion_risk(arguments: dict) -> ToolResult:
    """Classify an excursion with deterministic thresholds visible to participants."""
    try:
        values = ExcursionRiskInput.model_validate(arguments)
        if values.sensor_status == "OFFLINE":
            severity = "UNKNOWN"
            action = "MANUAL_INSPECTION"
            reason = "Telemetry is unavailable; stock safety cannot be inferred."
        elif 2 <= values.temperature_c <= 8:
            severity = "LOW"
            action = "CONTINUE_MONITORING"
            reason = "Temperature is inside the 2°C to 8°C storage range."
        elif values.duration_minutes >= 30:
            severity = "CRITICAL"
            action = "QUARANTINE_AND_TRANSFER"
            reason = "The temperature excursion exceeded the 30-minute critical threshold."
        else:
            severity = "HIGH"
            action = "QUARANTINE_STOCK"
            reason = "Temperature is outside the safe range, but below the critical duration."
        return ToolResult(
            ok=True,
            data={
                "clinic_id": values.clinic_id,
                "severity": severity,
                "recommended_action": action,
                "human_review_required": severity in {"HIGH", "CRITICAL", "UNKNOWN"},
                "reason": reason,
            },
        )
    except Exception as exc:
        return ToolResult(ok=False, error={"type": type(exc).__name__, "message": str(exc)})


def create_incident(arguments: dict) -> ToolResult:
    """Create an in-memory operational incident after strict validation."""
    try:
        values = IncidentInput.model_validate(arguments)
        incident = {
            "incident_id": f"INC-{len(INCIDENTS) + 1:03d}",
            "status": "AWAITING_HUMAN_REVIEW",
            **values.model_dump(),
        }
        INCIDENTS.append(incident)
        return ToolResult(ok=True, data=deepcopy(incident))
    except Exception as exc:
        return ToolResult(ok=False, error={"type": type(exc).__name__, "message": str(exc)})


def request_human_review(arguments: dict) -> ToolResult:
    """Simulate contacting the on-call operator and return an explicit human decision."""
    try:
        values = HumanReviewInput.model_validate(arguments)
        incident = next(
            (item for item in INCIDENTS if item["incident_id"] == values.incident_id),
            None,
        )
        if incident is None:
            return ToolResult(
                ok=False,
                error={"type": "IncidentNotFound", "message": f"Unknown incident: {values.incident_id}"},
            )
        expected_action = {
            "CRITICAL": "QUARANTINE_AND_TRANSFER",
            "HIGH": "QUARANTINE_STOCK",
            "UNKNOWN": "MANUAL_INSPECTION",
        }[incident["severity"]]
        approved = values.proposed_action == expected_action
        decision = {
            "review_id": f"REVIEW-{len(HUMAN_REVIEWS) + 1:03d}",
            "incident_id": values.incident_id,
            "channel": "simulated_on_call",
            "operator": "Awa K. (simulation)",
            "decision": "APPROVED" if approved else "REJECTED",
            "approved_action": values.proposed_action if approved else None,
            "expected_action": expected_action,
            "note": (
                "Human operator approval recorded. The action may now proceed."
                if approved
                else "Human operator rejected an action inconsistent with incident severity."
            ),
        }
        incident["status"] = "HUMAN_APPROVED" if approved else "HUMAN_REJECTED"
        HUMAN_REVIEWS.append(decision)
        return ToolResult(ok=True, data=decision)
    except Exception as exc:
        return ToolResult(ok=False, error={"type": type(exc).__name__, "message": str(exc)})


def reset_operations() -> None:
    INCIDENTS.clear()
    HUMAN_REVIEWS.clear()


TOOL_SCHEMAS = [
    {
        "name": "get_clinic_status",
        "description": "Read the latest cold-chain telemetry for a KoraCare clinic.",
        "parameters": ClinicStatusInput.model_json_schema(),
    },
    {
        "name": "search_cold_chain_sop",
        "description": "Search the verified local cold-chain procedures.",
        "parameters": SOPSearchInput.model_json_schema(),
    },
    {
        "name": "assess_excursion_risk",
        "description": "Classify cold-chain risk from validated telemetry.",
        "parameters": ExcursionRiskInput.model_json_schema(),
    },
    {
        "name": "create_incident",
        "description": "Create an operational incident for HIGH, CRITICAL, or UNKNOWN risk.",
        "parameters": IncidentInput.model_json_schema(),
    },
    {
        "name": "request_human_review",
        "description": "Contact the simulated on-call operator for an explicit decision.",
        "parameters": HumanReviewInput.model_json_schema(),
    },
]


def execute_tool(name: str, arguments: dict) -> ToolResult:
    if name == "get_clinic_status":
        return get_clinic_status(arguments)
    if name == "search_cold_chain_sop":
        return search_cold_chain_sop(arguments)
    if name == "assess_excursion_risk":
        return assess_excursion_risk(arguments)
    if name == "create_incident":
        return create_incident(arguments)
    if name == "request_human_review":
        return request_human_review(arguments)
    return ToolResult(
        ok=False,
        error={"type": "UnknownTool", "message": f"Unknown tool: {name}"},
    )
