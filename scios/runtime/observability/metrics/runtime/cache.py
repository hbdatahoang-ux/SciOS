"""
SciOS-NG Runtime Metrics Cache Engine

File:
    scios/runtime/observability/metrics/runtime/cache.py

Description
-----------
Runtime cache engine for metrics, aggregation results, and runtime
observability data.

The MetricCache provides a thread-safe cache layer used by Runtime
Collector, Aggregator, Recorder, Reporter, and RuntimeMonitor.

SciOS-NG v0.2
"""

from __future__ import annotations

from datetime import datetime
from threading import RLock
from typing import Any, Dict
from uuid import uuid4


class MetricCache:
    """
    Runtime Metrics Cache Engine.

    Responsibilities
    ----------------
    - Runtime metric cache
    - Aggregation cache
    - Snapshot cache
    - Temporary runtime storage
    - Runtime cache statistics

    Notes
    -----
    Part 1 implements only the cache foundation.
    Cache operations, lifecycle, serialization, events,
    and cache policies are implemented in later parts.
    """

    VERSION = "0.2.0"

    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        name: str = "MetricCache",
        description: str = "",
    ) -> None:
        """
        Initialize Runtime Metrics Cache Engine.
        """

        # ----------------------------------------------------------
        # Identity
        # ----------------------------------------------------------

        self._id: str = str(uuid4())
        self._name: str = name
        self._description: str = description

        # ----------------------------------------------------------
        # Cache Storage
        # ----------------------------------------------------------

        # Runtime cache
        self._cache: Dict[str, Any] = {}

        # Metadata for cache entries
        self._metadata: Dict[str, Dict[str, Any]] = {}

        # Runtime cache statistics
        self._statistics: Dict[str, Any] = {
            "hits": 0,
            "misses": 0,
            "puts": 0,
            "evictions": 0,
        }

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

    # ==============================================================
    # Internal Utilities
    # ==============================================================

    def _touch(self) -> None:
        """
        Update the modification timestamp.
        """
        self._updated_at = datetime.utcnow()
# ==================================================================
# Part 2. Cache API
# ==================================================================

from datetime import datetime
from typing import Any


# ------------------------------------------------------------------
# Internal Helper
# ------------------------------------------------------------------

def _ensure_writable(self) -> None:
    """
    Ensure the cache accepts write operations.
    """
    if self._closed:
        raise RuntimeError("MetricCache is closed.")

    if self._frozen:
        raise RuntimeError("MetricCache is frozen.")

    if not self._enabled:
        raise RuntimeError("MetricCache is disabled.")


def _update_metadata(self, key: str) -> None:
    """
    Update metadata for a cache entry.
    """
    now = datetime.utcnow()

    metadata = self._metadata.setdefault(
        key,
        {
            "created_at": now,
            "updated_at": now,
            "accessed_at": now,
            "access_count": 0,
            "ttl": None,
            "expires_at": None,
        },
    )

    metadata["updated_at"] = now


# ------------------------------------------------------------------
# Storage
# ------------------------------------------------------------------

def put(
    self,
    key: str,
    value: Any,
) -> Any:
    """
    Store a cache entry.
    """
    with self._lock:
        self._ensure_writable()

        self._cache[key] = value

        self._update_metadata(key)

        self._statistics["puts"] += 1

        self._touch()

        return value


def get(
    self,
    key: str,
    default: Any = None,
) -> Any:
    """
    Retrieve a cache entry.
    """
    with self._lock:

        if key not in self._cache:
            self._statistics["misses"] += 1
            return default

        metadata = self._metadata.get(key)

        if metadata is not None:
            metadata["accessed_at"] = datetime.utcnow()
            metadata["access_count"] += 1

        self._statistics["hits"] += 1

        return self._cache[key]


def set(
    self,
    key: str,
    value: Any,
) -> Any:
    """
    Alias of put().
    """
    return self.put(key, value)


def add(
    self,
    key: str,
    value: Any,
) -> Any:
    """
    Add a cache entry if it does not already exist.
    """
    with self._lock:
        self._ensure_writable()

        if key not in self._cache:
            return self.put(key, value)

        return self._cache[key]


def remove(
    self,
    key: str,
) -> Any:
    """
    Remove a cache entry.
    """
    with self._lock:
        value = self._cache.pop(key, None)
        self._metadata.pop(key, None)

        self._touch()

        return value


# ------------------------------------------------------------------
# Lookup
# ------------------------------------------------------------------

