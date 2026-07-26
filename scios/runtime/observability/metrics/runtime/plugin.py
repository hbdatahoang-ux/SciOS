"""
SciOS-NG Runtime Metrics Plugin Engine

File:
    scios/runtime/observability/metrics/runtime/plugin.py

Description:
    Runtime extension framework for Metrics subsystem.

SciOS-NG v0.2
"""


from __future__ import annotations

from datetime import datetime
from threading import RLock
from typing import Any
from uuid import uuid4



# ==================================================================
# Part 1. Foundation
# ==================================================================


class MetricPlugin:
    """
    Runtime Metrics Plugin Engine.

    Responsibilities
    ----------------
    - Register metric extensions
    - Manage runtime plugins
    - Extend observability pipeline
    - Integrate Runtime Metrics components
    """

    VERSION = "0.2.0"



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        name: str = "MetricPlugin",
        description: str = "",
    ) -> None:


        # ----------------------------------------------------------
        # Identity
        # ----------------------------------------------------------

        self._id = str(
            uuid4()
        )

        self._name = name

        self._description = description



        # ----------------------------------------------------------
        # Plugin Components
        # ----------------------------------------------------------

        # Registered plugin objects

        self._registry: dict[str, Any] = {}


        # Provided metrics

        self._metrics: dict[str, Any] = {}


        # Runtime configuration

        self._config: dict[str, Any] = {}


        # Plugin dependencies

        self._dependencies: list[Any] = []



        # ----------------------------------------------------------
        # Runtime State
        # ----------------------------------------------------------

        self._enabled = True

        self._loaded = False

        self._initialized = False

        self._closed = False



        # ----------------------------------------------------------
        # Synchronization
        # ----------------------------------------------------------

        self._lock = RLock()



        # ----------------------------------------------------------
        # Metadata
        # ----------------------------------------------------------

        now = datetime.utcnow()

        self._created_at = now

        self._updated_at = now

        self._version = self.VERSION



        # ----------------------------------------------------------
        # Internal Components
        # ----------------------------------------------------------

        self._hooks: dict[str, list[Any]] = {}

        self._events: list[dict[str, Any]] = []

        self._snapshot: dict[str, Any] | None = None

        self._context: dict[str, Any] = {}



    # ==============================================================
    # Internal Utilities
    # ==============================================================

    def _touch(
        self,
    ):
        """
        Update runtime timestamp.
        """

        self._updated_at = datetime.utcnow()



    def _ensure_open(
        self,
    ):
        """
        Validate plugin state.
        """

        if self._closed:

            raise RuntimeError(
                "MetricPlugin is closed."
            )



    def _ensure_enabled(
        self,
    ):
        """
        Validate plugin availability.
        """

        self._ensure_open()


        if not self._enabled:

            raise RuntimeError(
                "MetricPlugin is disabled."
            )
# ==================================================================
# Part 2. Plugin API
# ==================================================================


# ------------------------------------------------------------------
# Lifecycle Control
# ------------------------------------------------------------------

def load(
    self,
) -> "MetricPlugin":
    """
    Load plugin into Runtime.
    """

    with self._lock:

        self._ensure_open()


        if self._loaded:

            return self


        self.before_load()


        self._loaded = True


        self._touch()


        self.after_load()


    return self



def unload(
    self,
) -> "MetricPlugin":
    """
    Unload plugin from Runtime.
    """

    with self._lock:

        self._ensure_open()


        self.before_unload()


        self._loaded = False

        self._initialized = False


        self._touch()


        self.after_unload()


    return self



def initialize(
    self,
) -> "MetricPlugin":
    """
    Initialize plugin resources.
    """

    with self._lock:

        self._ensure_enabled()


        if not self._loaded:

            self.load()


        if self._initialized:

            return self


        self.before_initialize()


        self._initialized = True


        self._touch()


        self.after_initialize()


    return self



def start(
    self,
) -> "MetricPlugin":
    """
    Start plugin execution.
    """

    with self._lock:

        self._ensure_enabled()


        if not self._initialized:

            self.initialize()


        self.before_start()


        self._touch()


        self.after_start()


    return self



