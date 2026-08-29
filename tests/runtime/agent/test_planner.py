"""
SciOS Runtime Agent Planner Tests
=================================

Contract tests for Planner.

Planner currently implements a minimal deterministic planning model:

    goal -> [goal]

The test suite locks the public API without imposing
future planning strategies.
"""

from __future__ import annotations

from scios.runtime.agent.planner import Planner


# ==========================================================
# Construction
# ==========================================================

def test_planner_creation() -> None:

    planner = Planner()

    assert isinstance(
        planner,
        Planner,
    )


# ==========================================================
# plan()
# ==========================================================

def test_planner_plan() -> None:

    planner = Planner()

    plan = planner.plan(
        "build tool"
    )

    assert plan == [
        "build tool",
    ]


def test_planner_plan_preserves_goal() -> None:

    planner = Planner()

    goal = "analyze battery"

    plan = planner.plan(
        goal
    )

    assert len(plan) == 1
    assert plan[0] == goal


# ==========================================================
# create_plan()
# ==========================================================

def test_planner_create_plan() -> None:

    planner = Planner()

    plan = planner.create_plan(
        "build tool"
    )

    assert plan == [
        "build tool",
    ]


def test_create_plan_matches_plan() -> None:

    planner = Planner()

    goal = "scientific analysis"

    assert (
        planner.create_plan(goal)
        == planner.plan(goal)
    )


# ==========================================================
# Reset
# ==========================================================

def test_planner_reset() -> None:

    planner = Planner()

    assert planner.reset() is None


# ==========================================================
# Representation
# ==========================================================

def test_planner_repr() -> None:

    planner = Planner()

    assert repr(planner) == "Planner()"