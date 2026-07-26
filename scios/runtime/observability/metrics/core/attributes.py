"""
SciOS Observability
==================

Metric Attributes.

MetricAttributes is a thread-safe container used to store
structured metadata associated with metrics.

Unlike MetricLabels, attributes are intended to carry rich,
descriptive metadata and may contain nested structures.

Responsibilities
----------------
- Store runtime attributes
- Validate attribute names and values
- Support nested mappings
- Freeze / unfreeze
- Snapshot / restore
- Merge / clone
- Serialize to multiple formats
- Thread-safe mutation
- Production-grade diagnostics
"""

from __future__ import annotations

import copy
import json

from collections.abc import (
    Iterator,
    Mapping,
    MutableMapping,
)

from contextlib import contextmanager

from threading import RLock

from typing import (
    Any,
    Callable,
    Final,
    TypeAlias,
)

from .exceptions import (
    MetricFrozenError,
)

from .validation import (
    MetricValidator,
)

__all__ = [
    "MetricAttributes",
]

# =====================================================
# Constants
# =====================================================

DEFAULT_NAMESPACE: Final[str] = "default"

DEFAULT_VERSION: Final[int] = 0

MAX_ATTRIBUTE_DEPTH: Final[int] = 32

MAX_ATTRIBUTE_COUNT: Final[int] = 4096

# =====================================================
# Type Aliases
# =====================================================

AttributeValue: TypeAlias = Any

AttributeMapping: TypeAlias = Mapping[
    str,
    AttributeValue,
]

MutableAttributeMapping: TypeAlias = MutableMapping[
    str,
    AttributeValue,
]

AttributePredicate: TypeAlias = Callable[
    [str, AttributeValue],
    bool,
]

# =====================================================
# Helper Functions
# =====================================================

