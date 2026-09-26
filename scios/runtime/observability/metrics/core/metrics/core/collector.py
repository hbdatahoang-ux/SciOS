# ==========================================================
# Part 1. Imports
# ==========================================================

from __future__ import annotations

import copy as _copy
import json
from dataclasses import dataclass, field, replace as _replace
from typing import Any, TypeAlias

from .metric import Metric
from .metric_hooks import MetricHooks
from .registry import MetricRegistry


# ==========================================================
# Part 2. Constants & Type Aliases
# ==========================================================

DEFAULT_ENABLED: bool = True
DEFAULT_VERSION: str = "1.0"

MetricBuffer: TypeAlias = list[Metric]
MetricList: TypeAlias = list[Metric]
CollectorState: TypeAlias = dict[str, Any]


# ==========================================================
# Part 3. Dataclass / Core Container
# ==========================================================

@dataclass(slots=True)
class MetricCollector:
    """
    Runtime metric collector.

    Responsibilities
    ----------------
    • Collect metrics from a registry.
    • Execute lifecycle hooks.
    • Maintain an in-memory collection buffer.
    """

    registry: MetricRegistry = field(default_factory=MetricRegistry)
    hooks: MetricHooks = field(default_factory=MetricHooks)
    buffer: MetricBuffer = field(default_factory=list)

    enabled: bool = DEFAULT_ENABLED
    version: str = DEFAULT_VERSION

# ==========================================================
# Part 4. Validation
# ==========================================================

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> bool:
        """
        Validate collector state.

        Returns
        -------
        bool
            True if collector is valid.
        """

        if not isinstance(self.registry, MetricRegistry):
            raise TypeError(
                "registry must be a MetricRegistry"
            )

        if not isinstance(self.hooks, MetricHooks):
            raise TypeError(
                "hooks must be a MetricHooks"
            )

        if not isinstance(self.buffer, list):
            raise TypeError(
                "buffer must be a list"
            )

        #
        # Validate registry contents
        #
        if not isinstance(self.registry.metrics, dict):
            raise TypeError(
                "registry.metrics must be a dict"
            )

        for name, metric in self.registry.metrics.items():

            if not isinstance(metric, Metric):
                raise TypeError(
                    f"registry metric '{name}' must be Metric"
                )

            if not metric.is_valid():
                raise ValueError(
                    f"invalid registry metric: {name!r}"
                )

        #
        # Validate collector buffer
        #
        for metric in self.buffer:

            if not isinstance(metric, Metric):
                raise TypeError(
                    "buffer must contain Metric instances"
                )

            if not metric.is_valid():
                raise ValueError(
                    f"invalid buffered metric: {metric!r}"
                )

        if not isinstance(self.enabled, bool):
            raise TypeError(
                "enabled must be a bool"
            )

        if not isinstance(self.version, str):
            raise TypeError(
                "version must be a string"
            )

        if not self.registry.is_valid():
            raise ValueError(
                "registry is invalid"
            )

        if not self.hooks.is_valid():
            raise ValueError(
                "hooks are invalid"
            )

        return True

    def is_valid(self) -> bool:
        """
        Safe validation.
        """

        try:
            return self.validate()
        except Exception:
            return False


# ==========================================================
# Part 5. Collection API
# ==========================================================

    def collect(self) -> MetricList:
        """
        Collect every metric from the registry.
        """

        if not self.enabled:
            return []

        for callback in self.hooks.before_collect:
            callback()

        metrics = list(self.registry.values())

        self.buffer.extend(metrics)

        for callback in self.hooks.after_collect:
            callback()

        return metrics

    def collect_single(
        self,
        name: str,
    ) -> Metric | None:
        """
        Collect one metric.
        """

        metric = self.registry.get(name)

        if metric is None:
            return None

        self.buffer.append(metric)

        return metric

    def collect_multiple(
        self,
        names: list[str],
    ) -> MetricList:
        """
        Collect selected metrics.
        """

        metrics: MetricList = []

        for name in names:
            metric = self.registry.get(name)

            if metric is not None:
                metrics.append(metric)

        self.buffer.extend(metrics)

        return metrics

    def clear(self) -> None:
        """
        Clear collection buffer.
        """

        self.buffer.clear()


