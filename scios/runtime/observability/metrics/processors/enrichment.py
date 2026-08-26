"""
SciOS Runtime Metrics Enrichment Processor
==========================================

Metric enrichment processor.

Responsibilities
-----------------
- Add static fields to metrics.
- Evaluate dynamic field providers.
- Apply enrichment rules.
- Preserve input immutability.
- Track enrichment diagnostics and statistics.

Python 3.11+
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from .processor import MetricProcessor


__all__ = [
    "EnrichmentProcessor",
]


# ======================================================================
# Enrichment Processor
# ======================================================================


class EnrichmentProcessor(MetricProcessor):
    """
    Runtime metric enrichment processor.

    Fields may contain either concrete values or zero-argument callables.
    Rules may transform the enriched metric and are executed sequentially.

    The input metric is never mutated directly.
    """

    # ==================================================================
    # Constructor
    # ==================================================================

    def __init__(
        self,
        name: str = "EnrichmentProcessor",
        description: str = "",
        fields: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            name=name,
            description=description,
        )

        self._fields: dict[str, Any] = {}

        self._rules: list[Callable[[Any], Any]] = []

        self._enriched = 0
        self._skipped = 0

        self._errors: list[str] = []

        if fields is not None:
            for field_name, value in fields.items():
                self.add_field(
                    field_name,
                    value,
                )

    # ==================================================================
    # Static Fields
    # ==================================================================

    def add_field(
        self,
        name: str,
        value: Any,
    ) -> "EnrichmentProcessor":
        """
        Add or replace an enrichment field.

        ``value`` may be a concrete value or a zero-argument callable.
        """

        if not isinstance(name, str) or not name:
            raise ValueError(
                "Field name must not be empty"
            )

        self._fields[name] = value

        return self

    def remove_field(
        self,
        name: str,
    ) -> "EnrichmentProcessor":
        """
        Remove an enrichment field.

        Missing fields are ignored.
        """

        self._fields.pop(
            name,
            None,
        )

        return self

    def clear_fields(
        self,
    ) -> "EnrichmentProcessor":
        """
        Remove all configured enrichment fields.
        """

        self._fields.clear()

        return self

    def fields(
        self,
    ) -> dict[str, Any]:
        """
        Return a copy of configured enrichment fields.
        """

        return dict(
            self._fields
        )

    # ==================================================================
    # Rules
    # ==================================================================

    def add_rule(
        self,
        rule: Callable[[Any], Any],
    ) -> "EnrichmentProcessor":
        """
        Add an enrichment rule.
        """

        if not callable(rule):
            raise TypeError(
                "rule must be callable"
            )

        self._rules.append(
            rule
        )

        return self

    def remove_rule(
        self,
        rule: Callable[[Any], Any],
    ) -> "EnrichmentProcessor":
        """
        Remove a rule.

        Missing rules are ignored.
        """

        if rule in self._rules:
            self._rules.remove(
                rule
            )

        return self

    def clear_rules(
        self,
    ) -> "EnrichmentProcessor":
        """
        Remove all enrichment rules.
        """

        self._rules.clear()

        return self

    def rules(
        self,
    ) -> list[Callable[[Any], Any]]:
        """
        Return a copy of configured rules.
        """

        return list(
            self._rules
        )

    # ==================================================================
    # Field Evaluation
    # ==================================================================

    @staticmethod
    def _resolve_value(
        value: Any,
    ) -> Any:
        """
        Resolve a field value.

        Callable values are invoked without arguments.
        Concrete values are deep-copied.
        """

        if callable(value):
            return value()

        return deepcopy(value)

    # ==================================================================
    # Transform
    # ==================================================================

    def transform(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Enrich a metric.

        Dictionary metrics are copied before modification.

        Non-dictionary values pass through unchanged.

        Rule failures cause the metric to be skipped and return ``None``.
        """

        if not isinstance(metric, dict):
            return metric

        result = deepcopy(metric)

        try:
            # ----------------------------------------------------------
            # Static / dynamic fields
            # ----------------------------------------------------------

            for name, value in self._fields.items():
                result[name] = self._resolve_value(
                    value
                )

            # ----------------------------------------------------------
            # Enrichment rules
            # ----------------------------------------------------------

            for rule in self._rules:
                rule_result = rule(result)

                # ``None`` means the rule intentionally leaves the
                # current metric unchanged.
                if rule_result is not None:
                    result = rule_result

            self._enriched += 1

            return result

        except Exception as exc:
            self._skipped += 1
            self._errors.append(
                str(exc)
            )

            return None

    # ==================================================================
    # Convenience Enrichment
    # ==================================================================

    def enrich(
        self,
        metric: Any,
        **fields: Any,
    ) -> Any:
        """
        Temporarily enrich a metric with additional fields.

        Temporary fields are applied only to this operation and do not
        modify the processor's configured field set.
        """

        if not isinstance(metric, dict):
            return metric

        result = deepcopy(metric)

        try:
            for name, value in fields.items():
                result[name] = self._resolve_value(
                    value
                )

            return result

        except Exception as exc:
            self._skipped += 1
            self._errors.append(
                str(exc)
            )

            return None

    # ==================================================================
    # Diagnostics
    # ==================================================================

    def errors(
        self,
    ) -> list[str]:
        """
        Return a copy of recorded enrichment errors.
        """

        return list(
            self._errors
        )

    def clear_errors(
        self,
    ) -> "EnrichmentProcessor":
        """
        Clear recorded errors.
        """

        self._errors.clear()

        return self

    # ==================================================================
    # Statistics
    # ==================================================================

    def statistics(
        self,
    ) -> dict[str, Any]:
        """
        Return processor statistics.
        """

        data = super().statistics()

        data.update(
            {
                "enriched": self._enriched,
                "skipped": self._skipped,
                "fields": len(self._fields),
                "rules": len(self._rules),
                "errors": len(self._errors),
            }
        )

        return data

    # ==================================================================
    # Runtime
    # ==================================================================

    def reset(
        self,
    ) -> "EnrichmentProcessor":
        """
        Reset runtime state.

        Configuration survives reset.
        """

        self._enriched = 0
        self._skipped = 0
        self._errors.clear()

        return self

    # ==================================================================
    # Python Protocols
    # ==================================================================

    def __len__(
        self,
    ) -> int:
        """
        Return number of configured enrichment fields.
        """

        return len(
            self._fields
        )

    def __repr__(
        self,
    ) -> str:
        return (
            "EnrichmentProcessor("
            f"fields={len(self._fields)}, "
            f"rules={len(self._rules)}, "
            f"enriched={self._enriched}, "
            f"skipped={self._skipped}"
            ")"
        )
