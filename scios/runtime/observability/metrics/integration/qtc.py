"""
SciOS-NG
runtime/observability/metrics/integration/qtc.py

Part 1. Foundation
"""

from __future__ import annotations

# =============================================================================
# Imports
# =============================================================================

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Mapping
from typing import MutableMapping
from typing import Optional
from typing import TypeAlias
from uuid import uuid4

import json
import time


# =============================================================================
# Constants
# =============================================================================

DEFAULT_NAME = "MetricQTCIntegration"
DEFAULT_VERSION = "1.0.0"

DEFAULT_CONFIGURATION: Dict[str, Any] = {
    "tensor_metrics": True,
    "operator_metrics": True,
    "kernel_metrics": True,
    "energy_metrics": True,
    "entropy_metrics": True,
    "curvature_metrics": True,
    "constraint_metrics": True,
    "observer_metrics": True,
    "sampling_interval": 0.01,
    "auto_collect": False,
}

DEFAULT_STATISTICS: Dict[str, Any] = {
    "metrics": 0,
    "components": 0,
    "samples": 0,
    "errors": 0,
    "uptime": 0.0,
    "latency": 0.0,
}


# =============================================================================
# Type Aliases
# =============================================================================

Metric: TypeAlias = Callable[..., Any]
MetricRegistry: TypeAlias = Dict[str, Metric]

QTCRegistry: TypeAlias = Dict[str, Any]

Metadata: TypeAlias = Dict[str, Any]

Statistics: TypeAlias = Dict[str, Any]

HookRegistry: TypeAlias = Dict[str, List[Callable[..., Any]]]


# =============================================================================
# MetricQTCIntegration
# =============================================================================


class MetricQTCIntegration:
    """
    Observability bridge between the QTC runtime and the
    SciOS-NG metrics infrastructure.

    This class provides the common runtime state,
    metric registry and component registry used by
    later parts of the implementation.
    """

    VERSION = DEFAULT_VERSION

    # -------------------------------------------------------------------------
    # Constructor
    # -------------------------------------------------------------------------

    def __init__(
        self,
        name: str = DEFAULT_NAME,
        configuration: Optional[Mapping[str, Any]] = None,
    ) -> None:

        now = datetime.now(timezone.utc)

        # -----------------------------------------------------------------
        # Identity
        # -----------------------------------------------------------------

        self.id: str = str(uuid4())

        self.name: str = name

        self.version: str = self.VERSION

        self.created_at: datetime = now

        self.updated_at: datetime = now

        # -----------------------------------------------------------------
        # Runtime State
        # -----------------------------------------------------------------

        self.enabled: bool = True

        self.disabled: bool = False

        self.frozen: bool = False

        self.closed: bool = False

        self.running: bool = False

        self.active: bool = False

        # -----------------------------------------------------------------
        # Configuration
        # -----------------------------------------------------------------

        self.configuration: Dict[str, Any] = deepcopy(
            DEFAULT_CONFIGURATION
        )

        if configuration:
            self.configuration.update(configuration)

        # -----------------------------------------------------------------
        # Metric Registry
        # -----------------------------------------------------------------

        self.registry: MetricRegistry = {}

        # -----------------------------------------------------------------
        # QTC Registry
        # -----------------------------------------------------------------

        self.qtc_registry: QTCRegistry = {}

        # -----------------------------------------------------------------
        # Metadata
        # -----------------------------------------------------------------

        self.metadata: Metadata = {
            "component": "qtc",
            "version": self.version,
            "created_at": self.created_at.isoformat(),
        }

        # -----------------------------------------------------------------
        # Statistics
        # -----------------------------------------------------------------

        self.statistics: Statistics = deepcopy(
            DEFAULT_STATISTICS
        )

        # -----------------------------------------------------------------
        # Internal Runtime
        # -----------------------------------------------------------------

        self._metrics: Dict[str, Any] = {}

        self._components: Dict[str, Any] = {}

        self._results: Dict[str, Any] = {}

        self._hooks: HookRegistry = {}

        self._current_metric: Optional[Any] = None

        self._last_metric: Optional[Any] = None

        self._last_snapshot: Optional[Dict[str, Any]] = None

        self._start_time: Optional[float] = None

    # -------------------------------------------------------------------------
    # End Foundation
    # -------------------------------------------------------------------------
