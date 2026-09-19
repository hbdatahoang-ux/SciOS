"""
SciOS Runtime Metrics Validator Processor
=========================================

Metric validation processor.

Responsibilities
-----------------
- Validate metric structure.
- Apply custom validation rules.
- Validate declared schemas.
- Provide built-in required-field and range validators.
- Collect validation diagnostics.
- Expose processor statistics.

Python 3.11+
"""

from __future__ import annotations

from typing import Any, Callable

from .processor import MetricProcessor


__all__ = ["ValidatorProcessor"]


class ValidatorProcessor(MetricProcessor):
    """
    Runtime metric validation processor.

    A metric is returned unchanged when all validation rules pass.
    Invalid metrics return ``None`` and their validation errors are
    recorded for diagnostics.
    """

    def __init__(
        self,
        name: str = "ValidatorProcessor",
        description: str = "",
    ) -> None:
        super().__init__(
            name=name,
            description=description,
        )

        self._rules: list[Callable[[Any], Any]] = []
        self._schema: dict[str, type] = {}

        self._validated = 0
        self._invalid = 0
        self._errors: list[str] = []

    # ==============================================================
    # Processing
    # ==============================================================

    def transform(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Validate a metric.

        Returns
        -------
        Any
            The original metric if valid, otherwise ``None``.
        """

        valid, errors = self.validate(metric)

        if valid:
            self._validated += 1
            return metric

        self._invalid += 1
        self._errors.extend(errors)

        return None

    # ==============================================================
    # Validation
    # ==============================================================

    def validate(
        self,
        metric: Any,
    ) -> tuple[bool, list[str]]:
        """
        Run all registered rules and schema validation.

        Returns
        -------
        tuple[bool, list[str]]
            ``(True, [])`` when valid, otherwise ``(False, errors)``.
        """

        errors: list[str] = []

        for rule in self._rules:
            try:
                result = rule(metric)

                if result is False:
                    errors.append("Rule validation failed")

                elif isinstance(result, str):
                    errors.append(result)

            except Exception as exc:
                errors.append(str(exc))

        errors.extend(self.validate_schema(metric))

        return len(errors) == 0, errors

    # ==============================================================
    # Rule Management
    # ==============================================================

    def add_rule(
        self,
        rule: Callable[[Any], Any],
    ) -> ValidatorProcessor:
        """Register a custom validation rule."""

        if not callable(rule):
            raise TypeError("rule must be callable")

        self._rules.append(rule)
        return self

    def remove_rule(
        self,
        rule: Callable[[Any], Any],
    ) -> ValidatorProcessor:
        """Remove a previously registered validation rule."""

        if rule in self._rules:
            self._rules.remove(rule)

        return self

    def clear_rules(self) -> ValidatorProcessor:
        """Remove all custom validation rules."""

        self._rules.clear()
        return self

    def rules(self) -> list[Callable[[Any], Any]]:
        """Return a copy of registered rules."""

        return list(self._rules)

    # ==============================================================
    # Schema
    # ==============================================================

    def define_field(
        self,
        name: str,
        field_type: type,
    ) -> ValidatorProcessor:
        """Declare a required field and its expected type."""

        if not isinstance(name, str) or not name:
            raise ValueError("field name must be a non-empty string")

        if not isinstance(field_type, type):
            raise TypeError("field_type must be a type")

        self._schema[name] = field_type
        return self

    def remove_field(
        self,
        name: str,
    ) -> ValidatorProcessor:
        """Remove a field from the schema."""

        self._schema.pop(name, None)
        return self

    def schema(self) -> dict[str, type]:
        """Return a copy of the declared schema."""

        return dict(self._schema)

    def validate_schema(
        self,
        metric: Any,
    ) -> list[str]:
        """Validate a metric against the declared schema."""

        if not self._schema:
            return []

        if not isinstance(metric, dict):
            return ["Metric must be dictionary"]

        errors: list[str] = []

        for field, expected_type in self._schema.items():
            if field not in metric:
                errors.append(f"Missing field: {field}")
                continue

            if not isinstance(metric[field], expected_type):
                errors.append(
                    f"Invalid type for {field}"
                )

        return errors

    # ==============================================================
    # Built-in Validators
    # ==============================================================

    def require(
        self,
        *fields: str,
    ) -> ValidatorProcessor:
        """Require one or more dictionary fields."""

        def rule(metric: Any) -> bool | str:
            if not isinstance(metric, dict):
                return False

            for field in fields:
                if field not in metric:
                    return f"Missing required field: {field}"

            return True

        return self.add_rule(rule)

    def range(
        self,
        field: str,
        minimum: Any = None,
        maximum: Any = None,
    ) -> ValidatorProcessor:
        """Validate that a numeric/comparable field is within a range."""

        if minimum is None and maximum is None:
            raise ValueError(
                "range() requires minimum or maximum"
            )

        def rule(metric: Any) -> bool | str:
            if not isinstance(metric, dict):
                return False

            if field not in metric:
                return f"Missing field: {field}"

            value = metric[field]

            try:
                if minimum is not None and value < minimum:
                    return f"{field} below minimum"

                if maximum is not None and value > maximum:
                    return f"{field} above maximum"

            except TypeError:
                return f"Invalid value for {field}"

            return True

        return self.add_rule(rule)

    # ==============================================================
    # Diagnostics
    # ==============================================================

    def errors(self) -> list[str]:
        """Return collected validation errors."""

        return list(self._errors)

    def clear_errors(self) -> ValidatorProcessor:
        """Clear collected validation errors."""

        self._errors.clear()
        return self

    # ==============================================================
    # Statistics
    # ==============================================================

    def statistics(self) -> dict[str, Any]:
        """Return validator statistics."""

        data = super().statistics()

        data.update(
            {
                "validated": self._validated,
                "invalid": self._invalid,
                "rules": len(self._rules),
                "schema_fields": len(self._schema),
            }
        )

        return data

    # ==============================================================
    # Runtime
    # ==============================================================

    def reset(self) -> ValidatorProcessor:
        """Reset runtime validation counters and diagnostics."""

        self._validated = 0
        self._invalid = 0
        self._errors.clear()

        return self

    # ==============================================================
    # Python Protocols
    # ==============================================================

    def __len__(self) -> int:
        """Return number of registered custom rules."""

        return len(self._rules)

    def __repr__(self) -> str:
        return (
            "ValidatorProcessor("
            f"rules={len(self._rules)}, "
            f"validated={self._validated}, "
            f"invalid={self._invalid}"
            ")"
        )