def contains(
    self,
    key: str,
) -> bool:
    """
    Check whether a cache entry exists.
    """
    return key in self._cache


def exists(
    self,
    key: str,
) -> bool:
    """
    Alias of contains().
    """
    return self.contains(key)


# ------------------------------------------------------------------
# Update
# ------------------------------------------------------------------

def update(
    self,
    key: str,
    value: Any,
) -> Any:
    """
    Update an existing cache entry.
    """
    with self._lock:
        self._ensure_writable()

        if key not in self._cache:
            raise KeyError(key)

        self._cache[key] = value

        self._update_metadata(key)

        self._touch()

        return value


def replace(
    self,
    key: str,
    value: Any,
) -> Any:
    """
    Replace a cache entry.

    Alias of update().
    """
    return self.update(key, value)


# ------------------------------------------------------------------
# Batch Operations
# ------------------------------------------------------------------

def put_many(
    self,
    entries: dict[str, Any],
) -> None:
    """
    Store multiple cache entries.
    """
    for key, value in entries.items():
        self.put(key, value)


def get_many(
    self,
    keys: list[str],
) -> dict[str, Any]:
    """
    Retrieve multiple cache entries.
    """
    return {
        key: self.get(key)
        for key in keys
    }


def remove_many(
    self,
    keys: list[str],
) -> dict[str, Any]:
    """
    Remove multiple cache entries.
    """
    removed = {}

    for key in keys:
        removed[key] = self.remove(key)

    return removed
# ==================================================================
# Part 3. Cache Registry API
# ==================================================================

from datetime import datetime


# ------------------------------------------------------------------
# Registry
# ------------------------------------------------------------------

def keys(self):
    """
    Return all cache keys.
    """
    return self._cache.keys()


def values(self):
    """
    Return all cached values.
    """
    return self._cache.values()


def items(self):
    """
    Return all cache items.
    """
    return self._cache.items()


def entries(self) -> dict[str, Any]:
    """
    Return a shallow copy of the cache.
    """
    return dict(self._cache)


# ------------------------------------------------------------------
# Information
# ------------------------------------------------------------------

def count(self) -> int:
    """
    Return the number of cached entries.
    """
    return len(self._cache)


def size(self) -> int:
    """
    Alias of count().

    Represents the current cache occupancy.
    """
    return self.count()


def capacity(self):
    """
    Return the configured cache capacity.

    None means unlimited.
    """
    return getattr(self, "_capacity", None)


# ------------------------------------------------------------------
# Maintenance
# ------------------------------------------------------------------

def clear(self) -> "MetricCache":
    """
    Remove all cache entries.
    """
    with self._lock:

        self._cache.clear()
        self._metadata.clear()

        self._touch()

        return self


def clear_expired(self) -> int:
    """
    Remove expired cache entries.

    Expiration is determined by the 'expires_at'
    field stored in entry metadata.

    Returns
    -------
    int
        Number of removed entries.
    """
    with self._lock:

        now = datetime.utcnow()

        removed = []

        for key, meta in list(self._metadata.items()):

            expires_at = meta.get("expires_at")

            if (
                expires_at is not None
                and expires_at <= now
            ):
                removed.append(key)

        for key in removed:
            self._cache.pop(key, None)
            self._metadata.pop(key, None)

        if removed:
            self._touch()

        return len(removed)
# ==================================================================
# Part 4. Cache Policies
# ==================================================================

from collections import OrderedDict
from datetime import datetime, timedelta
import random as _random


# ------------------------------------------------------------------
# Built-in Policies
# ------------------------------------------------------------------

def fifo(self):
    """
    FIFO eviction policy.
    """
    with self._lock:

        if not self._cache:
            return None

        key = next(iter(self._cache))

        value = self.remove(key)

        self._statistics["evictions"] += 1

        return key, value


def lifo(self):
    """
    LIFO eviction policy.
    """
    with self._lock:

        if not self._cache:
            return None

        key = next(reversed(self._cache))

        value = self.remove(key)

        self._statistics["evictions"] += 1

        return key, value


def lru(self):
    """
    Least Recently Used eviction policy.
    """
    with self._lock:

        if not self._metadata:
            return None

        key = min(
            self._metadata,
            key=lambda k: self._metadata[k].get(
                "accessed_at",
                self._metadata[k]["created_at"],
            ),
        )

        value = self.remove(key)

        self._statistics["evictions"] += 1

        return key, value


