"""
SciOS-NG Runtime Metrics Dispatcher Engine

File:
    scios/runtime/observability/metrics/runtime/dispatcher.py

Description
-----------
Runtime dispatcher engine responsible for routing, handling,
and coordinating Runtime Metrics events.

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


class MetricDispatcher:
    """
    Runtime Metrics Dispatcher Engine.

    Responsibilities
    ----------------
    - Metric routing
    - Event dispatching
    - Handler orchestration
    - Subscriber notification
    - Runtime coordination
    """

    VERSION = "0.2.0"


    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        name: str = "MetricDispatcher",
        description: str = "",
    ) -> None:
        """
        Initialize Runtime Metrics Dispatcher.
        """

        # ----------------------------------------------------------
        # Identity
        # ----------------------------------------------------------

        self._id: str = str(uuid4())

        self._name: str = name

        self._description: str = description


        # ----------------------------------------------------------
        # Routing
        # ----------------------------------------------------------

        # Ordered routing rules
        self._routes: list[Any] = []

        # Named route registry
        self._route_registry: dict[str, Any] = {}

        # Runtime handlers
        self._handlers: dict[str, Any] = {}

        # Event subscribers
        self._subscribers: dict[str, list[Any]] = {}


        # ----------------------------------------------------------
        # Runtime State
        # ----------------------------------------------------------

        self._enabled: bool = True

        self._frozen: bool = False

        self._closed: bool = False


        # ----------------------------------------------------------
        # Synchronization
        # ----------------------------------------------------------

        self._lock = RLock()


        # ----------------------------------------------------------
        # Metadata
        # ----------------------------------------------------------

        now = datetime.utcnow()

        self._created_at: datetime = now

        self._updated_at: datetime = now

        self._version: str = self.VERSION


        # ----------------------------------------------------------
        # Internal Components
        # ----------------------------------------------------------

        self._statistics: dict[str, Any] = {
            "dispatch_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "route_count": 0,
            "handler_count": 0,
        }

        self._hooks: dict[str, list[Any]] = {}

        self._events: list[dict[str, Any]] = []

        self._snapshot: dict[str, Any] | None = None

        self._context: dict[str, Any] = {}


    # ==============================================================
    # Internal Utilities
    # ==============================================================

    def _touch(self) -> None:
        """
        Update runtime timestamp.
        """
        self._updated_at = datetime.utcnow()


    def _ensure_writable(self) -> None:
        """
        Validate dispatcher state.
        """

        if self._closed:
            raise RuntimeError(
                "MetricDispatcher is closed."
            )

        if self._frozen:
            raise RuntimeError(
                "MetricDispatcher is frozen."
            )

        if not self._enabled:
            raise RuntimeError(
                "MetricDispatcher is disabled."
            )
# ==================================================================
# Part 2. Dispatch API
# ==================================================================


# ------------------------------------------------------------------
# Dispatch
# ------------------------------------------------------------------

def dispatch(
    self,
    payload: Any = None,
    target: str | None = None,
) -> Any:
    """
    Main Runtime Metrics dispatch entry.
    """

    with self._lock:

        self._ensure_writable()

        self.before_dispatch(
            payload
        )

        try:

            if target:
                result = self.route(
                    target,
                    payload,
                )

            else:
                result = self.broadcast(
                    payload
                )

            self._statistics[
                "dispatch_count"
            ] += 1

            self._statistics[
                "success_count"
            ] += 1

            self._touch()

            self.after_dispatch(
                result
            )

            return result

        except Exception:

            self._statistics[
                "failure_count"
            ] += 1

            raise



def dispatch_metric(
    self,
    metric: Any,
    target: str | None = None,
) -> Any:
    """
    Dispatch a Runtime Metric.
    """

    return self.dispatch(
        {
            "type": "metric",
            "data": metric,
        },
        target,
    )



def dispatch_event(
    self,
    event: Any,
    target: str | None = None,
) -> Any:
    """
    Dispatch a Runtime Event.
    """

    return self.dispatch(
        {
            "type": "event",
            "data": event,
        },
        target,
    )



def dispatch_batch(
    self,
    payloads: list[Any],
) -> list[Any]:
    """
    Dispatch multiple payloads.
    """

    results = []

    for payload in payloads:

        results.append(
            self.dispatch(
                payload
            )
        )

    return results



# ------------------------------------------------------------------
# Routing
# ------------------------------------------------------------------

def route(
    self,
    name: str,
    payload: Any = None,
) -> Any:
    """
    Route payload to registered handler.
    """

    self.before_route(
        name,
        payload,
    )

    handler = self._handlers.get(
        name
    )

    if handler is None:

        route = self._route_registry.get(
            name
        )

        if route is not None:
            handler = route


    if handler is None:
        raise KeyError(
            f"Unknown route: {name}"
        )


    result = self.handle(
        handler,
        payload,
    )

    self.after_route(
        name,
        result,
    )

    return result



def forward(
    self,
    target: str,
    payload: Any = None,
) -> Any:
    """
    Forward payload to another route.
    """

    return self.route(
        target,
        payload,
    )



def broadcast(
    self,
    payload: Any = None,
) -> list[Any]:
    """
    Broadcast payload to all handlers.
    """

    results = []

    for name in self._handlers:

        results.append(
            self.route(
                name,
                payload,
            )
        )

    return results



# ------------------------------------------------------------------
# Processing
# ------------------------------------------------------------------

def handle(
    self,
    handler: Any,
    payload: Any = None,
) -> Any:
    """
    Execute handler.
    """

    self.before_handle(
        handler,
        payload,
    )

    try:

        if hasattr(
            handler,
            "handle",
        ):

            result = handler.handle(
                payload
            )

        elif callable(handler):

            result = handler(
                payload
            )

        else:

            raise TypeError(
                "Handler is not executable."
            )


        self.after_handle(
            handler,
            result,
        )

        return result


    except Exception:

        self._statistics[
            "failure_count"
        ] += 1

        raise



def process(
    self,
    payload: Any = None,
) -> Any:
    """
    Process runtime payload.
    """

    return self.dispatch(
        payload
    )



def execute(
    self,
    payload: Any = None,
) -> Any:
    """
    Execute dispatcher.
    """

    return self.dispatch(
        payload
    )



# ------------------------------------------------------------------
# Runtime
# ------------------------------------------------------------------

def update(
    self,
    context: dict[str, Any] | None = None,
) -> "MetricDispatcher":
    """
    Update dispatcher runtime context.
    """

    with self._lock:

        self._ensure_writable()

        if context:
            self._context.update(
                context
            )

        self._touch()

    return self



def flush(
    self,
) -> "MetricDispatcher":
    """
    Flush runtime context.
    """

    with self._lock:

        self._context.clear()

        self._touch()

    return self



def reset(
    self,
) -> "MetricDispatcher":
    """
    Reset dispatcher runtime state.
    """

    with self._lock:

        self._context.clear()

        self._statistics.update(
            {
                "dispatch_count": 0,
                "success_count": 0,
                "failure_count": 0,
            }
        )

        self._touch()

    return self
# ==================================================================
# Part 3. Route Registry API
# ==================================================================

# ------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------

def register_route(
    self,
    name: str,
    route: Any,
) -> Any:
    """
    Register a Runtime Metric route.
    """

    with self._lock:

        self._ensure_writable()

        self._route_registry[name] = route

        if route not in self._routes:
            self._routes.append(route)

        self._statistics[
            "route_count"
        ] = len(
            self._route_registry
        )

        self._touch()

        return route



def unregister_route(
    self,
    name: str,
) -> Any:
    """
    Remove a registered route.
    """

    with self._lock:

        route = self._route_registry.pop(
            name,
            None,
        )

        if route in self._routes:
            self._routes.remove(
                route
            )

        self._statistics[
            "route_count"
        ] = len(
            self._route_registry
        )

        self._touch()

        return route



# ------------------------------------------------------------------
# Lookup
# ------------------------------------------------------------------

def contains_route(
    self,
    name: str,
) -> bool:
    """
    Check route existence.
    """

    return name in self._route_registry



def exists_route(
    self,
    name: str,
) -> bool:
    """
    Alias for contains_route().
    """

    return self.contains_route(
        name
    )



def get_route(
    self,
    name: str,
    default=None,
):
    """
    Get route by name.
    """

    return self._route_registry.get(
        name,
        default,
    )



def find_route(
    self,
    name: str,
):
    """
    Find route or raise error.
    """

    route = self.get_route(
        name
    )

    if route is None:

        raise KeyError(
            f"Unknown route: {name}"
        )

    return route



# ------------------------------------------------------------------
# Enumeration
# ------------------------------------------------------------------

def routes(
    self,
) -> list[Any]:
    """
    Return ordered routes.
    """

    return list(
        self._routes
    )



def keys(
    self,
):
    """
    Return route names.
    """

    return self._route_registry.keys()



def values(
    self,
):
    """
    Return route objects.
    """

    return self._route_registry.values()



def items(
    self,
):
    """
    Return route registry items.
    """

    return self._route_registry.items()



# ------------------------------------------------------------------
# Information
# ------------------------------------------------------------------

def route_count(
    self,
) -> int:
    """
    Return number of routes.
    """

    return len(
        self._route_registry
    )



def route_names(
    self,
) -> list[str]:
    """
    Return route names.
    """

    return list(
        self._route_registry.keys()
    )



# ------------------------------------------------------------------
# Maintenance
# ------------------------------------------------------------------

def clear_routes(
    self,
) -> "MetricDispatcher":
    """
    Clear all registered routes.
    """

    with self._lock:

        self._ensure_writable()

        self._route_registry.clear()

        self._routes.clear()

        self._statistics[
            "route_count"
        ] = 0

        self._touch()

    return self
# ==================================================================
# Part 4. Handler Management
# ==================================================================

import asyncio
from concurrent.futures import ThreadPoolExecutor


# ------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------

def register_handler(
    self,
    name: str,
    handler: Any,
) -> Any:
    """
    Register Runtime Metric handler.
    """

    with self._lock:

        self._ensure_writable()

        self._handlers[name] = handler

        self._statistics[
            "handler_count"
        ] = len(
            self._handlers
        )

        self._touch()

        return handler



def remove_handler(
    self,
    name: str,
) -> Any:
    """
    Remove Runtime Metric handler.
    """

    with self._lock:

        handler = self._handlers.pop(
            name,
            None,
        )

        self._statistics[
            "handler_count"
        ] = len(
            self._handlers
        )

        self._touch()

        return handler



# ------------------------------------------------------------------
# Lookup
# ------------------------------------------------------------------

def handler(
    self,
    name: str,
    default=None,
):
    """
    Get handler by name.
    """

    return self._handlers.get(
        name,
        default,
    )



def handlers(
    self,
) -> dict[str, Any]:
    """
    Return all handlers.
    """

    return dict(
        self._handlers
    )



# ------------------------------------------------------------------
# Execution
# ------------------------------------------------------------------

def call_handler(
    self,
    name: str,
    payload: Any = None,
) -> Any:
    """
    Call handler by name.
    """

    handler = self.handler(
        name
    )

    if handler is None:

        raise KeyError(
            f"Unknown handler: {name}"
        )

    return self.invoke_handler(
        handler,
        payload,
    )



def invoke_handler(
    self,
    handler: Any,
    payload: Any = None,
) -> Any:
    """
    Invoke handler object.
    """

    self.before_handle(
        handler,
        payload,
    )

    try:

        if hasattr(
            handler,
            "handle",
        ):

            result = handler.handle(
                payload
            )

        elif callable(handler):

            result = handler(
                payload
            )

        else:

            raise TypeError(
                "Handler is not executable."
            )


        self.after_handle(
            handler,
            result,
        )

        return result


    except Exception:

        self._statistics[
            "failure_count"
        ] += 1

        raise



# ------------------------------------------------------------------
# Handler Strategies
# ------------------------------------------------------------------

def sync(
    self,
    handler: Any,
    payload: Any = None,
) -> Any:
    """
    Execute handler synchronously.
    """

    return self.invoke_handler(
        handler,
        payload,
    )



async def async_execute(
    self,
    handler: Any,
    payload: Any = None,
) -> Any:
    """
    Execute handler asynchronously.
    """

    loop = asyncio.get_running_loop()

    return await loop.run_in_executor(
        None,
        self.invoke_handler,
        handler,
        payload,
    )



def parallel(
    self,
    handlers: list[Any],
    payload: Any = None,
) -> list[Any]:
    """
    Execute multiple handlers in parallel.
    """

    with ThreadPoolExecutor() as executor:

        futures = [
            executor.submit(
                self.invoke_handler,
                handler,
                payload,
            )
            for handler in handlers
        ]

        return [
            future.result()
            for future in futures
        ]



# ------------------------------------------------------------------
# Strategy Management
# ------------------------------------------------------------------

def register_strategy(
    self,
    name: str,
    strategy: Any,
) -> "MetricDispatcher":
    """
    Register handler execution strategy.
    """

    if not hasattr(
        self,
        "_strategy_registry",
    ):

        self._strategy_registry = {}


    self._strategy_registry[name] = strategy

    return self



def remove_strategy(
    self,
    name: str,
) -> "MetricDispatcher":
    """
    Remove execution strategy.
    """

    registry = getattr(
        self,
        "_strategy_registry",
        {},
    )

    registry.pop(
        name,
        None,
    )

    return self



def strategy(
    self,
    name: str | None = None,
):
    """
    Get handler strategy.
    """

    builtin = {
        "sync": self.sync,
        "async": self.async_execute,
        "parallel": self.parallel,
    }


    if name is None:

        return getattr(
            self,
            "_strategy",
            "sync",
        )


    if name in builtin:

        self._strategy = name

        return builtin[name]


    registry = getattr(
        self,
        "_strategy_registry",
        {},
    )


    if name not in registry:

        raise KeyError(
            f"Unknown strategy: {name}"
        )


    self._strategy = name

    return registry[name]
# ==================================================================
# Part 5. Lifecycle Management
# ==================================================================

# ------------------------------------------------------------------
# Lifecycle
# ------------------------------------------------------------------

def enable(
    self,
) -> "MetricDispatcher":
    """
    Enable dispatcher.
    """

    with self._lock:

        if self._closed:
            raise RuntimeError(
                "MetricDispatcher is closed."
            )

        self._enabled = True

        self._touch()

    return self



def disable(
    self,
) -> "MetricDispatcher":
    """
    Disable dispatcher.
    """

    with self._lock:

        if self._closed:
            raise RuntimeError(
                "MetricDispatcher is closed."
            )

        self._enabled = False

        self._touch()

    return self



def freeze(
    self,
) -> "MetricDispatcher":
    """
    Freeze dispatcher modifications.
    """

    with self._lock:

        if self._closed:
            raise RuntimeError(
                "MetricDispatcher is closed."
            )

        self._frozen = True

        self._touch()

    return self



def unfreeze(
    self,
) -> "MetricDispatcher":
    """
    Unfreeze dispatcher.
    """

    with self._lock:

        if self._closed:
            raise RuntimeError(
                "MetricDispatcher is closed."
            )

        self._frozen = False

        self._touch()

    return self



def close(
    self,
) -> "MetricDispatcher":
    """
    Close dispatcher.
    """

    with self._lock:

        self.before_close()

        self._enabled = False

        self._frozen = False

        self._closed = True

        self._touch()

        self.after_close()

    return self



def reopen(
    self,
) -> "MetricDispatcher":
    """
    Reopen closed dispatcher.
    """

    with self._lock:

        self._closed = False

        self._enabled = True

        self._frozen = False

        self._touch()

    return self



# ------------------------------------------------------------------
# Properties
# ------------------------------------------------------------------

@property
def enabled(
    self,
) -> bool:
    """
    Dispatcher enabled state.
    """

    return self._enabled



@property
def disabled(
    self,
) -> bool:
    """
    Dispatcher disabled state.
    """

    return not self._enabled



@property
def frozen(
    self,
) -> bool:
    """
    Dispatcher frozen state.
    """

    return self._frozen



@property
def closed(
    self,
) -> bool:
    """
    Dispatcher closed state.
    """

    return self._closed



@property
def active(
    self,
) -> bool:
    """
    Dispatcher active state.
    """

    return (
        self._enabled
        and not self._frozen
        and not self._closed
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
    Create Runtime Dispatcher snapshot.
    """

    with self._lock:

        snapshot = {
            "id": self._id,
            "name": self._name,
            "description": self._description,

            "routes": deepcopy(
                self._routes
            ),

            "route_registry": deepcopy(
                self._route_registry
            ),

            "handlers": deepcopy(
                self._handlers
            ),

            "subscribers": deepcopy(
                self._subscribers
            ),

            "context": deepcopy(
                self._context
            ),

            "statistics": deepcopy(
                self._statistics
            ),

            "enabled": self._enabled,
            "frozen": self._frozen,
            "closed": self._closed,

            "created_at": self._created_at,
            "updated_at": self._updated_at,

            "version": self._version,
        }

        self._snapshot = deepcopy(
            snapshot
        )

        return snapshot



