# ==============================================================================
# SciOS Runtime Science
# Scientific Execution Result
# ==============================================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping
from uuid import uuid4

from .errors import InvalidExecutionResultError


# ==============================================================================
# Execution Status
# ==============================================================================


class ExecutionStatus(str, Enum):
    """
    Lifecycle status of a scientific execution.

    The lifecycle is:

        PENDING
            ↓
        RUNNING
            ↓
        COMPLETED

    or:

        PENDING
            ↓
        RUNNING
            ↓
        FAILED
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ==============================================================================
# Execution Result
# ==============================================================================


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    """
    Immutable result produced by one scientific execution.

    ExecutionResult records what happened during execution.

    It does not:

    - execute an experiment,
    - evaluate a hypothesis,
    - mutate world state,
    - create scientific knowledge.

    Semantic boundary:

        ExecutionContext
            ↓
        ScientificExecutor
            ↓
        ExecutionResult
            ↓
        Observation
            ↓
        Evaluator
    """

    execution_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    experiment_id: str = ""

    hypothesis_id: str = ""

    status: ExecutionStatus = ExecutionStatus.COMPLETED

    observation: Any = None

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        # ------------------------------------------------------------------
        # Execution ID
        # ------------------------------------------------------------------

        if (
            not isinstance(self.execution_id, str)
            or not self.execution_id.strip()
        ):
            raise InvalidExecutionResultError(
                "execution_id must be a non-empty string"
            )

        # ------------------------------------------------------------------
        # Experiment ID
        # ------------------------------------------------------------------

        if (
            not isinstance(self.experiment_id, str)
            or not self.experiment_id.strip()
        ):
            raise InvalidExecutionResultError(
                "experiment_id must be a non-empty string"
            )

        # ------------------------------------------------------------------
        # Hypothesis ID
        # ------------------------------------------------------------------

        if (
            not isinstance(self.hypothesis_id, str)
            or not self.hypothesis_id.strip()
        ):
            raise InvalidExecutionResultError(
                "hypothesis_id must be a non-empty string"
            )

        # ------------------------------------------------------------------
        # Status
        # ------------------------------------------------------------------

        if not isinstance(self.status, ExecutionStatus):
            raise InvalidExecutionResultError(
                "status must be an ExecutionStatus"
            )

        # ------------------------------------------------------------------
        # Timestamp
        # ------------------------------------------------------------------

        if not isinstance(self.created_at, datetime):
            raise InvalidExecutionResultError(
                "created_at must be a datetime"
            )

        if (
            self.created_at.tzinfo is None
            or self.created_at.utcoffset() is None
        ):
            raise InvalidExecutionResultError(
                "created_at must be timezone-aware"
            )

        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------

        if not isinstance(self.metadata, Mapping):
            raise InvalidExecutionResultError(
                "metadata must be a mapping"
            )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    # ==========================================================================
    # Status API
    # ==========================================================================

    @property
    def is_pending(self) -> bool:
        """Return True when execution has not started."""
        return self.status is ExecutionStatus.PENDING

    @property
    def is_running(self) -> bool:
        """Return True while execution is running."""
        return self.status is ExecutionStatus.RUNNING

    @property
    def is_completed(self) -> bool:
        """Return True when execution completed successfully."""
        return self.status is ExecutionStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Return True when execution failed."""
        return self.status is ExecutionStatus.FAILED

    # ==========================================================================
    # Result API
    # ==========================================================================

    @property
    def success(self) -> bool:
        """
        Return True when execution completed successfully.
        """
        return self.status is ExecutionStatus.COMPLETED

    @property
    def failed(self) -> bool:
        """
        Return True when execution failed.
        """
        return self.status is ExecutionStatus.FAILED

    # ==========================================================================
    # Observation API
    # ==========================================================================

    @property
    def has_observation(self) -> bool:
        """
        Return True if an observation is attached to the result.
        """
        return self.observation is not None

    # ==========================================================================
    # Metadata API
    # ==========================================================================

    @property
    def metadata_count(self) -> int:
        """Return the number of metadata entries."""
        return len(self.metadata)

    def has_metadata(self, name: str) -> bool:
        """
        Return True if metadata contains the given name.
        """

        if not isinstance(name, str):
            return False

        return name in self.metadata

    def get_metadata(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        """
        Return metadata by name.

        Missing metadata returns default.
        """

        return self.metadata.get(name, default)

    # ==========================================================================
    # Functional Update API
    # ==========================================================================

    def with_metadata(
        self,
        name: str,
        value: Any,
    ) -> ExecutionResult:
        """
        Return a new result with metadata added or replaced.

        The current result is never mutated.
        """

        if (
            not isinstance(name, str)
            or not name.strip()
        ):
            raise InvalidExecutionResultError(
                "metadata name must be a non-empty string"
            )

        metadata = dict(self.metadata)
        metadata[name] = value

        return ExecutionResult(
            execution_id=self.execution_id,
            experiment_id=self.experiment_id,
            hypothesis_id=self.hypothesis_id,
            status=self.status,
            observation=self.observation,
            created_at=self.created_at,
            metadata=metadata,
        )