# =============================================================================
# Part 2. Metric API
# =============================================================================

    # -------------------------------------------------------------------------
    # Metric Collection API
    # -------------------------------------------------------------------------

    def collect(
        self,
        name: str,
        *args,
        **kwargs,
    ) -> Any:
        """
        Collect a metric by name.

        Parameters
        ----------
        name:
            Registered metric name.

        Returns
        -------
        Any
            Metric result.
        """

        if self.closed:
            raise RuntimeError("QTC integration is closed.")

        if not self.enabled:
            raise RuntimeError("QTC integration is disabled.")

        if self.frozen:
            raise RuntimeError("QTC integration is frozen.")

        metric = self.registry.get(name)

        if metric is None:
            raise KeyError(f"Unknown metric: {name}")

        self.running = True
        self.active = True
        self._start_time = time.perf_counter()

        self.before_collect(name)

        try:

            if callable(metric):
                result = metric(*args, **kwargs)
            else:
                result = metric

            self._metrics[name] = result
            self._current_metric = result
            self._last_metric = result

            self.statistics["metrics"] += 1
            self.statistics["samples"] += 1

            return result

        except Exception:

            self.statistics["errors"] += 1
            raise

        finally:

            elapsed = time.perf_counter() - self._start_time

            self.statistics["latency"] = elapsed
            self.statistics["uptime"] += elapsed

            self.running = False
            self.active = False

            self.updated_at = datetime.now(timezone.utc)

            self.after_collect(name)

    # -------------------------------------------------------------------------

    def collect_tensor(self, *args, **kwargs) -> Any:
        """
        Collect tensor metrics.
        """

        return self.collect("tensor", *args, **kwargs)

    # -------------------------------------------------------------------------

    def collect_operator(self, *args, **kwargs) -> Any:
        """
        Collect operator metrics.
        """

        return self.collect("operator", *args, **kwargs)

    # -------------------------------------------------------------------------

    def collect_kernel(self, *args, **kwargs) -> Any:
        """
        Collect kernel metrics.
        """

        return self.collect("kernel", *args, **kwargs)

    # -------------------------------------------------------------------------

    def collect_energy(self, *args, **kwargs) -> Any:
        """
        Collect energy metrics.
        """

        return self.collect("energy", *args, **kwargs)

    # -------------------------------------------------------------------------

    def collect_entropy(self, *args, **kwargs) -> Any:
        """
        Collect entropy metrics.
        """

        return self.collect("entropy", *args, **kwargs)

    # -------------------------------------------------------------------------

    def collect_curvature(self, *args, **kwargs) -> Any:
        """
        Collect curvature metrics.
        """

        return self.collect("curvature", *args, **kwargs)

    # -------------------------------------------------------------------------

    def collect_constraint(self, *args, **kwargs) -> Any:
        """
        Collect constraint metrics.
        """

        return self.collect("constraint", *args, **kwargs)

    # -------------------------------------------------------------------------

    def collect_observer(self, *args, **kwargs) -> Any:
        """
        Collect observer metrics.
        """

        return self.collect("observer", *args, **kwargs)

    # -------------------------------------------------------------------------

    def collect_all(self) -> Dict[str, Any]:
        """
        Collect all enabled metrics.

        Returns
        -------
        Dict[str, Any]
            Mapping of metric names to collected values.
        """

        results: Dict[str, Any] = {}

        for name, metric in self.registry.items():

            enabled = True

            if isinstance(metric, dict):
                enabled = metric.get("enabled", True)

            if not enabled:
                continue

            try:
                results[name] = self.collect(name)

            except Exception as exc:
                results[name] = exc

        self._results.update(results)

        return deepcopy(results)