def restore(
    self,
    snapshot: dict[str, Any] | None = None,
) -> "MetricDispatcher":
    """
    Restore dispatcher state.
    """

    with self._lock:

        data = (
            snapshot
            or self._snapshot
        )

        if data is None:

            raise RuntimeError(
                "No snapshot available."
            )


        self._id = data["id"]

        self._name = data["name"]

        self._description = data[
            "description"
        ]


        self._routes = deepcopy(
            data["routes"]
        )

        self._route_registry = deepcopy(
            data["route_registry"]
        )

        self._handlers = deepcopy(
            data["handlers"]
        )

        self._subscribers = deepcopy(
            data["subscribers"]
        )


        self._context = deepcopy(
            data["context"]
        )

        self._statistics = deepcopy(
            data["statistics"]
        )


        self._enabled = data[
            "enabled"
        ]

        self._frozen = data[
            "frozen"
        ]

        self._closed = data[
            "closed"
        ]


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
) -> "MetricDispatcher":
    """
    Deep clone dispatcher.
    """

    return deepcopy(
        self
    )



def copy(
    self,
) -> "MetricDispatcher":
    """
    Shallow copy dispatcher.
    """

    return _copy(
        self
    )



# ------------------------------------------------------------------
# Cleanup
# ------------------------------------------------------------------