def stop(
    self,
) -> "MetricPlugin":
    """
    Stop plugin execution.
    """

    with self._lock:

        self.before_stop()


        self._touch()


        self.after_stop()


    return self



def enable(
    self,
) -> "MetricPlugin":
    """
    Enable plugin.
    """

    with self._lock:

        self._ensure_open()


        self._enabled = True


        self._touch()


    return self



def disable(
    self,
) -> "MetricPlugin":
    """
    Disable plugin.
    """

    with self._lock:

        self._enabled = False


        self._touch()


    return self



# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

def configure(
    self,
    config: dict[str, Any],
) -> "MetricPlugin":
    """
    Configure plugin runtime.
    """

    with self._lock:

        self._ensure_enabled()


        self._config.update(
            config
        )


        self._touch()


    return self



# ------------------------------------------------------------------
# Component Management
# ------------------------------------------------------------------

def register_component(
    self,
    name: str,
    component: Any,
) -> "MetricPlugin":
    """
    Register plugin component.
    """

    with self._lock:

        self._ensure_enabled()


        self._registry[name] = component


        self._touch()


    return self



def remove_component(
    self,
    name: str,
) -> Any:
    """
    Remove plugin component.
    """

    with self._lock:

        component = self._registry.pop(
            name,
            None,
        )


        self._touch()


    return component



def attach(
    self,
    component: Any,
) -> "MetricPlugin":
    """
    Attach external dependency.
    """

    with self._lock:

        self._ensure_enabled()


        self._dependencies.append(
            component
        )


        self._touch()


    return self



def detach(
    self,
    component: Any,
) -> "MetricPlugin":
    """
    Detach external dependency.
    """

    with self._lock:

        if component in self._dependencies:

            self._dependencies.remove(
                component
            )


        self._touch()


    return self
# ==================================================================
# Part 3. Component Registry API
# ==================================================================

# ------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------

def register(
    self,
    name: str,
    component: Any,
) -> "MetricPlugin":
    """
    Register runtime plugin component.
    """

    return self.register_component(
        name,
        component,
    )



def unregister(
    self,
    name: str,
) -> Any:
    """
    Remove runtime plugin component.
    """

    return self.remove_component(
        name
    )



# ------------------------------------------------------------------
# Lookup
# ------------------------------------------------------------------

def contains(
    self,
    name: str,
) -> bool:
    """
    Check component existence.
    """

    return name in self._registry



def exists(
    self,
    name: str,
) -> bool:
    """
    Alias for contains().
    """

    return self.contains(
        name
    )



def get(
    self,
    name: str,
    default=None,
):
    """
    Get component.
    """

    return self._registry.get(
        name,
        default,
    )



def find(
    self,
    name: str,
):
    """
    Find component or raise error.
    """

    component = self.get(
        name
    )


    if component is None:

        raise KeyError(
            f"Unknown component: {name}"
        )


    return component



# ------------------------------------------------------------------
# Enumeration
# ------------------------------------------------------------------

def keys(
    self,
):
    """
    Return component names.
    """

    return self._registry.keys()



def values(
    self,
):
    """
    Return registered components.
    """

    return self._registry.values()



def items(
    self,
):
    """
    Return registry items.
    """

    return self._registry.items()



def components(
    self,
) -> list[Any]:
    """
    Return all components.
    """

    return list(
        self._registry.values()
    )



# ------------------------------------------------------------------
# Information
# ------------------------------------------------------------------

def count(
    self,
) -> int:
    """
    Number of registered components.
    """

    return len(
        self._registry
    )



def component_names(
    self,
) -> list[str]:
    """
    Return component names.
    """

    return list(
        self._registry.keys()
    )



# ------------------------------------------------------------------
# Maintenance
# ------------------------------------------------------------------

def clear_registry(
    self,
) -> "MetricPlugin":
    """
    Clear component registry.
    """

    with self._lock:

        self._ensure_enabled()


        self._registry.clear()


        self._touch()


    return self
# ==================================================================
# Part 4. Plugin Dependency & Extension API
# ==================================================================

