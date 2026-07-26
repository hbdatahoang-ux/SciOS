"""
SciOS-NG Metrics Core - Metric State
===================================

Runtime state for Metric objects.

This module stores mutable runtime information only.

Design goals
------------
- Runtime-only state
- Thread-safe
- Snapshot-friendly
- Extensible
- Fully typed
"""

from __future__ import annotations

import threading
import time
import uuid
from abc import ABC
from typing import Any

__all__ = [
    "MetricState",
]


class MetricState(ABC):
    """
    Runtime state of a Metric.

    Notes
    -----
    MetricState intentionally stores only mutable runtime data.

    Static information such as name, description, unit,
    namespace, etc. belongs to MetricDescriptor.

    Labels and attributes are managed by their own classes.
    """

    # ==========================================================
    # Constructor
    # ==========================================================

    def __init__(
        self,
        value: Any = None,
    ) -> None:

        # ------------------------------------------------------
        # Identity
        # ------------------------------------------------------

        self._uuid: uuid.UUID = uuid.uuid4()

        # ------------------------------------------------------
        # Runtime Value
        # ------------------------------------------------------

        self._value: Any = value

        self._previous_value: Any = None

        self._update_count: int = 0

        self._timestamp: float = time.time()

        # ------------------------------------------------------
        # Lifecycle Flags
        # ------------------------------------------------------

        self._enabled: bool = True

        self._frozen: bool = False

        self._closed: bool = False

        # ------------------------------------------------------
        # Runtime Metadata
        # ------------------------------------------------------

        self._metadata: dict[str, Any] = {}

        self._labels: dict[str, str] = {}

        self._attributes: dict[str, Any] = {}

        # ------------------------------------------------------
        # Synchronization
        # ------------------------------------------------------

        self._lock = threading.RLock()
# ==========================================================
# Part 2. Runtime State
# ==========================================================

from typing import Any


# ----------------------------------------------------------
# Value
# ----------------------------------------------------------

@property
def value(self) -> Any:
    """
    Current metric value.
    """
    return self._value


# ----------------------------------------------------------
# Previous Value
# ----------------------------------------------------------

@property
def previous_value(self) -> Any:
    """
    Previous metric value.
    """
    return self._previous_value


# ----------------------------------------------------------
# Update Count
# ----------------------------------------------------------

@property
def update_count(self) -> int:
    """
    Number of successful updates.
    """
    return self._update_count


# ----------------------------------------------------------
# Enabled
# ----------------------------------------------------------

@property
def enabled(self) -> bool:
    """
    Whether the metric is enabled.
    """
    return self._enabled


# ----------------------------------------------------------
# Frozen
# ----------------------------------------------------------

@property
def frozen(self) -> bool:
    """
    Whether the metric is frozen.
    """
    return self._frozen


# ----------------------------------------------------------
# Closed
# ----------------------------------------------------------

@property
def closed(self) -> bool:
    """
    Whether the metric has been closed.
    """
    return self._closed


# ----------------------------------------------------------
# Timestamp
# ----------------------------------------------------------

@property
def timestamp(self) -> float:
    """
    Unix timestamp of the last update.
    """
    return self._timestamp
# ==========================================================
# Part 3. Value API
# ==========================================================


import time
from typing import Any

from .exceptions import (
    MetricClosedError,
    MetricDisabledError,
    MetricFrozenError,
)
from .validation import MetricValidator


# ----------------------------------------------------------
# Get
# ----------------------------------------------------------

def get(self) -> Any:
    """
    Return the current metric value.
    """
    return self._value


# ----------------------------------------------------------
# Set
# ----------------------------------------------------------

def set(self, value: Any) -> Any:
    """
    Set the current metric value.

    Returns
    -------
    Any
        The validated value.
    """

    with self._lock:

        if self._closed:
            raise MetricClosedError("Metric is closed.")

        if not self._enabled:
            raise MetricDisabledError("Metric is disabled.")

        if self._frozen:
            raise MetricFrozenError("Metric is frozen.")

        value = MetricValidator.validate_value(value)

        self._before_update(value)

        self._previous_value = self._value
        self._value = value
        self._update_count += 1
        self._timestamp = time.time()

        self._after_update(value)

        return self._value


# ----------------------------------------------------------
# Update
# ----------------------------------------------------------

def update(self, value: Any) -> Any:
    """
    Alias of set().
    """
    return self.set(value)


# ----------------------------------------------------------
# Reset
# ----------------------------------------------------------

def reset(self) -> None:
    """
    Reset the metric value.
    """

    with self._lock:

        self._previous_value = self._value
        self._value = None
        self._update_count = 0
        self._timestamp = time.time()


# ----------------------------------------------------------
# Clear
# ----------------------------------------------------------

def clear(self) -> None:
    """
    Alias of reset().
    """
    self.reset()


# ----------------------------------------------------------
# Delta
# ----------------------------------------------------------

