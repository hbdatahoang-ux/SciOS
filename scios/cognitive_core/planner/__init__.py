# scios/cognitive_core/planner/__init__.py

"""
SciOS Cognitive Core Planner
============================

Public API for the SciOS planning subsystem.

The :class:`Planner` class is the primary high-level entry point.
Supporting components are exported here to provide a stable public
API without requiring callers to depend on internal module paths.

Public components
-----------------
- Planner
- Goal / Plan / Task model components
- TaskGraph
- PlanningStrategy / PlanningPolicy
- Constraint / ConstraintSet
- PlanOptimizer / PlanValidator
- PlanExecutor / Scheduler
- ProgressMonitor / FailureRecovery
- PlannerState / PlanningStage
- PlanSerializer

Python 3.11+
"""

from __future__ import annotations

# ==========================================================
# Primary Planner API
# ==========================================================

from .planner import Planner


# ==========================================================
# Planning model
# ==========================================================

from .task import Task
from .task_graph import TaskGraph
from .plan import Plan


# ==========================================================
# Planning policy / strategy
# ==========================================================

from .strategy import PlanningStrategy
from .policy import PlanningPolicy


# ==========================================================
# Constraints
# ==========================================================

from .constraint import Constraint, ConstraintSet


# ==========================================================
# Planning optimization / validation
# ==========================================================

from .optimizer import PlanOptimizer
from .validator import PlanValidator


# ==========================================================
# Execution
# ==========================================================

from .executor import PlanExecutor
from .scheduler import Scheduler


# ==========================================================
# Monitoring / recovery / state
# ==========================================================

from .monitor import ProgressMonitor
from .recovery import FailureRecovery
from .state import PlannerState


# ==========================================================
# Lifecycle / serialization
# ==========================================================

from .stage import PlanningStage
from .serializer import PlanSerializer


# ==========================================================
# Public API
# ==========================================================

__all__ = [
    # Primary entry point
    "Planner",

    # Planning model
    "Task",
    "TaskGraph",
    "Plan",

    # Strategy / policy
    "PlanningStrategy",
    "PlanningPolicy",

    # Constraints
    "Constraint",
    "ConstraintSet",

    # Optimization / validation
    "PlanOptimizer",
    "PlanValidator",

    # Execution
    "PlanExecutor",
    "Scheduler",

    # Monitoring / recovery / state
    "ProgressMonitor",
    "FailureRecovery",
    "PlannerState",

    # Lifecycle / serialization
    "PlanningStage",
    "PlanSerializer",
]