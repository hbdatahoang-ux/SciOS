"""
SciOS Runtime Execution Result
==============================

Canonical execution result model for SciOS Runtime.

Responsibilities
-----------------
- Represent execution outcome.
- Capture success/failure state.
- Store returned values.
- Store errors and diagnostics.
- Provide stable factory APIs.
- Support serialization.
- Provide runtime compatibility API.

Python 3.11+
"""

from __future__ import annotations


from copy import deepcopy

from dataclasses import (
    dataclass,
    field,
)

from datetime import (
    datetime,
    timezone,
)

from typing import (
    Any,
)



__all__ = [
    "ExecutionResult",
]



# ==========================================================
# Helpers
# ==========================================================


def utc_now() -> str:
    """
    Return UTC ISO timestamp.
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
    Canonical SciOS runtime result.

    Compatible with:

    Executor:
        ExecutionResult(
            success=True,
            value=x,
            error=None,
            duration=t,
            metadata={}
        )

    Factory:

        ExecutionResult.ok(
            value
        )

        ExecutionResult.fail(
            error
        )
    """



    # ======================================================
    # Public compatibility status
    # ======================================================

    success: bool = True



    # ======================================================
    # Payload
    # ======================================================

    value: Any = None



    # ======================================================
    # Diagnostics
    # ======================================================

    error: Exception | None = None


    message: str | None = None



    # ======================================================
    # Runtime metrics
    # ======================================================

    duration: float = 0.0



    metadata: dict[str, Any] = field(
        default_factory=dict
    )



    # ======================================================
    # Timestamp
    # ======================================================

    timestamp: str = field(
        default_factory=utc_now
    )



    # ======================================================
    # Compatibility internal alias
    # ======================================================

    _status: bool = field(
        init=False,
        repr=False,
    )



    # ======================================================
    # Init
    # ======================================================

    def __post_init__(self):

        self.metadata = dict(
            self.metadata
        )


        self._status = bool(
            self.success
        )


        if (
            self.message is None
            and self.error is not None
        ):

            self.message = str(
                self.error
            )



    # ======================================================
    # State API
    # ======================================================

    @property
    def succeeded(
        self,
    ) -> bool:

        return self.success



    @property
    def failed(
        self,
    ) -> bool:

        return not self.success



    @property
    def is_success(
        self,
    ) -> bool:

        return self.success



    @property
    def has_value(
        self,
    ) -> bool:

        return self.value is not None



    @property
    def status(
        self,
    ) -> str:

        return (
            "SUCCESS"
            if self.success
            else
            "FAILED"
        )



    @property
    def result(
        self,
    ):
        """
        Compatibility alias.

        Some runtime code uses result.value
        and some uses result.result.
        """

        return self.value



    # ======================================================
    # Factory Methods
    # ======================================================

    @classmethod
    def success(
        cls,
        *,
        result=None,
        message=None,
        duration=0.0,
        **metadata,
    ):

        return cls(
            success=True,
            value=result,
            message=message,
            duration=duration,
            metadata=metadata,
        )



    @classmethod
    def ok(
        cls,
        value=None,
        *,
        message=None,
        duration=0.0,
        **metadata,
    ):

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
        message=None,
        duration=0.0,
        **metadata,
    ):

        return cls(
            success=False,
            error=error,
            message=(
                message
                or str(error)
            ),
            duration=duration,
            metadata=metadata,
        )



    # ======================================================
    # Convenience
    # ======================================================

    @classmethod
    def from_value(
        cls,
        value,
    ):

        return cls.ok(
            value
        )



    @classmethod
    def from_error(
        cls,
        error,
    ):

        return cls.fail(
            error
        )



    # ======================================================
    # Metadata
    # ======================================================

    def set(
        self,
        key: str,
        value: Any,
    ):

        self.metadata[key] = value



    def get(
        self,
        key: str,
        default=None,
    ):

        return self.metadata.get(
            key,
            default,
        )



    # ======================================================
    # Copy
    # ======================================================

    def copy(
        self,
    ):

        return deepcopy(
            self
        )



    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(
        self,
    ):

        return {

            "status":
                self.status,

            "success":
                self.success,

            "value":
                self.value,

            "message":
                self.message,

            "error":
                (
                    str(self.error)
                    if self.error
                    else None
                ),

            "duration":
                self.duration,

            "metadata":
                deepcopy(
                    self.metadata
                ),

            "timestamp":
                self.timestamp,

        }



    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ):

        error = data.get(
            "error"
        )


        return cls(

            success=data.get(
                "success",
                data.get(
                    "status"
                )
                == "SUCCESS",
            ),

            value=data.get(
                "value"
            ),

            error=(
                RuntimeError(error)
                if error
                else None
            ),

            message=data.get(
                "message"
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

    def __bool__(
        self,
    ):

        return self.success



    def __repr__(
        self,
    ):

        if self.success:

            return (
                "ExecutionResult("
                "status='SUCCESS', "
                f"value={self.value!r}, "
                f"duration={self.duration:.6f}s)"
            )


        return (
            "ExecutionResult("
            "status='FAILED', "
            f"error={self.message!r}, "
            f"duration={self.duration:.6f}s)"
        )