# ------------------------------------------------------------------
# Dependency Management
# ------------------------------------------------------------------

def add_dependency(
    self,
    dependency: Any,
) -> "MetricPlugin":
    """
    Add plugin dependency.
    """

    with self._lock:

        self._ensure_enabled()


        if dependency not in self._dependencies:

            self._dependencies.append(
                dependency
            )


        self._touch()


    return self



def remove_dependency(
    self,
    dependency: Any,
) -> "MetricPlugin":
    """
    Remove plugin dependency.
    """

    with self._lock:

        if dependency in self._dependencies:

            self._dependencies.remove(
                dependency
            )


        self._touch()


    return self



def dependencies(
    self,
) -> list[Any]:
    """
    Return plugin dependencies.
    """

    return list(
        self._dependencies
    )



def has_dependency(
    self,
    dependency: Any,
) -> bool:
    """
    Check dependency existence.
    """

    return dependency in self._dependencies



# ------------------------------------------------------------------
# Extension Points
# ------------------------------------------------------------------

def provide(
    self,
    name: str,
    resource: Any,
) -> "MetricPlugin":
    """
    Provide runtime extension resource.
    """

    with self._lock:

        self._ensure_enabled()


        self._metrics[name] = resource


        self._touch()


    return self



def revoke(
    self,
    name: str,
) -> Any:
    """
    Remove provided resource.
    """

    with self._lock:

        resource = self._metrics.pop(
            name,
            None,
        )


        self._touch()


    return resource



def resource(
    self,
    name: str,
    default=None,
):
    """
    Retrieve provided resource.
    """

    return self._metrics.get(
        name,
        default,
    )



def resources(
    self,
):
    """
    Return all resources.
    """

    return self._metrics.items()



def resource_count(
    self,
) -> int:
    """
    Number of provided resources.
    """

    return len(
        self._metrics
    )



# ------------------------------------------------------------------
# Plugin Context
# ------------------------------------------------------------------

def set_context(
    self,
    key: str,
    value: Any,
) -> "MetricPlugin":
    """
    Set runtime plugin context.
    """

    with self._lock:

        self._context[key] = value


        self._touch()


    return self



def get_context(
    self,
    key: str,
    default=None,
):
    """
    Get runtime context value.
    """

    return self._context.get(
        key,
        default,
    )



def update_context(
    self,
    context: dict[str, Any],
) -> "MetricPlugin":
    """
    Update runtime context.
    """

    with self._lock:

        self._context.update(
            context
        )


        self._touch()


    return self



def clear_context(
    self,
) -> "MetricPlugin":
    """
    Clear runtime context.
    """

    with self._lock:

        self._context.clear()


        self._touch()


    return self
# ==================================================================
# Part 5. Lifecycle Management
# ==================================================================

# ------------------------------------------------------------------
# Lifecycle
# ------------------------------------------------------------------

def activate(
    self,
) -> "MetricPlugin":
    """
    Activate plugin runtime.
    """

    with self._lock:

        self._ensure_open()


        if not self._loaded:

            self.load()


        if not self._initialized:

            self.initialize()


        self._enabled = True


        self._touch()


        self.emit(
            "activate"
        )


    return self



def deactivate(
    self,
) -> "MetricPlugin":
    """
    Deactivate plugin runtime.
    """

    with self._lock:

        self._enabled = False


        self._touch()


        self.emit(
            "deactivate"
        )


    return self



def freeze(
    self,
) -> "MetricPlugin":
    """
    Freeze plugin state.
    """

    with self._lock:

        self._ensure_open()


        self._context[
            "frozen"
        ] = True


        self._touch()


        self.emit(
            "freeze"
        )


    return self



def unfreeze(
    self,
) -> "MetricPlugin":
    """
    Unfreeze plugin state.
    """

    with self._lock:

        self._ensure_open()


        self._context[
            "frozen"
        ] = False


        self._touch()


        self.emit(
            "unfreeze"
        )


    return self



def close(
    self,
) -> "MetricPlugin":
    """
    Close plugin permanently.
    """

    with self._lock:

        if self._closed:

            return self


        self.before_close()


        self._enabled = False

        self._loaded = False

        self._initialized = False

        self._closed = True


        self._registry.clear()

        self._metrics.clear()

        self._dependencies.clear()


        self._touch()


        self.after_close()


    return self



