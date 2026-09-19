"""
Metric Registry Filter
======================

Filtering utilities for MetricEntry collections.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, TypeAlias

from .entry import MetricEntry
from .key import MetricKey

__all__ = [
    "DEFAULT_METRIC",
    "DEFAULT_PREDICATE",
    "MetricPredicate",
    "MetricSnapshot",
    "MetricFilter",
]

# ==============================================================================
# Part 1. Imports & Constants
# ==============================================================================

DEFAULT_METRIC: str | None = None
DEFAULT_PREDICATE: Callable[[MetricEntry], bool] | None = None

MetricPredicate: TypeAlias = Callable[[MetricEntry], bool]
MetricSnapshot: TypeAlias = dict[str, Any]


# ==============================================================================
# Part 2. MetricFilter
# ==============================================================================


@dataclass(slots=True)
class MetricFilter:
    """
    Declarative filter for MetricEntry objects.
    """

    name: str = ""

    namespace: str = ""

    labels: dict[str, str] = field(default_factory=dict)

    metric: str | None = DEFAULT_METRIC

    predicate: MetricPredicate | None = DEFAULT_PREDICATE

    state: MetricSnapshot = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:

        self._normalize()

        self._validate()

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    def _normalize(self) -> None:

        self.name = self.name.strip().lower()

        self.namespace = self.namespace.strip().lower()

        self.labels = {
            str(k).strip(): str(v).strip()
            for k, v in self.labels.items()
        }

        if isinstance(self.metric, str):
            self.metric = self.metric.strip().lower()

        if not isinstance(self.state, dict):
            self.state = {}

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self) -> None:

        if not isinstance(self.name, str):
            raise TypeError("name must be a string.")

        if not isinstance(self.namespace, str):
            raise TypeError("namespace must be a string.")

        if not isinstance(self.labels, dict):
            raise TypeError("labels must be a mapping.")

        if self.metric is not None and not isinstance(
            self.metric,
            str,
        ):
            raise TypeError("metric must be a string or None.")

        if (
            self.predicate is not None
            and not callable(self.predicate)
        ):
            raise TypeError(
                "predicate must be callable or None."
            )

        if not isinstance(self.state, dict):
            raise TypeError("state must be a mapping.")


# ==============================================================================
# Part 3. Properties
# ==============================================================================

    @property
    def has_name(self) -> bool:

        return bool(self.name)

    @property
    def has_namespace(self) -> bool:

        return bool(self.namespace)

    @property
    def has_labels(self) -> bool:

        return bool(self.labels)

    @property
    def has_metric(self) -> bool:

        return self.metric is not None

    @property
    def has_predicate(self) -> bool:

        return self.predicate is not None

    @property
    def is_empty(self) -> bool:

        return not (
            self.has_name
            or self.has_namespace
            or self.has_labels
            or self.has_metric
            or self.has_predicate
        )


# ==============================================================================
# Part 4. Matching
# ==============================================================================

    def match_name(
        self,
        key: MetricKey,
    ) -> bool:

        return (
            not self.name
            or key.name == self.name
        )

    def match_namespace(
        self,
        key: MetricKey,
    ) -> bool:

        return (
            not self.namespace
            or key.namespace == self.namespace
        )

    def match_labels(
        self,
        key: MetricKey,
    ) -> bool:

        return all(
            key.labels.get(k) == v
            for k, v in self.labels.items()
        )

    def match_metric(
        self,
        entry: MetricEntry,
    ) -> bool:

        return (
            self.metric is None
            or entry.metric == self.metric
        )

    def match(
        self,
        entry: MetricEntry,
    ) -> bool:
        """
        Match a MetricEntry.
        """

        if not self.match_name(entry.key):
            return False

        if not self.match_namespace(entry.key):
            return False

        if not self.match_labels(entry.key):
            return False

        if not self.match_metric(entry):
            return False

        if (
            self.predicate is not None
            and not self.predicate(entry)
        ):
            return False

        return True

    def filter(
        self,
        entries: list[MetricEntry],
    ) -> list[MetricEntry]:
        """
        Filter MetricEntry collection.
        """

        return [
            entry
            for entry in entries
            if self.match(entry)
        ]


# ==============================================================================
# Part 5. Serialization
# ==============================================================================

    def to_dict(self) -> MetricSnapshot:

        return {
            "name": self.name,
            "namespace": self.namespace,
            "labels": dict(self.labels),
            "metric": self.metric,
            "state": dict(self.state),
        }

    @classmethod
    def from_dict(
        cls,
        data: MetricSnapshot,
    ) -> "MetricFilter":

        return cls(
            name=data.get("name", ""),
            namespace=data.get(
                "namespace",
                "",
            ),
            labels=dict(
                data.get(
                    "labels",
                    {},
                )
            ),
            metric=data.get("metric"),
            state=dict(
                data.get(
                    "state",
                    {},
                )
            ),
        )

    def to_tuple(self) -> tuple:

        return (
            self.name,
            self.namespace,
            tuple(
                sorted(
                    self.labels.items(),
                )
            ),
            self.metric,
        )

    @classmethod
    def from_tuple(
        cls,
        value: tuple,
    ) -> "MetricFilter":

        name, namespace, labels, metric = value

        return cls(
            name=name,
            namespace=namespace,
            labels=dict(labels),
            metric=metric,
        )

    def snapshot(self) -> MetricSnapshot:

        return self.to_dict()

    def restore(
        self,
        snapshot: MetricSnapshot,
    ) -> "MetricFilter":

        restored = self.from_dict(snapshot)

        self.name = restored.name
        self.namespace = restored.namespace
        self.labels = restored.labels
        self.metric = restored.metric
        self.state = restored.state

        return self

# ==============================================================================
# Part 6. Validation
# ==============================================================================

    @staticmethod
    def validate_name(name: Any) -> bool:
        """
        Validate filter name.
        """
        return isinstance(name, str)

    @staticmethod
    def validate_namespace(namespace: Any) -> bool:
        """
        Validate namespace.
        """
        return isinstance(namespace, str)

    @staticmethod
    def validate_labels(labels: Any) -> bool:
        """
        Validate label mapping.
        """
        return isinstance(labels, dict)

    @staticmethod
    def validate_metric(metric: Any) -> bool:
        """
        Validate metric selector.
        """
        return metric is None or isinstance(metric, str)

    @classmethod
    def validate_filter(cls, value: Any) -> bool:
        """
        Validate MetricFilter instance.
        """
        return (
            isinstance(value, cls)
            and cls.validate_name(value.name)
            and cls.validate_namespace(value.namespace)
            and cls.validate_labels(value.labels)
            and cls.validate_metric(value.metric)
            and (
                value.predicate is None
                or callable(value.predicate)
            )
        )

    def validate(self) -> bool:
        """
        Validate current instance.
        """
        self._validate()
        return self.validate_filter(self)


# ==============================================================================
# Part 7. Utilities
# ==============================================================================

    def clone(self) -> "MetricFilter":
        """
        Deep clone.
        """
        return MetricFilter(
            name=self.name,
            namespace=self.namespace,
            labels=dict(self.labels),
            metric=self.metric,
            predicate=self.predicate,
            state=dict(self.state),
        )

    copy = clone

    def merge(
        self,
        *,
        name: str | None = None,
        namespace: str | None = None,
        labels: dict[str, str] | None = None,
        metric: str | None = None,
        predicate: MetricPredicate | None = None,
        state: MetricSnapshot | None = None,
    ) -> "MetricFilter":
        """
        Return merged copy.
        """
        merged_labels = dict(self.labels)

        if labels:
            merged_labels.update(labels)

        merged_state = dict(self.state)

        if state:
            merged_state.update(state)

        return MetricFilter(
            name=self.name if name is None else name,
            namespace=(
                self.namespace
                if namespace is None
                else namespace
            ),
            labels=merged_labels,
            metric=self.metric if metric is None else metric,
            predicate=(
                self.predicate
                if predicate is None
                else predicate
            ),
            state=merged_state,
        )

    def update(
        self,
        *,
        name: str | None = None,
        namespace: str | None = None,
        labels: dict[str, str] | None = None,
        metric: str | None = None,
        predicate: MetricPredicate | None = None,
        state: MetricSnapshot | None = None,
    ) -> "MetricFilter":
        """
        Update in-place.
        """
        if name is not None:
            self.name = name

        if namespace is not None:
            self.namespace = namespace

        if labels is not None:
            self.labels = dict(labels)

        if metric is not None:
            self.metric = metric

        if predicate is not None:
            self.predicate = predicate

        if state is not None:
            self.state = dict(state)

        self.normalize()
        self.validate()

        return self

    def clear(self) -> "MetricFilter":
        """
        Reset to defaults.
        """
        self.name = ""
        self.namespace = ""
        self.labels.clear()
        self.metric = DEFAULT_METRIC
        self.predicate = DEFAULT_PREDICATE
        self.state.clear()

        return self

    def normalize(self) -> "MetricFilter":
        """
        Public normalization.
        """
        self._normalize()
        return self


# ==============================================================================
# Part 8. Protocols
# ==============================================================================

    def __hash__(self) -> int:

        return hash(
            (
                self.name,
                self.namespace,
                tuple(sorted(self.labels.items())),
                self.metric,
            )
        )

    def __eq__(self, other: object) -> bool:

        if not isinstance(other, MetricFilter):
            return NotImplemented

        return (
            self.name == other.name
            and self.namespace == other.namespace
            and self.labels == other.labels
            and self.metric == other.metric
        )

    def __lt__(self, other: object) -> bool:

        if not isinstance(other, MetricFilter):
            return NotImplemented

        return (
            self.namespace,
            self.name,
            tuple(sorted(self.labels.items())),
            self.metric or "",
        ) < (
            other.namespace,
            other.name,
            tuple(sorted(other.labels.items())),
            other.metric or "",
        )

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"namespace={self.namespace!r}, "
            f"labels={self.labels!r}, "
            f"metric={self.metric!r})"
        )

    def __str__(self) -> str:

        if self.namespace:
            return f"{self.namespace}.{self.name}"

        return self.name

    def __bool__(self) -> bool:

        return not self.is_empty


# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================

    def summary(self) -> MetricSnapshot:

        return {
            "name": self.name,
            "namespace": self.namespace,
            "labels": dict(self.labels),
            "metric": self.metric,
            "has_predicate": self.has_predicate,
        }

    def diagnostics(self) -> MetricSnapshot:
        """
        Diagnostic information.
        """
        return {
            "valid": self.validate(),
            "empty": self.is_empty,
            **self.summary(),
        }

    def filter_report(self) -> MetricSnapshot:

        return {
            "summary": self.summary(),
            "diagnostics": self.diagnostics(),
        }

    def overall_status(self) -> bool:
        """
        Overall health.
        """
        return self.validate()


# ==============================================================================
# Part 10. Public API
# ==============================================================================

__all__ = [
    "DEFAULT_METRIC",
    "DEFAULT_PREDICATE",
    "MetricPredicate",
    "MetricSnapshot",
    "MetricFilter",
]        