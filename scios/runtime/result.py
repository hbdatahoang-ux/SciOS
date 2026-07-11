"""
SciOS Execution Result
======================

Canonical execution result for the SciOS Runtime.

Responsibilities
----------------
- Represent the outcome of one execution.
- Capture success or failure.
- Store execution output and diagnostics.
- Provide serialization helpers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

__all__ = [
    "ExecutionResult",
]


# ==========================================================
# Execution Result
# ==========================================================


@dataclass(slots=True)
class ExecutionResult:
    """
    Immutable representation of one execution result.
    """

    # ------------------------------------------------------
    # Status
    # ------------------------------------------------------

    success: bool = True

    # ------------------------------------------------------
    # Payload
    # ------------------------------------------------------

    value: Any = None

    # ------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------

    error: Exception | None = None

    message: str | None = None

    # ------------------------------------------------------
    # Metrics
    # ------------------------------------------------------

    duration: float = 0.0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # ------------------------------------------------------
    # Timestamp
    # ------------------------------------------------------

    timestamp: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    # ======================================================
    # Constructors
    # ======================================================

    @classmethod
    def ok(
        cls,
        value: Any = None,
        *,
        message: str | None = None,
        duration: float = 0.0,
        **metadata: Any,
    ) -> "ExecutionResult":
        """
        Create a successful execution result.
        """

        return cls(
            success=True,
            value=value,
            message=message,
            duration=duration,
            metadata=metadata,
        )

    @classmethod
    def fail(
        cls,
        error: Exception,
        *,
        message: str | None = None,
        duration: float = 0.0,
        **metadata: Any,
    ) -> "ExecutionResult":
        """
        Create a failed execution result.
        """

        return cls(
            success=False,
            error=error,
            message=message or str(error),
            duration=duration,
            metadata=metadata,
        )

    # ======================================================
    # Convenience Properties
    # ======================================================

    @property
    def failed(self) -> bool:
        """
        Whether execution failed.
        """

        return not self.success

    @property
    def has_value(self) -> bool:
        """
        Whether a value is available.
        """

        return self.value is not None

    # ======================================================
    # Metadata
    # ======================================================

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store metadata.
        """

        self.metadata[key] = value

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve metadata.
        """

        return self.metadata.get(
            key,
            default,
        )

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize to dictionary.
        """

        return {

            "success": self.success,

            "value": self.value,

            "message": self.message,

            "error": (
                str(self.error)
                if self.error
                else None
            ),

            "duration": self.duration,

            "metadata": dict(self.metadata),

            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "ExecutionResult":
        """
        Restore from serialized dictionary.
        """

        return cls(
            success=data.get(
                "success",
                True,
            ),
            value=data.get(
                "value",
            ),
            message=data.get(
                "message",
            ),
            duration=data.get(
                "duration",
                0.0,
            ),
            metadata=dict(
                data.get(
                    "metadata",
                    {},
                )
            ),
            timestamp=data.get(
                "timestamp",
                datetime.now(
                    timezone.utc
                ).isoformat(),
            ),
        )

    # ======================================================
    # Representation
    # ======================================================

    def __bool__(self) -> bool:
        """
        Truth value equals execution success.
        """

        return self.success

    def __repr__(self) -> str:

        status = "SUCCESS" if self.success else "FAILED"

        return (
            f"{self.__class__.__name__}("
            f"status={status}, "
            f"value={self.value!r})"
        )