def reopen(
    self,
) -> "MetricPlugin":
    """
    Reopen closed plugin.
    """

    with self._lock:

        self._closed = False

        self._enabled = True


        self._touch()


        self.emit(
            "reopen"
        )


    return self



# ------------------------------------------------------------------
# Lifecycle Properties
# ------------------------------------------------------------------

@property
def enabled(
    self,
) -> bool:
    """
    Plugin enabled state.
    """

    return self._enabled



@property
def disabled(
    self,
) -> bool:
    """
    Plugin disabled state.
    """

    return not self._enabled



@property
def loaded(
    self,
) -> bool:
    """
    Plugin loaded state.
    """

    return self._loaded



@property
def initialized(
    self,
) -> bool:
    """
    Plugin initialized state.
    """

    return self._initialized



@property
def closed(
    self,
) -> bool:
    """
    Plugin closed state.
    """

    return self._closed



@property
def active(
    self,
) -> bool:
    """
    Plugin active state.
    """

    return (
        self._enabled
        and
        self._loaded
        and
        self._initialized
        and
        not self._closed
    )



@property
def frozen(
    self,
) -> bool:
    """
    Plugin frozen state.
    """

    return self._context.get(
        "frozen",
        False,
    )
# ==================================================================
# Part 6. Runtime Operations
# ==================================================================

from copy import copy as _copy
from copy import deepcopy


# ------------------------------------------------------------------
# Snapshot
# ------------------------------------------------------------------

def snapshot(
    self,
) -> dict[str, Any]:
    """
    Create plugin runtime snapshot.
    """

    with self._lock:

        snapshot = {

            "id": self._id,

            "name": self._name,

            "description":
                self._description,


            "registry":
                deepcopy(
                    self._registry
                ),


            "metrics":
                deepcopy(
                    self._metrics
                ),


            "config":
                deepcopy(
                    self._config
                ),


            "dependencies":
                deepcopy(
                    self._dependencies
                ),


            "enabled":
                self._enabled,


            "loaded":
                self._loaded,


            "initialized":
                self._initialized,


            "closed":
                self._closed,


            "context":
                deepcopy(
                    self._context
                ),


            "created_at":
                self._created_at,


            "updated_at":
                self._updated_at,


            "version":
                self._version,

        }


        self._snapshot = deepcopy(
            snapshot
        )


        return snapshot



def restore(
    self,
    snapshot: dict[str, Any] | None = None,
) -> "MetricPlugin":
    """
    Restore plugin runtime state.
    """

    with self._lock:

        data = (
            snapshot
            or self._snapshot
        )


        if data is None:

            raise RuntimeError(
                "No plugin snapshot available."
            )


        self._id = data[
            "id"
        ]


        self._name = data[
            "name"
        ]


        self._description = data[
            "description"
        ]


        self._registry = deepcopy(
            data["registry"]
        )


        self._metrics = deepcopy(
            data["metrics"]
        )


        self._config = deepcopy(
            data["config"]
        )


        self._dependencies = deepcopy(
            data["dependencies"]
        )


        self._enabled = data[
            "enabled"
        ]


        self._loaded = data[
            "loaded"
        ]


        self._initialized = data[
            "initialized"
        ]


        self._closed = data[
            "closed"
        ]


        self._context = deepcopy(
            data["context"]
        )


        self._created_at = data[
            "created_at"
        ]


        self._updated_at = data[
            "updated_at"
        ]


        self._version = data[
            "version"
        ]


        self._touch()


    return self



# ------------------------------------------------------------------
# Object Management
# ------------------------------------------------------------------

def clone(
    self,
) -> "MetricPlugin":
    """
    Deep clone plugin.
    """

    return deepcopy(
        self
    )



def copy(
    self,
) -> "MetricPlugin":
    """
    Shallow copy plugin.
    """

    return _copy(
        self
    )



# ------------------------------------------------------------------
# Runtime Cleanup
# ------------------------------------------------------------------

