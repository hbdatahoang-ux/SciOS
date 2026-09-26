# ==============================================================================
# SciOS Runtime Science
# Scientific Execution Context
# ==============================================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping
from uuid import uuid4

from .errors import InvalidExecutionError


def _utc_now() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class ExecutionContext:
    """
    Immutable context for one scientific execution.

    ExecutionContext binds an Experiment to the WorldState in which
    that experiment is executed.

    Semantic boundary:

        Experiment
            ↓
        ExecutionContext
            ↓
        ScientificExecutor
            ↓
        WorldState
            ↓
        Observation

    The context does not execute experiments, mutate world state,
    or evaluate hypotheses.
    """

    experiment: Any
    state: Any

    execution_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    created_at: datetime = field(
        default_factory=_utc_now
    )

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        # ------------------------------------------------------------------
        # Experiment
        # ------------------------------------------------------------------

        if self.experiment is None:
            raise InvalidExecutionError(
                "experiment must not be None"
            )

        # ------------------------------------------------------------------
        # World state
        # ------------------------------------------------------------------

        if self.state is None:
            raise InvalidExecutionError(
                "state must not be None"
            )

        # ------------------------------------------------------------------
        # Execution ID
        # ------------------------------------------------------------------

        if (
            not isinstance(self.execution_id, str)
            or not self.execution_id.strip()
        ):
            raise InvalidExecutionError(
                "execution_id must be a non-empty string"
            )

        # ------------------------------------------------------------------
        # Timestamp
        # ------------------------------------------------------------------

        if not isinstance(self.created_at, datetime):
            raise InvalidExecutionError(
                "created_at must be a datetime"
            )

        if (
            self.created_at.tzinfo is None
            or self.created_at.utcoffset() is None
        ):
            raise InvalidExecutionError(
                "created_at must be timezone-aware"
            )

        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------

        if not isinstance(self.metadata, Mapping):
            raise InvalidExecutionError(
                "metadata must be a mapping"
            )

        # ------------------------------------------------------------------
        # Immutable storage
        # ------------------------------------------------------------------

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    # ==========================================================================
    # Identity API
    # ==========================================================================

    @property
    def experiment_id(self) -> str:
        """
        Return the experiment identifier.

        The Experiment remains the source of truth for experiment identity.
        """

        experiment_id = getattr(self.experiment, "id", None)

        if (
            not isinstance(experiment_id, str)
            or not experiment_id.strip()
        ):
            raise InvalidExecutionError(
                "experiment must expose a non-empty string 'id'"
            )

        return experiment_id

    @property
    def hypothesis_id(self) -> str:
        """
        Return the hypothesis identifier.

        The Hypothesis identity remains owned by the Experiment.
        """

        hypothesis_id = getattr(
            self.experiment,
            "hypothesis_id",
            None,
        )

        if (
            not isinstance(hypothesis_id, str)
            or not hypothesis_id.strip()
        ):
            raise InvalidExecutionError(
                "experiment must expose a non-empty string 'hypothesis_id'"
            )

        return hypothesis_id

    # ==========================================================================
    # Query API
    # ==========================================================================

    @property
    def metadata_count(self) -> int:
        """Return the number of metadata entries."""
        return len(self.metadata)

    def has_metadata(self, name: str) -> bool:
        """Return True when metadata contains ``name``."""

        if not isinstance(name, str):
            return False

        return name in self.metadata

    def get_metadata(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        """Return metadata by name."""
        return self.metadata.get(name, default)

    # ==========================================================================
    # Functional Update API
    # ==========================================================================

    def with_metadata(
        self,
        name: str,
        value: Any,
    ) -> ExecutionContext:
        """
        Return a new context with metadata added or replaced.

        The current context is never mutated.
        """

        if not isinstance(name, str) or not name.strip():
            raise InvalidExecutionError(
                "metadata name must be a non-empty string"
            )

        metadata = dict(self.metadata)
        metadata[name] = value

        return ExecutionContext(
            experiment=self.experiment,
            state=self.state,
            execution_id=self.execution_id,
            created_at=self.created_at,
            metadata=metadata,
        )