def clear(
    self,
) -> "MetricDispatcher":
    """
    Clear runtime data.
    """

    with self._lock:

        self._ensure_writable()

        self._context.clear()

        self._events.clear()

        self._touch()


    return self



def compact(
    self,
) -> "MetricDispatcher":
    """
    Compact runtime registries.
    """

    with self._lock:

        self._ensure_writable()


        self._routes = [
            route
            for route in self._routes
            if route is not None
        ]


        self._route_registry = {
            name: route
            for name, route
            in self._route_registry.items()
            if route is not None
        }


        self._handlers = {
            name: handler
            for name, handler
            in self._handlers.items()
            if handler is not None
        }


        self._statistics[
            "route_count"
        ] = len(
            self._route_registry
        )


        self._statistics[
            "handler_count"
        ] = len(
            self._handlers
        )


        self._touch()


    return self



def cleanup(
    self,
) -> "MetricDispatcher":
    """
    Cleanup dispatcher runtime.
    """

    with self._lock:

        self.compact()

        self.clear()

        self._touch()


    return self
# ==================================================================
# Part 7. Statistics & Diagnostics
# ==================================================================

from datetime import datetime


# ------------------------------------------------------------------
# Runtime Metrics
# ------------------------------------------------------------------

@property
def dispatch_count(
    self,
) -> int:
    """
    Total dispatch operations.
    """

    return self._statistics.get(
        "dispatch_count",
        0,
    )