def clear(
    self,
) -> "MetricPlugin":
    """
    Clear runtime plugin data.
    """

    with self._lock:

        self._ensure_open()


        self._registry.clear()

        self._metrics.clear()

        self._context.clear()


        self._touch()


        self.emit(
            "clear"
        )


    return self



def compact(
    self,
) -> "MetricPlugin":
    """
    Compact empty runtime entries.
    """

    with self._lock:

        self._ensure_open()


        self._registry = {

            k: v

            for k, v
            in self._registry.items()

            if v is not None

        }


        self._metrics = {

            k: v

            for k, v
            in self._metrics.items()

            if v is not None

        }


        self._dependencies = [

            dep

            for dep
            in self._dependencies

            if dep is not None

        ]


        self._touch()


    return self



def cleanup(
    self,
) -> "MetricPlugin":
    """
    Full runtime cleanup.
    """

    with self._lock:

        self.compact()

        self._events.clear()

        self._snapshot = None


        self._touch()


        self.emit(
            "cleanup"
        )


    return self
# ==================================================================
# Part 7. Statistics & Diagnostics
# ==================================================================


# ------------------------------------------------------------------
# Runtime Metrics
# ------------------------------------------------------------------

@property
def component_count(
    self,
) -> int:
    """
    Number of registered components.
    """

    return len(
        self._registry
    )



@property
def resource_count(
    self,
) -> int:
    """
    Number of provided resources.
    """

    return len(
        self._metrics
    )



@property
def dependency_count(
    self,
) -> int:
    """
    Number of dependencies.
    """

    return len(
        self._dependencies
    )



@property
def event_count(
    self,
) -> int:
    """
    Number of emitted events.
    """

    return len(
        self._events
    )



@property
def uptime(
    self,
) -> float:
    """
    Plugin uptime in seconds.
    """

    return (
        datetime.utcnow()
        -
        self._created_at
    ).total_seconds()



# ------------------------------------------------------------------
# Statistics
# ------------------------------------------------------------------

def summary(
    self,
) -> dict[str, Any]:
    """
    Return plugin summary.
    """

    return {

        "id":
            self._id,

        "name":
            self._name,

        "version":
            self._version,


        "components":
            self.component_count,


        "resources":
            self.resource_count,


        "dependencies":
            self.dependency_count,


        "events":
            self.event_count,


        "enabled":
            self.enabled,


        "loaded":
            self.loaded,


        "initialized":
            self.initialized,


        "active":
            self.active,


        "closed":
            self.closed,

    }



def statistics(
    self,
) -> dict[str, Any]:
    """
    Detailed plugin statistics.
    """

    return {

        **self.summary(),


        "uptime":
            self.uptime,


        "created_at":
            self._created_at,


        "updated_at":
            self._updated_at,


        "context_size":
            len(
                self._context
            ),

    }



def report(
    self,
) -> dict[str, Any]:
    """
    Generate runtime plugin report.
    """

    return {

        "summary":
            self.summary(),


        "statistics":
            self.statistics(),


        "status":
            self.status(),


        "health":
            self.health(),


        "diagnostics":
            self.diagnostics(),

    }



# ------------------------------------------------------------------
# Diagnostics
# ------------------------------------------------------------------

def health(
    self,
) -> str:
    """
    Plugin health state.
    """

    if self.closed:

        return "closed"



    if self.disabled:

        return "disabled"



    if not self.loaded:

        return "unloaded"



    if not self.initialized:

        return "not_initialized"



    return "healthy"



def status(
    self,
) -> dict[str, Any]:
    """
    Runtime status.
    """

    return {

        "health":
            self.health(),


        "enabled":
            self.enabled,


        "loaded":
            self.loaded,


        "initialized":
            self.initialized,


        "closed":
            self.closed,


        "active":
            self.active,


        "frozen":
            self.frozen,

    }



def performance(
    self,
) -> dict[str, Any]:
    """
    Plugin performance metrics.
    """

    return {

        "components":
            self.component_count,


        "resources":
            self.resource_count,


        "dependencies":
            self.dependency_count,


        "events":
            self.event_count,


        "uptime":
            self.uptime,

    }