def lfu(self):
    """
    Least Frequently Used eviction policy.
    """
    with self._lock:

        if not self._metadata:
            return None

        key = min(
            self._metadata,
            key=lambda k: self._metadata[k].get(
                "access_count",
                0,
            ),
        )

        value = self.remove(key)

        self._statistics["evictions"] += 1

        return key, value


def random(self):
    """
    Random eviction policy.
    """
    with self._lock:

        if not self._cache:
            return None

        key = _random.choice(list(self._cache.keys()))

        value = self.remove(key)

        self._statistics["evictions"] += 1

        return key, value


# ------------------------------------------------------------------
# Expiration
# ------------------------------------------------------------------

def ttl(
    self,
    key: str,
    seconds: float,
):
    """
    Configure TTL for a cache entry.
    """
    with self._lock:

        if key not in self._metadata:
            raise KeyError(key)

        now = datetime.utcnow()

        self._metadata[key]["ttl"] = seconds
        self._metadata[key]["expires_at"] = (
            now + timedelta(seconds=seconds)
        )

        self._touch()

        return self


def expire(
    self,
    key: str,
):
    """
    Expire a cache entry immediately.
    """
    with self._lock:

        if key not in self._cache:
            return False

        self.remove(key)

        self._statistics["evictions"] += 1

        return True


def refresh(
    self,
    key: str,
):
    """
    Refresh the expiration time of a cache entry.
    """
    with self._lock:

        metadata = self._metadata.get(key)

        if metadata is None:
            raise KeyError(key)

        ttl = metadata.get("ttl")

        if ttl is None:
            return self

        metadata["expires_at"] = (
            datetime.utcnow() +
            timedelta(seconds=ttl)
        )

        metadata["updated_at"] = datetime.utcnow()

        self._touch()

        return self


# ------------------------------------------------------------------
# Policy Management
# ------------------------------------------------------------------

def register_policy(
    self,
    name: str,
    policy,
):
    """
    Register a custom cache policy.
    """
    if not hasattr(self, "_policy_registry"):
        self._policy_registry = {}

    self._policy_registry[name] = policy

    return self


def remove_policy(
    self,
    name: str,
):
    """
    Remove a custom cache policy.
    """
    if hasattr(self, "_policy_registry"):
        self._policy_registry.pop(name, None)

    return self


def policy(
    self,
    name: str | None = None,
):
    """
    Get or set the active cache policy.
    """
    if name is None:
        return getattr(self, "_policy", None)

    builtin = {
        "fifo": self.fifo,
        "lifo": self.lifo,
        "lru": self.lru,
        "lfu": self.lfu,
        "random": self.random,
    }

    if name in builtin:
        self._policy = name
        return builtin[name]

    registry = getattr(
        self,
        "_policy_registry",
        {},
    )

    if name not in registry:
        raise KeyError(
            f"Unknown cache policy: {name}"
        )

    self._policy = name

    return registry[name]
# ==================================================================
# Part 5. Lifecycle Management
# ==================================================================

# ------------------------------------------------------------------
# Lifecycle
# ------------------------------------------------------------------

def enable(self) -> "MetricCache":
    """
    Enable the cache.
    """
    with self._lock:
        if self._closed:
            raise RuntimeError("MetricCache is closed.")

        self._enabled = True
        self._touch()

    return self


def disable(self) -> "MetricCache":
    """
    Disable the cache.
    """
    with self._lock:
        if self._closed:
            raise RuntimeError("MetricCache is closed.")

        self._enabled = False
        self._touch()

    return self


def freeze(self) -> "MetricCache":
    """
    Freeze the cache.

    Write operations are rejected while frozen.
    """
    with self._lock:
        if self._closed:
            raise RuntimeError("MetricCache is closed.")

        self._frozen = True
        self._touch()

    return self


def unfreeze(self) -> "MetricCache":
    """
    Unfreeze the cache.
    """
    with self._lock:
        if self._closed:
            raise RuntimeError("MetricCache is closed.")

        self._frozen = False
        self._touch()

    return self


def close(self) -> "MetricCache":
    """
    Close the cache.
    """
    with self._lock:
        self._enabled = False
        self._frozen = False
        self._closed = True

        self._touch()

    return self


def reopen(self) -> "MetricCache":
    """
    Reopen a previously closed cache.
    """
    with self._lock:
        self._closed = False
        self._enabled = True
        self._frozen = False

        self._touch()

    return self


# ------------------------------------------------------------------
# Runtime Properties
# ------------------------------------------------------------------

@property
def enabled(self) -> bool:
    """
    Whether the cache is enabled.
    """
    return self._enabled