def delta(self) -> Any:
    """
    Compute the difference between the current
    and previous value.

    Returns
    -------
    Any
        Numeric difference or None.
    """

    if self._previous_value is None:
        return None

    try:
        return self._value - self._previous_value
    except Exception:
        return None


# ----------------------------------------------------------
# Changed
# ----------------------------------------------------------

def changed(self) -> bool:
    """
    Return True if the current value differs from
    the previous value.
    """

    return self._value != self._previous_value  
# ==========================================================
# Part 4. Snapshot API
# ==========================================================


from .metric_snapshot import MetricSnapshot


# ----------------------------------------------------------
# Snapshot
# ----------------------------------------------------------

def snapshot(self) -> MetricSnapshot:
    """
    Create an immutable snapshot of the current runtime state.

    Returns
    -------
    MetricSnapshot
    """

    with self._lock:

        self._before_snapshot()

        snap = MetricSnapshot(

            uuid=self._uuid,

            value=self._value,

            previous_value=self._previous_value,

            update_count=self._update_count,

            enabled=self._enabled,

            frozen=self._frozen,

            closed=self._closed,

            timestamp=self._timestamp,

        )

        self._after_snapshot(snap)

        return snap


# ----------------------------------------------------------
# Restore
# ----------------------------------------------------------

def restore(
    self,
    snapshot: MetricSnapshot,
) -> None:
    """
    Restore runtime state from a snapshot.
    """

    with self._lock:

        self._value = snapshot.value

        self._previous_value = snapshot.previous_value

        self._update_count = snapshot.update_count

        self._enabled = snapshot.enabled

        self._frozen = snapshot.frozen

        self._closed = snapshot.closed

        self._timestamp = snapshot.timestamp


# ----------------------------------------------------------
# Clone
# ----------------------------------------------------------

def clone(self) -> "MetricState":
    """
    Deep clone this MetricState.
    """

    state = self.__class__()

    state.restore(self.snapshot())

    return state


# ----------------------------------------------------------
# Copy
# ----------------------------------------------------------

def copy(self) -> "MetricState":
    """
    Alias of clone().
    """

    return self.clone() 
# ==========================================================
# Part 5. Lifecycle
# ==========================================================


import time

from .exceptions import (
    MetricClosedError,
)


# ----------------------------------------------------------
# Freeze
# ----------------------------------------------------------

def freeze(self) -> None:
    """
    Freeze this metric.

    A frozen metric cannot be updated.
    """

    with self._lock:

        if self._closed:
            raise MetricClosedError("Metric is closed.")

        self._frozen = True
        self._timestamp = time.time()


# ----------------------------------------------------------
# Unfreeze
# ----------------------------------------------------------

def unfreeze(self) -> None:
    """
    Unfreeze this metric.
    """

    with self._lock:

        if self._closed:
            raise MetricClosedError("Metric is closed.")

        self._frozen = False
        self._timestamp = time.time()


# ----------------------------------------------------------
# Enable
# ----------------------------------------------------------

def enable(self) -> None:
    """
    Enable this metric.
    """

    with self._lock:

        if self._closed:
            raise MetricClosedError("Metric is closed.")

        self._enabled = True
        self._timestamp = time.time()


# ----------------------------------------------------------
# Disable
# ----------------------------------------------------------

def disable(self) -> None:
    """
    Disable this metric.
    """

    with self._lock:

        if self._closed:
            raise MetricClosedError("Metric is closed.")

        self._enabled = False
        self._timestamp = time.time()


# ----------------------------------------------------------
# Close
# ----------------------------------------------------------

def close(self) -> None:
    """
    Permanently close the runtime state.
    """

    with self._lock:

        self._closed = True
        self._timestamp = time.time()


# ----------------------------------------------------------
# Reopen
# ----------------------------------------------------------

def reopen(self) -> None:
    """
    Reopen a previously closed metric.
    """

    with self._lock:

        self._closed = False
        self._timestamp = time.time()     
# ==========================================================
# Part 6. Hooks
# ==========================================================


from typing import Any

from .metric_snapshot import MetricSnapshot


# ----------------------------------------------------------
# Before Update
# ----------------------------------------------------------

def _before_update(
    self,
    value: Any,
) -> None:
    """
    Hook called immediately before updating the metric value.

    Parameters
    ----------
    value:
        The validated value that will be assigned.

    Notes
    -----
    Override in subclasses if custom behavior is required.
    """
    return None


# ----------------------------------------------------------
# After Update
# ----------------------------------------------------------

def _after_update(
    self,
    value: Any,
) -> None:
    """
    Hook called immediately after a successful update.

    Parameters
    ----------
    value:
        The new metric value.

    Notes
    -----
    Override in subclasses if custom behavior is required.
    """
    return None


# ----------------------------------------------------------
# Before Snapshot
# ----------------------------------------------------------

def _before_snapshot(self) -> None:
    """
    Hook executed before creating a snapshot.

    Override in subclasses if needed.
    """
    return None


# ----------------------------------------------------------
# After Snapshot
# ----------------------------------------------------------