def diagnostics(
    self,
) -> dict[str, Any]:
    """
    Full diagnostics information.
    """

    return {

        "identity": {

            "id":
                self._id,

            "name":
                self._name,

            "version":
                self._version,

        },


        "state":
            self.status(),


        "runtime":
            self.performance(),


        "registry": {

            "components":
                self.component_names(),

            "resources":
                list(
                    self._metrics.keys()
                ),

        },


        "dependencies":
            self.dependency_count,

    }
# ==================================================================
# Part 8. Serialization
# ==================================================================

import json
import pickle

try:
    import yaml
except ImportError:
    yaml = None


try:
    import msgpack
except ImportError:
    msgpack = None



# ------------------------------------------------------------------
# Object Serialization
# ------------------------------------------------------------------

def to_dict(
    self,
) -> dict[str, Any]:
    """
    Convert plugin state to dictionary.
    """

    return {

        "id":
            self._id,

        "name":
            self._name,

        "description":
            self._description,


        "registry":
            self._registry,


        "metrics":
            self._metrics,


        "config":
            self._config,


        "dependencies":
            self._dependencies,


        "enabled":
            self._enabled,


        "loaded":
            self._loaded,


        "initialized":
            self._initialized,


        "closed":
            self._closed,


        "context":
            self._context,


        "created_at":
            self._created_at.isoformat(),


        "updated_at":
            self._updated_at.isoformat(),


        "version":
            self._version,

    }



@classmethod
def from_dict(
    cls,
    data: dict[str, Any],
) -> "MetricPlugin":
    """
    Restore plugin from dictionary.
    """

    plugin = cls(
        name=data.get(
            "name",
            "MetricPlugin",
        ),
        description=data.get(
            "description",
            "",
        ),
    )


    plugin._id = data.get(
        "id",
        plugin._id,
    )


    plugin._registry = data.get(
        "registry",
        {},
    )


    plugin._metrics = data.get(
        "metrics",
        {},
    )


    plugin._config = data.get(
        "config",
        {},
    )


    plugin._dependencies = data.get(
        "dependencies",
        [],
    )


    plugin._enabled = data.get(
        "enabled",
        True,
    )


    plugin._loaded = data.get(
        "loaded",
        False,
    )


    plugin._initialized = data.get(
        "initialized",
        False,
    )


    plugin._closed = data.get(
        "closed",
        False,
    )


    plugin._context = data.get(
        "context",
        {},
    )


    if "created_at" in data:

        plugin._created_at = datetime.fromisoformat(
            data["created_at"]
        )


    if "updated_at" in data:

        plugin._updated_at = datetime.fromisoformat(
            data["updated_at"]
        )


    plugin._version = data.get(
        "version",
        cls.VERSION,
    )


    return plugin



# ------------------------------------------------------------------
# JSON
# ------------------------------------------------------------------

def to_json(
    self,
    **kwargs,
) -> str:
    """
    Serialize plugin to JSON.
    """

    return json.dumps(
        self.to_dict(),
        default=str,
        **kwargs,
    )



@classmethod
def from_json(
    cls,
    data: str,
) -> "MetricPlugin":
    """
    Restore plugin from JSON.
    """

    return cls.from_dict(
        json.loads(
            data
        )
    )



# ------------------------------------------------------------------
# Generic Serialization
# ------------------------------------------------------------------

def serialize(
    self,
    fmt: str = "json",
):
    """
    Serialize plugin.

    Supported:
        json
        yaml
        pickle
        msgpack
    """

    fmt = fmt.lower()


    if fmt == "json":

        return self.to_json(
            indent=2
        )


    if fmt == "yaml":

        if yaml is None:

            raise RuntimeError(
                "PyYAML is not installed."
            )


        return yaml.safe_dump(
            self.to_dict(),
            sort_keys=False,
        )


    if fmt == "pickle":

        return pickle.dumps(
            self.to_dict()
        )


    if fmt == "msgpack":

        if msgpack is None:

            raise RuntimeError(
                "msgpack is not installed."
            )


        return msgpack.packb(
            self.to_dict(),
            use_bin_type=True,
        )


    raise ValueError(
        f"Unsupported format: {fmt}"
    )