@property
def success_count(
    self,
) -> int:
    """
    Successful dispatch operations.
    """

    return self._statistics.get(
        "success_count",
        0,
    )



@property
def failure_count(
    self,
) -> int:
    """
    Failed dispatch operations.
    """

    return self._statistics.get(
        "failure_count",
        0,
    )



@property
def route_count(
    self,
) -> int:
    """
    Number of registered routes.
    """

    return len(
        self._route_registry
    )



@property
def handler_count(
    self,
) -> int:
    """
    Number of registered handlers.
    """

    return len(
        self._handlers
    )



@property
def latency(
    self,
) -> float:
    """
    Average dispatch latency.

    Unit:
        seconds
    """

    total = self._statistics.get(
        "total_latency",
        0.0,
    )

    count = self.dispatch_count

    if count == 0:
        return 0.0

    return total / count



@property
def throughput(
    self,
) -> float:
    """
    Dispatch throughput.

    Unit:
        events / second
    """

    uptime = self.uptime

    if uptime <= 0:
        return 0.0

    return (
        self.dispatch_count
        /
        uptime
    )



@property
def uptime(
    self,
) -> float:
    """
    Dispatcher uptime.

    Unit:
        seconds
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
    Return dispatcher summary.
    """

    return {
        "id": self._id,
        "name": self._name,

        "routes": self.route_count,

        "handlers": self.handler_count,

        "dispatch_count": self.dispatch_count,

        "success_count": self.success_count,

        "failure_count": self.failure_count,

        "active": self.active,

        "uptime": self.uptime,
    }