@property
def disabled(self) -> bool:
    """
    Whether the cache is disabled.
    """
    return not self._enabled


@property
def frozen(self) -> bool:
    """
    Whether the cache is frozen.
    """
    return self._frozen


@property
def closed(self) -> bool:
    """
    Whether the cache is closed.
    """
    return self._closed


@property
def active(self) -> bool:
    """
    Whether the cache is active.

    An active cache is enabled, not frozen,
    and not closed.
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

def snapshot(self) -> dict[str, Any]:
    """
    Create a runtime snapshot.
    """
    with self._lock:

        snapshot = {
            "cache": deepcopy(self._cache),
            "metadata": deepcopy(self._metadata),
            "statistics": deepcopy(self._statistics),
            "enabled": self._enabled,
            "frozen": self._frozen,
            "closed": self._closed,
            "created_at": self._created_at,
            "updated_at": self._updated_at,
            "version": self._version,
        }

        self._snapshot = deepcopy(snapshot)

        return snapshot


def restore(
    self,
    snapshot: dict[str, Any] | None = None,
) -> "MetricCache":
    """
    Restore the cache from a snapshot.
    """
    with self._lock:

        data = snapshot or getattr(
            self,
            "_snapshot",
            None,
        )

        if data is None:
            raise RuntimeError(
                "No snapshot available."
            )

        self._cache = deepcopy(
            data["cache"]
        )

        self._metadata = deepcopy(
            data["metadata"]
        )

        self._statistics = deepcopy(
            data["statistics"]
        )

        self._enabled = data["enabled"]
        self._frozen = data["frozen"]
        self._closed = data["closed"]

        self._created_at = data["created_at"]
        self._updated_at = data["updated_at"]
        self._version = data["version"]

        self._touch()

        return self


# ------------------------------------------------------------------
# Object Management
# ------------------------------------------------------------------

def clone(self) -> "MetricCache":
    """
    Create a deep clone of the cache.
    """
    return deepcopy(self)


def copy(self) -> "MetricCache":
    """
    Create a shallow copy of the cache.
    """
    return _copy(self)


# ------------------------------------------------------------------
# Cleanup
# ------------------------------------------------------------------

def compact(self) -> "MetricCache":
    """
    Compact the cache by removing invalid entries.
    """
    with self._lock:

        invalid = []

        for key, value in self._cache.items():

            if value is None:
                invalid.append(key)

        for key in invalid:
            self._cache.pop(key, None)
            self._metadata.pop(key, None)

        self._touch()

        return self


def cleanup(self) -> "MetricCache":
    """
    Cleanup runtime cache.

    Performs expiration cleanup followed by compaction.
    """
    with self._lock:

        self.clear_expired()
        self.compact()

        self._touch()

        return self
# ==================================================================
# Part 7. Statistics & Diagnostics
# ==================================================================

import sys


# ------------------------------------------------------------------
# Runtime Metrics
# ------------------------------------------------------------------

@property
def hit_count(self) -> int:
    """
    Number of cache hits.
    """
    return self._statistics.get("hits", 0)


@property
def miss_count(self) -> int:
    """
    Number of cache misses.
    """
    return self._statistics.get("misses", 0)


@property
def hit_rate(self) -> float:
    """
    Cache hit rate.
    """
    hits = self.hit_count
    misses = self.miss_count

    total = hits + misses

    if total == 0:
        return 0.0

    return hits / total


@property
def evictions(self) -> int:
    """
    Number of evicted cache entries.
    """
    return self._statistics.get("evictions", 0)


@property
def expired(self) -> int:
    """
    Number of expired cache entries.
    """
    return self._statistics.get("expired", 0)


@property
def memory_usage(self) -> int:
    """
    Approximate memory usage in bytes.
    """
    return (
        sys.getsizeof(self._cache)
        + sys.getsizeof(self._metadata)
        + sys.getsizeof(self._statistics)
    )


# ------------------------------------------------------------------
# Statistics
# ------------------------------------------------------------------

def summary(self) -> dict[str, Any]:
    """
    Return a runtime summary.
    """
    return {
        "id": self._id,
        "name": self._name,
        "entries": self.count(),
        "capacity": self.capacity(),
        "hit_rate": self.hit_rate,
        "enabled": self.enabled,
        "frozen": self.frozen,
        "closed": self.closed,
    }


def statistics(self) -> dict[str, Any]:
    """
    Return runtime statistics.
    """
    return {
        **self.summary(),
        "hits": self.hit_count,
        "misses": self.miss_count,
        "evictions": self.evictions,
        "expired": self.expired,
        "memory_usage": self.memory_usage,
    }


def report(self) -> dict[str, Any]:
    """
    Generate a runtime report.
    """
    return {
        "summary": self.summary(),
        "statistics": self.statistics(),
        "diagnostics": self.status(),
    }


# ------------------------------------------------------------------
# Diagnostics
# ------------------------------------------------------------------

def health(self) -> str:
    """
    Return cache health status.
    """
    if self.closed:
        return "closed"

    if self.frozen:
        return "frozen"

    if self.disabled:
        return "disabled"

    return "healthy"


def status(self) -> dict[str, Any]:
    """
    Return runtime status.
    """
    return {
        "health": self.health(),
        "active": self.active,
        "enabled": self.enabled,
        "frozen": self.frozen,
        "closed": self.closed,
    }


def performance(self) -> dict[str, Any]:
    """
    Return runtime performance metrics.
    """
    return {
        "entries": self.count(),
        "hit_rate": self.hit_rate,
        "hits": self.hit_count,
        "misses": self.miss_count,
        "evictions": self.evictions,
        "expired": self.expired,
        "memory_usage": self.memory_usage,
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

def to_dict(self) -> dict[str, Any]:
    """
    Serialize the cache to a dictionary.
    """
    return {
        "id": self._id,
        "name": self._name,
        "description": self._description,
        "cache": deepcopy(self._cache),
        "metadata": deepcopy(self._metadata),
        "statistics": deepcopy(self._statistics),
        "enabled": self._enabled,
        "frozen": self._frozen,
        "closed": self._closed,
        "created_at": self._created_at.isoformat(),
        "updated_at": self._updated_at.isoformat(),
        "version": self._version,
    }


@classmethod
def from_dict(
    cls,
    data: dict[str, Any],
) -> "MetricCache":
    """
    Create a cache from a dictionary.
    """
    obj = cls(
        name=data.get("name", "MetricCache"),
        description=data.get("description", ""),
    )

    obj._id = data["id"]

    obj._cache = deepcopy(
        data.get("cache", {})
    )

    obj._metadata = deepcopy(
        data.get("metadata", {})
    )

    obj._statistics = deepcopy(
        data.get("statistics", {})
    )

    obj._enabled = data.get("enabled", True)
    obj._frozen = data.get("frozen", False)
    obj._closed = data.get("closed", False)

    obj._created_at = datetime.fromisoformat(
        data["created_at"]
    )

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
    Serialize the cache to JSON.
    """
    return json.dumps(
        self.to_dict(),
        **kwargs,
    )


