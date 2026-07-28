"""
SciOS Runtime Execution Result
==============================

Canonical execution result model for SciOS Runtime.

Responsibilities
-----------------
- Represent execution outcome.
- Store execution payload.
- Capture success/failure state.
- Store diagnostics.
- Support dictionary compatibility.
- Support serialization.
- Support runtime pipelines.

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
    Iterator,
)


__all__ = [
    "ExecutionResult",
]



# ==========================================================
# Helpers
# ==========================================================


def utc_now() -> str:
    """
    Current UTC timestamp.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()



# ==========================================================
# ExecutionResult
# ==========================================================


@dataclass(slots=True)
class ExecutionResult:
    """
    Canonical SciOS execution result.

    Example:

        result = ExecutionResult.ok(
            {
                "task": "battery",
                "status": "success"
            }
        )

        result.success
        result["task"]
        result.value
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
    # Runtime metrics
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

    def __post_init__(self):

        self.metadata = dict(
            self.metadata
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
    def status(
        self,
    ) -> str:

        return (
            "success"
            if self.success
            else
            "error"
        )



    @property
    def result(
        self,
    ):

        """
        Compatibility alias.
        """

        return self.value



    @property
    def has_value(
        self,
    ) -> bool:

        return self.value is not None



    # ======================================================
    # Factory API
    # ======================================================

    @classmethod
    def ok(
        cls,
        value=None,
        *,
        message=None,
        duration: float = 0.0,
        **metadata,
    ) -> "ExecutionResult":

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
        duration: float = 0.0,
        **metadata,
    ) -> "ExecutionResult":

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
    # Metadata API
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
    # Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            "status":
                self.status,


            "success":
                self.success,


            "value":
                self.value,


            "result":
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
                in {
                    "success",
                    "SUCCESS",
                },
            ),


            value=data.get(
                "value",
                data.get(
                    "result"
                ),
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
    # Mapping Compatibility
    # ======================================================

    def __getitem__(
        self,
        key: str,
    ):

        data = self.to_dict()


        if key in data:

            return data[key]



        if isinstance(
            self.value,
            dict,
        ):

            if key in self.value:

                return self.value[key]



        raise KeyError(
            key
        )



    def __contains__(
        self,
        key: str,
    ) -> bool:

        if key in self.to_dict():

            return True


        return (

            isinstance(
                self.value,
                dict,
            )

            and

            key in self.value

        )



    def keys(
        self,
    ):

        keys = set(
            self.to_dict().keys()
        )


        if isinstance(
            self.value,
            dict,
        ):

            keys.update(
                self.value.keys()
            )


        return keys



    def items(
        self,
    ):

        data = self.to_dict()


        if isinstance(
            self.value,
            dict,
        ):

            data.update(
                self.value
            )


        return data.items()



    def __iter__(
        self,
    ) -> Iterator:

        return iter(
            self.keys()
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
    # Protocol
    # ======================================================

    def __bool__(
        self,
    ):

        return self.success



    def __len__(
        self,
    ):

        if isinstance(
            self.value,
            dict,
        ):

            return len(
                self.value
            )

        return 0



    def __repr__(
        self,
    ):

        return (

            "ExecutionResult("
            f"status={self.status!r}, "
            f"value={self.value!r}, "
            f"duration={self.duration:.6f}s)"
        )