def _deepcopy_mapping(
    mapping: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Create a deep copy of a mapping.
    """

    return copy.deepcopy(
        dict(mapping)
    )


def _ensure_mapping(
    value: Any,
) -> dict[str, Any]:
    """
    Ensure a mapping object.
    """

    if value is None:

        return {}

    if isinstance(
        value,
        Mapping,
    ):

        return dict(value)

    raise TypeError(
        "Expected mapping."
    )


def _normalize_key(
    key: str,
) -> str:
    """
    Normalize attribute key.

    Removes surrounding whitespace.
    """

    return key.strip()


def _is_mapping(
    value: Any,
) -> bool:
    """
    Return True if value behaves
    like a mapping.
    """

    return isinstance(
        value,
        Mapping,
    )


def _flatten_dict(
    mapping: Mapping[str, Any],
    prefix: str = "",
) -> dict[str, Any]:
    """
    Flatten nested dictionaries.

    Example
    -------
    {"a": {"b": 1}}
        ->
    {"a.b": 1}
    """

    result: dict[str, Any] = {}

    for key, value in mapping.items():

        full_key = (
            f"{prefix}.{key}"
            if prefix
            else key
        )

        if isinstance(
            value,
            Mapping,
        ):

            result.update(
                _flatten_dict(
                    value,
                    full_key,
                )
            )

        else:

            result[
                full_key
            ] = value

    return result


def _unflatten_dict(
    mapping: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Restore flattened dictionary.

    Example
    -------
    {"a.b": 1}
        ->
    {"a":{"b":1}}
    """

    root: dict[str, Any] = {}

    for key, value in mapping.items():

        current = root

        parts = key.split(".")

        for part in parts[:-1]:

            current = current.setdefault(
                part,
                {},
            )

        current[
            parts[-1]
        ] = value

    return root


# =====================================================
# MetricAttributes
# =====================================================

class MetricAttributes(
    MutableMapping[
        str,
        AttributeValue,
    ]
):
    """
    Thread-safe container for metric attributes.

    MetricAttributes stores arbitrary runtime metadata
    associated with a metric.

    Compared to MetricLabels, attributes are richer,
    may contain nested mappings and are intended for
    descriptive metadata rather than metric identity.
    """

    ...
# =====================================================
# Construction API
# =====================================================

def __init__(
    self,
    attributes: AttributeMapping | None = None,
    *,
    namespace: str | None = DEFAULT_NAMESPACE,
    frozen: bool = False,
    validate: bool = True,
) -> None:
    """
    Initialize MetricAttributes.

    Parameters
    ----------
    attributes
        Initial attribute mapping.

    namespace
        Logical namespace.

    frozen
        Whether this instance starts frozen.

    validate
        Validate input mapping.
    """

    self._lock = RLock()

    self._attributes: dict[str, AttributeValue] = {}

    self._namespace = namespace

    self._version = DEFAULT_VERSION

    self._frozen = frozen

    if attributes is None:

        return

    mapping = _ensure_mapping(
        attributes
    )

    if validate:

        MetricValidator.validate_attributes(
            mapping
        )

    self._attributes.update(
        _deepcopy_mapping(
            mapping
        )
    )


# -----------------------------------------------------
# Factory Methods
# -----------------------------------------------------

@classmethod
def empty(
    cls,
) -> "MetricAttributes":
    """
    Create an empty container.
    """

    return cls()


@classmethod
def from_mapping(
    cls,
    mapping: AttributeMapping,
) -> "MetricAttributes":
    """
    Construct from mapping.
    """

    return cls(
        attributes=mapping,
    )


@classmethod
def from_pairs(
    cls,
    *pairs: tuple[str, AttributeValue],
) -> "MetricAttributes":
    """
    Construct from key/value tuples.

    Example
    -------
    MetricAttributes.from_pairs(
        ("host", "gpu01"),
        ("device", "cuda"),
    )
    """

    return cls(
        dict(pairs)
    )


@classmethod
def from_keys(
    cls,
    keys,
    value: Any = None,
) -> "MetricAttributes":
    """
    Equivalent to dict.fromkeys().
    """

    return cls(
        dict.fromkeys(
            keys,
            value,
        )
    )


@classmethod
def from_json(
    cls,
    text: str,
) -> "MetricAttributes":
    """
    Construct from JSON.
    """

    return cls(
        json.loads(text)
    )


# -----------------------------------------------------
# Validation
# -----------------------------------------------------

def validate(
    self,
) -> bool:
    """
    Validate all attributes.
    """

    MetricValidator.validate_attributes(
        self._attributes
    )

    return True


@property
def valid(
    self,
) -> bool:
    """
    Whether attributes are valid.
    """

    try:

        self.validate()

        return True

    except Exception:

        return False


# -----------------------------------------------------
# Internal Storage
# -----------------------------------------------------

@property
def storage(
    self,
) -> dict[str, AttributeValue]:
    """
    Internal storage (read-only copy).
    """

    with self._lock:

        return dict(
            self._attributes
        )


@property
def attribute_count(
    self,
) -> int:
    """
    Number of stored attributes.
    """

    return len(
        self._attributes
    )


@property
def empty(
    self,
) -> bool:
    """
    Whether no attributes exist.
    """

    return not self._attributes


# -----------------------------------------------------
# Namespace
# -----------------------------------------------------

@property
def namespace(
    self,
) -> str | None:
    """
    Current namespace.
    """

    return self._namespace


@namespace.setter
def namespace(
    self,
    value: str | None,
) -> None:
    """
    Set namespace.
    """

    with self._lock:

        self._require_mutable()

        self._namespace = value

        self._version += 1


# -----------------------------------------------------
# Version
# -----------------------------------------------------

@property
def version(
    self,
) -> int:
    """
    Internal version number.
    """

    return self._version


def touch(
    self,
) -> None:
    """
    Increment version.
    """

    with self._lock:

        self._version += 1


# -----------------------------------------------------
# Frozen State
# -----------------------------------------------------

@property
def frozen(
    self,
) -> bool:
    """
    Whether this container is frozen.
    """

    return self._frozen


def freeze(
    self,
) -> None:
    """
    Freeze the container.
    """

    with self._lock:

        self._frozen = True


def unfreeze(
    self,
) -> None:
    """
    Unfreeze the container.
    """

    with self._lock:

        self._frozen = False


def _require_mutable(
    self,
) -> None:
    """
    Raise if object is frozen.
    """

    if self._frozen:

        raise MetricFrozenError(
            "MetricAttributes is frozen."
        )
# =====================================================
# Mapping API
# =====================================================

def __getitem__(
    self,
    key: str,
) -> AttributeValue:
    """
    Return attribute value.

    Raises
    ------
    KeyError
        If key does not exist.
    """

    with self._lock:

        return self._attributes[key]


def __setitem__(
    self,
    key: str,
    value: AttributeValue,
) -> None:
    """
    Set attribute.

    Equivalent to:

        attrs[key] = value
    """

    with self._lock:

        self._require_mutable()

        MetricValidator.validate_attribute_key(
            key
        )

        MetricValidator.validate_attribute_value(
            value
        )

        self._attributes[key] = deepcopy(
            value
        )

        self._version += 1


def __delitem__(
    self,
    key: str,
) -> None:
    """
    Delete attribute.

    Raises
    ------
    KeyError
        If key is absent.
    """

    with self._lock:

        self._require_mutable()

        del self._attributes[key]

        self._version += 1


def __contains__(
    self,
    key: object,
) -> bool:
    """
    Membership test.

    Example
    -------
    if "host" in attrs:
        ...
    """

    return key in self._attributes


def __iter__(
    self,
):
    """
    Iterate over keys.

    Snapshot iterator to avoid mutation during iteration.
    """

    with self._lock:

        return iter(
            tuple(
                self._attributes.keys()
            )
        )


def __len__(
    self,
) -> int:
    """
    Number of attributes.
    """

    return len(
        self._attributes
    )


# -----------------------------------------------------
# View API
# -----------------------------------------------------

def keys(
    self,
):
    """
    Dynamic keys view.
    """

    with self._lock:

        return self._attributes.keys()


def values(
    self,
):
    """
    Dynamic values view.
    """

    with self._lock:

        return self._attributes.values()


def items(
    self,
):
    """
    Dynamic items view.
    """

    with self._lock:

        return self._attributes.items()


# -----------------------------------------------------
# Snapshot Views
# -----------------------------------------------------

@property
def key_list(
    self,
) -> list[str]:
    """
    Immutable key snapshot.
    """

    with self._lock:

        return list(
            self._attributes.keys()
        )


@property
def value_list(
    self,
) -> list[AttributeValue]:
    """
    Immutable value snapshot.
    """

    with self._lock:

        return list(
            deepcopy(
                list(
                    self._attributes.values()
                )
            )
        )


@property
def item_list(
    self,
) -> list[
    tuple[str, AttributeValue]
]:
    """
    Immutable item snapshot.
    """

    with self._lock:

        return [
            (
                k,
                deepcopy(v),
            )
            for k, v in self._attributes.items()
        ]
# =====================================================
# CRUD API
# =====================================================

def set(
    self,
    key: str,
    value: AttributeValue,
) -> None:
    """
    Set an attribute.

    Equivalent to:

        attrs[key] = value
    """

    self[key] = value


def get(
    self,
    key: str,
    default: AttributeValue | None = None,
) -> AttributeValue | None:
    """
    Get attribute.

    Returns
    -------
    default
        If key does not exist.
    """

    with self._lock:

        value = self._attributes.get(
            key,
            default,
        )

        return deepcopy(value)


def update(
    self,
    other: Mapping[str, AttributeValue] | None = None,
    **kwargs: AttributeValue,
) -> None:
    """
    Bulk update attributes.
    """

    with self._lock:

        self._require_mutable()

        updates: dict[str, AttributeValue] = {}

        if other:

            MetricValidator.validate_attributes(
                other
            )

            updates.update(other)

        if kwargs:

            MetricValidator.validate_attributes(
                kwargs
            )

            updates.update(kwargs)

        for key, value in updates.items():

            self._attributes[key] = deepcopy(
                value
            )

        if updates:

            self._version += 1


def pop(
    self,
    key: str,
    default: AttributeValue | None = None,
) -> AttributeValue | None:
    """
    Remove and return attribute.
    """

    with self._lock:

        self._require_mutable()

        if key in self._attributes:

            self._version += 1

            return deepcopy(
                self._attributes.pop(key)
            )

        return deepcopy(default)


def remove(
    self,
    key: str,
) -> bool:
    """
    Remove attribute.

    Returns
    -------
    bool
        True if removed.
    """

    with self._lock:

        self._require_mutable()

        if key not in self._attributes:

            return False

        del self._attributes[key]

        self._version += 1

        return True


def clear(
    self,
) -> None:
    """
    Remove all attributes.
    """

    with self._lock:

        self._require_mutable()

        if self._attributes:

            self._attributes.clear()

            self._version += 1


def setdefault(
    self,
    key: str,
    default: AttributeValue = None,
) -> AttributeValue:
    """
    Insert default value if absent.

    Returns
    -------
    Existing or inserted value.
    """

    with self._lock:

        self._require_mutable()

        if key in self._attributes:

            return deepcopy(
                self._attributes[key]
            )

        MetricValidator.validate_attribute_key(
            key
        )

        MetricValidator.validate_attribute_value(
            default
        )

        self._attributes[key] = deepcopy(
            default
        )

        self._version += 1

        return deepcopy(default)


def replace(
    self,
    mapping: Mapping[str, AttributeValue],
) -> None:
    """
    Replace entire attribute collection.
    """

    with self._lock:

        self._require_mutable()

        MetricValidator.validate_attributes(
            mapping
        )

        self._attributes.clear()

        self._attributes.update(
            deepcopy(dict(mapping))
        )

        self._version += 1


def rename(
    self,
    old_key: str,
    new_key: str,
    *,
    overwrite: bool = False,
) -> None:
    """
    Rename an attribute key.
    """

    with self._lock:

        self._require_mutable()

        if old_key not in self._attributes:

            raise KeyError(old_key)

        MetricValidator.validate_attribute_key(
            new_key
        )

        if (
            not overwrite
            and new_key in self._attributes
        ):
            raise KeyError(
                f"{new_key!r} already exists."
            )

        value = self._attributes.pop(
            old_key
        )

        self._attributes[new_key] = value

        self._version += 1


def move(
    self,
    source: str,
    destination: str,
    *,
    overwrite: bool = False,
) -> None:
    """
    Move attribute.

    Semantically identical to rename()
    but improves readability in pipelines.
    """

    self.rename(
        source,
        destination,
        overwrite=overwrite,
    )
# =====================================================
# Freeze / Snapshot API
# =====================================================

@property
def frozen(
    self,
) -> bool:
    """
    Whether the attribute collection is immutable.
    """

    with self._lock:
        return self._frozen


def freeze(
    self,
) -> "MetricAttributes":
    """
    Freeze this attribute collection.

    Returns
    -------
    MetricAttributes
        Self for fluent API.
    """

    with self._lock:

        self._frozen = True

        return self


def unfreeze(
    self,
) -> "MetricAttributes":
    """
    Unfreeze this attribute collection.
    """

    with self._lock:

        self._frozen = False

        return self


def snapshot(
    self,
) -> dict[str, Any]:
    """
    Create a complete runtime snapshot.

    The snapshot can later be restored.
    """

    with self._lock:

        return {

            "namespace": self._namespace,

            "version": self._version,

            "frozen": self._frozen,

            "attributes": deepcopy(
                self._attributes
            ),
        }


def restore(
    self,
    snapshot: Mapping[str, Any],
) -> "MetricAttributes":
    """
    Restore a previously created snapshot.
    """

    with self._lock:

        self._require_mutable()

        attrs = snapshot.get(
            "attributes",
            {},
        )

        MetricValidator.validate_attributes(
            attrs
        )

        self._attributes = deepcopy(
            dict(attrs)
        )

        self._namespace = snapshot.get(
            "namespace",
            self._namespace,
        )

        self._version = int(
            snapshot.get(
                "version",
                self._version,
            )
        )

        self._frozen = bool(
            snapshot.get(
                "frozen",
                False,
            )
        )

        return self


def copy(
    self,
) -> "MetricAttributes":
    """
    Create a shallow logical copy.

    Values are deep-copied to prevent aliasing.
    """

    with self._lock:

        clone = self.__class__(

            attributes=deepcopy(
                self._attributes
            ),

            namespace=self._namespace,

        )

        clone._version = self._version

        clone._frozen = self._frozen

        return clone


def clone(
    self,
) -> "MetricAttributes":
    """
    Alias of copy().

    Exists for API readability.
    """

    return self.copy()


def merge(
    self,
    other: Mapping[str, Any],
    *,
    overwrite: bool = True,
) -> "MetricAttributes":
    """
    Return a merged copy.

    Current object remains unchanged.
    """

    MetricValidator.validate_attributes(
        other
    )

    merged = self.copy()

    with merged._lock:

        for key, value in other.items():

            if overwrite:

                merged._attributes[key] = (
                    deepcopy(value)
                )

            elif key not in merged._attributes:

                merged._attributes[key] = (
                    deepcopy(value)
                )

        merged._version += 1

    return merged


def merge_inplace(
    self,
    other: Mapping[str, Any],
    *,
    overwrite: bool = True,
) -> "MetricAttributes":
    """
    Merge directly into this object.

    Returns
    -------
    MetricAttributes
        Self.
    """

    with self._lock:

        self._require_mutable()

        MetricValidator.validate_attributes(
            other
        )

        changed = False

        for key, value in other.items():

            if overwrite:

                if (
                    key not in self._attributes
                    or self._attributes[key] != value
                ):

                    self._attributes[key] = deepcopy(
                        value
                    )

                    changed = True

            else:

                if key not in self._attributes:

                    self._attributes[key] = deepcopy(
                        value
                    )

                    changed = True

        if changed:

            self._version += 1

        return self
# =====================================================
# Serialization API
# =====================================================

def to_dict(
    self,
) -> dict[str, Any]:
    """
    Serialize to a dictionary.

    Returns
    -------
    dict
        Serializable representation.
    """

    with self._lock:

        return {

            "namespace": self._namespace,

            "version": self._version,

            "frozen": self._frozen,

            "attributes": deepcopy(
                self._attributes
            ),
        }


@classmethod
def from_dict(
    cls,
    data: Mapping[str, Any],
) -> "MetricAttributes":
    """
    Construct a MetricAttributes instance from a dictionary.

    Parameters
    ----------
    data:
        Serialized dictionary.

    Returns
    -------
    MetricAttributes
    """

    attrs = cls(

        attributes=data.get(
            "attributes",
            {},
        ),

        namespace=data.get(
            "namespace",
            DEFAULT_NAMESPACE,
        ),
    )

    attrs._version = int(
        data.get(
            "version",
            1,
        )
    )

    attrs._frozen = bool(
        data.get(
            "frozen",
            False,
        )
    )

    return attrs


def to_json(
    self,
    *,
    indent: int | None = 2,
    sort_keys: bool = True,
    ensure_ascii: bool = False,
) -> str:
    """
    Serialize to JSON.

    Returns
    -------
    str
    """

    return json.dumps(

        self.to_dict(),

        indent=indent,

        sort_keys=sort_keys,

        ensure_ascii=ensure_ascii,

        default=str,
    )


@classmethod
def from_json(
    cls,
    text: str,
) -> "MetricAttributes":
    """
    Deserialize from JSON.
    """

    return cls.from_dict(
        json.loads(text)
    )


def as_tuple(
    self,
) -> tuple[tuple[str, Any], ...]:
    """
    Immutable tuple representation.

    Useful for:

    - hashing
    - cache keys
    - registry lookup
    - deterministic ordering
    """

    with self._lock:

        return tuple(

            sorted(

                (
                    key,
                    deepcopy(value),
                )

                for key, value in self._attributes.items()
            )
        )


# =====================================================
# Pickle Support
# =====================================================

def __getstate__(
    self,
) -> dict[str, Any]:
    """
    Pickle serialization.

    Locks are excluded because they cannot
    be pickled.
    """

    state = self.to_dict()

    return state


def __setstate__(
    self,
    state: Mapping[str, Any],
) -> None:
    """
    Restore pickled object.
    """

    self._lock = RLock()

    self._attributes = deepcopy(
        dict(
            state.get(
                "attributes",
                {},
            )
        )
    )

    self._namespace = state.get(
        "namespace",
        DEFAULT_NAMESPACE,
    )

    self._version = int(
        state.get(
            "version",
            1,
        )
    )

    self._frozen = bool(
        state.get(
            "frozen",
            False,
        )
    )


def __reduce__(
    self,
):
    """
    Stable pickle protocol.

    Allows compatibility across Python versions.
    """

    return (

        self.__class__.from_dict,

        (
            self.to_dict(),
        ),
    )
# =====================================================
# Operator API
# =====================================================

def __copy__(
    self,
) -> "MetricAttributes":
    """
    Shallow copy.

    Returns
    -------
    MetricAttributes
        Independent copy of this object.
    """
    return self.copy()


def __deepcopy__(
    self,
    memo: dict[int, Any],
) -> "MetricAttributes":
    """
    Deep copy support.

    Parameters
    ----------
    memo
        Python deepcopy memo table.

    Returns
    -------
    MetricAttributes
    """
    with self._lock:

        clone = self.__class__.from_dict(
            deepcopy(
                self.to_dict(),
                memo,
            )
        )

        memo[id(self)] = clone

        return clone


def __or__(
    self,
    other: Mapping[str, Any],
) -> "MetricAttributes":
    """
    Merge operator.

    Example
    -------
    attrs3 = attrs1 | attrs2
    attrs4 = attrs | {"gpu":0}
    """

    if isinstance(
        other,
        MetricAttributes,
    ):
        other = other._attributes

    return self.merge(
        other
    )


def __ior__(
    self,
    other: Mapping[str, Any],
) -> "MetricAttributes":
    """
    In-place merge.

    Example
    -------
    attrs |= {"gpu":0}
    """

    if isinstance(
        other,
        MetricAttributes,
    ):
        other = other._attributes

    self.merge_inplace(
        other
    )

    return self


def __eq__(
    self,
    other: object,
) -> bool:
    """
    Equality comparison.

    Equality ignores object identity and compares
    logical contents.
    """

    if self is other:
        return True

    if not isinstance(
        other,
        MetricAttributes,
    ):
        return False

    return (

        self._namespace
        == other._namespace

        and

        self._version
        == other._version

        and

        self._attributes
        == other._attributes

        and

        self._frozen
        == other._frozen
    )


def __hash__(
    self,
) -> int:
    """
    Stable hash.

    Allows MetricAttributes to be used as
    dictionary keys or stored in sets.

    Hash is deterministic regardless of insertion
    order.
    """

    with self._lock:

        items = tuple(

            sorted(

                (
                    k,
                    repr(v),
                )

                for k, v in self._attributes.items()
            )
        )

        return hash(
            (
                self._namespace,
                self._version,
                self._frozen,
                items,
            )
        )
# =====================================================
# Debug Helpers
# =====================================================

def __bool__(
    self,
) -> bool:
    """
    Truth-value testing.

    Returns
    -------
    bool
        True if any attributes exist.
    """
    return bool(self._attributes)


def __str__(
    self,
) -> str:
    """
    Human-readable representation.
    """

    preview = ", ".join(

        f"{k}={v!r}"

        for k, v in list(
            self._attributes.items()
        )[:5]

    )

    if len(self._attributes) > 5:
        preview += ", ..."

    return (
        f"MetricAttributes("
        f"{preview}"
        f")"
    )


def __repr__(
    self,
) -> str:
    """
    Developer representation.
    """

    return (
        f"{self.__class__.__name__}("
        f"namespace={self._namespace!r}, "
        f"version={self._version}, "
        f"count={len(self)}, "
        f"frozen={self._frozen})"
    )


# =====================================================
# Statistics
# =====================================================

@property
def statistics(
    self,
) -> dict[str, Any]:
    """
    Runtime statistics.

    Useful for diagnostics and monitoring.
    """

    with self._lock:

        return {

            "count": len(self),

            "namespace": self._namespace,

            "version": self._version,

            "frozen": self._frozen,

            "empty": len(self) == 0,

            "keys": sorted(
                self._attributes.keys()
            ),

        }


# =====================================================
# Diagnostics
# =====================================================

@property
def diagnostics(
    self,
) -> dict[str, Any]:
    """
    Detailed runtime diagnostics.

    Intended for debugging only.
    """

    with self._lock:

        return {

            "class": self.__class__.__name__,

            "id": hex(id(self)),

            "namespace": self._namespace,

            "version": self._version,

            "frozen": self._frozen,

            "count": len(self),

            "keys": sorted(
                self._attributes.keys()
            ),

            "attributes": deepcopy(
                self._attributes
            ),

            "memory_size": sys.getsizeof(
                self._attributes
            ),

            "lock_type": type(
                self._lock
            ).__name__,
        }


# =====================================================
# Pretty Printing
# =====================================================

def pprint(
    self,
) -> None:
    """
    Pretty-print attributes.

    Example
    -------
    >>> attrs.pprint()
    """

    pprint_module.pprint(
        self.to_dict(),

        sort_dicts=True,

        width=100,
    )


# =====================================================
# Dump
# =====================================================

def dump(
    self,
    *,
    indent: int = 2,
    sort_keys: bool = True,
) -> str:
    """
    Dump full object as formatted JSON.

    Useful for logging,
    debugging,
    telemetry,
    snapshots.
    """

    return json.dumps(

        self.to_dict(),

        indent=indent,

        sort_keys=sort_keys,

        ensure_ascii=False,

        default=str,
    )
# =====================================================
# Thread Safety
# =====================================================

from contextlib import contextmanager


# =====================================================
# Lock Helpers
# =====================================================

@property
def version(
    self,
) -> int:
    """
    Monotonically increasing version.

    Incremented whenever the internal state
    changes successfully.
    """
    return self._version_counter


@property
def locked(
    self,
) -> bool:
    """
    Best-effort indicator that the object
    is currently frozen.

    This does not indicate ownership of the
    threading lock.
    """
    return self._frozen


def _bump_version(
    self,
) -> int:
    """
    Increment internal version.

    Returns
    -------
    int
        New version number.
    """
    self._version_counter += 1
    return self._version_counter


def _ensure_mutable(
    self,
) -> None:
    """
    Internal mutation guard.
    """
    if self._frozen:
        raise MetricFrozenError(
            "MetricAttributes is frozen."
        )


# =====================================================
# Context Manager
# =====================================================

@contextmanager
def locked_context(
    self,
):
    """
    Execute multiple operations atomically.

    Example
    -------
    with attrs.locked_context():
        attrs.set(...)
        attrs.remove(...)
    """

    with self._lock:
        yield self


# =====================================================
# Atomic Update
# =====================================================

def atomic_update(
    self,
    updater,
):
    """
    Execute updater(self) atomically.

    Parameters
    ----------
    updater
        Callable accepting this instance.

    Returns
    -------
    Any
    """

    with self._lock:

        self._ensure_mutable()

        result = updater(self)

        self._bump_version()

        return result


# =====================================================
# Compare-And-Swap
# =====================================================

def compare_and_swap(
    self,
    expected_version: int,
    updates: Mapping[str, Any],
) -> bool:
    """
    Atomic compare-and-swap.

    Parameters
    ----------
    expected_version
        Version expected by caller.

    updates
        Attributes to apply.

    Returns
    -------
    bool
        True if update succeeded.
    """

    with self._lock:

        self._ensure_mutable()

        if self._version_counter != expected_version:
            return False

        self.update(
            updates
        )

        self._bump_version()

        return True


# =====================================================
# Internal Mutation Helpers
# =====================================================

def _mutate(
    self,
    func,
    *args,
    **kwargs,
):
    """
    Execute internal mutation safely.

    Used by all modifying APIs.
    """

    with self._lock:

        self._ensure_mutable()

        result = func(
            *args,
            **kwargs,
        )

        self._bump_version()

        return result


def _replace_storage(
    self,
    new_data: Mapping[str, Any],
) -> None:
    """
    Replace entire storage atomically.
    """

    with self._lock:

        self._ensure_mutable()

        self._attributes.clear()

        self._attributes.update(
            dict(new_data)
        )

        self._bump_version()


# =====================================================
# Version Helpers
# =====================================================

def reset_version(
    self,
) -> None:
    """
    Reset version counter.

    Intended primarily for testing.
    """

    with self._lock:

        self._version_counter = 0


def touch(
    self,
) -> int:
    """
    Force a version increment without
    modifying attributes.

    Returns
    -------
    int
        New version.
    """

    with self._lock:

        return self._bump_version()
# =====================================================
# Production Utilities
# =====================================================

from types import MappingProxyType
from collections.abc import Mapping

# =====================================================
# Immutable View
# =====================================================

@property
def immutable_view(
    self,
) -> Mapping[str, Any]:
    """
    Read-only mapping view.
    """

    return MappingProxyType(
        self._attributes
    )


# =====================================================
# Diff
# =====================================================

def diff(
    self,
    other: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    """
    Compare two attribute sets.

    Returns
    -------
    {
        "added":{},
        "removed":{},
        "changed":{}
    }
    """

    if isinstance(
        other,
        MetricAttributes,
    ):
        other = other._attributes

    added = {}
    removed = {}
    changed = {}

    for k, v in other.items():

        if k not in self:

            added[k] = v

        elif self[k] != v:

            changed[k] = (
                self[k],
                v,
            )

    for k, v in self.items():

        if k not in other:

            removed[k] = v

    return {

        "added": added,

        "removed": removed,

        "changed": changed,

    }


# =====================================================
# Filtering
# =====================================================

def filter(
    self,
    predicate,
) -> "MetricAttributes":
    """
    Keep attributes matching predicate.
    """

    return self.__class__.from_dict(

        {

            k: v

            for k, v in self.items()

            if predicate(
                k,
                v,
            )

        }

    )


def exclude(
    self,
    *keys: str,
) -> "MetricAttributes":
    """
    Remove keys.
    """

    excluded = set(keys)

    return self.filter(

        lambda k, _: k not in excluded

    )


def select(
    self,
    *keys: str,
) -> "MetricAttributes":
    """
    Keep only specified keys.
    """

    wanted = set(keys)

    return self.filter(

        lambda k, _: k in wanted

    )


# =====================================================
# Namespace Helpers
# =====================================================

def with_namespace(
    self,
    namespace: str,
) -> "MetricAttributes":
    """
    Clone using another namespace.
    """

    clone = self.copy()

    clone._namespace = namespace

    return clone


# =====================================================
# Prefix Helpers
# =====================================================

def add_prefix(
    self,
    prefix: str,
) -> "MetricAttributes":
    """
    Prefix all keys.
    """

    return self.__class__.from_dict(

        {

            f"{prefix}{k}": v

            for k, v in self.items()

        }

    )


def strip_prefix(
    self,
    prefix: str,
) -> "MetricAttributes":
    """
    Remove prefix if present.
    """

    result = {}

    for k, v in self.items():

        if k.startswith(prefix):

            k = k[len(prefix):]

        result[k] = v

    return self.__class__.from_dict(
        result
    )


# =====================================================
# Flatten
# =====================================================

def flatten(
    self,
    separator: str = ".",
) -> dict[str, Any]:

    result = {}

    def visit(
        prefix,
        value,
    ):

        if isinstance(
            value,
            Mapping,
        ):

            for k, v in value.items():

                visit(

                    f"{prefix}{separator}{k}"

                    if prefix

                    else k,

                    v,

                )

        else:

            result[prefix] = value

    visit(
        "",
        self.to_dict(),
    )

    return result


# =====================================================
# Unflatten
# =====================================================

@classmethod
def unflatten(
    cls,
    data: Mapping[str, Any],
    separator: str = ".",
):

    root = {}

    for key, value in data.items():

        node = root

        parts = key.split(
            separator
        )

        for part in parts[:-1]:

            node = node.setdefault(
                part,
                {},
            )

        node[
            parts[-1]
        ] = value

    return cls.from_dict(
        root
    )


# =====================================================
# Dot-path Access
# =====================================================

def path(
    self,
    dotted: str,
    default=None,
):
    """
    Example
    -------
    runtime.device.id
    """

    node = self._attributes

    for part in dotted.split("."):

        if not isinstance(
            node,
            Mapping,
        ):

            return default

        if part not in node:

            return default

        node = node[part]

    return node


# =====================================================
# Type Conversion
# =====================================================

def get_int(
    self,
    key,
    default=0,
):

    try:

        return int(
            self.get(
                key,
                default,
            )
        )

    except Exception:

        return default


def get_float(
    self,
    key,
    default=0.0,
):

    try:

        return float(
            self.get(
                key,
                default,
            )
        )

    except Exception:

        return default


def get_bool(
    self,
    key,
    default=False,
):

    value = self.get(
        key,
        default,
    )

    if isinstance(
        value,
        bool,
    ):
        return value

    if isinstance(
        value,
        str,
    ):

        return value.lower() in (

            "1",

            "true",

            "yes",

            "on",

        )

    return bool(
        value
    )


def get_str(
    self,
    key,
    default="",
):

    return str(

        self.get(
            key,
            default,
        )

    )


# =====================================================
# Validation
# =====================================================

def validate(
    self,
) -> bool:
    """
    Re-run validator.
    """

    MetricValidator.validate_attributes(

        self._attributes

    )

    return True


# =====================================================
# Final Polish
# =====================================================

@property
def empty(
    self,
) -> bool:

    return len(self) == 0


@property
def size(
    self,
) -> int:

    return len(
        self._attributes
    )


@property
def sorted_items(
    self,
):

    return sorted(

        self._attributes.items()

    )


def compact(
    self,
):

    """
    Remove values that are None.
    """

    return self.filter(

        lambda _, v: v is not None

    )                                                       