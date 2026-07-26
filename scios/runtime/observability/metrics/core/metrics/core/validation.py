"""
SciOS-NG Metrics Core - Validation
==================================

Central validation utilities for the Metrics subsystem.

Design goals
------------
- Single validation entry point.
- Fully typed.
- Production-ready.
- Reusable by Metric, Registry, Serializer and Manager.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from typing import Any

from .exceptions import (
    InvalidMetricAttribute,
    InvalidMetricLabel,
    InvalidMetricMetadata,
    InvalidMetricName,
    InvalidMetricUnit,
    InvalidMetricValue,
)

__all__ = [
    "MetricValidator",
]


class MetricValidator:
    """
    Static validation helper for Metric objects.
    """

    NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_.:/-]{0,127}$")

    LABEL_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]{0,63}$")

    ATTRIBUTE_PATTERN = LABEL_PATTERN

    UNIT_PATTERN = re.compile(r"^[A-Za-z0-9_%/.\-*]*$")

    # ---------------------------------------------------------
    # Metric Name
    # ---------------------------------------------------------

    @classmethod
    def validate_name(cls, name: str) -> str:

        if not isinstance(name, str):
            raise InvalidMetricName("Metric name must be a string.")

        name = name.strip()

        if not name:
            raise InvalidMetricName("Metric name cannot be empty.")

        if not cls.NAME_PATTERN.fullmatch(name):
            raise InvalidMetricName(
                f"Invalid metric name: {name!r}"
            )

        return name

    # ---------------------------------------------------------
    # Unit
    # ---------------------------------------------------------

    @classmethod
    def validate_unit(cls, unit: str | None) -> str:

        if unit is None:
            return ""

        if not isinstance(unit, str):
            raise InvalidMetricUnit("Unit must be a string.")

        unit = unit.strip()

        if not cls.UNIT_PATTERN.fullmatch(unit):
            raise InvalidMetricUnit(
                f"Invalid unit: {unit!r}"
            )

        return unit

    # ---------------------------------------------------------
    # Value
    # ---------------------------------------------------------

    @classmethod
    def validate_value(cls, value: Any) -> Any:

        if value is None:
            return value

        if isinstance(value, float):

            if math.isnan(value):
                raise InvalidMetricValue("NaN is not allowed.")

            if math.isinf(value):
                raise InvalidMetricValue("Infinite values are not allowed.")

        return value

    # ---------------------------------------------------------
    # Label
    # ---------------------------------------------------------

    @classmethod
    def validate_label(cls, key: str, value: str) -> tuple[str, str]:

        if not isinstance(key, str):
            raise InvalidMetricLabel("Label key must be a string.")

        if not isinstance(value, str):
            raise InvalidMetricLabel("Label value must be a string.")

        key = key.strip()

        if not cls.LABEL_PATTERN.fullmatch(key):
            raise InvalidMetricLabel(
                f"Invalid label key: {key!r}"
            )

        return key, value

    @classmethod
    def validate_labels(
        cls,
        labels: Mapping[str, str] | None,
    ) -> dict[str, str]:

        if labels is None:
            return {}

        if not isinstance(labels, Mapping):
            raise InvalidMetricLabel(
                "Labels must be a mapping."
            )

        result = {}

        for k, v in labels.items():

            k, v = cls.validate_label(k, v)

            result[k] = v

        return result

    # ---------------------------------------------------------
    # Attribute
    # ---------------------------------------------------------

    @classmethod
    def validate_attribute(
        cls,
        key: str,
        value: Any,
    ) -> tuple[str, Any]:

        if not isinstance(key, str):
            raise InvalidMetricAttribute(
                "Attribute key must be a string."
            )

        key = key.strip()

        if not cls.ATTRIBUTE_PATTERN.fullmatch(key):
            raise InvalidMetricAttribute(
                f"Invalid attribute key: {key!r}"
            )

        return key, value

    @classmethod
    def validate_attributes(
        cls,
        attributes: Mapping[str, Any] | None,
    ) -> dict[str, Any]:

        if attributes is None:
            return {}

        if not isinstance(attributes, Mapping):
            raise InvalidMetricAttribute(
                "Attributes must be a mapping."
            )

        result = {}

        for k, v in attributes.items():

            k, v = cls.validate_attribute(k, v)

            result[k] = v

        return result

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    @classmethod
    def validate_metadata(
        cls,
        metadata: Mapping[str, Any] | None,
    ) -> dict[str, Any]:

        if metadata is None:
            return {}

        if not isinstance(metadata, Mapping):
            raise InvalidMetricMetadata(
                "Metadata must be a mapping."
            )

        return dict(metadata)

    # ---------------------------------------------------------
    # State
    # ---------------------------------------------------------

    @classmethod
    def validate_state(
        cls,
        *,
        enabled: bool,
        frozen: bool,
        closed: bool,
    ) -> None:

        if not isinstance(enabled, bool):
            raise TypeError("enabled must be bool")

        if not isinstance(frozen, bool):
            raise TypeError("frozen must be bool")

        if not isinstance(closed, bool):
            raise TypeError("closed must be bool")