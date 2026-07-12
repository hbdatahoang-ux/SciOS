"""
SciOS Runtime Execution Result
==============================

Canonical execution result for the SciOS Runtime.

Responsibilities
----------------
- Represent the outcome of one execution.
- Capture success or failure.
- Store execution output and diagnostics.
- Provide metadata helpers.
- Support serialization.
- Be immutable in API semantics.
- Provide a stable Runtime v0.2 contract.

Python 3.11+
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


__all__ = [
    "ExecutionResult",
]


# ==========================================================
# Helpers
# ==========================================================


def utc_now() -> str:
    """
    Return current UTC ISO timestamp.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()


# ==========================================================
# Execution Result
# ==========================================================


@dataclass(slots=True)
class ExecutionResult:
    """
    Canonical runtime execution result.

    Construction
    ------------

    Success:

        ExecutionResult.ok(value)

    Failure:

        ExecutionResult.fail(error)

    Truth value:

        if result:
            ...

    Success state:

        result.success

    Failure state:

        result.failed
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
    # Runtime Metrics
    # ------------------------------------------------------

    duration: float = 0.0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # ------------------------------------------------------
    # Timestamp
    # ------------------------------------------------------

    timestamp: str = field(
        default_factory=utc_now
    )

    # ======================================================
    # Initialization
    # ======================================================

    def __post_init__(self) -> None:
        """
        Normalize runtime values.
        """

        self.metadata = dict(self.metadata)

        if self.message is None and self.error is not None:
            self.message = str(self.error)

    # ======================================================
    # Factory Methods
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
        Create a successful result.
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
        Create a failed result.
        """

        return cls(
            success=False,
            error=error,
            message=message or str(error),
            duration=duration,
            metadata=metadata,
        )

    # ------------------------------------------------------
    # Convenience Constructors
    # ------------------------------------------------------

    @classmethod
    def from_value(
        cls,
        value: Any,
    ) -> "ExecutionResult":
        """
        Alias for ok().
        """

        return cls.ok(value)

    @classmethod
    def from_error(
        cls,
        error: Exception,
    ) -> "ExecutionResult":
        """
        Alias for fail().
        """

        return cls.fail(error)

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
        Whether a value exists.
        """

        return self.value is not None

    @property
    def is_success(self) -> bool:
        """
        Explicit success alias.
        """

        return self.success

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
    # Copy
    # ======================================================

    def copy(self) -> "ExecutionResult":
        """
        Deep copy.
        """

        return deepcopy(self)

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize execution result.
        """

        return {

            "success": self.success,

            "value": self.value,

            "message": self.message,

            "error":
                str(self.error)
                if self.error
                else None,

            "duration": self.duration,

            "metadata":
                deepcopy(self.metadata),

            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "ExecutionResult":
        """
        Restore from serialized dictionary.

        Note:
            Original exception types cannot be faithfully
            reconstructed from serialized data. Therefore
            the error field is restored as RuntimeError.
        """

        error = data.get("error")

        return cls(

            success=data.get(
                "success",
                True,
            ),

            value=data.get(
                "value",
            ),

            error=(
                RuntimeError(error)
                if error
                else None
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
                utc_now(),
            ),
        )

    # ======================================================
    # Protocols
    # ======================================================

    def __bool__(self) -> bool:
        """
        Truth value equals execution success.
        """

        return self.success

    def __repr__(self) -> str:

        if self.success:

            return (
                f"{self.__class__.__name__}("
                f"status='SUCCESS', "
                f"value={self.value!r}, "
                f"duration={self.duration:.6f}s)"
            )

        return (
            f"{self.__class__.__name__}("
            f"status='FAILED', "
            f"error={self.message!r}, "
            f"duration={self.duration:.6f}s)"
        )