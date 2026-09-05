"""Small, visible evidence rules for the synthetic workshop, not medical policy."""
import re

from .models import ToolCall, ToolResult
from .tools import execute_tool


def latest(trace, tool):
    for entry in reversed(trace):
        if entry.tool == tool and entry.status == "success":
            return entry.result if isinstance(entry.result, dict) else {}
    return {}


def evidence_error(call, trace, question=""):
    """Validate provenance before executing any state-changing operation."""
    args = call.arguments
    status = latest(trace, "get_clinic_status")
    risk = latest(trace, "assess_excursion_risk")
    incident = latest(trace, "create_incident")
    requested = re.search(r"KCARE-[A-Z]{3}-\d{2}", question.upper())
    if call.name == "get_clinic_status" and requested:
        if args.get("clinic_id") != requested.group():
            return "La clinique demandée ne correspond pas / clinic mismatch."
    if call.name == "assess_excursion_risk":
        if not status or not latest(trace, "search_cold_chain_sop"):
            return "Mesure et procédure requises / telemetry and SOP required."
        expected = {
            "clinic_id": status["clinic_id"],
            "temperature_c": status["temperature_c"],
            "duration_minutes": status["excursion_minutes"],
            "sensor_status": status["sensor_status"],
        }
        if any(args.get(key) != value for key, value in expected.items()):
            return "Mesure altérée / arguments differ from observed telemetry."
    if call.name == "create_incident":
        if not risk.get("human_review_required") or any(
            args.get(key) != risk.get(key) for key in ("clinic_id", "severity")
        ):
            return "Incident incohérent / incident must match the assessed risk."
    if call.name == "request_human_review":
        if not incident or args.get("incident_id") != incident.get("incident_id"):
            return "Mauvais incident / review must refer to this run's incident."
    return None


def execute_checked(call, trace, question=""):
    error = evidence_error(call, trace, question)
    if error:
        return ToolResult(ok=False, error={"type": "EvidenceError", "message": error})
    return execute_tool(call.name, call.arguments)


def inspect_evidence(trace, question):
    """Return missing evidence, review obligation and matched approval separately."""
    for index, entry in enumerate(trace):
        call = ToolCall(id=entry.call_id, name=entry.tool, arguments=entry.arguments)
        error = evidence_error(call, trace[:index], question)
        if error or entry.status != "success":
            return {"missing": error or "Outil en erreur / tool failed.",
                    "human_required": False, "human_approved": False}
    status = latest(trace, "get_clinic_status")
    sop = latest(trace, "search_cold_chain_sop")
    risk = latest(trace, "assess_excursion_risk")
    incident = latest(trace, "create_incident")
    review = latest(trace, "request_human_review")
    normalized = question.casefold()
    status_only = any(word in normalized for word in ("status only", "statut uniquement"))
    procedure_only = not re.search(r"kcare-[a-z]{3}-\d{2}", normalized) and any(
        word in normalized for word in ("sop", "procedure", "procédure")
    )
    enough = bool(status) if status_only else bool(sop) if procedure_only else bool(status and sop and risk)
    required = bool(risk.get("human_review_required"))
    approved = bool(
        required and incident and review
        and incident.get("clinic_id") == risk.get("clinic_id")
        and incident.get("severity") == risk.get("severity")
        and review.get("incident_id") == incident.get("incident_id")
        and review.get("decision") == "APPROVED"
        and review.get("approved_action") == risk.get("recommended_action")
    )
    return {"missing": None if enough else "Preuves insuffisantes / insufficient evidence.",
            "human_required": required, "human_approved": approved}
