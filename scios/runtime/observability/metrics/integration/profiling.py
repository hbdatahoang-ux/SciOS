"""
SciOS-NG
metrics/integration/profiling.py

Part 1. Foundation

This module defines the foundation of the MetricProfilingIntegration.
Later parts (Profiling API, Lifecycle, Serialization, Hooks, etc.)
extend this class without changing the core state defined here.
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

DEFAULT_NAME = "MetricProfilingIntegration"
DEFAULT_VERSION = "1.0.0"

DEFAULT_CONFIGURATION: Dict[str, Any] = {
    "cpu": True,
    "memory": True,
    "gpu": False,
    "thread": True,
    "io": True,
    "sampling_interval": 0.01,
    "auto_start": False,
}

DEFAULT_STATISTICS: Dict[str, Any] = {
    "profiles": 0,
    "samples": 0,
    "errors": 0,
    "uptime": 0.0,
    "latency": 0.0,
}


# =============================================================================
# Type Aliases
# =============================================================================

Profiler: TypeAlias = Callable[..., Any]
ProfilerRegistry: TypeAlias = Dict[str, Profiler]
ProfileStore: TypeAlias = Dict[str, Any]
Metadata: TypeAlias = Dict[str, Any]
Statistics: TypeAlias = Dict[str, Any]
HookRegistry: TypeAlias = Dict[str, List[Callable[..., Any]]]


# =============================================================================
# MetricProfilingIntegration
# =============================================================================


class MetricProfilingIntegration:
    """
    Performance Profiling Integration Layer.

    Responsibilities
    ----------------
    * Manage profiler registry.
    * Maintain profiling runtime state.
    * Store profiling metadata.
    * Provide common profiling foundation.

    Notes
    -----
    Actual profiling APIs are implemented in later parts.
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
        """
        Initialize profiling integration.
        """

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
        # Profiling Configuration
        # -----------------------------------------------------------------

        self.configuration: Dict[str, Any] = deepcopy(
            DEFAULT_CONFIGURATION
        )

        if configuration:
            self.configuration.update(configuration)

        # -----------------------------------------------------------------
        # Profiler Registry
        # -----------------------------------------------------------------

        self.registry: ProfilerRegistry = {}

        # -----------------------------------------------------------------
        # Metadata
        # -----------------------------------------------------------------

        self.metadata: Metadata = {
            "component": "profiling",
            "version": self.version,
            "created_at": self.created_at.isoformat(),
        }

        # -----------------------------------------------------------------
        # Statistics
        # -----------------------------------------------------------------

        self.statistics: Statistics = deepcopy(DEFAULT_STATISTICS)

        # -----------------------------------------------------------------
        # Internal Runtime
        # -----------------------------------------------------------------

        self._profiles: ProfileStore = {}

        self._current_profile: Optional[Any] = None

        self._results: Dict[str, Any] = {}

        self._hooks: HookRegistry = {}

        self._start_time: Optional[float] = None

        self._last_profile: Optional[Any] = None

        self._last_snapshot: Optional[Dict[str, Any]] = None

    # -------------------------------------------------------------------------
    # End Foundation
    # -------------------------------------------------------------------------
# =============================================================================
# Part 2. Profiling API
# =============================================================================

