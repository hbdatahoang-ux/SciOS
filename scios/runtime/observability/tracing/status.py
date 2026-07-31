"""
SciOS Runtime Observability
===========================

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
# Part 2. Constants & Type Aliases
# ==============================================================================

DEFAULT_STATUS_MESSAGE = ""

DEFAULT_EXCEPTION = None

STATUS_VERSION = "1.0.0"

STATUS_API_VERSION = "1"


StatusAttributeMap: TypeAlias = dict[str, Any]

StatusJSON: TypeAlias = dict[str, Any]


# ==============================================================================
# Part 3. Exceptions & Enums
# ==============================================================================

class StatusError(Exception):
    pass


class StatusValidationError(StatusError):
    pass


class StatusSerializationError(StatusError):
    pass


class StatusCode(Enum):

    UNSET = auto()

    OK = auto()

    ERROR = auto()

    def __str__(self) -> str:
        return self.name


# ==============================================================================
# Part 4-10. Status Model
# ==============================================================================

@dataclass(slots=True)
class Status:

    code: StatusCode = StatusCode.UNSET

    message: str = DEFAULT_STATUS_MESSAGE

    exception: Exception | None = None

    attributes: StatusAttributeMap = field(
        default_factory=dict
    )


    # ------------------------------------------------------------------
    # Part 5. Constructor & Properties
    # ------------------------------------------------------------------

    def __post_init__(self):

        if not isinstance(
            self.code,
            StatusCode,
        ):
            raise StatusValidationError(
                "Invalid status code."
            )

        self.message = str(
            self.message
        )

        self.attributes = dict(
            self.attributes
        )


    @property
    def has_exception(self):

        return self.exception is not None


    @property
    def attribute_count(self):

        return len(
            self.attributes
        )


    # ------------------------------------------------------------------
    # Part 6. Core API
    # ------------------------------------------------------------------

    def is_unset(self):

        return self.code is StatusCode.UNSET


    def is_ok(self):

        return self.code is StatusCode.OK


    def is_error(self):

        return self.code is StatusCode.ERROR


    def set_ok(
        self,
        message: str = "",
    ):

        self.code = StatusCode.OK
        self.message = message
        self.exception = None

        return self


    def set_error(
        self,
        message: str = "",
        exception=None,
    ):

        self.code = StatusCode.ERROR
        self.message = message
        self.exception = exception

        return self


    def reset(self):

        self.code = StatusCode.UNSET
        self.message = ""
        self.exception = None
        self.attributes.clear()

        return self


    # ------------------------------------------------------------------
    # Part 7. Exception & Attributes
    # ------------------------------------------------------------------

    def attach_exception(
        self,
        exception: Exception,
    ):

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
            self.message = str(
                exception
            )

        return self


    def clear_exception(self):

        self.exception = None

        return self


    def exception_type(self):

        if self.exception is None:
            return None

        return type(
            self.exception
        ).__name__


    def exception_message(self):

        if self.exception is None:
            return None

        return str(
            self.exception
        )


    def set_attribute(
        self,
        key,
        value,
    ):

        self.attributes[key] = value

        return self


    def remove_attribute(
        self,
        key,
    ):

        self.attributes.pop(
            key,
            None,
        )

        return self


    # ------------------------------------------------------------------
    # Part 8. Serialization
    # ------------------------------------------------------------------

    def to_dict(self):

        return {

            "code":
                self.code.name,

            "message":
                self.message,

            "exception":
                self.exception_type(),

            "exception_message":
                self.exception_message(),

            "attributes":
                dict(
                    self.attributes
                ),
        }


    def to_json(self):

        return json.dumps(
            self.to_dict(),
            default=str,
        )


    @classmethod
    def from_dict(
        cls,
        data,
    ):

        return cls(

            code=StatusCode[
                data.get(
                    "code",
                    "UNSET",
                )
            ],

            message=data.get(
                "message",
                "",
            ),

            attributes=data.get(
                "attributes",
                {},
            ),
        )


    @classmethod
    def from_json(
        cls,
        value,
    ):

        return cls.from_dict(
            json.loads(value)
        )


    def snapshot(self):

        return self.to_dict()


    @classmethod
    def restore(
        cls,
        data,
    ):

        return cls.from_dict(
            data
        )


    def clone(self):

        return self.__class__.from_dict(
            copy_module.deepcopy(
                self.to_dict()
            )
        )


    def copy(self):

        return copy_module.copy(
            self
        )


    # ------------------------------------------------------------------
    # Part 9. Diagnostics
    # ------------------------------------------------------------------

    def validate(self):

        return (
            isinstance(
                self.code,
                StatusCode,
            )
            and
            isinstance(
                self.attributes,
                dict,
            )
        )


    def diagnostics(self):

        return {

            "valid":
                self.validate(),

            "code":
                self.code.name,

            "message":
                self.message,

            "attributes":
                dict(
                    self.attributes
                ),
        }


    def summary(self):

        return {

            "code":
                self.code.name,

            "message":
                self.message,
        }


    # ------------------------------------------------------------------
    # Part 10. Python Protocols
    # ------------------------------------------------------------------

    def __repr__(self):

        return (
            f"Status("
            f"code={self.code.name!r}, "
            f"message={self.message!r}"
            f")"
        )


    def __str__(self):

        return (
            f"{self.code.name}: "
            f"{self.message}"
        )


    def __len__(self):

        return len(
            self.attributes
        )


    def __contains__(
        self,
        key,
    ):

        return key in self.attributes


    def __getitem__(
        self,
        key,
    ):

        return self.attributes[key]


    def __setitem__(
        self,
        key,
        value,
    ):

        self.attributes[key] = value


    def __hash__(self):

        return hash(
            (
                self.code,
                self.message,
                self.exception_type(),
                repr(
                    self.attributes
                ),
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

]