def statistics(
    self,
) -> dict[str, Any]:
    """
    Return detailed runtime statistics.
    """

    return {

        **self.summary(),

        "latency": self.latency,

        "throughput": self.throughput,

        "runtime": dict(
            self._statistics
        ),

    }



def report(
    self,
) -> dict[str, Any]:
    """
    Generate dispatcher report.
    """

    return {

        "summary": self.summary(),

        "statistics": self.statistics(),

        "status": self.status(),

        "performance": self.performance(),

    }



# ------------------------------------------------------------------
# Diagnostics
# ------------------------------------------------------------------

def health(
    self,
) -> str:
    """
    Return dispatcher health state.
    """

    if self.closed:
        return "closed"


    if self.frozen:
        return "frozen"


    if self.disabled:
        return "disabled"


    if self.failure_count > 0:

        return "degraded"


    return "healthy"



def status(
    self,
) -> dict[str, Any]:
    """
    Runtime status.
    """

    return {

        "health": self.health(),

        "enabled": self.enabled,

        "disabled": self.disabled,

        "frozen": self.frozen,

        "closed": self.closed,

        "active": self.active,

    }



def performance(
    self,
) -> dict[str, Any]:
    """
    Performance metrics.
    """

    return {

        "dispatch_count": self.dispatch_count,

        "success_count": self.success_count,

        "failure_count": self.failure_count,

        "latency": self.latency,

        "throughput": self.throughput,

        "uptime": self.uptime,

    }