from contextlib import contextmanager
from functools import wraps


    # -------------------------------------------------------------------------
    # Profiling API
    # -------------------------------------------------------------------------

    def start_profile(self, name: str = "default") -> str:
        """
        Start a profiling session.

        Parameters
        ----------
        name:
            Profile session name.

        Returns
        -------
        str
            Profile identifier.
        """

        if self.closed:
            raise RuntimeError("Profiling integration is closed.")

        if not self.enabled:
            raise RuntimeError("Profiling integration is disabled.")

        profile_id = str(uuid4())

        self.running = True
        self.active = True

        self._start_time = time.perf_counter()

        profile = {
            "id": profile_id,
            "name": name,
            "started_at": datetime.now(timezone.utc),
            "finished_at": None,
            "duration": 0.0,
            "status": "running",
        }

        self._profiles[profile_id] = profile
        self._current_profile = profile

        self.statistics["profiles"] += 1
        self.updated_at = datetime.now(timezone.utc)

        return profile_id

    # -------------------------------------------------------------------------

    def stop_profile(self) -> Optional[dict]:
        """
        Stop current profiling session.
        """

        if self._current_profile is None:
            return None

        elapsed = 0.0

        if self._start_time is not None:
            elapsed = time.perf_counter() - self._start_time

        profile = self._current_profile

        profile["finished_at"] = datetime.now(timezone.utc)
        profile["duration"] = elapsed
        profile["status"] = "completed"

        self.statistics["uptime"] += elapsed
        self.statistics["latency"] = elapsed

        self.running = False
        self.active = False

        self._last_profile = profile
        self._current_profile = None
        self._start_time = None

        self.updated_at = datetime.now(timezone.utc)

        return profile

    # -------------------------------------------------------------------------

    def profile(
        self,
        func: Optional[Callable[..., Any]] = None,
        *,
        name: Optional[str] = None,
    ):
        """
        Generic profiling decorator.

        Usage
        -----

        @profiler.profile

        or

        @profiler.profile(name="solver")
        """

        if func is None:

            def decorator(f):
                return self.profile(f, name=name)

            return decorator

        @wraps(func)
        def wrapper(*args, **kwargs):

            self.start_profile(name or func.__name__)

            try:
                return func(*args, **kwargs)

            finally:
                self.stop_profile()

        return wrapper

    # -------------------------------------------------------------------------

    def profile_function(self, func: Callable[..., Any]):
        """
        Alias of profile().
        """

        return self.profile(func)

    # -------------------------------------------------------------------------

    @contextmanager
    def profile_block(self, name: str = "block"):
        """
        Profile a code block.

        Example
        -------

        with profiler.profile_block("training"):
            train()
        """

        self.start_profile(name)

        try:
            yield self

        finally:
            self.stop_profile()

    # -------------------------------------------------------------------------

    def snapshot_profile(self) -> Dict[str, Any]:
        """
        Snapshot current profiling state.
        """

        snapshot = {
            "running": self.running,
            "active": self.active,
            "current_profile": deepcopy(self._current_profile),
            "statistics": deepcopy(self.statistics),
            "timestamp": datetime.now(timezone.utc),
        }

        self._last_snapshot = snapshot

        return deepcopy(snapshot)

    # -------------------------------------------------------------------------

    def current_profile(self) -> Optional[dict]:
        """
        Return current active profile.
        """

        return self._current_profile

    # -------------------------------------------------------------------------

    def profile_result(self) -> Optional[dict]:
        """
        Return latest completed profile.
        """

        return self._last_profile
