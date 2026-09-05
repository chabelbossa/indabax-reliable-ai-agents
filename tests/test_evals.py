from evals.run_evals import evaluate


def test_offline_evaluation_suite_passes() -> None:
    rows = evaluate()
    assert len(rows) == 10
    assert all(row["passed"] for row in rows), rows