@classmethod
def deserialize(
    cls,
    data,
    fmt: str = "json",
) -> "MetricPlugin":
    """
    Deserialize plugin state.
    """

    fmt = fmt.lower()


    if fmt == "json":

        return cls.from_json(
            data
        )


    if fmt == "yaml":

        if yaml is None:

            raise RuntimeError(
                "PyYAML is not installed."
            )


        return cls.from_dict(
            yaml.safe_load(
                data
            )
        )


    if fmt == "pickle":

        return cls.from_dict(
            pickle.loads(
                data
            )
        )


    if fmt == "msgpack":

        if msgpack is None:

            raise RuntimeError(
                "msgpack is not installed."
            )


        return cls.from_dict(
            msgpack.unpackb(
                data,
                raw=False,
            )
        )


    raise ValueError(
        f"Unsupported format: {fmt}"
    )



# ------------------------------------------------------------------
# Import / Export
# ------------------------------------------------------------------

def export(
    self,
    path: str,
    fmt: str = "json",
) -> None:
    """
    Export plugin state.
    """

    data = self.serialize(
        fmt
    )


    binary = fmt.lower() in {
        "pickle",
        "msgpack",
    }


    mode = (
        "wb"
        if binary
        else "w"
    )


    with open(
        path,
        mode,
    ) as file:

        file.write(
            data
        )



@classmethod
def import_data(
    cls,
    path: str,
    fmt: str = "json",
) -> "MetricPlugin":
    """
    Import plugin state.
    """

    binary = fmt.lower() in {
        "pickle",
        "msgpack",
    }


    mode = (
        "rb"
        if binary
        else "r"
    )


    with open(
        path,
        mode,
    ) as file:

        data = file.read()


    return cls.deserialize(
        data,
        fmt,
    )
# ==================================================================
# Part 9. Events & Hooks
# ==================================================================

from typing import Callable


# ------------------------------------------------------------------
# Plugin Events
# ------------------------------------------------------------------

def before_load(
    self,
) -> None:
    """
    Trigger before plugin loading.
    """

    self.emit(
        "before_load"
    )



def after_load(
    self,
) -> None:
    """
    Trigger after plugin loading.
    """

    self.emit(
        "after_load"
    )



def before_unload(
    self,
) -> None:
    """
    Trigger before plugin unloading.
    """

    self.emit(
        "before_unload"
    )



def after_unload(
    self,
) -> None:
    """
    Trigger after plugin unloading.
    """

    self.emit(
        "after_unload"
    )



def before_initialize(
    self,
) -> None:
    """
    Trigger before initialization.
    """

    self.emit(
        "before_initialize"
    )



def after_initialize(
    self,
) -> None:
    """
    Trigger after initialization.
    """

    self.emit(
        "after_initialize"
    )



def before_start(
    self,
) -> None:
    """
    Trigger before plugin start.
    """

    self.emit(
        "before_start"
    )



def after_start(
    self,
) -> None:
    """
    Trigger after plugin start.
    """

    self.emit(
        "after_start"
    )



def before_close(
    self,
) -> None:
    """
    Trigger before plugin close.
    """

    self.emit(
        "before_close"
    )



def after_close(
    self,
) -> None:
    """
    Trigger after plugin close.
    """

    self.emit(
        "after_close"
    )



# ------------------------------------------------------------------
# Hook Management
# ------------------------------------------------------------------

def add_hook(
    self,
    event: str,
    callback: Callable,
) -> "MetricPlugin":
    """
    Register event callback.
    """

    with self._lock:

        if event not in self._hooks:

            self._hooks[event] = []


        self._hooks[event].append(
            callback
        )


    return self



def remove_hook(
    self,
    event: str,
    callback: Callable,
) -> "MetricPlugin":
    """
    Remove event callback.
    """

    with self._lock:

        hooks = self._hooks.get(
            event,
            [],
        )


        if callback in hooks:

            hooks.remove(
                callback
            )


    return self