# ==================================================================
# Part 8. Serialization
# ==================================================================

import json
import pickle
from copy import deepcopy
from datetime import datetime


try:
    import yaml
except ImportError:
    yaml = None


try:
    import msgpack
except ImportError:
    msgpack = None



# ------------------------------------------------------------------
# Serialization
# ------------------------------------------------------------------

def to_dict(
    self,
) -> dict[str, Any]:
    """
    Serialize dispatcher state to dictionary.
    """

    return {

        "id": self._id,

        "name": self._name,

        "description": self._description,


        "routes": deepcopy(
            self._routes
        ),

        "route_registry": deepcopy(
            self._route_registry
        ),

        "handlers": deepcopy(
            self._handlers
        ),

        "subscribers": deepcopy(
            self._subscribers
        ),


        "context": deepcopy(
            self._context
        ),


        "statistics": deepcopy(
            self._statistics
        ),


        "enabled": self._enabled,

        "frozen": self._frozen,

        "closed": self._closed,


        "created_at":
            self._created_at.isoformat(),

        "updated_at":
            self._updated_at.isoformat(),


        "version": self._version,

    }



@classmethod
def from_dict(
    cls,
    data: dict[str, Any],
) -> "MetricDispatcher":
    """
    Restore dispatcher from dictionary.
    """

    obj = cls(
        name=data.get(
            "name",
            "MetricDispatcher",
        ),
        description=data.get(
            "description",
            "",
        ),
    )


    obj._id = data.get(
        "id",
        obj._id,
    )


    obj._routes = deepcopy(
        data.get(
            "routes",
            [],
        )
    )


    obj._route_registry = deepcopy(
        data.get(
            "route_registry",
            {},
        )
    )


    obj._handlers = deepcopy(
        data.get(
            "handlers",
            {},
        )
    )


    obj._subscribers = deepcopy(
        data.get(
            "subscribers",
            {},
        )
    )


    obj._context = deepcopy(
        data.get(
            "context",
            {},
        )
    )


    obj._statistics = deepcopy(
        data.get(
            "statistics",
            {},
        )
    )


    obj._enabled = data.get(
        "enabled",
        True,
    )


    obj._frozen = data.get(
        "frozen",
        False,
    )


    obj._closed = data.get(
        "closed",
        False,
    )


    if "created_at" in data:

        obj._created_at = datetime.fromisoformat(
            data["created_at"]
        )


    if "updated_at" in data:

        obj._updated_at = datetime.fromisoformat(
            data["updated_at"]
        )


    obj._version = data.get(
        "version",
        cls.VERSION,
    )


    return obj



