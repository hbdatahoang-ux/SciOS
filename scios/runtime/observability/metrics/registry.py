"""
SciOS-NG Metrics Registry
=========================

Central registry for runtime metrics.

Responsibilities
-----------------
- Store metric instances.
- Identify metrics by name + label set.
- Prevent duplicate metric identities.
- Provide lookup and removal.
- Provide snapshots.
- Restore metric state.
- Reset or clear metrics.
- Support safe concurrent access.
- Preserve convenient name-based lookup.

Metric identity
---------------
A metric is uniquely identified by:

    metric.name + metric.labels

Therefore these are distinct metrics::

    requests{method="GET"}
    requests{method="POST"}

while these are duplicates::

    requests{method="GET"}
    requests{method="GET"}

Python 3.11+
"""

from __future__ import annotations

from copy import deepcopy
from threading import RLock
from typing import Any, Iterator


__all__ = [
    "MetricRegistry",
    "Registry",
]


class MetricRegistry:
    """
    Thread-safe registry for Metric-like objects.

    The registry is intentionally independent from concrete
    Counter, Gauge, and Histogram implementations.

    Metric identity is based on metric name and labels.
    """

    def __init__(self) -> None:
        # Internal identity key:
        #
        #     (metric_name, canonical_label_tuple)
        #
        self._metrics: dict[
            tuple[str, tuple[tuple[str, Any], ...]],
            Any,
        ] = {}

        self._lock = RLock()

    # ==========================================================
    # Identity Helpers
    # ==========================================================

    @staticmethod
    def _freeze_value(value: Any) -> Any:
        """
        Convert a label value into a stable hashable representation.
        """

        if isinstance(value, dict):
            return tuple(
                sorted(
                    (
                        str(key),
                        MetricRegistry._freeze_value(item),
                    )
                    for key, item in value.items()
                )
            )

        if isinstance(value, (list, tuple)):
            return tuple(
                MetricRegistry._freeze_value(item)
                for item in value
            )

        if isinstance(value, set):
            return tuple(
                sorted(
                    (
                        MetricRegistry._freeze_value(item)
                        for item in value
                    ),
                    key=repr,
                )
            )

        try:
            hash(value)
        except TypeError:
            return repr(value)

        return value

    @classmethod
    def _label_items(
        cls,
        metric: Any,
    ) -> tuple[tuple[str, Any], ...]:
        """
        Return canonical metric label items.
        """

        labels = getattr(metric, "labels", None)

        if labels is None:
            return ()

        if hasattr(labels, "to_dict"):
            labels = labels.to_dict()

        elif hasattr(labels, "items"):
            labels = dict(labels)

        else:
            try:
                labels = dict(labels)
            except (TypeError, ValueError):
                return ()

        return tuple(
            sorted(
                (
                    str(key),
                    cls._freeze_value(value),
                )
                for key, value in labels.items()
            )
        )

    @classmethod
    def _identity(
        cls,
        metric: Any,
    ) -> tuple[str, tuple[tuple[str, Any], ...]]:
        """
        Build the canonical identity of a metric.
        """

        name = getattr(metric, "name", None)

        if not isinstance(name, str) or not name:
            raise TypeError(
                "metric must provide a non-empty string name"
            )

        return (
            name,
            cls._label_items(metric),
        )

    @classmethod
    def _identity_from_parts(
        cls,
        name: str,
        labels: Any = None,
    ) -> tuple[str, tuple[tuple[str, Any], ...]]:
        """
        Build an identity from a metric name and optional labels.
        """

        class _MetricIdentity:
            pass

        metric = _MetricIdentity()
        metric.name = name
        metric.labels = labels or {}

        return cls._identity(metric)

    # ==========================================================
    # Registration
    # ==========================================================

    def register(self, metric: Any) -> Any:
        """
        Register a metric.

        Metrics with the same name but different label sets are
        allowed.

        Raises
        ------
        TypeError
            If metric is None or has no usable name.
        ValueError
            If the exact metric identity is already registered.
        """

        if metric is None:
            raise TypeError(
                "metric cannot be None"
            )

        identity = self._identity(metric)

        with self._lock:
            if identity in self._metrics:
                name = identity[0]

                raise ValueError(
                    f"metric already registered: {name!r}"
                )

            self._metrics[identity] = metric

        return metric

    def add(self, metric: Any) -> Any:
        """Alias for :meth:`register`."""
        return self.register(metric)

    # ==========================================================
    # Replacement
    # ==========================================================

    def replace(self, metric: Any) -> Any:
        """
        Replace an existing metric with the same identity.

        Raises
        ------
        TypeError
            If metric is invalid.
        KeyError
            If the metric identity is not registered.
        """

        if metric is None:
            raise TypeError(
                "metric cannot be None"
            )

        identity = self._identity(metric)

        with self._lock:
            if identity not in self._metrics:
                raise KeyError(
                    f"metric is not registered: "
                    f"{identity[0]!r}"
                )

            self._metrics[identity] = metric

        return metric

    # ==========================================================
    # Lookup
    # ==========================================================

    def get(
        self,
        name: str,
        default: Any = None,
        **labels: Any,
    ) -> Any:
        """
        Return a metric.

        With labels, the exact metric identity is requested::

            registry.get(
                "requests",
                method="GET",
            )

        Without labels, the first registered metric with the
        requested name is returned. This preserves the convenient
        legacy name-based lookup API.
        """

        with self._lock:

            if labels:
                identity = self._identity_from_parts(
                    name,
                    labels,
                )

                return self._metrics.get(
                    identity,
                    default,
                )

            for (
                metric_name,
                _label_identity,
            ), metric in self._metrics.items():

                if metric_name == name:
                    return metric

            return default

    def exists(
        self,
        name: str,
        **labels: Any,
    ) -> bool:
        """
        Return whether a metric exists.

        Without labels, checks whether any metric with that name
        exists.

        With labels, checks the exact metric identity.
        """

        with self._lock:

            if labels:
                identity = self._identity_from_parts(
                    name,
                    labels,
                )

                return identity in self._metrics

            return any(
                metric_name == name
                for metric_name, _ in self._metrics
            )

    # ==========================================================
    # Removal
    # ==========================================================

    def remove(
        self,
        name: str,
        **labels: Any,
    ) -> Any | bool:
        """
        Remove a metric.

        Without labels, removes the first metric registered under
        the supplied name.

        With labels, removes the exact metric identity.
        """

        with self._lock:

            if labels:
                identity = self._identity_from_parts(
                    name,
                    labels,
                )

                return self._metrics.pop(
                    identity,
                    False,
                )

            for identity in tuple(self._metrics):

                if identity[0] == name:
                    return self._metrics.pop(
                        identity,
                        False,
                    )

            return False

    def unregister(
        self,
        name: str,
        **labels: Any,
    ) -> Any | bool:
        """Alias for :meth:`remove`."""
        return self.remove(
            name,
            **labels,
        )

    # ==========================================================
    # Collection
    # ==========================================================

    def all(self) -> dict[str, Any]:
        """
        Return metrics grouped by name.

        For a name with multiple label sets, the first registered
        metric is represented by the name key.

        Use :meth:`values` or :meth:`items` when all metric
        instances are required.
        """

        with self._lock:

            result: dict[str, Any] = {}

            for (
                name,
                _labels,
            ), metric in self._metrics.items():

                result.setdefault(
                    name,
                    metric,
                )

            return result

    def names(self) -> list[str]:
        """
        Return unique registered metric names.
        """

        with self._lock:

            result: list[str] = []

            for name, _labels in self._metrics:

                if name not in result:
                    result.append(name)

            return result

    def values(self) -> list[Any]:
        """Return all registered metric instances."""

        with self._lock:
            return list(
                self._metrics.values()
            )

    def items(self) -> list[tuple[str, Any]]:
        """
        Return metric name / instance pairs.

        When multiple label sets share the same name, each metric
        instance appears as a separate item.
        """

        with self._lock:
            return [
                (
                    identity[0],
                    metric,
                )
                for identity, metric
                in self._metrics.items()
            ]

    # ==========================================================
    # Protocols
    # ==========================================================

    def __len__(self) -> int:
        """
        Return the number of registered metric instances.
        """

        with self._lock:
            return len(self._metrics)

    def __contains__(
        self,
        name: object,
    ) -> bool:
        """
        Test whether any metric with the supplied name exists.
        """

        if not isinstance(name, str):
            return False

        return self.exists(name)

    def __getitem__(
        self,
        name: str,
    ) -> Any:
        """
        Return the first metric registered under a name.

        Exact label-aware lookup should use ``get(name, **labels)``.
        """

        metric = self.get(name)

        if metric is None:
            raise KeyError(name)

        return metric

    def __setitem__(
        self,
        name: str,
        metric: Any,
    ) -> None:
        """
        Register a metric under its own name.

        The supplied key must match ``metric.name``.
        """

        if metric is None:
            raise TypeError(
                "metric cannot be None"
            )

        metric_name = getattr(
            metric,
            "name",
            None,
        )

        if metric_name != name:
            raise ValueError(
                f"metric name {metric_name!r} "
                f"does not match key {name!r}"
            )

        self.register(metric)

    def __delitem__(
        self,
        name: str,
    ) -> None:
        if not self.remove(name):
            raise KeyError(name)

    def __iter__(
        self,
    ) -> Iterator[Any]:
        """
        Iterate over metric instances.

        This intentionally yields Metric objects rather than names::

            for metric in registry:
                print(metric.name)
        """

        with self._lock:
            return iter(
                tuple(
                    self._metrics.values()
                )
            )

    # ==========================================================
    # Snapshot
    # ==========================================================

    def snapshot(self) -> dict[str, Any]:
        """
        Return a detached snapshot of all metrics.

        A single metric keeps the historical::

            {
                "requests": {...}
            }

        representation.

        When multiple label sets share a name, snapshots are grouped
        under the metric name and represented as a list.
        """

        with self._lock:

            grouped: dict[
                str,
                list[Any],
            ] = {}

            for (
                name,
                _labels,
            ), metric in self._metrics.items():

                if hasattr(metric, "snapshot"):

                    state = metric.snapshot()

                elif hasattr(metric, "to_dict"):

                    state = metric.to_dict()

                else:

                    state = metric

                grouped.setdefault(
                    name,
                    [],
                ).append(
                    deepcopy(state)
                )

            result: dict[str, Any] = {}

            for name, states in grouped.items():

                if len(states) == 1:
                    result[name] = states[0]

                else:
                    result[name] = states

            return result

    def to_dict(self) -> dict[str, Any]:
        """Alias for :meth:`snapshot`."""
        return self.snapshot()

    # ==========================================================
    # Restore
    # ==========================================================

    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> None:
        """
        Restore registered metric state.

        Existing metric objects are reused whenever their identity
        can be matched.

        Snapshots containing multiple label variants under one name
        are matched using the snapshot's ``labels`` field.
        """

        if not isinstance(snapshot, dict):
            raise TypeError(
                "snapshot must be a dictionary"
            )

        with self._lock:

            for name, state in snapshot.items():

                states = (
                    state
                    if isinstance(state, list)
                    else [state]
                )

                for state_item in states:

                    if not isinstance(
                        state_item,
                        dict,
                    ):
                        continue

                    labels = state_item.get(
                        "labels",
                        {},
                    )

                    identity = self._identity_from_parts(
                        name,
                        labels,
                    )

                    metric = self._metrics.get(
                        identity
                    )

                    if metric is None:
                        continue

                    restore = getattr(
                        metric,
                        "restore",
                        None,
                    )

                    if callable(restore):
                        restore(
                            deepcopy(state_item)
                        )

    # ==========================================================
    # Reset
    # ==========================================================

    def reset(self) -> None:
        """Reset every registered metric."""

        with self._lock:

            for metric in self._metrics.values():

                reset = getattr(
                    metric,
                    "reset",
                    None,
                )

                if callable(reset):
                    reset()

    # ==========================================================
    # Clear
    # ==========================================================

    def clear(self) -> None:
        """Remove every registered metric."""

        with self._lock:
            self._metrics.clear()

    # ==========================================================
    # Validation
    # ==========================================================

    def is_valid(self) -> bool:
        """Return whether registry state is structurally valid."""

        try:

            with self._lock:

                identities = set()

                for identity, metric in self._metrics.items():

                    name, _labels = identity

                    if not isinstance(
                        name,
                        str,
                    ) or not name:
                        return False

                    if metric is None:
                        return False

                    metric_name = getattr(
                        metric,
                        "name",
                        None,
                    )

                    if metric_name != name:
                        return False

                    calculated = self._identity(metric)

                    if calculated != identity:
                        return False

                    if identity in identities:
                        return False

                    identities.add(identity)

                return True

        except Exception:
            return False

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self) -> str:
        return (
            "MetricRegistry("
            f"metrics={len(self)}"
            ")"
        )


Registry = MetricRegistry