@classmethod
def from_json(
    cls,
    data: str,
) -> "MetricCache":
    """
    Create a cache from JSON.
    """
    return cls.from_dict(
        json.loads(data)
    )


def serialize(
    self,
    fmt: str = "json",
):
    """
    Serialize using the specified format.
    """
    fmt = fmt.lower()

    if fmt == "json":
        return self.to_json(indent=2)

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
) -> "MetricCache":
    """
    Deserialize from the specified format.
    """
    fmt = fmt.lower()

    if fmt == "json":
        return cls.from_json(data)

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
    Export the cache to a file.
    """
    data = self.serialize(fmt)

    mode = "wb" if isinstance(data, bytes) else "w"

    with open(path, mode) as f:
        f.write(data)


@classmethod
def import_data(
    cls,
    path: str,
    fmt: str = "json",
) -> "MetricCache":
    """
    Import a cache from a file.
    """
    mode = (
        "rb"
        if fmt.lower() in {"pickle", "msgpack"}
        else "r"
    )

    with open(path, mode) as f:
        data = f.read()

    return cls.deserialize(
        data,
        fmt=fmt,
    )
# ==================================================================
# Part 9. Events & Hooks
# ==================================================================

from datetime import datetime
from uuid import uuid4
from typing import Any, Callable


# ------------------------------------------------------------------
# Events
# ------------------------------------------------------------------

def before_put(self, key: str, value: Any) -> None:
    """
    Emit before_put event.
    """
    self.emit(
        "before_put",
        key=key,
        value=value,
    )


def after_put(self, key: str, value: Any) -> None:
    """
    Emit after_put event.
    """
    self.emit(
        "after_put",
        key=key,
        value=value,
    )


def before_get(self, key: str) -> None:
    """
    Emit before_get event.
    """
    self.emit(
        "before_get",
        key=key,
    )


def after_get(
    self,
    key: str,
    value: Any,
) -> None:
    """
    Emit after_get event.
    """
    self.emit(
        "after_get",
        key=key,
        value=value,
    )


def before_remove(self, key: str) -> None:
    """
    Emit before_remove event.
    """
    self.emit(
        "before_remove",
        key=key,
    )


def after_remove(
    self,
    key: str,
    value: Any,
) -> None:
    """
    Emit after_remove event.
    """
    self.emit(
        "after_remove",
        key=key,
        value=value,
    )


def before_clear(self) -> None:
    """
    Emit before_clear event.
    """
    self.emit("before_clear")


def after_clear(self) -> None:
    """
    Emit after_clear event.
    """
    self.emit("after_clear")


# ------------------------------------------------------------------
# Hook Management
# ------------------------------------------------------------------

def add_hook(
    self,
    event: str,
    callback: Callable[..., Any],
) -> "MetricCache":
    """
    Register a hook callback.
    """
    self._hooks.setdefault(
        event,
        [],
    ).append(callback)

    return self


def remove_hook(
    self,
    event: str,
    callback: Callable[..., Any],
) -> "MetricCache":
    """
    Remove a hook callback.
    """
    callbacks = self._hooks.get(event)

    if callbacks and callback in callbacks:
        callbacks.remove(callback)

    return self


def clear_hooks(
    self,
    event: str | None = None,
) -> "MetricCache":
    """
    Clear hook callbacks.
    """
    if event is None:
        self._hooks.clear()
    else:
        self._hooks.pop(event, None)

    return self


# ------------------------------------------------------------------
# Dispatcher
# ------------------------------------------------------------------

def emit(
    self,
    event: str,
    *args,
    **kwargs,
) -> None:
    """
    Emit a runtime event.
    """
    payload = {
        "id": str(uuid4()),
        "event": event,
        "source": self._name,
        "timestamp": datetime.utcnow(),
        "args": args,
        "kwargs": kwargs,
    }

    self._events.append(payload)

    self.notify(
        event,
        *args,
        **kwargs,
    )


def notify(
    self,
    event: str,
    *args,
    **kwargs,
) -> None:
    """
    Notify all registered hooks.
    """
    for callback in self._hooks.get(event, []):
        callback(*args, **kwargs)


def subscribe(
    self,
    event: str,
    callback: Callable[..., Any],
) -> "MetricCache":
    """
    Subscribe to an event.
    """
    return self.add_hook(
        event,
        callback,
    )


def unsubscribe(
    self,
    event: str,
    callback: Callable[..., Any],
) -> "MetricCache":
    """
    Unsubscribe from an event.
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

