"""
Metric Namespace
================

Namespace object used by the metric registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypeAlias

__all__ = [
    "DEFAULT_NAMESPACE",
    "DEFAULT_PARENT",
    "MetricSnapshot",
    "MetricNamespace",
]

# ==============================================================================
# Part 1. Imports & Constants
# ==============================================================================

DEFAULT_NAMESPACE: str = ""
DEFAULT_PARENT: str = ""

MetricSnapshot: TypeAlias = dict[str, Any]


# ==============================================================================
# Part 2. MetricNamespace
# ==============================================================================


@dataclass(slots=True)
class MetricNamespace:
    """
    Metric namespace.

    Example
    -------
    system.cpu
    system.memory
    runtime.scheduler
    """

    name: str = DEFAULT_NAMESPACE

    parent: str = DEFAULT_PARENT

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

        self.name = str(self.name).strip().lower()

        self.parent = str(self.parent).strip().lower()

        if self.parent.endswith("."):
            self.parent = self.parent[:-1]

        if self.name.startswith("."):
            self.name = self.name[1:]

        if not isinstance(self.state, dict):
            self.state = {}

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self) -> None:

        if not isinstance(self.name, str):
            raise TypeError("name must be str.")

        if not isinstance(self.parent, str):
            raise TypeError("parent must be str.")

        if not isinstance(self.state, dict):
            raise TypeError("state must be dict.")


# ==============================================================================
# Part 3. Properties
# ==============================================================================

    @property
    def fullname(self) -> str:

        if self.parent:
            return f"{self.parent}.{self.name}"

        return self.name

    @property
    def depth(self) -> int:

        if not self.fullname:
            return 0

        return len(self.fullname.split("."))

    @property
    def is_root(self) -> bool:

        return self.parent == ""

    @property
    def is_empty(self) -> bool:

        return self.name == ""

    @property
    def state_view(self) -> MetricSnapshot:

        return {
            "name": self.name,
            "parent": self.parent,
            "fullname": self.fullname,
            "depth": self.depth,
        }


# ==============================================================================
# Part 4. Operations
# ==============================================================================

    def rename(
        self,
        name: str,
    ) -> "MetricNamespace":

        self.name = name

        self.normalize()

        self.validate()

        return self

    def reparent(
        self,
        parent: str,
    ) -> "MetricNamespace":

        self.parent = parent

        self.normalize()

        self.validate()

        return self

    def clear(self) -> "MetricNamespace":

        self.name = DEFAULT_NAMESPACE
        self.parent = DEFAULT_PARENT
        self.state.clear()

        return self

    def normalize(self) -> "MetricNamespace":

        self._normalize()

        return self


# ==============================================================================
# Part 5. Serialization
# ==============================================================================

    def to_dict(self) -> MetricSnapshot:

        return {
            "name": self.name,
            "parent": self.parent,
            "state": dict(self.state),
        }

    @classmethod
    def from_dict(
        cls,
        data: MetricSnapshot,
    ) -> "MetricNamespace":

        return cls(
            name=data.get("name", DEFAULT_NAMESPACE),
            parent=data.get("parent", DEFAULT_PARENT),
            state=dict(data.get("state", {})),
        )

    def to_tuple(self) -> tuple[str, str]:

        return (
            self.name,
            self.parent,
        )

    @classmethod
    def from_tuple(
        cls,
        value: tuple[str, str],
    ) -> "MetricNamespace":

        return cls(
            name=value[0],
            parent=value[1],
        )

    def snapshot(self) -> MetricSnapshot:

        return self.to_dict()

    def restore(
        self,
        snapshot: MetricSnapshot,
    ) -> "MetricNamespace":

        self.name = snapshot.get(
            "name",
            DEFAULT_NAMESPACE,
        )

        self.parent = snapshot.get(
            "parent",
            DEFAULT_PARENT,
        )

        self.state = dict(
            snapshot.get(
                "state",
                {},
            )
        )

        self.normalize()

        self.validate()

        return self

# ==============================================================================
# Part 6. Validation
# ==============================================================================

    @staticmethod
    def validate_name(name: Any) -> bool:
        """
        Validate namespace name.
        """
        return isinstance(name, str)

    @staticmethod
    def validate_parent(parent: Any) -> bool:
        """
        Validate parent namespace.
        """
        return parent is None or isinstance(parent, str)

    @classmethod
    def validate_namespace(cls, namespace: Any) -> bool:
        """
        Validate MetricNamespace instance.
        """
        return (
            isinstance(namespace, cls)
            and cls.validate_name(namespace.name)
            and cls.validate_parent(namespace.parent)
        )

    def validate(self) -> bool:
        """
        Validate current instance.
        """
        self._validate()
        return self.validate_namespace(self)


# ==============================================================================
# Part 7. Utilities
# ==============================================================================

    def clone(self) -> "MetricNamespace":
        """
        Deep clone.
        """
        return MetricNamespace(
            name=self.name,
            parent=self.parent,
        )

    copy = clone

    def merge(
        self,
        *,
        name: str | None = None,
        parent: str | None = None,
    ) -> "MetricNamespace":
        """
        Return merged copy.
        """
        return MetricNamespace(
            name=self.name if name is None else name,
            parent=self.parent if parent is None else parent,
        )

    def update(
        self,
        *,
        name: str | None = None,
        parent: str | None = None,
    ) -> "MetricNamespace":
        """
        Update namespace in-place.
        """
        if name is not None:
            self.name = name

        if parent is not None:
            self.parent = parent

        self.normalize()
        self.validate()

        return self

    def clear(self) -> "MetricNamespace":
        """
        Reset namespace.
        """
        self.name = ""
        self.parent = None
        return self


# ==============================================================================
# Part 8. Protocols
# ==============================================================================

    def __hash__(self) -> int:
        return hash(
            (
                self.name,
                self.parent,
            )
        )

    def __eq__(self, other: object) -> bool:

        if not isinstance(other, MetricNamespace):
            return NotImplemented

        return (
            self.name == other.name
            and self.parent == other.parent
        )

    def __lt__(self, other: object) -> bool:

        if not isinstance(other, MetricNamespace):
            return NotImplemented

        return (
            self.fullname,
            self.depth,
        ) < (
            other.fullname,
            other.depth,
        )

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"parent={self.parent!r})"
        )

    def __str__(self) -> str:

        return self.fullname

    def __bool__(self) -> bool:

        return bool(self.name)


# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================

    def summary(self) -> MetricSnapshot:

        return {
            "name": self.name,
            "parent": self.parent,
            "fullname": self.fullname,
            "depth": self.depth,
        }

    def diagnostics(self) -> MetricSnapshot:
        """
        Diagnostic information.
        """
        return {
            "valid": self.validate(),
            **self.summary(),
        }

    def namespace_report(self) -> MetricSnapshot:

        return {
            "summary": self.summary(),
            "diagnostics": self.diagnostics(),
        }

    def overall_status(self) -> bool:
        """
        Overall namespace health.
        """
        return self.validate()


# ==============================================================================
# Part 10. Public API
# ==============================================================================

__all__ = [
    "DEFAULT_NAMESPACE",
    "MetricSnapshot",
    "MetricNamespace",
]        