def _after_snapshot(
    self,
    snapshot: MetricSnapshot,
) -> None:
    """
    Hook executed after a snapshot has been created.

    Parameters
    ----------
    snapshot:
        Newly created MetricSnapshot.

    Override in subclasses if needed.
    """
    return None     
# ==========================================================
# Part 7. Context Manager
# ==========================================================


from types import TracebackType


# ----------------------------------------------------------
# Enter
# ----------------------------------------------------------

def __enter__(self) -> "MetricState":
    """
    Enter the runtime context.

    Returns
    -------
    MetricState
        The current MetricState instance.
    """
    return self


# ----------------------------------------------------------
# Exit
# ----------------------------------------------------------

def __exit__(
    self,
    exc_type: type[BaseException] | None,
    exc_value: BaseException | None,
    traceback: TracebackType | None,
) -> bool:
    """
    Exit the runtime context.

    Parameters
    ----------
    exc_type:
        Exception type.

    exc_value:
        Exception instance.

    traceback:
        Traceback object.

    Returns
    -------
    bool
        False to propagate any exception.
    """

    # Do not suppress exceptions.
    return False 
# ==========================================================
# Part 8. Rich API
# ==========================================================


from collections.abc import Iterator
from typing import Any


# ----------------------------------------------------------
# repr()
# ----------------------------------------------------------

def __repr__(self) -> str:
    """
    Developer-friendly representation.
    """

    return (
        f"{self.__class__.__name__}("
        f"uuid={self._uuid!s}, "
        f"value={self._value!r}, "
        f"updates={self._update_count}, "
        f"enabled={self._enabled}, "
        f"frozen={self._frozen}, "
        f"closed={self._closed})"
    )


# ----------------------------------------------------------
# str()
# ----------------------------------------------------------

def __str__(self) -> str:
    """
    Human-readable representation.
    """

    return str(self._value)


# ----------------------------------------------------------
# Equality
# ----------------------------------------------------------

def __eq__(self, other: object) -> bool:

    if not isinstance(other, MetricState):
        return NotImplemented

    return self._uuid == other._uuid


# ----------------------------------------------------------
# Hash
# ----------------------------------------------------------

def __hash__(self) -> int:

    return hash(self._uuid)


# ----------------------------------------------------------
# Bool
# ----------------------------------------------------------

def __bool__(self) -> bool:
    """
    True if the metric is active.

    A metric is considered active when it is:

        enabled
        not frozen
        not closed
    """

    return (
        self._enabled
        and not self._frozen
        and not self._closed
    )


# ----------------------------------------------------------
# Iterator
# ----------------------------------------------------------

def __iter__(self) -> Iterator[Any]:
    """
    Iterate over the current value.

    - Iterable value -> iterate elements
    - Scalar value -> iterate single element
    - None -> empty iterator
    """

    if self._value is None:
        return iter(())

    try:
        return iter(self._value)

    except TypeError:
        return iter((self._value,))


# ----------------------------------------------------------
# Length
# ----------------------------------------------------------

def __len__(self) -> int:
    """
    Return logical length.

    Rules
    -----
    Iterable value -> len(value)

    Scalar value -> 1

    None -> 0
    """

    if self._value is None:
        return 0

    try:
        return len(self._value)

    except TypeError:
        return 1  
# ==========================================================
# Part 9. Debug Helpers
# ==========================================================


import time
from typing import Any


# ----------------------------------------------------------
# State
# ----------------------------------------------------------

@property
def state(self) -> dict[str, Any]:
    """
    Return the complete runtime state.

    Useful for debugging and monitoring.
    """

    return {
        "uuid": str(self._uuid),
        "value": self._value,
        "previous_value": self._previous_value,
        "update_count": self._update_count,
        "enabled": self._enabled,
        "frozen": self._frozen,
        "closed": self._closed,
        "timestamp": self._timestamp,
    }


# ----------------------------------------------------------
# Age
# ----------------------------------------------------------

@property
def age(self) -> float:
    """
    Seconds since the last update.
    """

    return max(0.0, time.time() - self._timestamp)


# ----------------------------------------------------------
# Is Empty
# ----------------------------------------------------------

@property
def is_empty(self) -> bool:
    """
    True if the metric currently has no value.
    """

    return self._value is None


# ----------------------------------------------------------
# Statistics
# ----------------------------------------------------------

@property
def statistics(self) -> dict[str, Any]:
    """
    Runtime statistics.
    """

    return {
        "updates": self._update_count,
        "age": self.age,
        "has_value": not self.is_empty,
        "active": bool(self),
    }


# ----------------------------------------------------------
# Health
# ----------------------------------------------------------

@property
def health(self) -> str:
    """
    Human-readable runtime health.

    Returns
    -------
    str
        "closed"
        "disabled"
        "frozen"
        "empty"
        "healthy"
    """

    if self._closed:
        return "closed"

    if not self._enabled:
        return "disabled"

    if self._frozen:
        return "frozen"

    if self.is_empty:
        return "empty"

    return "healthy"                            