def __repr__(self) -> str:
    """
    Official string representation.
    """
    return (
        f"{self.__class__.__name__}("
        f"id={self._id!r}, "
        f"name={self._name!r}, "
        f"entries={self.count()}, "
        f"active={self.active})"
    )


def __str__(self) -> str:
    """
    Human-readable representation.
    """
    return (
        f"{self._name} "
        f"({self.count()} cached entries)"
    )


# ------------------------------------------------------------------
# Container
# ------------------------------------------------------------------

def __len__(self) -> int:
    """
    Number of cached entries.
    """
    return self.count()


def __iter__(self):
    """
    Iterate over cache items.
    """
    return iter(self._cache.items())


def __contains__(
    self,
    key: str,
) -> bool:
    """
    Membership test.
    """
    return self.contains(key)


# ------------------------------------------------------------------
# Mapping
# ------------------------------------------------------------------

def __getitem__(
    self,
    key: str,
):
    """
    Dictionary-style lookup.
    """
    return self.get(key)


def __setitem__(
    self,
    key: str,
    value,
) -> None:
    """
    Dictionary-style assignment.
    """
    self.put(key, value)


def __delitem__(
    self,
    key: str,
) -> None:
    """
    Dictionary-style deletion.
    """
    self.remove(key)


# ------------------------------------------------------------------
# Context Manager
# ------------------------------------------------------------------

def __enter__(self) -> "MetricCache":
    """
    Enter runtime context.
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
    Exit runtime context.
    """
    self.close()
    return False


# ------------------------------------------------------------------
# Callable
# ------------------------------------------------------------------

def __call__(
    self,
    key: str,
    value=...,
):
    """
    Shortcut API.

    cache(key)
        -> get(key)

    cache(key, value)
        -> put(key, value)
    """
    if value is ...:
        return self.get(key)

    self.put(key, value)

    return value


# ------------------------------------------------------------------
# Copy
# ------------------------------------------------------------------

def __copy__(self):
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