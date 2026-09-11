from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCIOS_ROOT = REPO_ROOT / "scios"


def _python_files(root: Path):
    return root.rglob("*.py")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _parse(path: Path) -> ast.Module:
    return ast.parse(_read(path), filename=str(path))


def _imports_symbol(path: Path, symbol: str) -> bool:
    tree = _parse(path)

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if any(alias.name == symbol for alias in node.names):
                return True

        if isinstance(node, ast.Import):
            if any(alias.name == symbol for alias in node.names):
                return True

    return False


def test_execution_public_surface_is_canonical():
    graph_init = _read(SCIOS_ROOT / "execution" / "graph" / "__init__.py")
    node_init = _read(SCIOS_ROOT / "execution" / "node" / "__init__.py")
    scheduler_init = _read(
        SCIOS_ROOT / "execution" / "scheduler" / "__init__.py"
    )

    assert "ExecutionGraph" in graph_init
    assert "ExecutionEdge" in graph_init

    assert "ExecutionNode" in node_init
    assert "NodeKind" in node_init
    assert "NodeStatus" in node_init

    assert "Scheduler" in scheduler_init
    assert "SchedulingPolicy" in scheduler_init
    assert "TaskQueue" in scheduler_init


def test_execution_has_no_legacy_subsystems():
    forbidden = (
        "executor",
        "optimizer",
        "context",
        "ir",
        "replay",
        "monitor",
    )

    execution_root = SCIOS_ROOT / "execution"

    for name in forbidden:
        assert not (execution_root / name).exists(), (
            f"Legacy execution subsystem reappeared: {name}"
        )


def test_execution_contains_no_runtime_imports():
    execution_root = SCIOS_ROOT / "execution"

    for path in _python_files(execution_root):
        text = _read(path)

        assert "scios.runtime" not in text
        assert "runtime.context" not in text
        assert "ExecutionContext" not in text


def test_execution_graph_has_only_canonical_consumers():
    candidate_paths = [
        SCIOS_ROOT / "compilation" / "plan_compiler.py",
        SCIOS_ROOT / "execution" / "graph" / "__init__.py",
        SCIOS_ROOT / "execution" / "scheduler" / "scheduler.py",
    ]

    consumers = []

    for path in candidate_paths:
        tree = _parse(path)

        imported = False
        constructed = False

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if any(
                    alias.name == "ExecutionGraph"
                    for alias in node.names
                ):
                    imported = True

            elif isinstance(node, ast.Call):
                if (
                    isinstance(node.func, ast.Name)
                    and node.func.id == "ExecutionGraph"
                ):
                    constructed = True

        if imported or constructed:
            consumers.append(
                path.relative_to(SCIOS_ROOT).as_posix()
            )

    assert sorted(consumers) == [
        "compilation/plan_compiler.py",
        "execution/graph/__init__.py",
        "execution/scheduler/scheduler.py",
    ]


def test_cognitive_plan_has_only_canonical_compilation_boundary():
    candidate_paths = [
        SCIOS_ROOT / "cognitive_core" / "planner" / "__init__.py",
        SCIOS_ROOT / "cognitive_core" / "planner" / "planner.py",
        SCIOS_ROOT / "cognitive_core" / "planner" / "serializer.py",
        SCIOS_ROOT / "cognitive_core" / "planner" / "strategy.py",
        SCIOS_ROOT / "cognitive_core" / "planner" / "validator.py",
        SCIOS_ROOT / "compilation" / "plan_compiler.py",
    ]

    consumers = []

    for path in candidate_paths:
        tree = _parse(path)

        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue

            if not any(alias.name == "Plan" for alias in node.names):
                continue

            if node.level > 0:
                if (
                    node.module == "plan"
                    and path.parent.name == "planner"
                ):
                    consumers.append(
                        path.relative_to(SCIOS_ROOT).as_posix()
                    )

            elif node.module == "scios.cognitive_core.planner.plan":
                consumers.append(
                    path.relative_to(SCIOS_ROOT).as_posix()
                )

    assert sorted(set(consumers)) == [
        "cognitive_core/planner/__init__.py",
        "cognitive_core/planner/planner.py",
        "cognitive_core/planner/serializer.py",
        "cognitive_core/planner/strategy.py",
        "cognitive_core/planner/validator.py",
        "compilation/plan_compiler.py",
    ]


def test_plan_compiler_has_no_runtime_boundary():
    path = SCIOS_ROOT / "compilation" / "plan_compiler.py"
    text = _read(path)

    forbidden = (
        "ExecutionContext",
        "scios.runtime",
        "runtime.context",
        "ToolRouter",
        "RuntimeScheduler",
        "RuntimeExecutor",
    )

    for symbol in forbidden:
        assert symbol not in text


def test_execution_scheduler_is_not_an_executor():
    path = SCIOS_ROOT / "execution" / "scheduler" / "scheduler.py"
    tree = _parse(path)

    class_names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    }

    assert class_names == {"Scheduler"}

    text = _read(path)

    forbidden = (
        "ToolRouter",
        "ToolExecutor",
        "Worker",
        "WorkerPool",
        "ExecutionContext",
        "dispatch(",
        "execute(",
        "submit(",
    )

    for symbol in forbidden:
        assert symbol not in text


def test_execution_node_has_no_runtime_execution_state():
    path = SCIOS_ROOT / "execution" / "node" / "node.py"
    tree = _parse(path)

    forbidden_fields = {
        "handler",
        "inputs",
        "result",
        "context",
    }

    dataclass_fields = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            dataclass_fields.add(node.target.id)

    assert not forbidden_fields.intersection(dataclass_fields)

    text = _read(path)

    forbidden_dependencies = (
        "ExecutionContext",
        "ToolRouter",
        "WorkerPool",
    )

    for symbol in forbidden_dependencies:
        assert symbol not in text
