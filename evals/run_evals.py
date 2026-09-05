from __future__ import annotations

import json
from pathlib import Path

from src.agent import LLMClient, MockLLM, run_agent
from src.observability import run_summary
from src.tools import reset_operations
from .adversarial import AdversarialClient, workshop_cases


CASES_PATH = Path(__file__).with_name("test_cases.json")


def evaluate(client: LLMClient | None = None, runner=run_agent, base_only=False) -> list[dict]:
    selected_client = client or MockLLM()
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    if not base_only:
        cases = workshop_cases(cases)
    rows = []
    for case in cases:
        reset_operations()
        case_client = AdversarialClient(case["fault"]) if "fault" in case else selected_client
        run = runner(case["prompt"], case_client)
        actual_tools = [entry.tool for entry in run.trace]
        summary = run_summary(run)
        observable = all(
            entry.step == index and entry.call_id != "unknown"
            for index, entry in enumerate(run.trace, start=1)
        )
        checks = {
            "tool_sequence": actual_tools == case["expected_tools"],
            "outcome": run.outcome == case["expected_outcome"],
            "safety": run.safety_status == case["expected_safety_status"],
            "human_review": summary["human_reviewed"] is case["expected_human_review"],
            "observable": observable,
            "answer": case["expected_substring"].casefold() in run.answer.casefold(),
        }
        rows.append(
            {
                "id": case["id"],
                "passed": all(checks.values()),
                "checks": checks,
                "actual_tools": actual_tools,
                "outcome": run.outcome,
                "safety_status": run.safety_status,
                "answer": run.answer,
            }
        )
    return rows


def main() -> int:
    rows = evaluate()
    for row in rows:
        marker = "PASS" if row["passed"] else "FAIL"
        path = " → ".join(row["actual_tools"])
        print(
            f"{marker:4}  {row['id']:<36} "
            f"{row['safety_status']:<15} {path}"
        )
    passed = sum(row["passed"] for row in rows)
    print(f"\n{passed} / {len(rows)} incident scenarios passed")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
