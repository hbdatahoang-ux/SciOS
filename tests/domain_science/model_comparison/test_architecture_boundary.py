from __future__ import annotations

import ast
from pathlib import Path


FORBIDDEN_ROOTS = (
    "scios.runtime",
    "scios.agents",
    "scios.cognitive_core",
)


def _production_files() -> list[Path]:
    root = Path(__file__).parents[3] / "scios" / "domain_science"
    return list(root.rglob("*.py")) if root.exists() else []


def _imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    modules: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)

        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)

    return modules


def test_domain_science_has_no_forbidden_imports():
    violations: list[str] = []

    for path in _production_files():
        for module in _imported_modules(path):
            if any(
                module == root or module.startswith(root + ".")
                for root in FORBIDDEN_ROOTS
            ):
                violations.append(f"{path}: {module}")

    assert violations == [], "\n".join(
        ["Forbidden domain_science imports:", *violations]
    )
