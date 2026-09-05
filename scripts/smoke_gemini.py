#!/usr/bin/env python3
"""Run the complete KoraCare path against Gemini without storing the API key."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agent import make_client, run_agent  # noqa: E402
from src.observability import format_trace, run_summary  # noqa: E402
from src.tools import reset_operations  # noqa: E402
from scripts.notebook_runtime import load_runtime  # noqa: E402
from src.safety import inspect_evidence  # noqa: E402


QUESTION = (
    "Alerte KCARE-ADJ-01 : prends en charge l'excursion de température, "
    "applique la procédure et escalade si nécessaire."
)
EXPECTED_TOOLS = [
    "get_clinic_status",
    "search_cold_chain_sop",
    "assess_excursion_risk",
    "create_incident",
    "request_human_review",
]


def live_checks(run) -> dict[str, bool]:
    """Return the exact behavioral contract required before the workshop."""
    return {
        "gemini_mode": run.mode == "gemini",
        "five_tool_path": [entry.tool for entry in run.trace] == EXPECTED_TOOLS,
        "no_tool_errors": all(entry.status == "success" for entry in run.trace),
        "human_approved": run.safety_status == "human_approved",
        "incident_escalated": run.outcome == "escalated",
        "approval_evidence_matches": inspect_evidence(run.trace, QUESTION)["human_approved"],
    }


def main() -> int:
    if not os.getenv("GEMINI_API_KEY"):
        print(
            "GEMINI_API_KEY is not configured. Set a fresh key in the environment; "
            "the smoke test will not fall back to mock mode.",
            file=sys.stderr,
        )
        return 2

    client = make_client("gemini")
    print(f"Gemini live smoke | model={client.model} | key=hidden")
    reset_operations()
    runtime = load_runtime()
    run = runtime["run_workshop_mission"](QUESTION, client)
    print(format_trace(run))
    print(json.dumps(run_summary(run), indent=2, ensure_ascii=False))

    checks = live_checks(run)
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'}  {name}")
    if all(checks.values()):
        print("LIVE GEMINI SMOKE PASSED")
        return 0

    print("LIVE GEMINI SMOKE FAILED: keep the explicit mock fallback ready.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
