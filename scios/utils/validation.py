"""
SciOS Validation Framework
==========================

Common validation utilities used throughout the
Scientific Cognitive Operating System (SciOS).

The validation module provides lightweight runtime
checks for values, types and object integrity.

Features
--------
- Generic validation helpers
- Type checking
- None checking
- Empty checking
- Numeric validation
- Validator facade
"""

from __future__ import annotations

from collections.abc import Collection
from typing import Any
from typing import Type

from scios.shared.exceptions import ValidationError

__all__ = [
    "Validator",
    "require",
    "require_not_none",
    "require_type",
    "require_instance",
    "require_non_empty",
    "require_positive",
    "require_range",
]


# ==========================================================
# Primitive Validators
# ==========================================================


def require(
    condition: bool,
    message: str = "Validation failed.",
) -> None:
    """
    Require a condition to be True.
    """

    if not condition:
        raise ValidationError(message)


def require_not_none(
    value: Any,
    name: str = "value",
) -> Any:
    """
    Ensure value is not None.
    """

    if value is None:
        raise ValidationError(
            f"{name} must not be None."
        )

    return value


def require_type(
    value: Any,
    expected: Type[Any] | tuple[Type[Any], ...],
    name: str = "value",
) -> Any:
    """
    Validate the exact type of a value.
    """

    if not isinstance(value, expected):
        raise ValidationError(
            f"{name} must be of type "
            f"{expected}, got {type(value)}."
        )

    return value


def require_instance(
    value: Any,
    expected: Type[Any] | tuple[Type[Any], ...],
    name: str = "value",
) -> Any:
    """
    Alias of require_type for readability.
    """

    return require_type(
        value,
        expected,
        name,
    )


def require_non_empty(
    value: Collection[Any],
    name: str = "value",
) -> Collection[Any]:
    """
    Ensure a collection is not empty.
    """

    if len(value) == 0:
        raise ValidationError(
            f"{name} must not be empty."
        )

    return value


def require_positive(
    value: int | float,
    name: str = "value",
) -> int | float:
    """
    Ensure a numeric value is positive.
    """

    if value <= 0:
        raise ValidationError(
            f"{name} must be positive."
        )

    return value


def require_range(
    value: int | float,
    minimum: int | float,
    maximum: int | float,
    name: str = "value",
) -> int | float:
    """
    Ensure a numeric value falls within a range.
    """

    if not minimum <= value <= maximum:
        raise ValidationError(
            f"{name} must be between "
            f"{minimum} and {maximum}."
        )

    return value


# ==========================================================
# Validator Facade
# ==========================================================


class Validator:
    """
    Unified validation facade.

    Examples
    --------

    >>> Validator.require(x > 0)

    >>> Validator.require_not_none(config)

    >>> Validator.require_type(task, dict)

    >>> Validator.require_positive(score)
    """

    require = staticmethod(require)

    require_not_none = staticmethod(require_not_none)

    require_type = staticmethod(require_type)

    require_instance = staticmethod(require_instance)

    require_non_empty = staticmethod(require_non_empty)

    require_positive = staticmethod(require_positive)

    require_range = staticmethod(require_range)
