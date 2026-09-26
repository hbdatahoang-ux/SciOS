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
- Store execution metadata.
- Support mapping-style compatibility.
- Support serialization and restoration.
- Support deep-copy snapshots.
- Integrate with Runtime ExecutionContext and Pipeline.

Contract
--------

    ExecutionResult
        |
        +-- success
        +-- value
        +-- error
        +-- message
        +-- duration
        +-- metadata
        +-- timestamp


Success
-------

    result = ExecutionResult.ok(123)

    result.success == True
    result.status == "success"
    result.value == 123
    result.error is None


Failure
-------

    error = ValueError("boom")
    result = ExecutionResult.fail(error)

    result.success == False
    result.status == "error"
    result.value is None
    result.error is error


Mapping compatibility
---------------------

    result["value"]
    result["status"]
    result["task"]       # when value is a dict

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
    Mapping,
)


__all__ = [
    "ExecutionResult",
]


# ==========================================================
# Constants
# ==========================================================

SUCCESS_STATUS = "success"
ERROR_STATUS = "error"


# ==========================================================
# Helpers
# ==========================================================


def utc_now() -> str:
    """
    Return the current UTC timestamp in ISO-8601 format.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()


# ==========================================================
# ExecutionResult
# ==========================================================


@dataclass(
    slots=True,
)
class ExecutionResult:
    """
    Canonical SciOS runtime execution result.

    The object represents the outcome of one execution.

    Parameters
    ----------
    success:
        Whether execution completed successfully.

    value:
        Actual execution payload.

    error:
        Exception associated with a failed execution.

    message:
        Human-readable diagnostic message.

    duration:
        Execution duration in seconds.

    metadata:
        Additional execution metadata.

    timestamp:
        Result creation timestamp.

    Examples
    --------
    Successful result:

        result = ExecutionResult.ok(
            {"answer": 42}
        )

    Failed result:

        result = ExecutionResult.fail(
            ValueError("invalid input")
        )

    Access:

        result.success
        result.status
        result.value
        result.error
        result["value"]
    """

    # ======================================================
    # Outcome
    # ======================================================

    success: bool = True

    # ======================================================
    # Payload
    # ======================================================

    value: Any = None

    # ======================================================
    # Diagnostics
    # ======================================================

    error: BaseException | None = None

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
    # Initialization
    # ======================================================

    def __post_init__(
        self,
    ) -> None:
        """
        Normalize runtime fields after dataclass construction.
        """

        self.success = bool(
            self.success
        )

        self.duration = float(
            self.duration
        )

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

        # A successful result must not expose an error.
        if self.success:
            self.error = None

        # A failed result should have a useful message
        # whenever an exception exists.
        elif (
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
        """
        Whether execution succeeded.
        """

        return self.success

    @property
    def failed(
        self,
    ) -> bool:
        """
        Whether execution failed.
        """

        return not self.success

    @property
    def is_success(
        self,
    ) -> bool:
        """
        Compatibility alias for ``success``.
        """

        return self.success

    @property
    def status(
        self,
    ) -> str:
        """
        Canonical textual execution status.

        Returns
        -------
        str
            ``"success"`` or ``"error"``.
        """

        return (
            SUCCESS_STATUS
            if self.success
            else ERROR_STATUS
        )

    @property
    def result(
        self,
    ) -> Any:
        """
        Compatibility alias for ``value``.
        """

        return self.value

    @property
    def has_value(
        self,
    ) -> bool:
        """
        Whether a non-None payload exists.
        """

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
        metadata: dict[str, Any] | None = None,
        **extra_metadata,
    ) -> "ExecutionResult":
        """
        Create a successful execution result.

        Supports both:

            ExecutionResult.ok(
                123,
                source="test",
            )

        and:

            ExecutionResult.ok(
                123,
                metadata={
                    "source": "test",
                },
            )

        Explicit ``metadata`` is merged with keyword metadata.
        Keyword metadata takes precedence on conflicts.
        """

        merged_metadata: dict[str, Any] = {}

        if metadata is not None:
            merged_metadata.update(
                deepcopy(metadata)
            )

        merged_metadata.update(
            extra_metadata
        )

        return cls(
            success=True,
            value=value,
            message=message,
            duration=duration,
            metadata=merged_metadata,
        )

    @classmethod
    def fail(
        cls,
        error: BaseException,
        *,
        message=None,
        duration: float = 0.0,
        metadata: dict[str, Any] | None = None,
        **extra_metadata,
    ) -> "ExecutionResult":
        """
        Create a failed execution result.

        Supports both explicit metadata mapping and
        keyword metadata.
        """

        merged_metadata: dict[str, Any] = {}

        if metadata is not None:
            merged_metadata.update(
                deepcopy(metadata)
            )

        merged_metadata.update(
            extra_metadata
        )

        return cls(
            success=False,
            error=error,
            message=(
                message
                if message is not None
                else str(error)
            ),
            duration=duration,
            metadata=merged_metadata,
        )

    @classmethod
    def from_value(
        cls,
        value: Any,
    ) -> "ExecutionResult":
        """
        Create a successful result from a raw value.
        """

        return cls.ok(
            value
        )

    @classmethod
    def from_error(
        cls,
        error: BaseException,
    ) -> "ExecutionResult":
        """
        Create a failed result from an exception.
        """

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
    ) -> "ExecutionResult":
        """
        Set one metadata value.

        Returns
        -------
        ExecutionResult
            ``self`` for fluent chaining.
        """

        self.metadata[key] = value

        return self

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve one metadata value.
        """

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
        """
        Serialize the execution result into a plain dictionary.

        The returned dictionary is detached from the live result.
        """

        return {
            "status": self.status,
            "success": self.success,

            "value": deepcopy(
                self.value
            ),

            # Compatibility alias.
            "result": deepcopy(
                self.value
            ),

            "message": self.message,

            "error": (
                str(self.error)
                if self.error is not None
                else None
            ),

            "duration": self.duration,

            "metadata": deepcopy(
                self.metadata
            ),

            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "ExecutionResult":
        """
        Restore an ExecutionResult from serialized data.

        Notes
        -----
        Serialized exceptions are restored as RuntimeError
        instances because arbitrary exception classes cannot be
        reconstructed safely from a plain dictionary.
        """

        if not isinstance(
            data,
            Mapping,
        ):
            raise TypeError(
                "ExecutionResult.from_dict() "
                "expects a mapping"
            )

        status = data.get(
            "status"
        )

        success_value = data.get(
            "success"
        )

        if success_value is None:

            success = (
                str(status).lower()
                == SUCCESS_STATUS
            )

        else:

            success = bool(
                success_value
            )

        value = data.get(
            "value",
            data.get(
                "result"
            ),
        )

        error_value = data.get(
            "error"
        )

        error: BaseException | None

        if (
            not success
            and error_value
        ):

            error = RuntimeError(
                str(error_value)
            )

        else:

            error = None

        message = data.get(
            "message"
        )

        if (
            message is None
            and error is not None
        ):
            message = str(
                error
            )

        metadata = data.get(
            "metadata",
            {},
        )

        if metadata is None:
            metadata = {}

        if not isinstance(
            metadata,
            Mapping,
        ):
            raise TypeError(
                "ExecutionResult.metadata "
                "must be a mapping"
            )

        return cls(
            success=success,
            value=deepcopy(
                value
            ),
            error=error,
            message=message,
            duration=float(
                data.get(
                    "duration",
                    0.0,
                )
            ),
            metadata=dict(
                metadata
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
    ) -> Any:
        """
        Mapping-compatible item access.

        Resolution order:

        1. Result fields.
        2. Metadata fields.
        3. Dictionary payload fields.
        """

        data = self.to_dict()

        # --------------------------------------------------
        # Result fields
        # --------------------------------------------------

        if key in data:
            return data[key]

        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        if key in self.metadata:
            return self.metadata[key]

        # --------------------------------------------------
        # Dictionary payload
        # --------------------------------------------------

        if isinstance(
            self.value,
            Mapping,
        ) and key in self.value:

            return self.value[key]

        raise KeyError(
            key
        )


    def __contains__(
        self,
        key: str,
    ) -> bool:
        """
        Check whether a key exists in the result,
        metadata, or dictionary payload.
        """

        if key in self.to_dict():
            return True

        if key in self.metadata:
            return True

        return (
            isinstance(
                self.value,
                Mapping,
            )
            and key in self.value
        )


    def keys(
        self,
    ) -> list[str]:
        """
        Return deterministic mapping keys.

        Resolution order:

        1. Result fields.
        2. Metadata fields.
        3. Dictionary payload fields.

        Duplicate keys are emitted only once.
        """

        result_keys = list(
            self.to_dict().keys()
        )

        keys = list(
            result_keys
        )

        for key in self.metadata:

            if key not in keys:
                keys.append(key)

        if isinstance(
            self.value,
            Mapping,
        ):

            for key in self.value:

                if key not in keys:
                    keys.append(key)

        return keys


    def items(
        self,
    ):
        """
        Return deterministic mapping-compatible
        key/value pairs.
        """

        data = self.to_dict()

        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        for key, value in self.metadata.items():

            if key not in data:
                data[key] = value

        # --------------------------------------------------
        # Dictionary payload
        # --------------------------------------------------

        if isinstance(
            self.value,
            Mapping,
        ):

            for key, value in self.value.items():

                if key not in data:
                    data[key] = value

        return data.items()


    def __iter__(
        self,
    ) -> Iterator[str]:
        """
        Iterate over mapping keys.
        """

        return iter(
            self.keys()
        )

    # ======================================================
    # Copy API
    # ======================================================

    def copy(
        self,
    ) -> "ExecutionResult":
        """
        Create an independent deep copy.
        """

        return deepcopy(
            self
        )

    # ======================================================
    # Protocol API
    # ======================================================

    def __bool__(
        self,
    ) -> bool:
        """
        Truth value follows execution success.
        """

        return self.success

    def __len__(
        self,
    ) -> int:
        """
        Return payload size for dictionary payloads.

        Non-mapping payloads have length zero.
        """

        if isinstance(
            self.value,
            Mapping,
        ):
            return len(
                self.value
            )

        return 0

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(
        self,
    ) -> str:
        """
        Developer-friendly representation.
        """

        return (
            "ExecutionResult("
            f"status={self.status!r}, "
            f"value={self.value!r}, "
            f"duration={self.duration:.6f}s"
            ")"
        )