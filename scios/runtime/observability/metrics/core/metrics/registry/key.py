"""
Metric Registry Key
===================

Immutable metric identifier used throughout the metrics registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Mapping, TypeAlias

# ==============================================================================
# Part 1. Imports & Constants
# ==============================================================================

__all__ = [
    "DEFAULT_NAMESPACE",
    "SEPARATOR",
    "MetricLabels",
    "MetricSnapshot",
    "MetricKey",
]

DEFAULT_NAMESPACE: str = ""
SEPARATOR: str = "."

MetricLabels: TypeAlias = dict[str, str]
MetricSnapshot: TypeAlias = dict[str, Any]


# ==============================================================================
# Part 2. MetricKey
# ==============================================================================

@dataclass(slots=True)
class MetricKey:
    """
    Immutable metric registry key.
    """

    SEPARATOR: ClassVar[str] = SEPARATOR

    name: str = ""
    namespace: str = DEFAULT_NAMESPACE
    labels: MetricLabels = field(default_factory=dict)

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

        self.name = str(self.name).strip().lower()

        self.namespace = str(self.namespace).strip().lower()

        self.labels = {
            str(k).strip().lower(): str(v).strip()
            for k, v in sorted(dict(self.labels).items())
        }

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


# ==============================================================================
# Part 3. Properties
# ==============================================================================

    @property
    def fullname(self) -> str:
        """
        Fully-qualified metric name.
        """

        if self.namespace:
            return f"{self.namespace}{self.SEPARATOR}{self.name}"

        return self.name

    @property
    def state(self) -> MetricSnapshot:
        """
        Dynamic key state.
        """

        return {
            "name": self.name,
            "namespace": self.namespace,
            "labels": dict(self.labels),
        }


# ==============================================================================
# Part 4. Comparison
# ==============================================================================

    def equals(
        self,
        other: object,
    ) -> bool:

        return isinstance(other, MetricKey) and self == other

    def ordering(self) -> tuple:

        return (
            self.namespace,
            self.name,
            tuple(sorted(self.labels.items())),
        )

    def matching(
        self,
        other: "MetricKey",
    ) -> bool:

        return (
            self.name == other.name
            and self.namespace == other.namespace
            and self.labels == other.labels
        )

    def compatibility(
        self,
        other: "MetricKey",
    ) -> bool:

        return (
            self.name == other.name
            and self.namespace == other.namespace
        )


# ==============================================================================
# Part 5. Serialization
# ==============================================================================

    def to_dict(self) -> MetricSnapshot:

        return {
            "name": self.name,
            "namespace": self.namespace,
            "labels": dict(self.labels),
        }

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "MetricKey":

        return cls(
            name=data.get("name", ""),
            namespace=data.get(
                "namespace",
                DEFAULT_NAMESPACE,
            ),
            labels=dict(data.get("labels", {})),
        )

    def to_tuple(self) -> tuple[str, str, MetricLabels]:

        return (
            self.name,
            self.namespace,
            dict(self.labels),
        )

    @classmethod
    def from_tuple(
        cls,
        value: tuple,
    ) -> "MetricKey":

        if len(value) == 3:

            name, namespace, labels = value

        elif len(value) == 4:

            name, namespace, labels, _ = value

        else:

            raise ValueError(
                "MetricKey tuple must contain 3 or 4 items."
            )

        return cls(
            name=name,
            namespace=namespace,
            labels=dict(labels),
        )

    def snapshot(self) -> MetricSnapshot:

        return self.to_dict()

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "MetricKey":

        self.name = str(
            snapshot.get("name", "")
        ).strip().lower()

        self.namespace = str(
            snapshot.get(
                "namespace",
                DEFAULT_NAMESPACE,
            )
        ).strip().lower()

        self.labels = {
            str(k).strip().lower(): str(v).strip()
            for k, v in dict(
                snapshot.get("labels", {})
            ).items()
        }

        return self

# ==============================================================================
# Part 6. Validation
# ==============================================================================

    @staticmethod
    def validate_name(name: str) -> bool:
        """
        Validate a metric name.
        """
        return (
            isinstance(name, str)
            and bool(name.strip())
        )

    @staticmethod
    def validate_namespace(namespace: str) -> bool:
        """
        Validate a namespace.
        """
        return (
            isinstance(namespace, str)
            and bool(namespace.strip())
        )

    @staticmethod
    def validate_labels(labels: MetricLabels) -> bool:
        """
        Validate metric labels.
        """
        if not isinstance(labels, dict):
            return False

        return all(
            isinstance(k, str)
            and isinstance(v, str)
            for k, v in labels.items()
        )

    def validate_key(self) -> bool:
        """
        Validate the complete key.
        """
        return (
            self.validate_name(self.name)
            and self.validate_namespace(self.namespace)
            and self.validate_labels(self.labels)
        )

    def validate(self) -> bool:
        if not self.validate_name(self.name):
            raise ValueError("Invalid metric name.")

        if not self.validate_namespace(self.namespace):
            raise ValueError("Invalid metric namespace.")

        if not self.validate_labels(self.labels):
            raise ValueError("Invalid metric labels.")

        return True


# ==============================================================================
# Part 7. Utilities
# ==============================================================================

    def clone(self) -> "MetricKey":
        """
        Return a deep copy of this metric key.
        """
        return MetricKey(
            name=self.name,
            namespace=self.namespace,
            labels=dict(self.labels),
        )

    def copy(self) -> "MetricKey":
        """
        Alias of clone().
        """
        return self.clone()

    def merge(
        self,
        *,
        name: str | None = None,
        namespace: str | None = None,
        labels: MetricLabels | None = None,
    ) -> "MetricKey":
        """
        Return a new MetricKey with merged values.
        """
        merged_labels = dict(self.labels)

        if labels is not None:
            merged_labels.update(labels)

        return MetricKey(
            name=self.name if name is None else name,
            namespace=(
                self.namespace
                if namespace is None
                else namespace
            ),
            labels=merged_labels,
        )

    def update(
        self,
        *,
        name: str | None = None,
        namespace: str | None = None,
        labels: MetricLabels | None = None,
    ) -> "MetricKey":
        """
        Update this MetricKey in-place.
        """
        if name is not None:
            self.name = name

        if namespace is not None:
            self.namespace = namespace

        if labels is not None:
            self.labels = dict(labels)

        self.normalize()
        self.validate()

        return self

    def clear(self) -> "MetricKey":
        """
        Reset this MetricKey to its default state.
        """
        self.name = ""
        self.namespace = ""
        self.labels.clear()

        return self

    def normalize(self) -> "MetricKey":
        """
        Normalize all key components.
        """
        self._normalize()
        return self


# ==============================================================================
# Part 8. Protocols
# ==============================================================================

    def __hash__(self) -> int:
        """
        Stable hash based on the immutable identity of the key.
        """
        return hash(self.ordering())

    def __eq__(self, other: object) -> bool:
        """
        Structural equality.
        """
        if not isinstance(other, MetricKey):
            return NotImplemented

        return self.ordering() == other.ordering()

    def __lt__(self, other: object) -> bool:
        """
        Lexicographical ordering.
        """
        if not isinstance(other, MetricKey):
            return NotImplemented

        return self.ordering() < other.ordering()

    def __repr__(self) -> str:
        """
        Developer representation.
        """
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"namespace={self.namespace!r}, "
            f"labels={self.labels!r})"
        )

    def __str__(self) -> str:
        """
        Human-readable representation.
        """
        return self.fullname

    def __bool__(self) -> bool:
        """
        A MetricKey is considered valid when it has a non-empty metric name.
        """
        return bool(self.name.strip())


# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================

    def summary(self) -> MetricSnapshot:
        """
        Compact summary.
        """
        return {
            "name": self.name,
            "namespace": self.namespace,
            "fullname": self.fullname,
            "labels": len(self.labels),
        }

    def diagnostics(self) -> MetricSnapshot:
        """
        Validation diagnostics.
        """
        return {
            "valid": self.validate_key(),
            "name": self.validate_name(self.name),
            "namespace": self.validate_namespace(
                self.namespace
            ),
            "labels": self.validate_labels(
                self.labels
            ),
        }

    def key_report(self) -> MetricSnapshot:
        """
        Complete report.
        """
        return {
            "summary": self.summary(),
            "diagnostics": self.diagnostics(),
            "snapshot": self.snapshot(),
        }

    def overall_status(self) -> bool:
        """
        Overall health.
        """
        return self.validate_key()


# ==============================================================================
# Part 10. Public API
# ==============================================================================

__all__ = [
    "DEFAULT_NAMESPACE",
    "DEFAULT_STATE",
    "MetricLabels",
    "MetricSnapshot",
    "MetricKey",
]