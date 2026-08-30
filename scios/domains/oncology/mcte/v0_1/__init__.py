"""
MCTE v0.1
=========

Minimal Computational Tumor Ecosystem.

Frozen v0.1 computational model for:

- phenotype state
- environment and host state
- fitness
- evolutionary dynamics
- therapeutic control
- objective evaluation
- simulation

The v0.1 public API is intentionally explicit and stable.
"""

from __future__ import annotations

# =============================================================================
# State
# =============================================================================

from .state import (
    PHENOTYPES,
    STATE_DIMENSION,
    PhenotypeState,
)

# =============================================================================
# Environment
# =============================================================================

from .environment import (
    EnvironmentState,
    HostState,
)

# =============================================================================
# Fitness
# =============================================================================

from .fitness import (
    BaseFitnessModel,
    ToyLinearFitnessModel,
)

# =============================================================================
# Dynamics
# =============================================================================

from .dynamics import (
    compute_system_derivatives,
)

# =============================================================================
# Control
# =============================================================================

from .control import (
    BaseControlPolicy,
    ConstantControlPolicy,
    ControlPolicy,
    Intervention,
    MetronomicControlPolicy,
)

# =============================================================================
# Objective
# =============================================================================

from .objective import (
    EvaluationMetrics,
    compute_step_metrics,
)

# =============================================================================
# Simulation
# =============================================================================

from .simulation import (
    SimulationEngine,
    SimulationResult,
)

# =============================================================================
# Public API
# =============================================================================

__all__ = [
    # -------------------------------------------------------------------------
    # State
    # -------------------------------------------------------------------------
    "PhenotypeState",
    "PHENOTYPES",
    "STATE_DIMENSION",

    # -------------------------------------------------------------------------
    # Environment
    # -------------------------------------------------------------------------
    "EnvironmentState",
    "HostState",

    # -------------------------------------------------------------------------
    # Fitness
    # -------------------------------------------------------------------------
    "BaseFitnessModel",
    "ToyLinearFitnessModel",

    # -------------------------------------------------------------------------
    # Dynamics
    # -------------------------------------------------------------------------
    "compute_system_derivatives",

    # -------------------------------------------------------------------------
    # Control
    # -------------------------------------------------------------------------
    "Intervention",
    "ControlPolicy",
    "BaseControlPolicy",
    "ConstantControlPolicy",
    "MetronomicControlPolicy",

    # -------------------------------------------------------------------------
    # Objective
    # -------------------------------------------------------------------------
    "EvaluationMetrics",
    "compute_step_metrics",

    # -------------------------------------------------------------------------
    # Simulation
    # -------------------------------------------------------------------------
    "SimulationResult",
    "SimulationEngine",
]