# ==========================================================
# Part 6. Registration API
# ==========================================================

    def register(
        self,
        metric: Metric,
    ) -> None:
        """
        Register metric.
        """

        self.registry.register(metric)

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove metric.
        """

        self.registry.unregister(name)

    def replace(
        self,
        metric: Metric,
    ) -> None:
        """
        Replace existing metric.
        """

        self.registry.replace(metric)

# ==========================================================
# Part 7. Lookup API
# ==========================================================

    def get(
        self,
        name: str,
        default: Metric | None = None,
    ) -> Metric | None:
        """
        Get metric by name.
        """
        metric = self.registry.get(name)
        return default if metric is None else metric

    def items(self):
        """
        Registry items.
        """
        return self.registry.items()

    def keys(self):
        """
        Registry keys.
        """
        return self.registry.keys()

    def values(self):
        """
        Registry values.
        """
        return self.registry.values()

    def metrics(self) -> MetricList:
        """
        Metrics list.
        """
        return list(self.registry.values())


# ==========================================================
# Part 8. Serialization
# ==========================================================

    def to_dict(self) -> CollectorState:
        """
        Serialize collector.
        """
        return {
            "registry": self.registry.to_dict(),
            "hooks": self.hooks.to_dict(),
            "buffer": [metric.to_dict() for metric in self.buffer],
            "enabled": self.enabled,
            "version": self.version,
        }

    @classmethod
    def from_dict(
        cls,
        data: CollectorState,
    ) -> "MetricCollector":
        """
        Deserialize collector.
        """
        collector = cls(
            registry=MetricRegistry.from_dict(
                data.get("registry", {}),
            ),
            enabled=data.get(
                "enabled",
                DEFAULT_ENABLED,
            ),
            version=data.get(
                "version",
                DEFAULT_VERSION,
            ),
        )

        # restore hooks
        collector.hooks = MetricHooks.from_dict(
            data.get("hooks", {}),
        )

        # restore buffer
        collector.buffer = [
            Metric.from_dict(item)
            for item in data.get("buffer", [])
        ]

        return collector

    def to_json(self) -> str:
        """
        JSON serialization.
        """
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
        )

    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "MetricCollector":
        """
        JSON deserialization.
        """
        return cls.from_dict(
            json.loads(payload),
        )

# ==========================================================
# Part 9. Copy API
# ==========================================================

    def copy(self) -> "MetricCollector":
        """
        Shallow copy.
        """
        return MetricCollector(
            registry=self.registry.copy(),
            hooks=self.hooks.copy(),
            buffer=list(self.buffer),
            enabled=self.enabled,
            version=self.version,
        )

    def clone(self) -> "MetricCollector":
        """
        Alias of copy().
        """
        return self.copy()

    def deepcopy(self) -> "MetricCollector":
        """
        Deep copy.
        """
        return _copy.deepcopy(self)

    def replace(
        self,
        **changes: Any,
    ) -> "MetricCollector":
        """
        Dataclass replace.
        """
        return _replace(self, **changes)


# ==========================================================
# Part 10. Comparison
# ==========================================================

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MetricCollector):
            return False

        return (
            self.registry == other.registry
            and self.buffer == other.buffer
            and self.enabled == other.enabled
            and self.version == other.version
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.registry,
                self.hooks,
                tuple(self.buffer),
                self.enabled,
                self.version,
            )
        )

# ==========================================================
# Part 11. Python Protocols
# ==========================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"size={len(self.registry)}, "
            f"enabled={self.enabled!r}, "
            f"version={self.version!r})"
        )

    def __str__(self) -> str:
        return self.__repr__()

    def __bool__(self) -> bool:
        """
        Collector is truthy when it contains registered metrics.
        """

        return len(self) > 0

    def __len__(self) -> int:
        return len(self.registry)

    def __iter__(self):
        return iter(self.registry.keys())

    def __contains__(
        self,
        key: object,
    ) -> bool:
        return key in self.registry

    def __getitem__(
        self,
        key: str,
    ) -> Metric:
        return self.registry[key]

    def __setitem__(
        self,
        key: str,
        value: Metric,
    ) -> None:
        if not isinstance(value, Metric):
            raise TypeError("value must be a Metric")

        if value.name != key:
            value = value.replace(name=key)

        self.registry[key] = value

    def __delitem__(
        self,
        key: str,
    ) -> None:
        del self.registry[key]


# ==========================================================
# Part 12. Pickle Support
# ==========================================================

    def __getstate__(self) -> dict[str, Any]:
        """
        Serialize collector.
        """
        return self.to_dict()

    def __setstate__(
        self,
        state: dict[str, Any],
    ) -> None:
        """
        Restore collector.
        """
        restored = self.from_dict(state)

        self.registry = restored.registry
        self.hooks = restored.hooks
        self.buffer = restored.buffer
        self.enabled = restored.enabled
        self.version = restored.version


# ==========================================================
# Part 13. Public API
# ==========================================================

__all__ = [
    "CollectorState",
    "MetricCollector",
]                    