from scripts.smoke_gemini import live_checks
from src.agent import MockLLM, run_agent
from src.tools import reset_operations


QUESTION = (
    "Alerte KCARE-ADJ-01 : prends en charge l'excursion de température, "
    "applique la procédure et escalade si nécessaire."
)


def test_live_smoke_requires_the_complete_approved_gemini_path() -> None:
    reset_operations()
    deterministic_run = run_agent(QUESTION, MockLLM())
    equivalent_gemini_run = deterministic_run.model_copy(update={"mode": "gemini"})
    assert all(live_checks(equivalent_gemini_run).values())

    incomplete_run = equivalent_gemini_run.model_copy(
        update={"trace": equivalent_gemini_run.trace[:-1]}
    )
    assert live_checks(incomplete_run)["five_tool_path"] is False
