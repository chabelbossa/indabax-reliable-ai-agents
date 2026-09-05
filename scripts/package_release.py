"""Build a secret-free source + teaching-material archive from this checkout."""
from pathlib import Path
import hashlib
import re
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def package(output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    paths = [ROOT / name for name in (
        "README.md", "FACILITATOR_RUNBOOK_FR.md", "SUBMISSION_PACKAGE.md", "VALIDATION.md",
        "requirements.txt", "requirements-build.txt", "LICENSE",
    )]
    for directory in ("src", "scripts", "tests", "data", "evals", "notebooks", "slides"):
        paths.extend(path for path in (ROOT / directory).rglob("*")
                     if path.is_file() and "__pycache__" not in path.parts
                     and path.suffix in {".py", ".json", ".ipynb", ".pptx", ".pdf", ".png"})
    for path in paths:
        if re.search(rb"AIza[0-9A-Za-z_-]{30,}", path.read_bytes()):
            raise RuntimeError(f"Credential-like value found: {path.name}")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(paths):
            archive.write(path, str(Path(ROOT.name) / path.relative_to(ROOT)))
        template = ROOT.parent / "IndabaX Bénin — Speaker Deck Template.pptx"
        archive.write(template, template.name)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
    print(output)
    print("SHA256", hashlib.sha256(Path(output).read_bytes()).hexdigest())


if __name__ == "__main__":
    package(ROOT.parent / "work/INDABAX_WORKSHOP_FINAL_FR_EN.zip")