# =============================================================================
# Part 3. Metric Registry
# =============================================================================

    # -------------------------------------------------------------------------
    # Metric Registry API
    # -------------------------------------------------------------------------

    def register_metric(
        self,
        name: str,
        metric: Callable[..., Any],
        *,
        enabled: bool = True,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register a metric collector.

        Parameters
        ----------
        name:
            Unique metric name.

        metric:
            Callable used to collect the metric.

        enabled:
            Whether the metric is enabled.

        metadata:
            Optional metadata describing the metric.

        Returns
        -------
        Dict[str, Any]
            Registry entry.
        """

        if not callable(metric):
            raise TypeError("Metric must be callable.")

        entry = {
            "name": name,
            "metric": metric,
            "enabled": enabled,
            "metadata": dict(metadata or {}),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        self.registry[name] = entry

        self.updated_at = datetime.now(timezone.utc)

        return entry

    # -------------------------------------------------------------------------

    def remove_metric(
        self,
        name: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Remove a registered metric.
        """

        self.updated_at = datetime.now(timezone.utc)

        return self.registry.pop(name, None)

    # -------------------------------------------------------------------------

    def metric(
        self,
        name: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Return a metric registry entry.
        """

        return self.registry.get(name)

    # -------------------------------------------------------------------------

    def metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Return all registered metrics.
        """

        return deepcopy(self.registry)

    # -------------------------------------------------------------------------

    def contains_metric(
        self,
        name: str,
    ) -> bool:
        """
        Check whether a metric exists.
        """

        return name in self.registry

    # -------------------------------------------------------------------------

    def enable_metric(
        self,
        name: str,
    ) -> None:
        """
        Enable a registered metric.
        """

        if name not in self.registry:
            raise KeyError(f"Unknown metric: {name}")

        self.registry[name]["enabled"] = True
        self.registry[name]["updated_at"] = datetime.now(timezone.utc)

        self.updated_at = datetime.now(timezone.utc)

    # -------------------------------------------------------------------------

    def disable_metric(
        self,
        name: str,
    ) -> None:
        """
        Disable a registered metric.
        """

        if name not in self.registry:
            raise KeyError(f"Unknown metric: {name}")

        self.registry[name]["enabled"] = False
        self.registry[name]["updated_at"] = datetime.now(timezone.utc)

        self.updated_at = datetime.now(timezone.utc)

    # -------------------------------------------------------------------------

    def execute_metric(
        self,
        name: str,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute a registered metric collector.

        Parameters
        ----------
        name:
            Metric name.

        Returns
        -------
        Any
            Metric result.
        """

        entry = self.registry.get(name)

        if entry is None:
            raise KeyError(f"Unknown metric: {name}")

        if not entry["enabled"]:
            raise RuntimeError(
                f"Metric '{name}' is disabled."
            )

        collector = entry["metric"]

        started = time.perf_counter()

        self.before_collect(name)

        try:

            result = collector(*args, **kwargs)

            self._metrics[name] = result
            self._last_metric = result

            self.statistics["metrics"] += 1
            self.statistics["samples"] += 1

            return result

        except Exception:

            self.statistics["errors"] += 1
            raise

        finally:

            elapsed = time.perf_counter() - started

            self.statistics["latency"] = elapsed
            self.statistics["uptime"] += elapsed

            entry["updated_at"] = datetime.now(timezone.utc)
            self.updated_at = datetime.now(timezone.utc)

            self.after_collect(name)
# =============================================================================
# Part 4. QTC Registry
# =============================================================================

    # -------------------------------------------------------------------------
    # QTC Component Registry API
    # -------------------------------------------------------------------------

    def register_component(
        self,
        name: str,
        component: Any,
        *,
        enabled: bool = True,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register a QTC component.

        Parameters
        ----------
        name:
            Component name.

        component:
            Component object or callable.

        enabled:
            Whether the component is enabled.

        metadata:
            Optional component metadata.
        """

        entry = {
            "name": name,
            "component": component,
            "enabled": enabled,
            "metadata": dict(metadata or {}),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        self.qtc_registry[name] = entry
        self._components[name] = entry

        self.statistics["components"] = len(self.qtc_registry)

        self.updated_at = datetime.now(timezone.utc)

        return entry

    # -------------------------------------------------------------------------

    def remove_component(
        self,
        name: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Remove a registered QTC component.
        """

        self._components.pop(name, None)

        component = self.qtc_registry.pop(name, None)

        self.statistics["components"] = len(self.qtc_registry)

        self.updated_at = datetime.now(timezone.utc)

        return component

    # -------------------------------------------------------------------------

    def component(
        self,
        name: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Return a registered component.
        """

        return self.qtc_registry.get(name)

    # -------------------------------------------------------------------------

    def components(self) -> Dict[str, Dict[str, Any]]:
        """
        Return all registered QTC components.
        """

        return deepcopy(self.qtc_registry)

    # -------------------------------------------------------------------------

    def contains_component(
        self,
        name: str,
    ) -> bool:
        """
        Check whether a component exists.
        """

        return name in self.qtc_registry

    # -------------------------------------------------------------------------

    def enable_component(
        self,
        name: str,
    ) -> None:
        """
        Enable a registered component.
        """

        if name not in self.qtc_registry:
            raise KeyError(f"Unknown component: {name}")

        self.qtc_registry[name]["enabled"] = True
        self.qtc_registry[name]["updated_at"] = datetime.now(timezone.utc)

        self.updated_at = datetime.now(timezone.utc)

    # -------------------------------------------------------------------------

    def disable_component(
        self,
        name: str,
    ) -> None:
        """
        Disable a registered component.
        """

        if name not in self.qtc_registry:
            raise KeyError(f"Unknown component: {name}")

        self.qtc_registry[name]["enabled"] = False
        self.qtc_registry[name]["updated_at"] = datetime.now(timezone.utc)

        self.updated_at = datetime.now(timezone.utc)

    # -------------------------------------------------------------------------

    def component_names(self) -> List[str]:
        """
        Return registered component names.
        """

        return sorted(self.qtc_registry.keys())

    # -------------------------------------------------------------------------

    @property
    def component_count(self) -> int:
        """
        Number of registered QTC components.
        """

        return len(self.qtc_registry)

    # -------------------------------------------------------------------------

    def clear_components(self) -> None:
        """
        Remove all registered components.
        """

        self.qtc_registry.clear()
        self._components.clear()

        self.statistics["components"] = 0

        self.updated_at = datetime.now(timezone.utc)

    # -------------------------------------------------------------------------

    def execute_component(
        self,
        name: str,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute a registered QTC component.

        If the component is callable it is invoked.
        Otherwise the component object is returned.
        """

        entry = self.qtc_registry.get(name)

        if entry is None:
            raise KeyError(f"Unknown component: {name}")

        if not entry["enabled"]:
            raise RuntimeError(
                f"Component '{name}' is disabled."
            )

        component = entry["component"]

        started = time.perf_counter()

        self.before_component(name)

        try:

            if callable(component):
                result = component(*args, **kwargs)
            else:
                result = component

            self._results[name] = result

            self.statistics["samples"] += 1

            return result

        except Exception:

            self.statistics["errors"] += 1
            raise

        finally:

            elapsed = time.perf_counter() - started

            self.statistics["latency"] = elapsed
            self.statistics["uptime"] += elapsed

            entry["updated_at"] = datetime.now(timezone.utc)
            self.updated_at = datetime.now(timezone.utc)

            self.after_component(name)
# =============================================================================
# Part 5. Lifecycle
# =============================================================================

    # -------------------------------------------------------------------------
    # Lifecycle API
    # -------------------------------------------------------------------------

    def enable(self) -> "MetricQTCIntegration":
        """
        Enable the QTC integration.
        """

        if self.closed:
            raise RuntimeError(
                "Cannot enable a closed QTC integration."
            )

        self.enabled = True
        self.disabled = False

        self.updated_at = datetime.now(timezone.utc)

        return self

    # -------------------------------------------------------------------------

    def disable(self) -> "MetricQTCIntegration":
        """
        Disable the QTC integration.

        Registered metrics and components are preserved.
        """

        self.enabled = False
        self.disabled = True

        self.running = False
        self.active = False

        self.updated_at = datetime.now(timezone.utc)

        return self

    # -------------------------------------------------------------------------

    def freeze(self) -> "MetricQTCIntegration":
        """
        Freeze metric collection and component execution.

        Existing state is preserved but no collection or execution
        is allowed until the integration is unfrozen.
        """

        if self.closed:
            raise RuntimeError(
                "Cannot freeze a closed QTC integration."
            )

        self.frozen = True

        self.updated_at = datetime.now(timezone.utc)

        return self

    # -------------------------------------------------------------------------

    def unfreeze(self) -> "MetricQTCIntegration":
        """
        Resume a frozen QTC integration.
        """

        if self.closed:
            raise RuntimeError(
                "Cannot unfreeze a closed QTC integration."
            )

        self.frozen = False

        self.updated_at = datetime.now(timezone.utc)

        return self

    # -------------------------------------------------------------------------

    def close(self) -> "MetricQTCIntegration":
        """
        Close the integration.

        Runtime activity is stopped while keeping configuration,
        metrics and components available for future restoration.
        """

        self.running = False
        self.active = False

        self.enabled = False
        self.disabled = True

        self.frozen = False
        self.closed = True

        self.updated_at = datetime.now(timezone.utc)

        return self

    # -------------------------------------------------------------------------

    def reopen(self) -> "MetricQTCIntegration":
        """
        Reopen a previously closed integration.
        """

        self.closed = False

        self.enabled = True
        self.disabled = False

        self.running = False
        self.active = False

        self.updated_at = datetime.now(timezone.utc)

        return self
# =============================================================================
# Part 6. Runtime Operations
# =============================================================================

    # -------------------------------------------------------------------------
    # Runtime Operations
    # -------------------------------------------------------------------------

    def reset(self) -> "MetricQTCIntegration":
        """
        Reset the runtime state while preserving configuration,
        metric registry and component registry.
        """

        self.running = False
        self.active = False
        self.frozen = False

        self._current_metric = None
        self._last_metric = None
        self._last_snapshot = None
        self._start_time = None

        self._results.clear()
        self._metrics.clear()

        self.statistics = deepcopy(DEFAULT_STATISTICS)

        self.updated_at = datetime.now(timezone.utc)

        return self

    # -------------------------------------------------------------------------

    def clear(self) -> "MetricQTCIntegration":
        """
        Clear runtime data, metric registry, component registry,
        collected results and hooks.

        Configuration and identity are preserved.
        """

        self.registry.clear()
        self.qtc_registry.clear()

        self._metrics.clear()
        self._components.clear()
        self._results.clear()
        self._hooks.clear()

        self._current_metric = None
        self._last_metric = None
        self._last_snapshot = None
        self._start_time = None

        self.statistics = deepcopy(DEFAULT_STATISTICS)

        self.updated_at = datetime.now(timezone.utc)

        return self

    # -------------------------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """
        Create a complete runtime snapshot.
        """

        snapshot = {
            "identity": {
                "id": self.id,
                "name": self.name,
                "version": self.version,
            },
            "runtime": {
                "enabled": self.enabled,
                "disabled": self.disabled,
                "running": self.running,
                "active": self.active,
                "frozen": self.frozen,
                "closed": self.closed,
            },
            "configuration": deepcopy(self.configuration),
            "registry": deepcopy(self.registry),
            "qtc_registry": deepcopy(self.qtc_registry),
            "metrics": deepcopy(self._metrics),
            "components": deepcopy(self._components),
            "results": deepcopy(self._results),
            "statistics": deepcopy(self.statistics),
            "metadata": deepcopy(self.metadata),
            "timestamp": datetime.now(timezone.utc),
        }

        self._last_snapshot = deepcopy(snapshot)

        return snapshot

    # -------------------------------------------------------------------------

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "MetricQTCIntegration":
        """
        Restore the integration from a snapshot.
        """

        runtime = snapshot.get("runtime", {})

        self.enabled = runtime.get("enabled", True)
        self.disabled = runtime.get("disabled", False)
        self.running = runtime.get("running", False)
        self.active = runtime.get("active", False)
        self.frozen = runtime.get("frozen", False)
        self.closed = runtime.get("closed", False)

        self.configuration = deepcopy(
            snapshot.get("configuration", {})
        )

        self.registry = deepcopy(
            snapshot.get("registry", {})
        )

        self.qtc_registry = deepcopy(
            snapshot.get("qtc_registry", {})
        )

        self._metrics = deepcopy(
            snapshot.get("metrics", {})
        )

        self._components = deepcopy(
            snapshot.get("components", {})
        )

        self._results = deepcopy(
            snapshot.get("results", {})
        )

        self.statistics = deepcopy(
            snapshot.get("statistics", {})
        )

        self.metadata = deepcopy(
            snapshot.get("metadata", {})
        )

        self.updated_at = datetime.now(timezone.utc)

        return self

    # -------------------------------------------------------------------------

    def clone(self) -> "MetricQTCIntegration":
        """
        Return a deep clone of this integration.
        """

        return deepcopy(self)

    # -------------------------------------------------------------------------

    def copy(self) -> "MetricQTCIntegration":
        """
        Alias of clone().
        """

        return self.clone()
# =============================================================================
# Part 7. Statistics & Diagnostics
# =============================================================================

    # -------------------------------------------------------------------------
    # Statistics & Diagnostics
    # -------------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """
        Return a concise summary of the QTC integration.
        """

        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "running": self.running,
            "active": self.active,
            "metrics": self.metric_count,
            "components": self.component_count,
            "samples": self.sample_count,
            "errors": self.error_count,
            "uptime": self.uptime,
            "latency": self.latency,
        }

    # -------------------------------------------------------------------------

    def report(self) -> Dict[str, Any]:
        """
        Return a detailed diagnostic report.
        """

        return {
            "identity": {
                "id": self.id,
                "name": self.name,
                "version": self.version,
            },
            "runtime": {
                "enabled": self.enabled,
                "disabled": self.disabled,
                "running": self.running,
                "active": self.active,
                "frozen": self.frozen,
                "closed": self.closed,
            },
            "configuration": deepcopy(self.configuration),
            "statistics": deepcopy(self.statistics),
            "metric_registry": list(self.registry.keys()),
            "component_registry": list(self.qtc_registry.keys()),
            "metadata": deepcopy(self.metadata),
            "results": deepcopy(self._results),
            "metrics": deepcopy(self._metrics),
        }

    # -------------------------------------------------------------------------

    def health(self) -> Dict[str, Any]:
        """
        Return health information.
        """

        if self.closed:
            state = "closed"
        elif self.frozen:
            state = "frozen"
        elif not self.enabled:
            state = "disabled"
        elif self.running:
            state = "running"
        else:
            state = "ready"

        healthy = (
            self.enabled
            and not self.closed
            and self.error_count == 0
        )

        return {
            "healthy": healthy,
            "state": state,
            "running": self.running,
            "active": self.active,
            "errors": self.error_count,
            "timestamp": datetime.now(timezone.utc),
        }

    # -------------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        """
        Return current runtime status.
        """

        return {
            "enabled": self.enabled,
            "disabled": self.disabled,
            "running": self.running,
            "active": self.active,
            "frozen": self.frozen,
            "closed": self.closed,
        }

    # -------------------------------------------------------------------------
    # Statistics Properties
    # -------------------------------------------------------------------------

    @property
    def metric_count(self) -> int:
        """
        Number of registered metrics.
        """

        return len(self.registry)

    # -------------------------------------------------------------------------

    @property
    def component_count(self) -> int:
        """
        Number of registered QTC components.
        """

        return len(self.qtc_registry)

    # -------------------------------------------------------------------------

    @property
    def sample_count(self) -> int:
        """
        Number of collected samples.
        """

        return int(self.statistics.get("samples", 0))

    # -------------------------------------------------------------------------

    @property
    def error_count(self) -> int:
        """
        Number of runtime errors.
        """

        return int(self.statistics.get("errors", 0))

    # -------------------------------------------------------------------------

    @property
    def uptime(self) -> float:
        """
        Total accumulated runtime.
        """

        return float(self.statistics.get("uptime", 0.0))

    # -------------------------------------------------------------------------

    @property
    def latency(self) -> float:
        """
        Latest execution latency.
        """

        return float(self.statistics.get("latency", 0.0))
# =============================================================================
# Part 8. Serialization
# =============================================================================

    # -------------------------------------------------------------------------
    # Serialization API
    # -------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize this integration to a Python dictionary.
        """

        return {
            "identity": {
                "id": self.id,
                "name": self.name,
                "version": self.version,
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
            },
            "runtime": {
                "enabled": self.enabled,
                "disabled": self.disabled,
                "running": self.running,
                "active": self.active,
                "frozen": self.frozen,
                "closed": self.closed,
            },
            "configuration": deepcopy(self.configuration),
            "metric_registry": deepcopy(self.registry),
            "qtc_registry": deepcopy(self.qtc_registry),
            "metrics": deepcopy(self._metrics),
            "components": deepcopy(self._components),
            "results": deepcopy(self._results),
            "statistics": deepcopy(self.statistics),
            "metadata": deepcopy(self.metadata),
        }

    # -------------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "MetricQTCIntegration":
        """
        Create a MetricQTCIntegration from a dictionary.
        """

        identity = data.get("identity", {})
        runtime = data.get("runtime", {})

        obj = cls(
            name=identity.get("name", DEFAULT_NAME),
            configuration=data.get("configuration", {}),
        )

        obj.id = identity.get("id", obj.id)
        obj.version = identity.get("version", obj.version)

        if identity.get("created_at"):
            obj.created_at = datetime.fromisoformat(
                identity["created_at"]
            )

        if identity.get("updated_at"):
            obj.updated_at = datetime.fromisoformat(
                identity["updated_at"]
            )

        obj.enabled = runtime.get("enabled", True)
        obj.disabled = runtime.get("disabled", False)
        obj.running = runtime.get("running", False)
        obj.active = runtime.get("active", False)
        obj.frozen = runtime.get("frozen", False)
        obj.closed = runtime.get("closed", False)

        obj.registry = deepcopy(
            data.get("metric_registry", {})
        )

        obj.qtc_registry = deepcopy(
            data.get("qtc_registry", {})
        )

        obj._metrics = deepcopy(
            data.get("metrics", {})
        )

        obj._components = deepcopy(
            data.get("components", {})
        )

        obj._results = deepcopy(
            data.get("results", {})
        )

        obj.statistics = deepcopy(
            data.get("statistics", {})
        )

        obj.metadata = deepcopy(
            data.get("metadata", {})
        )

        return obj

    # -------------------------------------------------------------------------

    def to_json(
        self,
        *,
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> str:
        """
        Serialize this integration to JSON.
        """

        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=ensure_ascii,
            default=str,
        )

    # -------------------------------------------------------------------------

    @classmethod
    def from_json(
        cls,
        data: str,
    ) -> "MetricQTCIntegration":
        """
        Create a MetricQTCIntegration from a JSON string.
        """

        return cls.from_dict(json.loads(data))

    # -------------------------------------------------------------------------

    def serialize(self) -> Dict[str, Any]:
        """
        Generic serialization interface.

        Alias of to_dict().
        """

        return self.to_dict()

    # -------------------------------------------------------------------------

    @classmethod
    def deserialize(
        cls,
        data: Mapping[str, Any] | str,
    ) -> "MetricQTCIntegration":
        """
        Generic deserialization interface.

        Accepts either a dictionary or a JSON string.
        """

        if isinstance(data, str):
            return cls.from_json(data)

        return cls.from_dict(data)
# =============================================================================
# Part 9. Events & Hooks
# =============================================================================

    # -------------------------------------------------------------------------
    # Collection Events
    # -------------------------------------------------------------------------

    def before_collect(
        self,
        metric: Optional[str] = None,
    ) -> None:
        """
        Emit before a metric collection starts.
        """

        self.emit("before_collect", metric)

    # -------------------------------------------------------------------------

    def after_collect(
        self,
        metric: Optional[str] = None,
    ) -> None:
        """
        Emit after a metric collection finishes.
        """

        self.emit("after_collect", metric)

    # -------------------------------------------------------------------------

    def before_component(
        self,
        component: Optional[str] = None,
    ) -> None:
        """
        Emit before a QTC component executes.
        """

        self.emit("before_component", component)

    # -------------------------------------------------------------------------

    def after_component(
        self,
        component: Optional[str] = None,
    ) -> None:
        """
        Emit after a QTC component executes.
        """

        self.emit("after_component", component)

    # -------------------------------------------------------------------------
    # Hook Registry
    # -------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback: Callable[..., Any],
    ) -> Callable[..., Any]:
        """
        Register a callback for an event.

        Parameters
        ----------
        event:
            Event name.

        callback:
            Callable invoked when the event is emitted.
        """

        if not callable(callback):
            raise TypeError("Hook callback must be callable.")

        self._hooks.setdefault(event, []).append(callback)

        return callback

    # -------------------------------------------------------------------------

    def remove_hook(
        self,
        event: str,
        callback: Callable[..., Any],
    ) -> bool:
        """
        Remove a previously registered callback.

        Returns
        -------
        bool
            True if removed successfully.
        """

        callbacks = self._hooks.get(event)

        if callbacks is None:
            return False

        try:

            callbacks.remove(callback)

            if not callbacks:
                self._hooks.pop(event, None)

            return True

        except ValueError:

            return False

    # -------------------------------------------------------------------------

    def emit(
        self,
        event: str,
        *args,
        **kwargs,
    ) -> None:
        """
        Emit an event to all subscribers.

        Any callback exception is isolated so it does not
        interrupt metric collection.
        """

        callbacks = tuple(self._hooks.get(event, ()))

        for callback in callbacks:

            try:

                callback(*args, **kwargs)

            except Exception:

                self.statistics["errors"] += 1

    # -------------------------------------------------------------------------

    def subscribe(
        self,
        event: str,
        callback: Callable[..., Any],
    ) -> Callable[..., Any]:
        """
        Alias of add_hook().
        """

        return self.add_hook(event, callback)
# =============================================================================
# Part 10. Python Protocols
# =============================================================================

    # -------------------------------------------------------------------------
    # Object Representation
    # -------------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"enabled={self.enabled}, "
            f"running={self.running}, "
            f"metrics={self.metric_count}, "
            f"components={self.component_count})"
        )

    # -------------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        if self.closed:
            state = "closed"
        elif self.frozen:
            state = "frozen"
        elif self.running:
            state = "running"
        elif self.enabled:
            state = "ready"
        else:
            state = "disabled"

        return (
            f"{self.name} "
            f"[{state}] "
            f"(metrics={self.metric_count}, "
            f"components={self.component_count}, "
            f"samples={self.sample_count})"
        )

    # -------------------------------------------------------------------------
    # Container Protocol
    # -------------------------------------------------------------------------

    def __len__(self) -> int:
        """
        Return the number of registered metrics.
        """

        return self.metric_count

    # -------------------------------------------------------------------------

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over registered metric names.
        """

        return iter(self.registry)

    # -------------------------------------------------------------------------

    def __contains__(
        self,
        item: object,
    ) -> bool:
        """
        Membership test.

        Example
        -------
        "energy" in integration
        """

        if not isinstance(item, str):
            return False

        return item in self.registry

    # -------------------------------------------------------------------------
    # Callable Protocol
    # -------------------------------------------------------------------------

    def __call__(
        self,
        metric: str,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute a registered metric collector.

        Example
        -------
        integration("energy")
        integration("tensor", tensor)
        """

        return self.execute_metric(
            metric,
            *args,
            **kwargs,
        )

    # -------------------------------------------------------------------------
    # Copy Protocol
    # -------------------------------------------------------------------------

    def __copy__(self) -> "MetricQTCIntegration":
        """
        Return a shallow copy.
        """

        cls = self.__class__

        obj = cls.__new__(cls)

        obj.__dict__.update(self.__dict__)

        return obj

    # -------------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo: Optional[Dict[int, Any]] = None,
    ) -> "MetricQTCIntegration":
        """
        Return a deep copy.
        """

        if memo is None:
            memo = {}

        cls = self.__class__

        obj = cls.__new__(cls)

        memo[id(self)] = obj

        for key, value in self.__dict__.items():
            setattr(
                obj,
                key,
                deepcopy(value, memo),
            )

        return obj                                                                            