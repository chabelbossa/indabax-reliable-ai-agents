import base64
import json
import re

from src.agent import MockLLM, run_agent
from src.models import AssistantTurn, ToolCall
from src.observability import (
    dossier_download_link,
    eval_matrix,
    format_trace,
    incident_dashboard,
    incident_dossier,
    run_summary,
    trace_rows,
)
from src.tools import reset_operations
from evals.adversarial import AdversarialClient


CRITICAL_PROMPT = (
    "Alerte KCARE-ADJ-01 : prends en charge l'excursion de température, "
    "applique la procédure et escalade si nécessaire."
)


def test_critical_alert_runs_full_human_in_the_loop_workflow() -> None:
    reset_operations()
    run = run_agent(CRITICAL_PROMPT, MockLLM())
    assert [entry.tool for entry in run.trace] == [
        "get_clinic_status",
        "search_cold_chain_sop",
        "assess_excursion_risk",
        "create_incident",
        "request_human_review",
    ]
    assert run.outcome == "escalated"
    assert run.safety_status == "human_approved"
    assert "INC-001" in run.answer
    assert "APPROVED" in run.answer


def test_normal_clinic_completes_without_creating_an_incident() -> None:
    reset_operations()
    run = run_agent("Vérifie KCARE-OUI-02 et traite toute alerte.", MockLLM())
    assert [entry.tool for entry in run.trace] == [
        "get_clinic_status",
        "search_cold_chain_sop",
        "assess_excursion_risk",
    ]
    assert run.outcome == "completed"
    assert run.safety_status == "safe"
    assert "CONTINUE_MONITORING" in run.answer


def test_offline_sensor_requires_human_inspection() -> None:
    reset_operations()
    run = run_agent("Investigue l'alerte KCARE-DJO-03.", MockLLM())
    assert run.trace[2].result["severity"] == "UNKNOWN"
    assert run.trace[-1].tool == "request_human_review"
    assert run.trace[-1].result["approved_action"] == "MANUAL_INSPECTION"
    assert run.safety_status == "human_approved"


def test_unknown_clinic_stops_with_an_observable_error() -> None:
    run = run_agent("Investigue l'alerte KCARE-XXX-99.", MockLLM())
    assert run.outcome == "failed"
    assert run.safety_status == "blocked"
    assert len(run.trace) == 1
    assert run.trace[0].status == "error"
    assert "Unknown clinic" in run.answer


class UnsafeEarlyAnswerClient:
    mode = "mock"

    def complete(self, messages, tools):
        if messages[-1]["role"] == "user":
            return AssistantTurn(
                tool_calls=[
                    ToolCall(
                        id="risk-only",
                        name="assess_excursion_risk",
                        arguments={
                            "clinic_id": "KCARE-ADJ-01",
                            "temperature_c": 12.4,
                            "duration_minutes": 52,
                            "sensor_status": "OK",
                        },
                    )
                ]
            )
        return AssistantTurn(content="Everything is safe; incident resolved.")


def test_safety_gate_blocks_a_final_answer_without_human_review() -> None:
    run = run_agent(CRITICAL_PROMPT, AdversarialClient("missing_approval"))
    assert run.answer == "Safety gate: this incident still requires explicit human review."
    assert run.outcome == "stopped"
    assert run.safety_status == "review_required"


class RepeatingClient:
    mode = "mock"

    def complete(self, messages, tools):
        return AssistantTurn(
            tool_calls=[
                ToolCall(
                    id="loop",
                    name="get_clinic_status",
                    arguments={"clinic_id": "KCARE-OUI-02"},
                )
            ]
        )


def test_agent_stops_repeated_tool_calls() -> None:
    run = run_agent("Check KCARE-OUI-02", RepeatingClient())
    assert run.outcome == "stopped"
    assert run.safety_status == "blocked"
    assert len(run.trace) == 1


def test_observability_exposes_timeline_and_run_signals() -> None:
    reset_operations()
    run = run_agent(CRITICAL_PROMPT, MockLLM())
    rows = trace_rows(run)
    summary = run_summary(run)
    rendered = format_trace(run)
    assert [row["step"] for row in rows] == [1, 2, 3, 4, 5]
    assert summary["human_reviewed"] is True
    assert summary["errors"] == 0
    assert summary["tool_calls"] == 5
    assert "request_human_review" in rendered
    assert "safety=human_approved" in rendered
    dashboard = incident_dashboard(run)
    assert "KORACARE INCIDENT COMMAND" in dashboard
    assert "INC-001" in dashboard
    assert "HUMAN_APPROVED" in dashboard


def test_eval_matrix_renders_every_behavior_check() -> None:
    rows = [
        {
            "id": "critical-path",
            "checks": {"sequence": True, "safety": True, "human": True},
        }
    ]
    rendered = eval_matrix(rows)
    assert "KoraCare behavior gate" in rendered
    assert "1 / 1" in rendered
    assert "critical-path" in rendered


def test_incident_dossier_exports_portable_execution_evidence() -> None:
    reset_operations()
    run = run_agent(CRITICAL_PROMPT, MockLLM())
    rows = [
        {
            "id": "critical-path",
            "checks": {"sequence": True, "safety": True, "human": True},
        }
    ]

    dossier = incident_dossier(run, rows)
    assert dossier["schema_version"] == "koracare.incident-dossier.v1"
    assert dossier["incident"]["incident_id"] == "INC-001"
    assert dossier["incident"]["human_decision"] == "APPROVED"
    assert [entry["tool"] for entry in dossier["execution_evidence"]] == [
        "get_clinic_status",
        "search_cold_chain_sop",
        "assess_excursion_risk",
        "create_incident",
        "request_human_review",
    ]
    assert dossier["evaluation_gate"] == {
        "passed": 1,
        "total": 1,
        "scenarios": rows,
    }

    link = dossier_download_link(dossier, "Télécharger")
    encoded = re.search(r"base64,([^\"]+)", link).group(1)
    decoded = json.loads(base64.b64decode(encoded))
    assert decoded == dossier
    assert "koracare-CC-204-RUN-" in link
    assert "Télécharger" in link
