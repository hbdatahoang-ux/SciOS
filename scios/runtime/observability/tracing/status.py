"""
SciOS Runtime Tracing Status
============================

Status model for tracing and runtime diagnostics.

Python 3.11+
"""

from __future__ import annotations

import copy as copy_module
import json

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, TypeAlias


# ==============================================================================
# Part 1. Constants & Type Aliases
# ==============================================================================

DEFAULT_STATUS_MESSAGE = ""
DEFAULT_EXCEPTION = None

STATUS_VERSION = "1.0.0"
STATUS_API_VERSION = "1"

StatusAttributeMap: TypeAlias = dict[str, Any]
StatusJSON: TypeAlias = dict[str, Any]


# ==============================================================================
# Part 2. Exceptions & Enums
# ==============================================================================


class StatusError(Exception):
    """Base exception for status-related errors."""


class StatusValidationError(StatusError):
    """Raised when a status contains invalid data."""


class StatusSerializationError(StatusError):
    """Raised when status serialization or deserialization fails."""


class StatusCode(Enum):
    """Status state."""

    UNSET = auto()
    OK = auto()
    ERROR = auto()

    def __str__(self) -> str:
        return self.name


# ==============================================================================
# Part 3. Status Model
# ==============================================================================


@dataclass(slots=True)
class Status:
    """
    Runtime tracing status.

    A Status represents one of three states:

        UNSET
        OK
        ERROR

    It may additionally carry:

        - a human-readable message
        - an attached exception
        - arbitrary diagnostic attributes
    """

    code: StatusCode = StatusCode.UNSET

    message: str = DEFAULT_STATUS_MESSAGE

    exception: Exception | None = DEFAULT_EXCEPTION

    attributes: StatusAttributeMap = field(
        default_factory=dict,
    )

    # --------------------------------------------------------------------------
    # Constructor validation
    # --------------------------------------------------------------------------

    def __post_init__(self) -> None:
        if not isinstance(self.code, StatusCode):
            raise StatusValidationError(
                "Invalid status code."
            )

        self.message = str(self.message)

        if self.exception is not None and not isinstance(
            self.exception,
            BaseException,
        ):
            raise StatusValidationError(
                "Invalid exception."
            )

        try:
            self.attributes = dict(self.attributes)
        except (TypeError, ValueError) as exc:
            raise StatusValidationError(
                "Invalid status attributes."
            ) from exc

    # --------------------------------------------------------------------------
    # Properties
    # --------------------------------------------------------------------------

    @property
    def has_exception(self) -> bool:
        """Return True when an exception is attached."""
        return self.exception is not None

    @property
    def attribute_count(self) -> int:
        """Return the number of status attributes."""
        return len(self.attributes)

    # ==========================================================================
    # Part 4. State Inspection
    # ==========================================================================

    def is_unset(self) -> bool:
        """Return True when status is UNSET."""
        return self.code is StatusCode.UNSET

    def is_ok(self) -> bool:
        """Return True when status is OK."""
        return self.code is StatusCode.OK

    def is_error(self) -> bool:
        """Return True when status is ERROR."""
        return self.code is StatusCode.ERROR

    # ==========================================================================
    # Part 5. State Mutation
    # ==========================================================================

    def set_ok(
        self,
        message: str = DEFAULT_STATUS_MESSAGE,
    ) -> Status:
        """
        Set status to OK.

        Any previously attached exception is cleared.
        """
        self.code = StatusCode.OK
        self.message = str(message)
        self.exception = None

        return self

    def set_error(
        self,
        message: str = DEFAULT_STATUS_MESSAGE,
        exception: Exception | None = None,
    ) -> Status:
        """
        Set status to ERROR.
        """
        if exception is not None and not isinstance(
            exception,
            BaseException,
        ):
            raise StatusValidationError(
                "Invalid exception."
            )

        self.code = StatusCode.ERROR
        self.message = str(message)
        self.exception = exception

        return self

    def reset(self) -> Status:
        """
        Reset status to its initial UNSET state.
        """
        self.code = StatusCode.UNSET
        self.message = DEFAULT_STATUS_MESSAGE
        self.exception = None
        self.attributes.clear()

        return self

    # ==========================================================================
    # Part 6. Exception API
    # ==========================================================================

    def attach_exception(
        self,
        exception: Exception,
    ) -> Status:
        """
        Attach an exception and transition status to ERROR.
        """
        if not isinstance(
            exception,
            BaseException,
        ):
            raise StatusValidationError(
                "Invalid exception."
            )

        self.code = StatusCode.ERROR
        self.exception = exception

        if not self.message:
            self.message = str(exception)

        return self

    def clear_exception(self) -> Status:
        """Remove the attached exception."""
        self.exception = None

        return self

    def exception_type(self) -> str | None:
        """Return the exception class name."""
        if self.exception is None:
            return None

        return type(self.exception).__name__

    def exception_message(self) -> str | None:
        """Return the exception message."""
        if self.exception is None:
            return None

        return str(self.exception)

    # ==========================================================================
    # Part 7. Attributes API
    # ==========================================================================

    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> Status:
        """Set a diagnostic attribute."""
        self.attributes[key] = value

        return self

    def remove_attribute(
        self,
        key: str,
    ) -> Status:
        """Remove a diagnostic attribute if present."""
        self.attributes.pop(
            key,
            None,
        )

        return self

    # ==========================================================================
    # Part 8. Serialization API
    # ==========================================================================

    def to_dict(self) -> StatusJSON:
        """
        Convert status into a JSON-compatible dictionary.
        """
        return {
            "code": self.code.name,
            "message": self.message,
            "exception": self.exception_type(),
            "exception_message": self.exception_message(),
            "attributes": copy_module.deepcopy(
                self.attributes,
            ),
        }

    def to_json(self) -> str:
        """
        Serialize status to JSON.
        """
        try:
            return json.dumps(
                self.to_dict(),
                default=str,
            )
        except (TypeError, ValueError) as exc:
            raise StatusSerializationError(
                "Failed to serialize status."
            ) from exc

    @classmethod
    def from_dict(
        cls,
        data: StatusJSON,
    ) -> Status:
        """
        Restore a Status from a dictionary.
        """
        if not isinstance(data, dict):
            raise StatusSerializationError(
                "Status data must be a dictionary."
            )

        raw_code = data.get(
            "code",
            StatusCode.UNSET.name,
        )

        try:
            code = (
                raw_code
                if isinstance(raw_code, StatusCode)
                else StatusCode[str(raw_code)]
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise StatusSerializationError(
                f"Invalid status code: {raw_code!r}"
            ) from exc

        try:
            return cls(
                code=code,
                message=data.get(
                    "message",
                    DEFAULT_STATUS_MESSAGE,
                ),
                attributes=data.get(
                    "attributes",
                    {},
                ),
            )
        except StatusValidationError as exc:
            raise StatusSerializationError(
                "Invalid serialized status."
            ) from exc

    @classmethod
    def from_json(
        cls,
        value: str,
    ) -> Status:
        """
        Restore a Status from JSON.
        """
        if not isinstance(value, str):
            raise StatusSerializationError(
                "JSON value must be a string."
            )

        try:
            data = json.loads(value)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise StatusSerializationError(
                "Invalid status JSON."
            ) from exc

        return cls.from_dict(data)

    def snapshot(self) -> StatusJSON:
        """
        Create a serializable snapshot.
        """
        return self.to_dict()

    @classmethod
    def restore(
        cls,
        data: StatusJSON,
    ) -> Status:
        """
        Restore a status from a snapshot.
        """
        return cls.from_dict(data)

    def clone(self) -> Status:
        """
        Create an independent deep copy.
        """
        return self.__class__(
            code=self.code,
            message=self.message,
            exception=copy_module.deepcopy(
                self.exception,
            ),
            attributes=copy_module.deepcopy(
                self.attributes,
            ),
        )

    def copy(self) -> Status:
        """
        Create a shallow copy.
        """
        return copy_module.copy(self)

    # ==========================================================================
    # Part 9. Diagnostics
    # ==========================================================================

    def validate(self) -> bool:
        """
        Validate the current status structure.
        """
        if not isinstance(
            self.code,
            StatusCode,
        ):
            return False

        if not isinstance(
            self.message,
            str,
        ):
            return False

        if self.exception is not None and not isinstance(
            self.exception,
            BaseException,
        ):
            return False

        if not isinstance(
            self.attributes,
            dict,
        ):
            return False

        return True

    def diagnostics(self) -> StatusJSON:
        """
        Return detailed diagnostic information.
        """
        return {
            "valid": self.validate(),
            "code": self.code.name,
            "message": self.message,
            "has_exception": self.has_exception,
            "exception": self.exception_type(),
            "exception_message": self.exception_message(),
            "attribute_count": self.attribute_count,
            "attributes": copy_module.deepcopy(
                self.attributes,
            ),
        }

    def summary(self) -> StatusJSON:
        """
        Return a compact status summary.
        """
        return {
            "code": self.code.name,
            "message": self.message,
        }

    # ==========================================================================
    # Part 10. Python Protocols
    # ==========================================================================

    def __repr__(self) -> str:
        return (
            "Status("
            f"code={self.code.name!r}, "
            f"message={self.message!r}"
            ")"
        )

    def __str__(self) -> str:
        return (
            f"{self.code.name}: "
            f"{self.message}"
        )

    def __len__(self) -> int:
        return len(self.attributes)

    def __contains__(
        self,
        key: str,
    ) -> bool:
        return key in self.attributes

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        return self.attributes[key]

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.attributes[key] = value

    def __delitem__(
        self,
        key: str,
    ) -> None:
        del self.attributes[key]

    def __iter__(self):
        return iter(self.attributes)

    def __bool__(self) -> bool:
        return self.validate()

    def __hash__(self) -> int:
        """
        Provide deterministic hashability without hashing the
        mutable attributes mapping directly.
        """
        attributes_hash = hash(
            tuple(
                sorted(
                    (
                        str(key),
                        repr(value),
                    )
                    for key, value in self.attributes.items()
                )
            )
        )

        return hash(
            (
                self.code,
                self.message,
                self.exception_type(),
                self.exception_message(),
                attributes_hash,
            )
        )


# ==============================================================================
# Compatibility
# ==============================================================================

TraceStatus = Status


# ==============================================================================
# Part 11. Public API
# ==============================================================================

__all__ = [
    "Status",
    "StatusCode",
    "TraceStatus",
    "StatusError",
    "StatusValidationError",
    "StatusSerializationError",
    "StatusAttributeMap",
    "StatusJSON",
    "DEFAULT_STATUS_MESSAGE",
    "DEFAULT_EXCEPTION",
    "STATUS_VERSION",
    "STATUS_API_VERSION",
]