def clear_hooks(
    self,
    event: str | None = None,
) -> "MetricPlugin":
    """
    Clear registered hooks.
    """

    with self._lock:

        if event is None:

            self._hooks.clear()

        else:

            self._hooks.pop(
                event,
                None,
            )


    return self



# ------------------------------------------------------------------
# Event Dispatcher
# ------------------------------------------------------------------

def emit(
    self,
    event: str,
    **payload,
) -> None:
    """
    Emit runtime plugin event.
    """

    record = {

        "event":
            event,

        "timestamp":
            datetime.utcnow(),

        "payload":
            payload,

    }


    self._events.append(
        record
    )


    self.notify(
        event,
        **payload,
    )



def notify(
    self,
    event: str,
    **payload,
) -> None:
    """
    Notify event subscribers.
    """

    callbacks = self._hooks.get(
        event,
        [],
    )


    for callback in callbacks:

        callback(
            **payload
        )



def subscribe(
    self,
    event: str,
    callback: Callable,
) -> "MetricPlugin":
    """
    Subscribe callback to event.
    """

    return self.add_hook(
        event,
        callback,
    )



def unsubscribe(
    self,
    event: str,
    callback: Callable,
) -> "MetricPlugin":
    """
    Remove event subscriber.
    """

    return self.remove_hook(
        event,
        callback,
    )
# ==================================================================
# Part 10. Python Protocols
# ==================================================================


from copy import copy as _copy
from copy import deepcopy



# ------------------------------------------------------------------
# Representation
# ------------------------------------------------------------------

def __repr__(
    self,
) -> str:
    """
    Developer representation.
    """

    return (
        f"{self.__class__.__name__}("
        f"id={self._id!r}, "
        f"name={self._name!r}, "
        f"components={self.component_count}, "
        f"active={self.active}"
        f")"
    )



def __str__(
    self,
) -> str:
    """
    Human readable representation.
    """

    return (
        f"{self._name} "
        f"[version={self._version}, "
        f"components={self.component_count}, "
        f"active={self.active}]"
    )



# ------------------------------------------------------------------
# Container Protocol
# ------------------------------------------------------------------

def __len__(
    self,
) -> int:
    """
    Number of registered components.
    """

    return self.component_count



def __iter__(
    self,
):
    """
    Iterate registered components.
    """

    return iter(
        self._registry
    )



def __contains__(
    self,
    name: str,
) -> bool:
    """
    Component existence check.
    """

    return self.contains(
        name
    )



# ------------------------------------------------------------------
# Mapping Protocol
# ------------------------------------------------------------------

def __getitem__(
    self,
    name: str,
):
    """
    Dictionary style access.
    """

    return self.get(
        name
    )



def __setitem__(
    self,
    name: str,
    component: Any,
) -> None:
    """
    Dictionary style registration.
    """

    self.register(
        name,
        component,
    )



def __delitem__(
    self,
    name: str,
) -> None:
    """
    Dictionary style removal.
    """

    self.unregister(
        name
    )



# ------------------------------------------------------------------
# Context Manager
# ------------------------------------------------------------------

def __enter__(
    self,
) -> "MetricPlugin":
    """
    Enter plugin runtime context.
    """

    self.activate()

    return self



def __exit__(
    self,
    exc_type,
    exc_value,
    traceback,
) -> bool:
    """
    Exit plugin runtime context.
    """

    self.close()

    return False



# ------------------------------------------------------------------
# Callable
# ------------------------------------------------------------------

def __call__(
    self,
    component: str,
    *args,
    **kwargs,
):
    """
    Execute registered component.

    Example:
        plugin("collector")
    """

    target = self.get(
        component
    )


    if target is None:

        raise KeyError(
            f"Unknown component: {component}"
        )


    if callable(target):

        return target(
            *args,
            **kwargs
        )


    return target



# ------------------------------------------------------------------
# Copy Protocol
# ------------------------------------------------------------------

def __copy__(
    self,
):
    """
    Shallow copy.
    """

    return self.copy()



def __deepcopy__(
    self,
    memo,
):
    """
    Deep copy.
    """

    return self.clone()                                            