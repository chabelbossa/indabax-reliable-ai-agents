"""Check the actual learner edits, without a provider or prefilled solution runtime."""
import ast

from scripts.build_notebooks import common_cells, exercise_cells
from scripts.notebook_runtime import load_runtime
from src.agent import MockLLM, SYSTEM_PROMPT
from src.tools import reset_operations


def test_four_edits_build_a_working_agent_and_observation_changes_next_call():
    for language in ("fr", "en"):
        cells = common_cells(language) + exercise_cells(False, language)
        namespace = load_runtime(cells=cells)
        replacements = {
            1: ("turn = None", "turn = selected_client.complete(messages, TOOL_SCHEMAS)"),
            2: ("    pass", "    messages.extend([assistant_message, tool_message])"),
            3: ("if False:", "if human_required and not human_approved:"),
            4: ("return False", "return all(row['checks'].values())"),
        }
        for cell in cells:
            if cell.cell_type != "code":
                continue
            for number, (old, new) in replacements.items():
                if f"# TODO {number}:" in cell.source:
                    assert old in cell.source
                    exec(compile(ast.parse(cell.source.replace(old, new)), "<learner-edit>", "exec"), namespace)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Investigue KCARE-ADJ-01."},
        ]
        client = MockLLM()
        turn, call = namespace["propose_tool"](messages, client)
        assert call.name == "get_clinic_status"
        result, entry = namespace["execute_and_trace"](call, 1)
        assert result.data["temperature_c"] == 12.4
        namespace["append_observation"](messages, turn, call, result)
        assert [m["role"] for m in messages] == ["system", "user", "assistant", "tool"]
        _, next_call = namespace["propose_tool"](messages, client)
        assert next_call.name == "search_cold_chain_sop"
        reset_operations()
        run = namespace["run_workshop_mission"]("Investigue KCARE-ADJ-01.", client)
        assert run.safety_status == "human_approved"
        assert len(run.trace) == 5
        rows = namespace["evaluate_workshop_agent"]()
        assert len(rows) == 10
        assert all(namespace["case_passes"](row) for row in rows)


def test_unfinished_observation_repeats_first_call_and_gate_demo_restores_function(capsys):
    namespace = load_runtime(cells=common_cells("fr") + exercise_cells(True, "fr"))
    messages = [{"role": "user", "content": "Investigue KCARE-ADJ-01."}]
    assert MockLLM().complete(messages, []).tool_calls[0].name == "get_clinic_status"
    original = namespace["finish_with_safety"]
    namespace["compare_approval_gate"]()
    assert namespace["finish_with_safety"] is original
    output = capsys.readouterr().out
    assert "completed safe" in output
    assert "stopped review_required" in output