def to_json(
    self,
    **kwargs,
) -> str:
    """
    Serialize dispatcher to JSON.
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
) -> "MetricDispatcher":
    """
    Restore dispatcher from JSON.
    """

    return cls.from_dict(
        json.loads(data)
    )



def serialize(
    self,
    fmt: str = "json",
):
    """
    Generic serialization.

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
) -> "MetricDispatcher":
    """
    Deserialize dispatcher.
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
            yaml.safe_load(data)
        )



    if fmt == "pickle":

        return cls.from_dict(
            pickle.loads(data)
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
    Export dispatcher state to file.
    """

    data = self.serialize(
        fmt
    )


    mode = (
        "wb"
        if isinstance(data, bytes)
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
) -> "MetricDispatcher":
    """
    Import dispatcher from file.
    """

    binary_formats = {
        "pickle",
        "msgpack",
    }


    mode = (
        "rb"
        if fmt.lower()
        in binary_formats
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

from datetime import datetime
from uuid import uuid4
from typing import Callable, Any



# ------------------------------------------------------------------
# Events
# ------------------------------------------------------------------

def before_dispatch(
    self,
    payload: Any = None,
) -> None:
    """
    Trigger before_dispatch event.
    """

    self.emit(
        "before_dispatch",
        payload=payload,
    )



def after_dispatch(
    self,
    result: Any = None,
) -> None:
    """
    Trigger after_dispatch event.
    """

    self.emit(
        "after_dispatch",
        result=result,
    )



def before_route(
    self,
    route: str,
    payload: Any = None,
) -> None:
    """
    Trigger before_route event.
    """

    self.emit(
        "before_route",
        route=route,
        payload=payload,
    )



def after_route(
    self,
    route: str,
    result: Any = None,
) -> None:
    """
    Trigger after_route event.
    """

    self.emit(
        "after_route",
        route=route,
        result=result,
    )



def before_handle(
    self,
    handler: Any,
    payload: Any = None,
) -> None:
    """
    Trigger before_handle event.
    """

    self.emit(
        "before_handle",
        handler=handler,
        payload=payload,
    )



def after_handle(
    self,
    handler: Any,
    result: Any = None,
) -> None:
    """
    Trigger after_handle event.
    """

    self.emit(
        "after_handle",
        handler=handler,
        result=result,
    )



def before_flush(
    self,
) -> None:
    """
    Trigger before_flush event.
    """

    self.emit(
        "before_flush"
    )



def after_flush(
    self,
) -> None:
    """
    Trigger after_flush event.
    """

    self.emit(
        "after_flush"
    )



def before_close(
    self,
) -> None:
    """
    Trigger before_close event.
    """

    self.emit(
        "before_close"
    )



def after_close(
    self,
) -> None:
    """
    Trigger after_close event.
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
) -> "MetricDispatcher":
    """
    Add runtime event hook.
    """

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
) -> "MetricDispatcher":
    """
    Remove runtime event hook.
    """

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
) -> "MetricDispatcher":
    """
    Clear event hooks.
    """

    if event is None:

        self._hooks.clear()

    else:

        self._hooks.pop(
            event,
            None,
        )


    return self



# ------------------------------------------------------------------
# Dispatcher Events
# ------------------------------------------------------------------

def emit(
    self,
    event: str,
    **payload,
) -> None:
    """
    Emit dispatcher event.
    """

    event_record = {

        "id": str(
            uuid4()
        ),

        "event": event,

        "timestamp":
            datetime.utcnow(),

        "payload": payload,

    }


    self._events.append(
        event_record
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
    Notify registered hooks.
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
) -> "MetricDispatcher":
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
) -> "MetricDispatcher":
    """
    Unsubscribe callback from event.
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
        f"routes={self.route_count}, "
        f"handlers={self.handler_count}, "
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
        f"[routes={self.route_count}, "
        f"handlers={self.handler_count}]"
    )



