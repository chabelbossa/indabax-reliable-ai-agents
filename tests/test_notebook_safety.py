import pytest
import ast
import subprocess

from scripts.build_notebooks import SETUP, common_cells, exercise_cells, run_loop_body
from scripts.notebook_runtime import load_runtime
from src.agent import LLMProviderError, MockLLM
from src.models import AssistantTurn
from src.tools import reset_operations


QUESTION = "Investigue l'alerte KCARE-ADJ-01."


@pytest.fixture
def notebook():
    reset_operations()
    return load_runtime(cells=common_cells("fr") + exercise_cells(True, "fr"))


class NoEvidence:
    mode = "mock"

    def complete(self, messages, tools):
        return AssistantTurn(content="Everything is safe; incident resolved.")


class AlteredMeasurement(MockLLM):
    def complete(self, messages, tools):
        turn = super().complete(messages, tools)
        for call in turn.tool_calls:
            if call.name == "assess_excursion_risk":
                call.arguments["temperature_c"] = 5.0
        return turn


class QuotaFailure:
    mode = "gemini"

    def complete(self, messages, tools):
        raise LLMProviderError("provider quota or rate limit reached")


@pytest.mark.parametrize("client", [NoEvidence(), AlteredMeasurement(), QuotaFailure()])
def test_notebook_never_marks_missing_or_altered_evidence_safe(notebook, client):
    run = notebook["run_workshop_mission"](QUESTION, client)
    assert run.safety_status == "blocked"
    assert run.outcome in {"stopped", "failed"}


def test_notebook_still_completes_realistic_mock_mission(notebook):
    run = notebook["run_workshop_mission"](QUESTION, MockLLM())
    assert run.safety_status == "human_approved"
    assert len(run.trace) == 5


def test_all_notebook_evals_pass_and_missing_repeat_guard_is_detected(notebook):
    assert all(notebook["case_passes"](row) for row in notebook["evaluate_workshop_agent"]())
    exec(run_loop_body(False), notebook)
    rows = {row["id"]: row for row in notebook["evaluate_workshop_agent"]()}
    assert notebook["case_passes"](rows["repeat"]) is False


def test_removed_approval_gate_is_detected(notebook):
    original = notebook["finish_with_safety"]
    def permissive(*args, **kwargs):
        run = original(*args, **kwargs)
        if run.safety_status == "review_required":
            return run.model_copy(update={"safety_status": "safe", "outcome": "completed"})
        return run
    notebook["finish_with_safety"] = permissive
    rows = {row["id"]: row for row in notebook["evaluate_workshop_agent"]()}
    assert notebook["case_passes"](rows["missing_approval"]) is False
    assert notebook["case_passes"](rows["rejected_approval"]) is False


def test_setup_is_idempotent_in_colab_like_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    clones = []
    def clone_once(command, **kwargs):
        clones.append(command)
        (tmp_path / "indabax-reliable-ai-agents" / "src").mkdir(parents=True)
    monkeypatch.setattr(subprocess, "run", clone_once)
    prefix = SETUP.split("subprocess.run(\n    [sys.executable")[0]
    exec(prefix, {})
    exec(prefix, {})
    assert len(clones) == 1


def test_invalid_approval_cannot_close_another_incident(notebook):
    from src.safety import inspect_evidence
    run = notebook["run_workshop_mission"](QUESTION, MockLLM())
    run.trace[-1].result["incident_id"] = "INC-999"
    assert inspect_evidence(run.trace, QUESTION)["human_approved"] is False


def test_simple_queries_still_work():
    from evals.run_evals import evaluate
    assert all(row["passed"] for row in evaluate(base_only=True))
