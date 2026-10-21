"""
SciOS Runtime Metrics Filter Processor
======================================

Metric filtering processor.

SciOS-NG v0.2
"""

from __future__ import annotations

from typing import Any, Callable

from .processor import MetricProcessor


__all__ = [
    "FilterProcessor",
]


class FilterProcessor(MetricProcessor):
    """
    Runtime Metric Filter Processor.

    Responsibilities
    ----------------
    - Accept or reject metrics.
    - Support callable predicates.
    - Support multiple filter rules.
    - Track accepted and rejected metrics.
    - Allow dynamic rule management.
    - Provide runtime statistics and reset.
    """

    def __init__(
        self,
        predicate: Callable[[Any], bool] | None = None,
        name: str = "FilterProcessor",
        description: str = "",
    ) -> None:
        super().__init__(
            name=name,
            description=description,
        )

        self._rules: list[Callable[[Any], bool]] = []

        self._accepted = 0
        self._rejected = 0
        self._total = 0

        if predicate is not None:
            self.add_rule(predicate)

    # ==============================================================
    # Processing
    # ==============================================================

    def transform(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any | None:
        """
        Apply all filter rules.

        Returns
        -------
        metric | None
            The original metric when accepted, otherwise ``None``.

        Notes
        -----
        All configured rules must accept the metric.
        An empty rule set accepts every metric.
        """

        self._total += 1

        if self.accepts(metric):
            self._accepted += 1
            return metric

        self._rejected += 1
        return None

    # ==============================================================
    # Filtering
    # ==============================================================

    def accepts(
        self,
        metric: Any,
    ) -> bool:
        """
        Determine whether a metric passes all filter rules.
        """

        for rule in self._rules:
            try:
                if not bool(rule(metric)):
                    return False
            except Exception:
                return False

        return True

    # ==============================================================
    # Rule Management
    # ==============================================================

    def add_rule(
        self,
        rule: Callable[[Any], bool],
    ) -> FilterProcessor:
        """
        Add a filter rule.
        """

        if not callable(rule):
            raise TypeError(
                "Filter rule must be callable"
            )

        self._rules.append(rule)

        return self

    def remove_rule(
        self,
        rule: Callable[[Any], bool],
    ) -> FilterProcessor:
        """
        Remove a filter rule if present.
        """

        if rule in self._rules:
            self._rules.remove(rule)

        return self

    def clear_rules(
        self,
    ) -> FilterProcessor:
        """
        Remove all filter rules.
        """

        self._rules.clear()

        return self

    def rules(
        self,
    ) -> list[Callable[[Any], bool]]:
        """
        Return a copy of configured rules.
        """

        return list(self._rules)

    # ==============================================================
    # Built-in Filters
    # ==============================================================

    def require_field(
        self,
        field: str,
    ) -> FilterProcessor:
        """
        Require a field to exist on dictionary metrics.
        """

        if not isinstance(field, str):
            raise TypeError(
                "field must be a string"
            )

        def rule(metric: Any) -> bool:
            return (
                isinstance(metric, dict)
                and field in metric
            )

        return self.add_rule(rule)

    def field_equals(
        self,
        field: str,
        expected: Any,
    ) -> FilterProcessor:
        """
        Require a dictionary field to equal a value.
        """

        if not isinstance(field, str):
            raise TypeError(
                "field must be a string"
            )

        def rule(metric: Any) -> bool:
            return (
                isinstance(metric, dict)
                and metric.get(field) == expected
            )

        return self.add_rule(rule)

    def field_in(
        self,
        field: str,
        values: Any,
    ) -> FilterProcessor:
        """
        Require a dictionary field to belong to ``values``.
        """

        if not isinstance(field, str):
            raise TypeError(
                "field must be a string"
            )

        allowed = set(values)

        def rule(metric: Any) -> bool:
            return (
                isinstance(metric, dict)
                and metric.get(field) in allowed
            )

        return self.add_rule(rule)

    # ==============================================================
    # Statistics
    # ==============================================================

    def statistics(
        self,
    ) -> dict[str, Any]:
        """
        Return processor statistics.
        """

        data = super().statistics()

        data.update(
            {
                "total": self._total,
                "accepted": self._accepted,
                "rejected": self._rejected,
                "rules": len(self._rules),
                "acceptance_rate": (
                    self._accepted / self._total
                    if self._total
                    else 0.0
                ),
                "rejection_rate": (
                    self._rejected / self._total
                    if self._total
                    else 0.0
                ),
            }
        )

        return data

    # ==============================================================
    # Reset
    # ==============================================================

    def reset(
        self,
    ) -> FilterProcessor:
        """
        Reset runtime statistics.

        Configured rules are preserved.
        """

        self._total = 0
        self._accepted = 0
        self._rejected = 0

        return self

    # ==============================================================
    # Python Protocols
    # ==============================================================

    def __len__(
        self,
    ) -> int:
        return len(self._rules)

    def __repr__(
        self,
    ) -> str:
        return (
            "FilterProcessor("
            f"rules={len(self._rules)}, "
            f"accepted={self._accepted}, "
            f"rejected={self._rejected}"
            ")"
        )