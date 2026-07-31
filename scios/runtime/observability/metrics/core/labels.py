"""
SciOS-NG Observability Metrics
==============================

Metric Labels
-------------

Production-grade label container for SciOS-NG.

Responsibilities
----------------
- Immutable-aware mapping interface
- Thread-safe operations
- Validation integration
- Snapshot / Restore
- Copy / Clone
- Merge / Diff
- Serialization
- Namespace helpers
- Filtering
- Prometheus-compatible labels
- OpenTelemetry-compatible attributes

Design Goals
------------
- Pythonic Mapping interface
- Thread-safe
- High performance
- Deterministic hashing
- Deep-copy safe
- Minimal allocations
- Production ready

Thread Safety
-------------
All mutating operations are protected by an internal RLock.

This class is intended to be safely shared between runtime
threads inside the SciOS observability subsystem.
"""

from __future__ import annotations

import json

from copy import deepcopy

from threading import RLock

from typing import (
    Any,
    Iterable,
    Iterator,
    Mapping,
)

from collections.abc import Mapping as MappingABC

from .exceptions import (
    MetricFrozenError,
)

from .validation import (
    MetricValidator,
)


__all__ = [
    "MetricLabels",
]

# ======================================================
# Internal Sentinel
# ======================================================

_MISSING = object()

# ==========================================================
# Constants
# ==========================================================

_EMPTY_DICT: dict[str, Any] = {}

_DEFAULT_NAMESPACE_SEPARATOR = "."

_DEFAULT_PREFIX_SEPARATOR = "_"

_RESERVED_PREFIXES = (
    "__",
)

# ==========================================================
# Helper Functions
# ==========================================================


