"""Load the notebook's actual definitions without setup, prompts or API calls."""
import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_runtime(path=None, cells=None):
    if cells is None:
        path = Path(path or ROOT / "notebooks/workshop-solution-fr.ipynb")
        cells = json.loads(path.read_text(encoding="utf-8"))["cells"]
    namespace = {"__name__": "workshop_runtime"}
    for cell in cells:
        if cell["cell_type"] != "code":
            continue
        tree = ast.parse("".join(cell["source"]))
        definitions = [node for node in tree.body if isinstance(
            node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef)
        )]
        exec(compile(ast.Module(body=definitions, type_ignores=[]), "<notebook>", "exec"), namespace)
    return namespace
