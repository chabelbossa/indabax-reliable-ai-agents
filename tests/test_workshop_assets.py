import json
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _notebook(name: str) -> dict:
    return json.loads((ROOT / "notebooks" / name).read_text())


def _code_text(notebook: dict) -> str:
    return "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    )


def _output_text(notebook: dict) -> str:
    chunks = []
    for cell in notebook["cells"]:
        for output in cell.get("outputs", []):
            if output.get("output_type") == "stream":
                chunks.extend(output.get("text", []))
            for value in output.get("data", {}).values():
                chunks.extend(value if isinstance(value, list) else [value])
    return "\n".join(value for value in chunks if isinstance(value, str))


def test_participant_notebooks_preserve_ten_decision_todos() -> None:
    for language in ("fr", "en"):
        participant = _notebook(f"workshop-{language}.ipynb")
        solution = _notebook(f"workshop-solution-{language}.ipynb")

        todo_ids = [
            int(value)
            for value in re.findall(r"# TODO (\d+):", _code_text(participant))
        ]
        assert todo_ids == list(range(1, 11))
        assert not re.findall(r"# TODO (\d+):", _code_text(solution))
        assert len(participant["cells"]) == len(solution["cells"]) == 28
        assert [cell["cell_type"] for cell in participant["cells"]] == [
            cell["cell_type"] for cell in solution["cells"]
        ]
        assert "Evidence bundle unlocked" not in _output_text(participant)
        assert ("Dossier de preuves disponible" if language == "fr" else "Evidence bundle unlocked") in _output_text(solution)
        assert "data:application/json;base64," in _output_text(solution)


def test_french_first_bilingual_delivery_contract() -> None:
    readme = (ROOT / "README.md").read_text()
    french = _notebook("workshop-fr.ipynb")
    english = _notebook("workshop-en.ipynb")

    assert "Le français est le parcours\nprincipal" in readme
    assert readme.index("notebook participant en français") < readme.index(
        "English participant notebook"
    )
    assert len(french["cells"]) == len(english["cells"]) == 28
    assert [cell["cell_type"] for cell in french["cells"]] == [
        cell["cell_type"] for cell in english["cells"]
    ]
    french_text = "\n".join(
        "".join(cell.get("source", [])) for cell in french["cells"]
    )
    english_text = "\n".join(
        "".join(cell.get("source", [])) for cell in english["cells"]
    )
    assert all(
        term in french_text
        for term in ("Rôle Modèle", "Rôle Orchestrateur", "Échangez les rôles")
    )
    assert all(
        term in english_text
        for term in ("Model role", "Orchestrator role", "Swap roles")
    )


def test_facilitator_runbook_keeps_the_participatory_safety_path() -> None:
    runbook = (ROOT / "FACILITATOR_RUNBOOK_FR.md").read_text()
    required_moments = (
        "vote à main levée",
        "Défendez votre choix",
        "Former des binômes",
        "Échanger les rôles",
        "contre-exemple",
        "checkpoint 4",
        "46–50 min",
    )

    assert all(moment in runbook for moment in required_moments)
    assert 'MODE = "mock"' in runbook
    assert "Ne jamais présenter les sorties mock" in runbook


def test_bilingual_decks_keep_twenty_notes_without_duplicate_parts() -> None:
    for language in ("fr", "en"):
        path = ROOT / "slides" / f"indabax-reliable-ai-agents-{language}.pptx"
        with zipfile.ZipFile(path) as archive:
            assert len(archive.namelist()) == len(set(archive.namelist()))
            notes = [
                name
                for name in archive.namelist()
                if name.startswith("ppt/notesSlides/notesSlide")
                and name.endswith(".xml")
            ]
        assert len(notes) == 20


def test_saved_notebook_solutions_pass_the_adverse_cases():
    from scripts.notebook_runtime import load_runtime
    for language in ("fr", "en"):
        runtime = load_runtime(ROOT / "notebooks" / f"workshop-solution-{language}.ipynb")
        rows = runtime["evaluate_workshop_agent"]()
        assert len(rows) == 10
        assert all(runtime["case_passes"](row) for row in rows)