def _deepcopy_mapping(
    mapping: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Return a deep copy of a mapping.
    """

    return deepcopy(dict(mapping))


def _sorted_items(
    mapping: Mapping[str, Any],
) -> tuple[tuple[str, Any], ...]:
    """
    Deterministic ordering for hashing.

    Example
    -------
    {"b":2,"a":1}

    becomes

    (
        ("a",1),
        ("b",2),
    )
    """

    return tuple(
        sorted(
            mapping.items(),
            key=lambda item: item[0],
        )
    )


def _ensure_mapping(
    value: Mapping[str, Any] | None,
) -> Mapping[str, Any]:
    """
    Normalize optional mapping.
    """

    if value is None:
        return _EMPTY_DICT

    if not isinstance(
        value,
        MappingABC,
    ):
        raise TypeError(
            "labels must be a Mapping."
        )

    return value


def _validate_labels(
    labels: Mapping[str, Any],
) -> None:
    """
    Delegate validation to MetricValidator.
    """

    MetricValidator.validate_labels(
        labels
    )


def _validate_label(
    key: str,
    value: Any,
) -> None:
    """
    Validate one label.
    """

    MetricValidator.validate_label_key(
        key
    )

    MetricValidator.validate_label_value(
        value
    )


# ==========================================================
# MetricLabels
# ==========================================================


class MetricLabels(MappingABC[str, Any]):
    """
    Thread-safe runtime label container.

    Features
    --------
    ✓ Mapping interface

    ✓ Validation

    ✓ Thread-safe

    ✓ Immutable-aware

    ✓ Snapshot

    ✓ Restore

    ✓ Merge

    ✓ Serialization

    ✓ Hashable

    ✓ Prometheus compatible

    ✓ OpenTelemetry compatible

    Notes
    -----
    Labels should remain relatively stable during
    the lifetime of a metric.

    Examples
    --------

    labels = MetricLabels(
        {
            "service": "kernel",
            "node": "gpu01",
        }
    )

    labels["service"]

    labels.freeze()

    snapshot = labels.snapshot()
    """

    # ======================================================
    # Construction
    # ======================================================

    def __init__(
        self,
        labels: Mapping[str, Any] | None = None,
    ) -> None:
        """
        Constructor.

        Full initialization logic is implemented
        in Part 2 (Construction API).
        """

        self._lock = RLock()

        self._labels: dict[str, Any] = {}

        self._frozen: bool = False

        self._namespace: str | None = None

        self._version: int = 0

        self._dirty: bool = False

        self._hash_cache: int | None = None

        self._snapshot_cache: dict[str, Any] | None = None

        # actual initialization continues
        # in Part 2

    # ======================================================
    # Internal Helpers
    # ======================================================

    def _invalidate_cache(
        self,
    ) -> None:
        """
        Invalidate cached values after mutation.
        """

        self._dirty = True

        self._hash_cache = None

        self._snapshot_cache = None

    def _require_mutable(
        self,
    ) -> None:
        """
        Raise if container is frozen.
        """

        if self._frozen:

            raise MetricFrozenError(
                "MetricLabels is frozen."
            )

    def _bump_version(
        self,
    ) -> None:
        """
        Increment internal version.

        Used for cache invalidation and
        future synchronization support.
        """

        self._version += 1

        self._invalidate_cache()

    # ======================================================
    # Remaining APIs
    # ======================================================

    #
    # Part 2
    # Construction API
    #

    #
    # Part 3
    # Mapping API
    #

    #
    # Part 4
    # CRUD API
    #

    #
    # Part 5
    # Snapshot API
    #

    #
    # Part 6
    # Serialization API
    #

    #
    # Part 7
    # Operator API
    #

    #
    # Part 8
    # Debug Helpers
    #

    #
    # Part 9
    # Thread Safety
    #

    #
    # Part 10
    # Production Utilities
    #
# ======================================================
# Construction API
# ======================================================

def __init__(
    self,
    labels: Mapping[str, Any] | None = None,
    *,
    namespace: str | None = None,
    frozen: bool = False,
    validate: bool = True,
) -> None:
    """
    Construct a MetricLabels object.

    Parameters
    ----------
    labels:
        Initial label mapping.

    namespace:
        Optional namespace.

    frozen:
        Start as immutable.

    validate:
        Validate labels during construction.
    """

    self._lock = RLock()

    self._labels: dict[str, Any] = {}

    self._namespace = namespace

    self._frozen = False

    self._version = 0

    self._dirty = False

    self._hash_cache = None

    self._snapshot_cache = None

    labels = _ensure_mapping(labels)

    if validate:

        _validate_labels(labels)

    self._labels.update(
        _deepcopy_mapping(labels)
    )

    if frozen:

        self.freeze()


# ======================================================
# Factory Methods
# ======================================================

@classmethod
def empty(
    cls,
) -> "MetricLabels":
    """
    Create an empty label container.
    """

    return cls()


@classmethod
def from_dict(
    cls,
    data: Mapping[str, Any],
) -> "MetricLabels":
    """
    Construct from mapping.
    """

    return cls(data)


@classmethod
def from_pairs(
    cls,
    pairs: Iterable[tuple[str, Any]],
) -> "MetricLabels":
    """
    Construct from iterable of pairs.
    """

    return cls(
        dict(pairs)
    )


@classmethod
def from_keys(
    cls,
    keys: Iterable[str],
    value: Any = "",
) -> "MetricLabels":
    """
    Build labels using identical values.
    """

    return cls(
        {
            key: value
            for key in keys
        }
    )


@classmethod
def from_json(
    cls,
    text: str,
) -> "MetricLabels":
    """
    Construct from JSON string.
    """

    data = json.loads(text)

    if not isinstance(
        data,
        dict,
    ):
        raise TypeError(
            "JSON must represent an object."
        )

    return cls(data)


@classmethod
def copy_of(
    cls,
    other: "MetricLabels",
) -> "MetricLabels":
    """
    Deep-copy another MetricLabels.
    """

    if not isinstance(
        other,
        MetricLabels,
    ):
        raise TypeError(
            "copy_of() expects MetricLabels."
        )

    return cls(
        other._labels,
        namespace=other._namespace,
        frozen=other._frozen,
    )


# ======================================================
# Validation
# ======================================================

@staticmethod
def validate(
    labels: Mapping[str, Any],
) -> None:
    """
    Validate a mapping.
    """

    _validate_labels(labels)


@staticmethod
def validate_label(
    key: str,
    value: Any,
) -> None:
    """
    Validate a single label.
    """

    _validate_label(
        key,
        value,
    )


@staticmethod
def is_valid(
    labels: Mapping[str, Any],
) -> bool:
    """
    Return True if labels are valid.
    """

    try:

        _validate_labels(labels)

        return True

    except Exception:

        return False


@staticmethod
def normalize(
    labels: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate and normalize labels.
    """

    _validate_labels(labels)

    return dict(labels)


# ======================================================
# Internal Storage
# ======================================================

@property
def storage(
    self,
) -> dict[str, Any]:
    """
    Internal mutable storage.

    Intended for advanced runtime components.
    """

    return self._labels


@property
def namespace(
    self,
) -> str | None:
    """
    Namespace assigned to labels.
    """

    return self._namespace


@namespace.setter
def namespace(
    self,
    value: str | None,
) -> None:

    with self._lock:

        self._require_mutable()

        self._namespace = value

        self._bump_version()


@property
def version(
    self,
) -> int:
    """
    Internal version counter.
    """

    return self._version


@property
def frozen(
    self,
) -> bool:
    """
    Immutable state.
    """

    return self._frozen


@property
def dirty(
    self,
) -> bool:
    """
    Indicates cached data is stale.
    """

    return self._dirty


@property
def size(
    self,
) -> int:
    """
    Number of labels.
    """

    return len(
        self._labels
    )


@property
def empty(
    self,
) -> bool:
    """
    True if no labels exist.
    """

    return not self._labels


@property
def snapshot_cached(
    self,
) -> bool:
    """
    Whether snapshot cache exists.
    """

    return (
        self._snapshot_cache
        is not None
    )


def clear_cache(
    self,
) -> None:
    """
    Clear all caches.
    """

    self._invalidate_cache()


def reset(
    self,
) -> None:
    """
    Reset container to empty state.
    """

    with self._lock:

        self._require_mutable()

        self._labels.clear()

        self._namespace = None

        self._bump_version()


def initialize(
    self,
    labels: Mapping[str, Any],
    *,
    validate: bool = True,
) -> None:
    """
    Replace internal storage.
    """

    with self._lock:

        self._require_mutable()

        if validate:

            _validate_labels(labels)

        self._labels = _deepcopy_mapping(labels)

        self._bump_version()
# ======================================================
# Mapping API
# ======================================================

def __getitem__(
    self,
    key: str,
) -> Any:
    """
    Retrieve a label value.

    Raises
    ------
    KeyError
        If the key does not exist.
    """

    return self._labels[key]


def __iter__(
    self,
) -> Iterator[str]:
    """
    Iterate over label keys.

    A snapshot iterator is returned to avoid runtime
    modification during iteration.
    """

    with self._lock:

        return iter(tuple(self._labels.keys()))


def __len__(
    self,
) -> int:
    """
    Number of labels.
    """

    return len(self._labels)


def __contains__(
    self,
    key: object,
) -> bool:
    """
    Membership test.

    Example
    -------
    >>> "host" in labels
    """

    return key in self._labels


# ======================================================
# Standard Mapping Views
# ======================================================

def keys(
    self,
):
    """
    Return a dynamic keys view.

    Equivalent to dict.keys().
    """

    return self._labels.keys()


def values(
    self,
):
    """
    Return a dynamic values view.

    Equivalent to dict.values().
    """

    return self._labels.values()


def items(
    self,
):
    """
    Return a dynamic items view.

    Equivalent to dict.items().
    """

    return self._labels.items()


# ======================================================
# Snapshot Views
# ======================================================

@property
def keys_list(
    self,
) -> list[str]:
    """
    Immutable list of keys.
    """

    with self._lock:

        return list(self._labels.keys())


@property
def values_list(
    self,
) -> list[Any]:
    """
    Immutable list of values.
    """

    with self._lock:

        return list(self._labels.values())


@property
def items_list(
    self,
) -> list[tuple[str, Any]]:
    """
    Immutable list of items.
    """

    with self._lock:

        return list(self._labels.items())


# ======================================================
# Lookup Helpers
# ======================================================

def get(
    self,
    key: str,
    default: Any = None,
) -> Any:
    """
    Safe lookup.

    Equivalent to dict.get().
    """

    return self._labels.get(
        key,
        default,
    )


def first(
    self,
) -> tuple[str, Any] | None:
    """
    Return the first label.

    Returns
    -------
    tuple | None
    """

    with self._lock:

        for item in self._labels.items():

            return item

    return None


def last(
    self,
) -> tuple[str, Any] | None:
    """
    Return the last inserted label.

    Python dictionaries preserve insertion order.
    """

    with self._lock:

        if not self._labels:

            return None

        key = next(
            reversed(self._labels)
        )

        return (
            key,
            self._labels[key],
        )


# ======================================================
# Query Helpers
# ======================================================

def has_key(
    self,
    key: str,
) -> bool:
    """
    Alias of __contains__().
    """

    return key in self._labels


def has_value(
    self,
    value: Any,
) -> bool:
    """
    Check whether a value exists.
    """

    return value in self._labels.values()


def contains_all(
    self,
    keys: Iterable[str],
) -> bool:
    """
    True if every key exists.
    """

    return all(
        key in self._labels
        for key in keys
    )


def contains_any(
    self,
    keys: Iterable[str],
) -> bool:
    """
    True if at least one key exists.
    """

    return any(
        key in self._labels
        for key in keys
    )


# ======================================================
# Iterators
# ======================================================

def iter_keys(
    self,
) -> Iterator[str]:
    """
    Stable iterator over keys.
    """

    return iter(
        self.keys_list
    )


def iter_values(
    self,
) -> Iterator[Any]:
    """
    Stable iterator over values.
    """

    return iter(
        self.values_list
    )


def iter_items(
    self,
) -> Iterator[tuple[str, Any]]:
    """
    Stable iterator over items.
    """

    return iter(
        self.items_list
    )


# ======================================================
# Ordering Helpers
# ======================================================

def sorted_keys(
    self,
) -> list[str]:
    """
    Keys sorted alphabetically.
    """

    return sorted(
        self._labels
    )


def sorted_items(
    self,
) -> list[tuple[str, Any]]:
    """
    Items sorted by key.
    """

    return sorted(
        self._labels.items(),
        key=lambda item: item[0],
    )


# ======================================================
# Convenience
# ======================================================

@property
def count(
    self,
) -> int:
    """
    Alias of len(labels).
    """

    return len(self)


@property
def is_empty(
    self,
) -> bool:
    """
    True if container has no labels.
    """

    return len(self) == 0


@property
def is_not_empty(
    self,
) -> bool:
    """
    True if container contains labels.
    """

    return len(self) > 0
# ======================================================
# CRUD API
# ======================================================

def set(
    self,
    key: str,
    value: Any,
) -> "MetricLabels":
    """
    Set a label value.

    Returns
    -------
    MetricLabels
        Self for fluent chaining.
    """

    with self._lock:

        self._require_mutable()

        _validate_label(
            key,
            value,
        )

        previous = self._labels.get(key)

        if previous != value:

            self._labels[key] = value

            self._bump_version()

        return self


def get(
    self,
    key: str,
    default: Any = None,
) -> Any:
    """
    Safe lookup.

    Equivalent to dict.get().
    """

    return self._labels.get(
        key,
        default,
    )


def update(
    self,
    labels: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> "MetricLabels":
    """
    Update labels.

    Examples
    --------
    labels.update(
        {"host": "gpu01"}
    )

    labels.update(
        region="asia"
    )

    labels.update(
        {"host": "gpu01"},
        env="prod",
    )
    """

    with self._lock:

        self._require_mutable()

        merged: dict[str, Any] = {}

        if labels:

            labels = _ensure_mapping(labels)

            _validate_labels(labels)

            merged.update(labels)

        if kwargs:

            _validate_labels(kwargs)

            merged.update(kwargs)

        changed = False

        for key, value in merged.items():

            if self._labels.get(key) != value:

                self._labels[key] = value

                changed = True

        if changed:

            self._bump_version()

        return self


def pop(
    self,
    key: str,
    default: Any = _MISSING,
) -> Any:
    """
    Remove and return a label.

    Raises
    ------
    KeyError
        If missing and no default supplied.
    """

    with self._lock:

        self._require_mutable()

        if default is _MISSING:

            value = self._labels.pop(key)

        else:

            value = self._labels.pop(
                key,
                default,
            )

        self._bump_version()

        return value


def remove(
    self,
    key: str,
) -> bool:
    """
    Remove a label.

    Returns
    -------
    bool
        True if removed.
    """

    with self._lock:

        self._require_mutable()

        if key not in self._labels:

            return False

        del self._labels[key]

        self._bump_version()

        return True


def clear(
    self,
) -> "MetricLabels":
    """
    Remove all labels.
    """

    with self._lock:

        self._require_mutable()

        if self._labels:

            self._labels.clear()

            self._bump_version()

        return self


def setdefault(
    self,
    key: str,
    default: Any = None,
) -> Any:
    """
    Insert default value if key does not exist.

    Returns
    -------
    Existing or inserted value.
    """

    with self._lock:

        self._require_mutable()

        if key in self._labels:

            return self._labels[key]

        _validate_label(
            key,
            default,
        )

        self._labels[key] = default

        self._bump_version()

        return default


# ======================================================
# Bulk Helpers
# ======================================================

def extend(
    self,
    other: Mapping[str, Any],
) -> "MetricLabels":
    """
    Alias of update().
    """

    return self.update(other)


def replace(
    self,
    labels: Mapping[str, Any],
) -> "MetricLabels":
    """
    Replace the entire label set.
    """

    with self._lock:

        self._require_mutable()

        labels = _ensure_mapping(labels)

        _validate_labels(labels)

        self._labels.clear()

        self._labels.update(
            _deepcopy_mapping(labels)
        )

        self._bump_version()

        return self


def rename(
    self,
    old_key: str,
    new_key: str,
) -> "MetricLabels":
    """
    Rename a label key.
    """

    with self._lock:

        self._require_mutable()

        if old_key not in self._labels:

            raise KeyError(old_key)

        _validate_label(
            new_key,
            self._labels[old_key],
        )

        self._labels[new_key] = self._labels.pop(
            old_key
        )

        self._bump_version()

        return self


def increment(
    self,
    key: str,
    amount: int | float = 1,
) -> Any:
    """
    Increment a numeric label.
    """

    with self._lock:

        self._require_mutable()

        current = self._labels.get(
            key,
            0,
        )

        if not isinstance(
            current,
            (int, float),
        ):
            raise TypeError(
                f"Label '{key}' is not numeric."
            )

        current += amount

        self._labels[key] = current

        self._bump_version()

        return current


def decrement(
    self,
    key: str,
    amount: int | float = 1,
) -> Any:
    """
    Decrement a numeric label.
    """

    return self.increment(
        key,
        -amount,
    )
# ======================================================
# Freeze / Snapshot API
# ======================================================

@property
def frozen(
    self,
) -> bool:
    """
    Whether this container is immutable.
    """

    return self._frozen


def freeze(
    self,
) -> "MetricLabels":
    """
    Freeze this label container.

    Returns
    -------
    MetricLabels
        Self.
    """

    with self._lock:

        self._frozen = True

        return self


def unfreeze(
    self,
) -> "MetricLabels":
    """
    Make labels mutable again.
    """

    with self._lock:

        self._frozen = False

        return self


# ======================================================
# Snapshot
# ======================================================

def snapshot(
    self,
) -> dict[str, Any]:
    """
    Create an immutable snapshot.

    Returns
    -------
    dict
    """

    with self._lock:

        return _deepcopy_mapping(
            self._labels
        )


def restore(
    self,
    snapshot: Mapping[str, Any],
) -> "MetricLabels":
    """
    Restore labels from snapshot.
    """

    with self._lock:

        self._require_mutable()

        snapshot = _ensure_mapping(snapshot)

        _validate_labels(snapshot)

        self._labels.clear()

        self._labels.update(
            _deepcopy_mapping(snapshot)
        )

        self._bump_version()

        return self


# ======================================================
# Copy
# ======================================================

def copy(
    self,
) -> "MetricLabels":
    """
    Deep copy.

    Frozen state is preserved.
    """

    with self._lock:

        clone = self.__class__(

            labels=self._labels,

            namespace=self._namespace,

            frozen=self._frozen,

            validate=False,

        )

        return clone


def clone(
    self,
    *,
    frozen: bool | None = None,
) -> "MetricLabels":
    """
    Clone with optional frozen override.
    """

    obj = self.copy()

    if frozen is not None:

        if frozen:

            obj.freeze()

        else:

            obj.unfreeze()

    return obj


# ======================================================
# Merge
# ======================================================

def merge(
    self,
    other: Mapping[str, Any]
    | "MetricLabels",
    *,
    overwrite: bool = True,
) -> "MetricLabels":
    """
    Merge labels into a new object.

    Parameters
    ----------
    overwrite
        Existing keys are overwritten if True.
    """

    if isinstance(
        other,
        MetricLabels,
    ):

        other = other.snapshot()

    other = _ensure_mapping(other)

    _validate_labels(other)

    merged = self.copy()

    for key, value in other.items():

        if overwrite:

            merged._labels[key] = value

        elif key not in merged._labels:

            merged._labels[key] = value

    merged._bump_version()

    return merged


def merge_inplace(
    self,
    other: Mapping[str, Any]
    | "MetricLabels",
    *,
    overwrite: bool = True,
) -> "MetricLabels":
    """
    Merge into this object.
    """

    with self._lock:

        self._require_mutable()

        if isinstance(
            other,
            MetricLabels,
        ):

            other = other.snapshot()

        other = _ensure_mapping(other)

        _validate_labels(other)

        changed = False

        for key, value in other.items():

            if overwrite:

                if self._labels.get(key) != value:

                    self._labels[key] = value

                    changed = True

            else:

                if key not in self._labels:

                    self._labels[key] = value

                    changed = True

        if changed:

            self._bump_version()

        return self


# ======================================================
# Diff
# ======================================================

def diff(
    self,
    other: Mapping[str, Any]
    | "MetricLabels",
) -> dict[str, tuple[Any, Any]]:
    """
    Compute differences.

    Returns
    -------
    dict

        key -> (old, new)
    """

    if isinstance(
        other,
        MetricLabels,
    ):

        other = other.snapshot()

    other = dict(other)

    result = {}

    keys = set(self._labels)

    keys.update(other)

    for key in keys:

        left = self._labels.get(key)

        right = other.get(key)

        if left != right:

            result[key] = (
                left,
                right,
            )

    return result


# ======================================================
# Equality Helpers
# ======================================================

def equals(
    self,
    other: object,
) -> bool:
    """
    Semantic equality.
    """

    if not isinstance(
        other,
        MetricLabels,
    ):

        return False

    return self._labels == other._labels
# ======================================================
# Serialization API
# ======================================================

def to_dict(
    self,
    *,
    include_metadata: bool = False,
) -> dict[str, Any]:
    """
    Serialize labels to a dictionary.

    Parameters
    ----------
    include_metadata
        Include internal metadata.

    Returns
    -------
    dict
    """

    with self._lock:

        labels = _deepcopy_mapping(
            self._labels
        )

        if not include_metadata:

            return labels

        return {
            "labels": labels,
            "namespace": self._namespace,
            "version": self._version,
            "frozen": self._frozen,
        }


@classmethod
def from_dict(
    cls,
    data: Mapping[str, Any],
) -> "MetricLabels":
    """
    Construct MetricLabels from dictionary.

    Supports both formats:

    {
        "host": "gpu01"
    }

    and

    {
        "labels": {...},
        "namespace": "...",
        "version": 3,
        "frozen": False
    }
    """

    data = _ensure_mapping(data)

    if "labels" in data:

        obj = cls(

            labels=data.get("labels", {}),

            namespace=data.get("namespace"),

            frozen=data.get("frozen", False),

            validate=False,

        )

        obj._version = int(
            data.get("version", 0)
        )

        return obj

    return cls(
        labels=data,
    )


def to_json(
    self,
    *,
    indent: int | None = 2,
    sort_keys: bool = True,
    include_metadata: bool = False,
    ensure_ascii: bool = False,
) -> str:
    """
    Serialize to JSON.
    """

    return json.dumps(

        self.to_dict(
            include_metadata=include_metadata,
        ),

        indent=indent,

        sort_keys=sort_keys,

        ensure_ascii=ensure_ascii,
    )


@classmethod
def from_json(
    cls,
    text: str,
) -> "MetricLabels":
    """
    Deserialize from JSON.
    """

    data = json.loads(text)

    return cls.from_dict(
        data
    )


def as_tuple(
    self,
    *,
    sort_keys: bool = True,
) -> tuple[tuple[str, Any], ...]:
    """
    Immutable tuple representation.

    Useful for hashing, cache keys,
    registry lookups, and equality.
    """

    with self._lock:

        items = list(
            self._labels.items()
        )

    if sort_keys:

        items.sort(
            key=lambda x: x[0]
        )

    return tuple(items)


# ======================================================
# Pickle Support
# ======================================================

def __getstate__(
    self,
) -> dict[str, Any]:
    """
    Pickle support.
    """

    return self.to_dict(
        include_metadata=True
    )


def __setstate__(
    self,
    state: Mapping[str, Any],
) -> None:
    """
    Restore from pickle.
    """

    restored = self.from_dict(
        state
    )

    self.__dict__.update(
        restored.__dict__
    )


# ======================================================
# String Helpers
# ======================================================

def __str__(
    self,
) -> str:
    """
    Human-readable representation.
    """

    return self.to_json(
        indent=None,
        include_metadata=False,
    )
# ======================================================
# Operator API
# ======================================================

def __copy__(
    self,
) -> "MetricLabels":
    """
    Shallow copy.

    Since labels are treated as immutable values,
    this is equivalent to copy().
    """

    return self.copy()


def __deepcopy__(
    self,
    memo: dict[int, Any],
) -> "MetricLabels":
    """
    Deep copy.

    Compatible with the standard copy module.
    """

    obj = self.__class__(

        labels=_deepcopy_mapping(
            self._labels
        ),

        namespace=self._namespace,

        frozen=self._frozen,

        validate=False,

    )

    obj._version = self._version

    memo[id(self)] = obj

    return obj


def __or__(
    self,
    other: Mapping[str, Any] | "MetricLabels",
) -> "MetricLabels":
    """
    Merge labels.

    Examples
    --------
    labels = labels | {
        "host": "gpu01"
    }

    labels = labels | other_labels
    """

    return self.merge(
        other,
        overwrite=True,
    )


def __ior__(
    self,
    other: Mapping[str, Any] | "MetricLabels",
) -> "MetricLabels":
    """
    In-place merge.

    Examples
    --------
    labels |= {
        "env": "prod"
    }
    """

    return self.merge_inplace(
        other,
        overwrite=True,
    )


def __eq__(
    self,
    other: object,
) -> bool:
    """
    Equality ignores metadata and compares only
    label contents.
    """

    if self is other:

        return True

    if not isinstance(
        other,
        MetricLabels,
    ):

        return False

    return (
        self._labels
        == other._labels
    )


def __hash__(
    self,
) -> int:
    """
    Stable hash based on label contents.

    Raises
    ------
    TypeError
        If a label value is unhashable.
    """

    try:

        return hash(
            self.as_tuple()
        )

    except TypeError as exc:

        raise TypeError(
            "MetricLabels contains "
            "unhashable values."
        ) from exc
# ======================================================
# Debug Helpers
# ======================================================

def __bool__(
    self,
) -> bool:
    """
    Truth value.

    Empty labels evaluate to False.
    """

    return bool(self._labels)


def __str__(
    self,
) -> str:
    """
    Human-readable representation.

    Returns only the labels without internal metadata.
    """

    return self.to_json(
        indent=None,
        include_metadata=False,
    )


def __repr__(
    self,
) -> str:
    """
    Developer-friendly representation.
    """

    return (
        f"{self.__class__.__name__}("
        f"count={len(self)}, "
        f"namespace={self._namespace!r}, "
        f"version={self._version}, "
        f"frozen={self._frozen})"
    )


# ======================================================
# Statistics
# ======================================================

@property
def statistics(
    self,
) -> dict[str, Any]:
    """
    Runtime statistics.

    Useful for dashboards and diagnostics.
    """

    with self._lock:

        return {

            "count": len(self._labels),

            "version": self._version,

            "frozen": self._frozen,

            "namespace": self._namespace,

            "empty": not self._labels,

            "keys": tuple(
                sorted(self._labels.keys())
            ),

        }


# ======================================================
# Diagnostics
# ======================================================

@property
def diagnostics(
    self,
) -> dict[str, Any]:
    """
    Extended runtime diagnostics.

    Intended for debugging and observability.
    """

    with self._lock:

        return {

            "class": self.__class__.__name__,

            "id": hex(id(self)),

            "count": len(self._labels),

            "namespace": self._namespace,

            "version": self._version,

            "frozen": self._frozen,

            "empty": not self._labels,

            "keys": list(
                sorted(
                    self._labels.keys()
                )
            ),

            "values_types": {

                key: type(value).__name__

                for key, value in self._labels.items()

            },

            "memory_bytes": (
                self._labels.__sizeof__()
            ),

            "hash": (
                hash(self)
                if self._labels
                else None
            ),

        }


def pprint(
    self,
) -> None:
    """
    Pretty-print labels.
    """

    print(
        self.to_json(
            indent=2,
            include_metadata=True,
        )
    )


def dump(
    self,
) -> dict[str, Any]:
    """
    Alias for diagnostics().
    """

    return self.diagnostics


def is_empty(
    self,
) -> bool:
    """
    Whether no labels exist.
    """

    return not self._labels


def contains_key(
    self,
    key: str,
) -> bool:
    """
    Whether a key exists.
    """

    return key in self._labels


def contains_value(
    self,
    value: Any,
) -> bool:
    """
    Whether a value exists.
    """

    return value in self._labels.values()
# ======================================================
# Thread Safety
# ======================================================

from contextlib import contextmanager

# ------------------------------------------------------
# Lock Helpers
# ------------------------------------------------------

@property
def lock(
    self,
) -> RLock:
    """
    Return the internal re-entrant lock.

    Advanced users may synchronize several
    MetricLabels instances manually.
    """

    return self._lock


@property
def locked(
    self,
) -> bool:
    """
    Best-effort indication that this object
    owns a lock.

    Since Python's RLock does not expose a
    reliable locked() API across versions,
    this simply indicates that a lock exists.
    """

    return self._lock is not None


# ------------------------------------------------------
# Context Manager
# ------------------------------------------------------

@contextmanager
def synchronized(
    self,
):
    """
    Execute multiple operations atomically.

    Example
    -------
    with labels.synchronized():

        labels.set("host", "gpu01")
        labels.set("device", "cuda")
    """

    self._lock.acquire()

    try:

        yield self

    finally:

        self._lock.release()


# ------------------------------------------------------
# Atomic Operations
# ------------------------------------------------------

def atomic_update(
    self,
    updater,
) -> "MetricLabels":
    """
    Execute an update callback while holding
    the internal lock.

    Parameters
    ----------
    updater
        Callable accepting this MetricLabels
        instance.

    Returns
    -------
    MetricLabels
    """

    with self._lock:

        self._require_mutable()

        updater(self)

        self._bump_version()

        return self


def compare_and_swap(
    self,
    key: str,
    expected: Any,
    new_value: Any,
) -> bool:
    """
    Atomic compare-and-swap.

    Returns
    -------
    bool
        True if replacement succeeded.
    """

    with self._lock:

        self._require_mutable()

        current = self._labels.get(key)

        if current != expected:

            return False

        MetricValidator.validate_label_key(
            key
        )

        MetricValidator.validate_label_value(
            new_value
        )

        self._labels[key] = new_value

        self._bump_version()

        return True


def replace_all(
    self,
    labels: Mapping[str, Any],
) -> "MetricLabels":
    """
    Atomically replace all labels.
    """

    with self._lock:

        self._require_mutable()

        _validate_labels(labels)

        self._labels.clear()

        self._labels.update(
            _deepcopy_mapping(labels)
        )

        self._bump_version()

        return self


# ------------------------------------------------------
# Internal Mutation Guards
# ------------------------------------------------------

def _require_mutable(
    self,
) -> None:
    """
    Ensure the object is mutable.
    """

    if self._frozen:

        raise MetricFrozenError(
            "MetricLabels is frozen."
        )


def _mutate(
    self,
    callback,
):
    """
    Internal mutation helper.

    All write operations should eventually
    route through this helper.
    """

    with self._lock:

        self._require_mutable()

        result = callback()

        self._bump_version()

        return result


def _bump_version(
    self,
) -> None:
    """
    Increment internal version.
    """

    self._version += 1


# ------------------------------------------------------
# Context Protocol
# ------------------------------------------------------

def __enter__(
    self,
) -> "MetricLabels":
    """
    Acquire internal lock.
    """

    self._lock.acquire()

    return self


def __exit__(
    self,
    exc_type,
    exc,
    tb,
) -> bool:
    """
    Release internal lock.
    """

    self._lock.release()

    return False
# ======================================================
# Production Utilities
# ======================================================

from types import MappingProxyType

# ------------------------------------------------------
# Immutable Views
# ------------------------------------------------------

@property
def view(
    self,
) -> Mapping[str, Any]:
    """
    Read-only view of the labels.
    """

    return MappingProxyType(
        self._labels
    )


def immutable(
    self,
) -> Mapping[str, Any]:
    """
    Alias for immutable view.
    """

    return self.view


# ------------------------------------------------------
# Diff
# ------------------------------------------------------

def diff(
    self,
    other: Mapping[str, Any] | "MetricLabels",
) -> dict[str, dict[str, Any]]:
    """
    Compute differences.

    Returns
    -------
    {
        "added": {},
        "removed": {},
        "changed": {}
    }
    """

    if isinstance(
        other,
        MetricLabels,
    ):
        other = other.to_dict()

    other = dict(other)

    added = {}
    removed = {}
    changed = {}

    for key, value in other.items():

        if key not in self._labels:

            added[key] = value

        elif self._labels[key] != value:

            changed[key] = (

                self._labels[key],
                value,
            )

    for key, value in self._labels.items():

        if key not in other:

            removed[key] = value

    return {

        "added": added,

        "removed": removed,

        "changed": changed,

    }


# ------------------------------------------------------
# Filtering
# ------------------------------------------------------

def select(
    self,
    *keys: str,
) -> "MetricLabels":
    """
    Keep only selected keys.
    """

    return self.__class__(

        {

            k: v

            for k, v in self._labels.items()

            if k in keys

        },

        namespace=self._namespace,

    )


def exclude(
    self,
    *keys: str,
) -> "MetricLabels":
    """
    Remove selected keys.
    """

    return self.__class__(

        {

            k: v

            for k, v in self._labels.items()

            if k not in keys

        },

        namespace=self._namespace,

    )


def filter(
    self,
    predicate,
) -> "MetricLabels":
    """
    Generic filtering.
    """

    return self.__class__(

        {

            k: v

            for k, v in self._labels.items()

            if predicate(k, v)

        },

        namespace=self._namespace,

    )


# ------------------------------------------------------
# Prefix Helpers
# ------------------------------------------------------

def with_prefix(
    self,
    prefix: str,
) -> "MetricLabels":
    """
    Prefix every key.
    """

    return self.__class__(

        {

            f"{prefix}{k}": v

            for k, v in self._labels.items()

        },

        namespace=self._namespace,

    )


def strip_prefix(
    self,
    prefix: str,
) -> "MetricLabels":
    """
    Remove prefix from keys.
    """

    n = len(prefix)

    return self.__class__(

        {

            (

                k[n:]

                if k.startswith(prefix)

                else k

            ): v

            for k, v in self._labels.items()

        },

        namespace=self._namespace,

    )


def startswith(
    self,
    prefix: str,
) -> "MetricLabels":
    """
    Select keys starting with prefix.
    """

    return self.filter(

        lambda k, _: k.startswith(
            prefix
        )

    )


# ------------------------------------------------------
# Namespace Helpers
# ------------------------------------------------------

@property
def namespace(
    self,
) -> str | None:
    """
    Current namespace.
    """

    return self._namespace


def with_namespace(
    self,
    namespace: str,
) -> "MetricLabels":
    """
    Clone with new namespace.
    """

    clone = self.copy()

    clone._namespace = namespace

    return clone


def clear_namespace(
    self,
) -> "MetricLabels":
    """
    Remove namespace.
    """

    return self.with_namespace(
        None
    )


# ------------------------------------------------------
# Final Polish
# ------------------------------------------------------

@property
def size(
    self,
) -> int:
    """
    Number of labels.
    """

    return len(
        self._labels
    )


@property
def version(
    self,
) -> int:
    """
    Internal version.
    """

    return self._version


def validate(
    self,
) -> bool:
    """
    Validate all labels.
    """

    MetricValidator.validate_labels(
        self._labels
    )

    return True


def touch(
    self,
) -> None:
    """
    Increment version without modifying labels.
    """

    with self._lock:

        self._bump_version()


def reset(
    self,
) -> None:
    """
    Clear labels and reset state.
    """

    with self._lock:

        self._require_mutable()

        self._labels.clear()

        self._version = 0


def seal(
    self,
) -> "MetricLabels":
    """
    Finalize object for production.

    Equivalent to freeze().
    """

    self.freeze()

    return self                                            