"""
SciOS Runtime Metrics Cache

Runtime cache for metrics, collectors, exporters, and plugins.

Python 3.11+
"""

# ==============================================================================
# Part 1. Header
# ==============================================================================

from __future__ import annotations

import json
import time

from typing import Any, TypeAlias


# ==============================================================================
# Part 2. Constants
# ==============================================================================

DEFAULT_NAME: str = "runtime"

DEFAULT_ENABLED: bool = True

DEFAULT_MAX_SIZE: int = 1024

DEFAULT_TTL: float = 300.0

DEFAULT_CLEAN_INTERVAL: float = 60.0

DEFAULT_HITS: int = 0

DEFAULT_MISSES: int = 0


__all__ = [
    # constants
    "DEFAULT_NAME",
    "DEFAULT_ENABLED",
    "DEFAULT_MAX_SIZE",
    "DEFAULT_TTL",
    "DEFAULT_CLEAN_INTERVAL",
    "DEFAULT_HITS",
    "DEFAULT_MISSES",
    # aliases
    "CacheValue",
    "CacheEntry",
    "CacheMap",
    "CacheState",
    "CacheStats",
    # classes
    "RuntimeCache",
]


# ==============================================================================
# Part 3. Type Aliases
# ==============================================================================

CacheValue: TypeAlias = Any

CacheEntry: TypeAlias = dict[str, Any]

CacheMap: TypeAlias = dict[str, CacheEntry]

CacheState: TypeAlias = dict[str, Any]

CacheStats: TypeAlias = dict[str, int]


# ==============================================================================
# Part 4. RuntimeCache
# ==============================================================================


class RuntimeCache:
    """
    Runtime metrics cache.
    """

    __slots__ = (
        "_name",
        "_enabled",
        "_max_size",
        "_ttl",
        "_entries",
        "_hits",
        "_misses",
        "_clean_interval",
    )

    def __init__(
        self,
        *,
        name: str = DEFAULT_NAME,
        enabled: bool = DEFAULT_ENABLED,
        max_size: int = DEFAULT_MAX_SIZE,
        ttl: float = DEFAULT_TTL,
        clean_interval: float = DEFAULT_CLEAN_INTERVAL,
    ) -> None:

        self._name = str(name)

        self._enabled = bool(enabled)

        self._max_size = int(max_size)

        self._ttl = float(ttl)

        self._entries: CacheMap = {}

        self._hits = DEFAULT_HITS

        self._misses = DEFAULT_MISSES

        self._clean_interval = float(clean_interval)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:

        return self._name

    @property
    def enabled(self) -> bool:

        return self._enabled

    @property
    def max_size(self) -> int:

        return self._max_size

    @property
    def ttl(self) -> float:

        return self._ttl

    @property
    def entries(self) -> CacheMap:

        return self._entries

    @property
    def hits(self) -> int:

        return self._hits

    @property
    def misses(self) -> int:

        return self._misses

    @property
    def size(self) -> int:

        return len(self._entries)

    @property
    def utilization(self) -> float:

        if self._max_size <= 0:
            return 0.0

        return self.size / self._max_size


# ==============================================================================
# Part 5. Lifecycle
# ==============================================================================

    def enable(self) -> None:

        self._enabled = True

    def disable(self) -> None:

        self._enabled = False

    def clear(self) -> None:

        self._entries.clear()

    def reset(self) -> None:

        self.clear()

        self._hits = DEFAULT_HITS

        self._misses = DEFAULT_MISSES

        self._enabled = DEFAULT_ENABLED

    def cleanup(self) -> None:

        now = time.time()

        expired = [
            key
            for key, entry in self._entries.items()
            if now - entry["time"] >= self._ttl
        ]

        for key in expired:
            self._entries.pop(key, None)

    def expire(self) -> None:

        self.cleanup()