# =============================================================================
# Part 3. Profilers
# =============================================================================

    # -------------------------------------------------------------------------
    # Profiler Registry API
    # -------------------------------------------------------------------------

    def add_profiler(
        self,
        name: str,
        profiler: Callable[..., Any],
        *,
        enabled: bool = True,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """
        Register a profiler backend.
        """

        if not callable(profiler):
            raise TypeError("Profiler must be callable.")

        self.registry[name] = {
            "name": name,
            "profiler": profiler,
            "enabled": enabled,
            "metadata": dict(metadata or {}),
            "created_at": datetime.now(timezone.utc),
        }

        self.updated_at = datetime.now(timezone.utc)

    # -------------------------------------------------------------------------

    def remove_profiler(self, name: str) -> Optional[dict]:
        """
        Remove a profiler from registry.
        """

        self.updated_at = datetime.now(timezone.utc)

        return self.registry.pop(name, None)

    # -------------------------------------------------------------------------

    def profiler(self, name: str) -> Optional[dict]:
        """
        Return profiler entry.
        """

        return self.registry.get(name)

    # -------------------------------------------------------------------------

    def profilers(self) -> Dict[str, dict]:
        """
        Return all registered profilers.
        """

        return deepcopy(self.registry)

    # -------------------------------------------------------------------------

    def execute_profiler(
        self,
        name: str,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute a registered profiler.
        """

        entry = self.registry.get(name)

        if entry is None:
            raise KeyError(f"Unknown profiler: {name}")

        if not entry["enabled"]:
            raise RuntimeError(f"Profiler '{name}' is disabled.")

        profiler = entry["profiler"]

        started = time.perf_counter()

        try:
            result = profiler(*args, **kwargs)

            return result

        except Exception:

            self.statistics["errors"] += 1

            raise

        finally:

            elapsed = time.perf_counter() - started

            self.statistics["samples"] += 1

            self.statistics["latency"] = elapsed

            self.updated_at = datetime.now(timezone.utc)

    # -------------------------------------------------------------------------

    def enable_profiler(self, name: str) -> None:
        """
        Enable a profiler.
        """

        if name not in self.registry:
            raise KeyError(name)

        self.registry[name]["enabled"] = True

        self.updated_at = datetime.now(timezone.utc)

    # -------------------------------------------------------------------------

    def disable_profiler(self, name: str) -> None:
        """
        Disable a profiler.
        """

        if name not in self.registry:
            raise KeyError(name)

        self.registry[name]["enabled"] = False

        self.updated_at = datetime.now(timezone.utc)

    # -------------------------------------------------------------------------

    def builtin_profilers(self) -> Dict[str, str]:
        """
        Return supported built-in profiler names.

        This method advertises the profiler types supported by the
        integration. Actual implementations may be registered later.
        """

        return {
            "cpu": "CPU profiler",
            "memory": "Memory profiler",
            "gpu": "GPU profiler",
            "thread": "Thread profiler",
            "io": "I/O profiler",
            "function": "Function profiler",
            "walltime": "Wall-clock timer",
        }
# =============================================================================
# Part 4. Profiler Registry API
# =============================================================================

    # -------------------------------------------------------------------------
    # Profile Registry API
    # -------------------------------------------------------------------------

    def register_profile(
        self,
        name: str,
        profile: Any,
        *,
        enabled: bool = True,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        """
        Register a profile object.
        """

        obj = {
            "name": name,
            "profile": profile,
            "enabled": enabled,
            "metadata": dict(metadata or {}),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        self._profiles[name] = obj
        self.updated_at = datetime.now(timezone.utc)

        return obj

    # -------------------------------------------------------------------------

    def remove_profile(self, name: str) -> Optional[dict]:
        """
        Remove a registered profile.
        """

        self.updated_at = datetime.now(timezone.utc)

        return self._profiles.pop(name, None)

    # -------------------------------------------------------------------------

    def profile_object(self, name: str) -> Optional[dict]:
        """
        Return a registered profile.
        """

        return self._profiles.get(name)

    # -------------------------------------------------------------------------

    def profiles(self) -> Dict[str, dict]:
        """
        Return all registered profiles.
        """

        return deepcopy(self._profiles)

    # -------------------------------------------------------------------------

    def contains_profile(self, name: str) -> bool:
        """
        Check whether a profile exists.
        """

        return name in self._profiles

    # -------------------------------------------------------------------------

    def exists_profile(self, name: str) -> bool:
        """
        Alias of contains_profile().
        """

        return self.contains_profile(name)

    # -------------------------------------------------------------------------

    def enable_profile(self, name: str) -> None:
        """
        Enable a registered profile.
        """

        if name not in self._profiles:
            raise KeyError(name)

        self._profiles[name]["enabled"] = True
        self._profiles[name]["updated_at"] = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    # -------------------------------------------------------------------------

    def disable_profile(self, name: str) -> None:
        """
        Disable a registered profile.
        """

        if name not in self._profiles:
            raise KeyError(name)

        self._profiles[name]["enabled"] = False
        self._profiles[name]["updated_at"] = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    # -------------------------------------------------------------------------

    def profile_names(self) -> List[str]:
        """
        Return registered profile names.
        """

        return sorted(self._profiles.keys())

    # -------------------------------------------------------------------------

    def profile_count(self) -> int:
        """
        Return number of registered profiles.
        """

        return len(self._profiles)

    # -------------------------------------------------------------------------

    def clear_profiles(self) -> None:
        """
        Remove all registered profiles.
        """

        self._profiles.clear()
        self._current_profile = None

        self.updated_at = datetime.now(timezone.utc)

    # -------------------------------------------------------------------------

    def execute_profile(
        self,
        name: str,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute a registered profile.

        If the stored profile object is callable, it is invoked directly.
        Otherwise, the object itself is returned.
        """

        entry = self._profiles.get(name)

        if entry is None:
            raise KeyError(f"Unknown profile: {name}")

        if not entry["enabled"]:
            raise RuntimeError(f"Profile '{name}' is disabled.")

        profile = entry["profile"]

        started = time.perf_counter()

        try:

            if callable(profile):
                result = profile(*args, **kwargs)
            else:
                result = profile

            self.statistics["profiles"] += 1

            return result

        except Exception:

            self.statistics["errors"] += 1
            raise

        finally:

            elapsed = time.perf_counter() - started

            self.statistics["samples"] += 1
            self.statistics["latency"] = elapsed

            entry["updated_at"] = datetime.now(timezone.utc)
            self.updated_at = datetime.now(timezone.utc)
# =============================================================================
# Part 5. Lifecycle
# =============================================================================

    # -------------------------------------------------------------------------
    # Lifecycle API
    # -------------------------------------------------------------------------

    def enable(self) -> "MetricProfilingIntegration":
        """
        Enable the profiling integration.
        """

        if self.closed:
            raise RuntimeError(
                "Cannot enable a closed profiling integration."
            )

        self.enabled = True
        self.disabled = False

        self.updated_at = datetime.now(timezone.utc)

        return self

    # -------------------------------------------------------------------------

    def disable(self) -> "MetricProfilingIntegration":
        """
        Disable the profiling integration.
        """

        self.enabled = False
        self.disabled = True
        self.running = False
        self.active = False

        self.updated_at = datetime.now(timezone.utc)

        return self

    # -------------------------------------------------------------------------

    def freeze(self) -> "MetricProfilingIntegration":
        """
        Freeze profiling operations.

        A frozen integration preserves its state but rejects
        profiling execution until unfrozen.
        """

        self.frozen = True

        self.updated_at = datetime.now(timezone.utc)

        return self

    # -------------------------------------------------------------------------

    def unfreeze(self) -> "MetricProfilingIntegration":
        """
        Resume a frozen profiling integration.
        """

        if self.closed:
            raise RuntimeError(
                "Cannot unfreeze a closed profiling integration."
            )

        self.frozen = False

        self.updated_at = datetime.now(timezone.utc)

        return self

    # -------------------------------------------------------------------------

    def close(self) -> "MetricProfilingIntegration":
        """
        Permanently close the profiling integration.

        Active profiling sessions are stopped before closing.
        """

        if self.running:
            self.stop_profile()

        self.enabled = False
        self.disabled = True

        self.running = False
        self.active = False

        self.frozen = False
        self.closed = True

        self.updated_at = datetime.now(timezone.utc)

        return self

    # -------------------------------------------------------------------------

    def reopen(self) -> "MetricProfilingIntegration":
        """
        Reopen a previously closed profiling integration.
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

    def reset(self) -> "MetricProfilingIntegration":
        """
        Reset runtime state while preserving configuration and registered
        profilers.
        """

        self.running = False
        self.active = False
        self.frozen = False

        self._current_profile = None
        self._last_profile = None
        self._last_snapshot = None
        self._start_time = None

        self.statistics = deepcopy(DEFAULT_STATISTICS)

        self.updated_at = datetime.now(timezone.utc)

        return self

    # -------------------------------------------------------------------------

    def clear(self) -> "MetricProfilingIntegration":
        """
        Clear all runtime data including registered profiles and results,
        while preserving profiler registry and configuration.
        """

        self._profiles.clear()
        self._results.clear()
        self._hooks.clear()

        self._current_profile = None
        self._last_profile = None
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
            "statistics": deepcopy(self.statistics),
            "metadata": deepcopy(self.metadata),
            "profiles": deepcopy(self._profiles),
            "results": deepcopy(self._results),
            "registry": deepcopy(self.registry),
            "timestamp": datetime.now(timezone.utc),
        }

        self._last_snapshot = deepcopy(snapshot)

        return snapshot

    # -------------------------------------------------------------------------

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "MetricProfilingIntegration":
        """
        Restore runtime from a snapshot.
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

        self.statistics = deepcopy(
            snapshot.get("statistics", {})
        )

        self.metadata = deepcopy(
            snapshot.get("metadata", {})
        )

        self.registry = deepcopy(
            snapshot.get("registry", {})
        )

        self._profiles = deepcopy(
            snapshot.get("profiles", {})
        )

        self._results = deepcopy(
            snapshot.get("results", {})
        )

        self.updated_at = datetime.now(timezone.utc)

        return self

    # -------------------------------------------------------------------------

    def clone(self) -> "MetricProfilingIntegration":
        """
        Return a deep clone of this integration.
        """

        return deepcopy(self)

    # -------------------------------------------------------------------------

    def copy(self) -> "MetricProfilingIntegration":
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
        Return a concise summary of the profiling integration.
        """

        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "running": self.running,
            "active": self.active,
            "profiles": self.profile_count,
            "profilers": len(self.registry),
            "samples": self.sample_count,
            "errors": self.error_count,
            "uptime": self.uptime,
            "latency": self.latency,
        }

    # -------------------------------------------------------------------------

    def report(self) -> Dict[str, Any]:
        """
        Return a detailed profiling report.
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
            "profilers": list(self.registry.keys()),
            "profiles": self.profile_names(),
            "current_profile": deepcopy(self._current_profile),
            "last_profile": deepcopy(self._last_profile),
            "metadata": deepcopy(self.metadata),
        }

    # -------------------------------------------------------------------------

    def health(self) -> Dict[str, Any]:
        """
        Return integration health information.
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
            "errors": self.error_count,
            "running": self.running,
            "active": self.active,
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
    def profile_count(self) -> int:
        """
        Number of registered profiles.
        """

        return len(self._profiles)

    # -------------------------------------------------------------------------

    @property
    def sample_count(self) -> int:
        """
        Number of collected profiling samples.
        """

        return int(self.statistics.get("samples", 0))

    # -------------------------------------------------------------------------

    @property
    def error_count(self) -> int:
        """
        Number of profiling errors.
        """

        return int(self.statistics.get("errors", 0))

    # -------------------------------------------------------------------------

    @property
    def uptime(self) -> float:
        """
        Total accumulated profiling runtime.
        """

        return float(self.statistics.get("uptime", 0.0))

    # -------------------------------------------------------------------------

    @property
    def latency(self) -> float:
        """
        Latest profiling latency.
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
            "registry": deepcopy(self.registry),
            "profiles": deepcopy(self._profiles),
            "statistics": deepcopy(self.statistics),
            "metadata": deepcopy(self.metadata),
            "results": deepcopy(self._results),
        }

    # -------------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "MetricProfilingIntegration":
        """
        Create an integration from a dictionary.
        """

        obj = cls(
            name=data.get("identity", {}).get("name", DEFAULT_NAME),
            configuration=data.get("configuration", {}),
        )

        identity = data.get("identity", {})
        runtime = data.get("runtime", {})

        obj.id = identity.get("id", obj.id)
        obj.version = identity.get("version", obj.version)

        if "created_at" in identity:
            obj.created_at = datetime.fromisoformat(
                identity["created_at"]
            )

        if "updated_at" in identity:
            obj.updated_at = datetime.fromisoformat(
                identity["updated_at"]
            )

        obj.enabled = runtime.get("enabled", True)
        obj.disabled = runtime.get("disabled", False)
        obj.running = runtime.get("running", False)
        obj.active = runtime.get("active", False)
        obj.frozen = runtime.get("frozen", False)
        obj.closed = runtime.get("closed", False)

        obj.registry = deepcopy(data.get("registry", {}))
        obj._profiles = deepcopy(data.get("profiles", {}))
        obj.statistics = deepcopy(data.get("statistics", {}))
        obj.metadata = deepcopy(data.get("metadata", {}))
        obj._results = deepcopy(data.get("results", {}))

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
    ) -> "MetricProfilingIntegration":
        """
        Create an integration from a JSON string.
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
    ) -> "MetricProfilingIntegration":
        """
        Generic deserialization interface.

        Accepts either a dictionary or JSON string.
        """

        if isinstance(data, str):
            return cls.from_json(data)

        return cls.from_dict(data)
# =============================================================================
# Part 9. Events & Hooks
# =============================================================================

    # -------------------------------------------------------------------------
    # Event Hooks
    # -------------------------------------------------------------------------

    def before_profile(
        self,
        profile: Optional[Any] = None,
    ) -> None:
        """
        Emit before a profiling session starts.
        """

        self.emit("before_profile", profile)

    # -------------------------------------------------------------------------

    def after_profile(
        self,
        profile: Optional[Any] = None,
    ) -> None:
        """
        Emit after a profiling session finishes.
        """

        self.emit("after_profile", profile)

    # -------------------------------------------------------------------------

    def before_sample(
        self,
        sample: Optional[Any] = None,
    ) -> None:
        """
        Emit before a profiling sample is collected.
        """

        self.emit("before_sample", sample)

    # -------------------------------------------------------------------------

    def after_sample(
        self,
        sample: Optional[Any] = None,
    ) -> None:
        """
        Emit after a profiling sample is collected.
        """

        self.emit("after_sample", sample)

    # -------------------------------------------------------------------------
    # Hook Registry
    # -------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback: Callable[..., Any],
    ) -> Callable[..., Any]:
        """
        Register an event callback.
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
        Remove a registered callback.

        Returns
        -------
        bool
            True if the callback was removed.
        """

        callbacks = self._hooks.get(event)

        if not callbacks:
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
        Emit an event to all registered subscribers.
        """

        callbacks = self._hooks.get(event, ())

        for callback in tuple(callbacks):

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
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"enabled={self.enabled}, "
            f"running={self.running}, "
            f"profiles={self.profile_count}, "
            f"profilers={len(self.registry)})"
        )

    # -------------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        state = "running" if self.running else "idle"

        return (
            f"{self.name} "
            f"[{state}] "
            f"(profiles={self.profile_count}, "
            f"samples={self.sample_count})"
        )

    # -------------------------------------------------------------------------
    # Container Protocol
    # -------------------------------------------------------------------------

    def __len__(self) -> int:
        """
        Number of registered profiles.
        """

        return self.profile_count

    # -------------------------------------------------------------------------

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over registered profile names.
        """

        return iter(self._profiles)

    # -------------------------------------------------------------------------

    def __contains__(self, item: object) -> bool:
        """
        Membership test.

        Example
        -------
        "startup" in profiler
        """

        if not isinstance(item, str):
            return False

        return item in self._profiles

    # -------------------------------------------------------------------------
    # Callable Protocol
    # -------------------------------------------------------------------------

    def __call__(
        self,
        func: Optional[Callable[..., Any]] = None,
        *,
        name: Optional[str] = None,
    ):
        """
        Allow the integration instance to be used directly as a decorator.

        Example
        -------
        @profiler
        def train():
            ...

        @profiler(name="training")
        def train():
            ...
        """

        return self.profile(func, name=name)

    # -------------------------------------------------------------------------
    # Copy Protocol
    # -------------------------------------------------------------------------

    def __copy__(self) -> "MetricProfilingIntegration":
        """
        Shallow copy.
        """

        cls = self.__class__

        obj = cls.__new__(cls)

        obj.__dict__.update(self.__dict__)

        return obj

    # -------------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo: Optional[Dict[int, Any]] = None,
    ) -> "MetricProfilingIntegration":
        """
        Deep copy.
        """

        if memo is None:
            memo = {}

        cls = self.__class__

        obj = cls.__new__(cls)

        memo[id(self)] = obj

        for key, value in self.__dict__.items():
            setattr(obj, key, deepcopy(value, memo))

        return obj                                                                        