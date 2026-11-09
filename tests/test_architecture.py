"""Enforces the allowed-to-use specification in docs/uml/01_architecture_*.puml."""
import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
ALLOWED = {
    "config": set(),
    "data": {"config"},
    "validation": {"config"},
    "labels": {"config"},
    "router": {"config"},
    "parameter_ranges": {"config"},
    "confidence": {"config"},
    "air_quality": {"config"},
    "decider": {"config"},
    "model": {"config"},
    "features": {"config", "router"},
    "weather_policy": {"config", "confidence"},
    "llm_manager": {"config", "confidence"},
    "research_advisor": {"config", "confidence", "router"},
    "retraining": {"config", "data", "labels", "features", "model"},
    "cycle": {"config", "parameter_ranges", "router", "features", "model", "confidence",
              "weather_policy", "air_quality", "llm_manager", "decider", "research_advisor"},
}


def core_imports(path):
    found = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module == "core":
                found |= {alias.name for alias in node.names}
            elif node.module.startswith("core."):
                found.add(node.module.split(".")[1])
        elif isinstance(node, ast.Import):
            found |= {a.name.split(".")[1] for a in node.names if a.name.startswith("core.")}
    return found


@pytest.mark.parametrize("module", sorted(ALLOWED))
def test_module_exists_and_imports_only_allowed(module):
    assert core_imports(ROOT / "core" / f"{module}.py") <= ALLOWED[module]


def test_no_undeclared_core_modules():
    actual = {p.stem for p in (ROOT / "core").glob("*.py") if p.stem != "__init__"}
    assert actual == set(ALLOWED)


def test_gui_uses_only_cycle_and_ranges():
    assert core_imports(ROOT / "app.py") <= {"cycle", "parameter_ranges", "air_quality", "config"}


def test_only_llm_manager_reaches_ollama():
    for path in (ROOT / "core").glob("*.py"):
        if path.stem not in {"llm_manager", "config"}:
            assert "OLLAMA" not in path.read_text() and "/api/chat" not in path.read_text(), path.name


def test_no_cloud_llm_backend():
    for path in list((ROOT / "core").glob("*.py")) + [ROOT / "app.py"]:
        text = path.read_text().lower()
        assert "anthropic" not in text and "openai" not in text, path.name