# ==============================================================================
# Part 6. Cache API
# ==============================================================================

    def put(
        self,
        key: str,
        value: CacheValue,
    ) -> None:

        if self.size >= self._max_size and key not in self._entries:
            raise RuntimeError("cache capacity exceeded")

        self._entries[str(key)] = {
            "value": value,
            "time": time.time(),
        }

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        entry = self._entries.get(str(key))

        if entry is None:
            self._misses += 1
            return default

        if time.time() - entry["time"] >= self._ttl:
            self._entries.pop(str(key), None)
            self._misses += 1
            return default

        self._hits += 1

        return entry["value"]

    def remove(
        self,
        key: str,
    ) -> Any:

        entry = self._entries.pop(str(key), None)

        if entry is None:
            return None

        return entry["value"]

    def has(
        self,
        key: str,
    ) -> bool:

        return str(key) in self._entries

    def touch(
        self,
        key: str,
    ) -> bool:

        entry = self._entries.get(str(key))

        if entry is None:
            return False

        entry["time"] = time.time()

        return True

    def pop(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        entry = self._entries.pop(str(key), None)

        if entry is None:
            return default

        return entry["value"]

    def keys(self) -> list[str]:

        return list(self._entries.keys())

    def values(self) -> list[Any]:

        return [
            entry["value"]
            for entry in self._entries.values()
        ]

    def items(self) -> list[tuple[str, Any]]:

        return [
            (
                key,
                entry["value"],
            )
            for key, entry in self._entries.items()
        ]

    def clear_entries(self) -> None:

        self._entries.clear()

# ==============================================================================
# Part 7. Statistics
# ==============================================================================

    def record_hit(self) -> None:

        self._hits += 1

    def record_miss(self) -> None:

        self._misses += 1

    @property
    def hit_rate(self) -> float:

        total = self._hits + self._misses

        if total == 0:
            return 0.0

        return self._hits / total

    @property
    def miss_rate(self) -> float:

        total = self._hits + self._misses

        if total == 0:
            return 0.0

        return self._misses / total

    def stats(self) -> CacheStats:

        return {
            "hits": self._hits,
            "misses": self._misses,
        }

    def reset_stats(self) -> None:

        self._hits = DEFAULT_HITS
        self._misses = DEFAULT_MISSES


# ==============================================================================
# Part 8. Operations
# ==============================================================================

    def clone(self) -> "RuntimeCache":

        return self.from_dict(self.to_dict())

    copy = clone

    def merge(
        self,
        other: "RuntimeCache",
    ) -> "RuntimeCache":

        self._entries.update(other.entries)

        self._hits += other.hits

        self._misses += other.misses

        return self

    def update(
        self,
        state: CacheState,
    ) -> "RuntimeCache":

        self.restore(state)

        return self

    def snapshot(self) -> CacheState:

        return self.to_dict()

    def restore(
        self,
        state: CacheState,
    ) -> None:

        obj = self.from_dict(state)

        self._name = obj.name
        self._enabled = obj.enabled
        self._max_size = obj.max_size
        self._ttl = obj.ttl
        self._entries = obj.entries
        self._hits = obj.hits
        self._misses = obj.misses
        self._clean_interval = obj._clean_interval


# ==============================================================================
# Part 9. Validation
# ==============================================================================

    def validate_name(self) -> bool:

        return (
            isinstance(self._name, str)
            and
            bool(self._name.strip())
        )

    def validate_entries(self) -> bool:

        return isinstance(
            self._entries,
            dict,
        )

    def validate_limits(self) -> bool:

        return (
            self._max_size >= 0
            and
            self._ttl >= 0
            and
            self._clean_interval >= 0
        )

    def validate(self) -> bool:

        return all(
            (
                self.validate_name(),
                self.validate_entries(),
                self.validate_limits(),
            )
        )

    def normalize(self) -> "RuntimeCache":

        self._name = self._name.strip()

        return self


# ==============================================================================
# Part 10. Serialization
# ==============================================================================

    def to_dict(self) -> CacheState:

        return {
            "name": self._name,
            "enabled": self._enabled,
            "max_size": self._max_size,
            "ttl": self._ttl,
            "clean_interval": self._clean_interval,
            "entries": dict(self._entries),
            "hits": self._hits,
            "misses": self._misses,
        }

    @classmethod
    def from_dict(
        cls,
        data: CacheState,
    ) -> "RuntimeCache":

        cache = cls(
            name=data.get(
                "name",
                DEFAULT_NAME,
            ),
            enabled=data.get(
                "enabled",
                DEFAULT_ENABLED,
            ),
            max_size=data.get(
                "max_size",
                DEFAULT_MAX_SIZE,
            ),
            ttl=data.get(
                "ttl",
                DEFAULT_TTL,
            ),
            clean_interval=data.get(
                "clean_interval",
                DEFAULT_CLEAN_INTERVAL,
            ),
        )

        cache._entries.update(
            data.get(
                "entries",
                {},
            )
        )

        cache._hits = data.get(
            "hits",
            DEFAULT_HITS,
        )

        cache._misses = data.get(
            "misses",
            DEFAULT_MISSES,
        )

        return cache

    def to_tuple(self) -> tuple[Any, ...]:

        return (
            self._name,
            self._enabled,
            self._max_size,
            self._ttl,
            self._clean_interval,
            dict(self._entries),
            self._hits,
            self._misses,
        )

    @classmethod
    def from_tuple(
        cls,
        data: tuple[Any, ...],
    ) -> "RuntimeCache":

        cache = cls(
            name=data[0],
            enabled=data[1],
            max_size=data[2],
            ttl=data[3],
            clean_interval=data[4],
        )

        cache._entries.update(data[5])
        cache._hits = data[6]
        cache._misses = data[7]

        return cache

    def to_json(self) -> str:

        return json.dumps(
            self.to_dict(),
            indent=2,
            sort_keys=True,
        )

    @classmethod
    def from_json(
        cls,
        text: str,
    ) -> "RuntimeCache":

        return cls.from_dict(
            json.loads(text)
        )


# ==============================================================================
# Part 11. Diagnostics
# ==============================================================================

    def summary(self) -> dict[str, Any]:

        return {
            "name": self._name,
            "enabled": self._enabled,
            "size": self.size,
            "hits": self._hits,
            "misses": self._misses,
        }

    def diagnostics(self) -> dict[str, Any]:

        return {
            **self.summary(),
            "hit_rate": self.hit_rate,
            "miss_rate": self.miss_rate,
            "utilization": self.utilization,
            "valid": self.validate(),
        }

    def report(self) -> dict[str, Any]:

        return self.diagnostics()

    def status(self) -> str:

        if not self._enabled:
            return "disabled"

        return "enabled"


# ==============================================================================
# Part 12. Protocols
# ==============================================================================

    def __len__(self) -> int:

        return self.size

    def __contains__(
        self,
        key: object,
    ) -> bool:

        return str(key) in self._entries

    def __iter__(self):

        return iter(self.items())

    def __hash__(self) -> int:

        return hash(
            (
                self._name,
                self._max_size,
                self._ttl,
            )
        )

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(
            other,
            RuntimeCache,
        ):
            return False

        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"size={self.size}, "
            f"enabled={self._enabled})"
        )

    def __str__(self) -> str:

        return self._name

    def __bool__(self) -> bool:

        return self._enabled        