# ------------------------------------------------------------------
# Container
# ------------------------------------------------------------------

def __len__(
    self,
) -> int:
    """
    Number of registered routes.
    """

    return self.route_count



def __iter__(
    self,
):
    """
    Iterate through routes.
    """

    return iter(
        self._route_registry
    )



def __contains__(
    self,
    name: str,
) -> bool:
    """
    Route existence check.
    """

    return self.contains_route(
        name
    )



# ------------------------------------------------------------------
# Mapping
# ------------------------------------------------------------------

def __getitem__(
    self,
    name: str,
):
    """
    Dictionary style route lookup.
    """

    return self.get_route(
        name
    )



def __setitem__(
    self,
    name: str,
    route: Any,
) -> None:
    """
    Dictionary style route registration.
    """

    self.register_route(
        name,
        route,
    )



def __delitem__(
    self,
    name: str,
) -> None:
    """
    Dictionary style route removal.
    """

    self.unregister_route(
        name
    )



# ------------------------------------------------------------------
# Context Manager
# ------------------------------------------------------------------

def __enter__(
    self,
) -> "MetricDispatcher":
    """
    Enter dispatcher context.
    """

    self.enable()

    return self



def __exit__(
    self,
    exc_type,
    exc_value,
    traceback,
) -> bool:
    """
    Exit dispatcher context.
    """

    self.close()

    return False



# ------------------------------------------------------------------
# Callable
# ------------------------------------------------------------------

def __call__(
    self,
    payload: Any = None,
    target: str | None = None,
):
    """
    Callable dispatcher interface.
    """

    return self.dispatch(
        payload,
        target,
    )



# ------------------------------------------------------------------
# Copy
# ------------------------------------------------------------------

def __copy__(
    self,
):
    """
    Shallow copy protocol.
    """

    return self.copy()



def __deepcopy__(
    self,
    memo,
):
    """
    Deep copy protocol.
    """

    return self.clone()                                            