"""
SciOS-NG Metrics Core - Metric
==============================

High-level Metric abstraction.

A Metric composes:

    - MetricDescriptor
    - MetricLabels
    - MetricAttributes
    - MetricState
    - MetricHooks

Design goals
------------
- Composition over inheritance
- Thread-safe
- Extensible
- Lightweight
"""

from __future__ import annotations

from typing import Any

from .attributes import MetricAttributes
from .descriptor import MetricDescriptor
from .hooks import MetricHooks
from .labels import MetricLabels
from .metadata import MetricMetadata
from .metric_state import MetricState

__all__ = [
    "Metric",
]


class Metric:
    """
    High-level Metric object.

    Metric itself stores almost no state.

    Runtime information belongs to MetricState.
    """

    # ==========================================================
    # Constructor
    # ==========================================================

    def __init__(
        self,
        *,
        metadata: MetricMetadata,
        value: Any = None,
        metric_type: str = "gauge",
        value_type: type = float,
    ) -> None:

        # ------------------------------------------------------
        # Descriptor
        # ------------------------------------------------------

        self._descriptor = MetricDescriptor(
            metadata=metadata,
            metric_type=metric_type,
            value_type=value_type,
        )

        # ------------------------------------------------------
        # Labels
        # ------------------------------------------------------

        self._labels = MetricLabels()

        # ------------------------------------------------------
        # Attributes
        # ------------------------------------------------------

        self._attributes = MetricAttributes()

        # ------------------------------------------------------
        # Runtime State
        # ------------------------------------------------------

        self._state = MetricState(
            value=value,
        )

        # ------------------------------------------------------
        # Hooks
        # ------------------------------------------------------

        self._hooks = MetricHooks()

    # ==========================================================
    # Composition
    # ==========================================================

    @property
    def descriptor(self) -> MetricDescriptor:
        return self._descriptor

    @property
    def state(self) -> MetricState:
        return self._state

    @property
    def labels(self) -> MetricLabels:
        return self._labels

    @property
    def attributes(self) -> MetricAttributes:
        return self._attributes

    @property
    def hooks(self) -> MetricHooks:
        return self._hooks

    # ==========================================================
    # Runtime Identity
    # ==========================================================

    @property
    def uuid(self):
        """
        Runtime UUID.

        Delegated to MetricState.
        """
        return self._state.uuid
# ==========================================================
# Part 2. Descriptor API
# ==========================================================


from typing import Any

from .descriptor import MetricDescriptor


# ----------------------------------------------------------
# Descriptor
# ----------------------------------------------------------

@property
def descriptor(self) -> MetricDescriptor:
    """
    Return the immutable MetricDescriptor.
    """
    return self._descriptor


# ----------------------------------------------------------
# Metadata
# ----------------------------------------------------------

@property
def metadata(self):
    """
    Shortcut for descriptor.metadata.
    """
    return self._descriptor.metadata


# ----------------------------------------------------------
# Name
# ----------------------------------------------------------

@property
def name(self) -> str:
    """
    Metric name.
    """
    return self._descriptor.name


# ----------------------------------------------------------
# Description
# ----------------------------------------------------------

@property
def description(self) -> str:
    """
    Metric description.
    """
    return self._descriptor.description


# ----------------------------------------------------------
# Unit
# ----------------------------------------------------------

@property
def unit(self) -> str:
    """
    Metric unit.
    """
    return self._descriptor.unit


# ----------------------------------------------------------
# Namespace
# ----------------------------------------------------------

@property
def namespace(self) -> str:
    """
    Metric namespace.
    """
    return self._descriptor.namespace


# ----------------------------------------------------------
# Category
# ----------------------------------------------------------

@property
def category(self) -> str:
    """
    Metric category.
    """
    return self._descriptor.category


# ----------------------------------------------------------
# Owner
# ----------------------------------------------------------

@property
def owner(self) -> str:
    """
    Metric owner.
    """
    return self._descriptor.owner


# ----------------------------------------------------------
# Version
# ----------------------------------------------------------

@property
def version(self) -> str:
    """
    Metric version.
    """
    return self._descriptor.version


# ----------------------------------------------------------
# Tags
# ----------------------------------------------------------

@property
def tags(self) -> tuple[str, ...]:
    """
    Metric tags.
    """
    return self._descriptor.tags


# ----------------------------------------------------------
# Metric Type
# ----------------------------------------------------------

@property
def metric_type(self) -> str:
    """
    Metric instrument type.
    """
    return self._descriptor.metric_type


# ----------------------------------------------------------
# Value Type
# ----------------------------------------------------------

@property
def value_type(self) -> type:
    """
    Runtime value type.
    """
    return self._descriptor.value_type


# ----------------------------------------------------------
# Enabled
# ----------------------------------------------------------

@property
def descriptor_enabled(self) -> bool:
    """
    Whether the descriptor is enabled.

    Note
    ----
    This is different from MetricState.enabled.
    """
    return self._descriptor.enabled


# ----------------------------------------------------------
# Extras
# ----------------------------------------------------------

@property
def extras(self) -> dict[str, Any]:
    """
    Additional descriptor metadata.
    """
    return dict(self._descriptor.extras)    
# ==========================================================
# Part 3. Labels API
# ==========================================================


from typing import Iterator

from .labels import MetricLabels


# ----------------------------------------------------------
# Labels
# ----------------------------------------------------------

@property
def labels(self) -> MetricLabels:
    """
    Return the MetricLabels object.
    """
    return self._labels


# ----------------------------------------------------------
# Get Label
# ----------------------------------------------------------

def get_label(
    self,
    key: str,
    default: str | None = None,
) -> str | None:
    """
    Return a label value.
    """

    return self._labels.get(key, default)


# ----------------------------------------------------------
# Set Label
# ----------------------------------------------------------

def set_label(
    self,
    key: str,
    value: str,
) -> None:
    """
    Set a label.
    """

    self._labels.set(key, value)


# ----------------------------------------------------------
# Remove Label
# ----------------------------------------------------------

def remove_label(
    self,
    key: str,
) -> None:
    """
    Remove a label.
    """

    self._labels.remove(key)


# ----------------------------------------------------------
# Has Label
# ----------------------------------------------------------

def has_label(
    self,
    key: str,
) -> bool:
    """
    Return True if the label exists.
    """

    return key in self._labels


# ----------------------------------------------------------
# Update Labels
# ----------------------------------------------------------

def update_labels(
    self,
    labels: dict[str, str],
) -> None:
    """
    Bulk update labels.
    """

    self._labels.update(labels)


# ----------------------------------------------------------
# Clear Labels
# ----------------------------------------------------------

def clear_labels(self) -> None:
    """
    Remove all labels.
    """

    self._labels.clear()


# ----------------------------------------------------------
# Label Keys
# ----------------------------------------------------------

@property
def label_keys(self) -> tuple[str, ...]:
    """
    Return all label keys.
    """

    return tuple(self._labels.keys())


# ----------------------------------------------------------
# Label Values
# ----------------------------------------------------------

@property
def label_values(self) -> tuple[str, ...]:
    """
    Return all label values.
    """

    return tuple(self._labels.values())


# ----------------------------------------------------------
# Label Items
# ----------------------------------------------------------

@property
def label_items(self) -> tuple[tuple[str, str], ...]:
    """
    Return all label items.
    """

    return tuple(self._labels.items())


# ----------------------------------------------------------
# Label Count
# ----------------------------------------------------------

@property
def label_count(self) -> int:
    """
    Number of labels.
    """

    return len(self._labels)


# ----------------------------------------------------------
# Iterate Labels
# ----------------------------------------------------------

def iter_labels(self) -> Iterator[tuple[str, str]]:
    """
    Iterate over labels.
    """

    return iter(self._labels.items())  
# ==========================================================
# Part 4. Attributes API
# ==========================================================


from collections.abc import Iterator
from typing import Any

from .attributes import MetricAttributes


# ----------------------------------------------------------
# Attributes
# ----------------------------------------------------------

@property
def attributes(self) -> MetricAttributes:
    """
    Return the MetricAttributes object.
    """
    return self._attributes


# ----------------------------------------------------------
# Get Attribute
# ----------------------------------------------------------

def get_attribute(
    self,
    key: str,
    default: Any = None,
) -> Any:
    """
    Return an attribute value.
    """
    return self._attributes.get(key, default)


# ----------------------------------------------------------
# Set Attribute
# ----------------------------------------------------------

def set_attribute(
    self,
    key: str,
    value: Any,
) -> "Metric":
    """
    Set an attribute.
    """
    self._attributes.set(key, value)
    return self


# ----------------------------------------------------------
# Remove Attribute
# ----------------------------------------------------------

def remove_attribute(
    self,
    key: str,
) -> "Metric":
    """
    Remove an attribute.
    """
    self._attributes.remove(key)
    return self


# ----------------------------------------------------------
# Has Attribute
# ----------------------------------------------------------

def has_attribute(
    self,
    key: str,
) -> bool:
    """
    Return True if the attribute exists.
    """
    return key in self._attributes


# ----------------------------------------------------------
# Update Attributes
# ----------------------------------------------------------

def update_attributes(
    self,
    attributes: dict[str, Any],
) -> "Metric":
    """
    Bulk update attributes.
    """
    self._attributes.update(attributes)
    return self


# ----------------------------------------------------------
# Clear Attributes
# ----------------------------------------------------------

def clear_attributes(self) -> "Metric":
    """
    Remove all attributes.
    """
    self._attributes.clear()
    return self


# ----------------------------------------------------------
# Attribute Keys
# ----------------------------------------------------------

@property
def attribute_keys(self) -> tuple[str, ...]:
    """
    Return all attribute keys.
    """
    return tuple(self._attributes.keys())


# ----------------------------------------------------------
# Attribute Values
# ----------------------------------------------------------

@property
def attribute_values(self) -> tuple[Any, ...]:
    """
    Return all attribute values.
    """
    return tuple(self._attributes.values())


# ----------------------------------------------------------
# Attribute Items
# ----------------------------------------------------------

@property
def attribute_items(self) -> tuple[tuple[str, Any], ...]:
    """
    Return all attribute items.
    """
    return tuple(self._attributes.items())


# ----------------------------------------------------------
# Attribute Count
# ----------------------------------------------------------

@property
def attribute_count(self) -> int:
    """
    Number of attributes.
    """
    return len(self._attributes)


# ----------------------------------------------------------
# Iterate Attributes
# ----------------------------------------------------------

def iter_attributes(self) -> Iterator[tuple[str, Any]]:
    """
    Iterate over all attributes.
    """
    return iter(self._attributes.items())  
# ==========================================================
# Part 5. State API
# ==========================================================


from typing import Any

from .metric_state import MetricState


# ----------------------------------------------------------
# State
# ----------------------------------------------------------

@property
def state(self) -> MetricState:
    """
    Runtime MetricState.
    """
    return self._state


# ----------------------------------------------------------
# Value
# ----------------------------------------------------------

@property
def value(self) -> Any:
    """
    Current metric value.
    """
    return self._state.value


# ----------------------------------------------------------
# Previous Value
# ----------------------------------------------------------

@property
def previous_value(self) -> Any:
    """
    Previous metric value.
    """
    return self._state.previous_value


# ----------------------------------------------------------
# Timestamp
# ----------------------------------------------------------

@property
def timestamp(self) -> float:
    """
    Last update timestamp.
    """
    return self._state.timestamp


# ----------------------------------------------------------
# Update Count
# ----------------------------------------------------------

@property
def update_count(self) -> int:
    """
    Number of successful updates.
    """
    return self._state.update_count


# ----------------------------------------------------------
# Lifecycle
# ----------------------------------------------------------

@property
def enabled(self) -> bool:
    return self._state.enabled


@property
def frozen(self) -> bool:
    return self._state.frozen


@property
def closed(self) -> bool:
    return self._state.closed


# ----------------------------------------------------------
# Get
# ----------------------------------------------------------

def get(self) -> Any:
    """
    Return current value.
    """
    return self._state.get()


# ----------------------------------------------------------
# Set
# ----------------------------------------------------------

def set(
    self,
    value: Any,
) -> "Metric":
    """
    Set metric value.
    """

    self._state.set(value)

    return self


# ----------------------------------------------------------
# Update
# ----------------------------------------------------------

def update(
    self,
    value: Any,
) -> "Metric":
    """
    Update metric value.
    """

    self._state.update(value)

    return self


# ----------------------------------------------------------
# Reset
# ----------------------------------------------------------

def reset(self) -> "Metric":

    self._state.reset()

    return self


# ----------------------------------------------------------
# Clear
# ----------------------------------------------------------

def clear(self) -> "Metric":

    self._state.clear()

    return self


# ----------------------------------------------------------
# Delta
# ----------------------------------------------------------

def delta(self):

    return self._state.delta()


# ----------------------------------------------------------
# Changed
# ----------------------------------------------------------

def changed(self) -> bool:

    return self._state.changed()    
# ==========================================================
# Part 6. Snapshot API
# ==========================================================


from .metric_snapshot import MetricSnapshot


# ----------------------------------------------------------
# Snapshot
# ----------------------------------------------------------

def snapshot(self) -> MetricSnapshot:
    """
    Create a snapshot of the current runtime state.

    Returns
    -------
    MetricSnapshot
        Immutable runtime snapshot.
    """
    return self._state.snapshot()


# ----------------------------------------------------------
# Restore
# ----------------------------------------------------------

def restore(
    self,
    snapshot: MetricSnapshot,
) -> "Metric":
    """
    Restore the runtime state from a snapshot.

    Parameters
    ----------
    snapshot:
        Snapshot previously created by MetricState.

    Returns
    -------
    Metric
        Self for fluent chaining.
    """
    self._state.restore(snapshot)
    return self


# ----------------------------------------------------------
# Clone
# ----------------------------------------------------------

def clone(self) -> "Metric":
    """
    Create a deep clone of this Metric.

    Descriptor, labels and attributes are copied,
    runtime state is restored from a snapshot.
    """

    metric = self.__class__(
        metadata=self.metadata,
        value=self.value,
        metric_type=self.metric_type,
        value_type=self.value_type,
    )

    metric.update_labels(dict(self.labels.items()))
    metric.update_attributes(dict(self.attributes.items()))

    metric.restore(self.snapshot())

    return metric


# ----------------------------------------------------------
# Copy
# ----------------------------------------------------------

def copy(self) -> "Metric":
    """
    Alias of clone().
    """
    return self.clone()    
# ==========================================================
# Part 7. Hook API
# ==========================================================


from collections.abc import Callable
from typing import Any

from .metric_hooks import MetricHooks

Hook = Callable[..., None]


# ----------------------------------------------------------
# Hooks
# ----------------------------------------------------------

@property
def hooks(self) -> MetricHooks:
    """
    Return the MetricHooks manager.
    """
    return self._hooks


# ----------------------------------------------------------
# Register Hook
# ----------------------------------------------------------

def register_hook(
    self,
    event: str,
    callback: Hook,
) -> "Metric":
    """
    Register a hook callback.

    Parameters
    ----------
    event:
        Hook event name.

    callback:
        Callable to invoke when the event is dispatched.
    """

    self._hooks.register(event, callback)

    return self


# ----------------------------------------------------------
# Unregister Hook
# ----------------------------------------------------------

def unregister_hook(
    self,
    event: str,
    callback: Hook,
) -> "Metric":
    """
    Remove a hook callback.
    """

    self._hooks.unregister(event, callback)

    return self


# ----------------------------------------------------------
# Dispatch Hook
# ----------------------------------------------------------

def dispatch_hook(
    self,
    event: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Dispatch an event.
    """

    self._hooks.dispatch(
        event,
        *args,
        **kwargs,
    )


# ----------------------------------------------------------
# Clear Hooks
# ----------------------------------------------------------

def clear_hooks(
    self,
    event: str | None = None,
) -> "Metric":
    """
    Remove hook callbacks.

    If event is None, all hooks are removed.
    """

    self._hooks.clear(event)

    return self


# ----------------------------------------------------------
# Has Hooks
# ----------------------------------------------------------

def has_hooks(
    self,
    event: str,
) -> bool:
    """
    Return True if hooks are registered
    for the given event.
    """

    return self._hooks.has_hooks(event)


# ----------------------------------------------------------
# Hook Events
# ----------------------------------------------------------

@property
def hook_events(self) -> tuple[str, ...]:
    """
    Return all registered event names.
    """

    return self._hooks.events()


# ----------------------------------------------------------
# Hook Callbacks
# ----------------------------------------------------------

def hook_callbacks(
    self,
    event: str,
):
    """
    Return callbacks for an event.
    """

    return self._hooks.callbacks(event)    
# ==========================================================
# Part 8. Serialization API
# ==========================================================


from typing import Any

from ..serialization.metric_serializer import MetricSerializer


# ----------------------------------------------------------
# To Dict
# ----------------------------------------------------------

def to_dict(self) -> dict[str, Any]:
    """
    Serialize this Metric into a dictionary.
    """

    return MetricSerializer.to_dict(self)


# ----------------------------------------------------------
# From Dict
# ----------------------------------------------------------

@classmethod
def from_dict(
    cls,
    data: dict[str, Any],
) -> "Metric":
    """
    Construct a Metric from a dictionary.
    """

    return MetricSerializer.from_dict(data)


# ----------------------------------------------------------
# To JSON
# ----------------------------------------------------------

def to_json(
    self,
    *,
    indent: int | None = 2,
) -> str:
    """
    Serialize this Metric to JSON.
    """

    return MetricSerializer.to_json(
        self,
        indent=indent,
    )


# ----------------------------------------------------------
# From JSON
# ----------------------------------------------------------

@classmethod
def from_json(
    cls,
    text: str,
) -> "Metric":
    """
    Construct a Metric from JSON.
    """

    return MetricSerializer.from_json(text)


# ----------------------------------------------------------
# Save
# ----------------------------------------------------------

def save(
    self,
    path: str,
) -> None:
    """
    Save Metric to disk.
    """

    MetricSerializer.save(
        self,
        path,
    )


# ----------------------------------------------------------
# Load
# ----------------------------------------------------------

@classmethod
def load(
    cls,
    path: str,
) -> "Metric":
    """
    Load Metric from disk.
    """

    return MetricSerializer.load(path)  
# ==========================================================
# Part 9. Rich API
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
        f"name={self.name!r}, "
        f"type={self.metric_type!r}, "
        f"value={self.value!r}, "
        f"unit={self.unit!r})"
    )


# ----------------------------------------------------------
# str()
# ----------------------------------------------------------

def __str__(self) -> str:
    """
    Human-readable representation.
    """

    if self.unit:
        return f"{self.value} {self.unit}"

    return str(self.value)


# ----------------------------------------------------------
# Equality
# ----------------------------------------------------------

def __eq__(self, other: object) -> bool:
    """
    Metrics are equal if they share the same runtime UUID.
    """

    if not isinstance(other, Metric):
        return NotImplemented

    return self.uuid == other.uuid


# ----------------------------------------------------------
# Hash
# ----------------------------------------------------------

def __hash__(self) -> int:
    """
    Hash based on runtime UUID.
    """

    return hash(self.uuid)


# ----------------------------------------------------------
# Bool
# ----------------------------------------------------------

def __bool__(self) -> bool:
    """
    Delegate truthiness to MetricState.
    """

    return bool(self.state)


# ----------------------------------------------------------
# Iterator
# ----------------------------------------------------------

def __iter__(self) -> Iterator[Any]:
    """
    Delegate iteration to MetricState.
    """

    return iter(self.state)


# ----------------------------------------------------------
# Length
# ----------------------------------------------------------

def __len__(self) -> int:
    """
    Delegate length to MetricState.
    """

    return len(self.state)    
# ==========================================================
# Part 10. Debug Helpers
# ==========================================================


from typing import Any


# ----------------------------------------------------------
# Runtime State
# ----------------------------------------------------------

@property
def state_info(self) -> dict[str, Any]:
    """
    Runtime state information.
    """

    return self.state.state


# ----------------------------------------------------------
# Statistics
# ----------------------------------------------------------

@property
def statistics(self) -> dict[str, Any]:
    """
    Runtime statistics.
    """

    return self.state.statistics


# ----------------------------------------------------------
# Health
# ----------------------------------------------------------

@property
def health(self) -> str:
    """
    Runtime health.
    """

    return self.state.health


# ----------------------------------------------------------
# Age
# ----------------------------------------------------------

@property
def age(self) -> float:
    """
    Seconds since last update.
    """

    return self.state.age


# ----------------------------------------------------------
# Is Empty
# ----------------------------------------------------------

@property
def is_empty(self) -> bool:
    """
    True if the metric currently has no value.
    """

    return self.state.is_empty


# ----------------------------------------------------------
# Summary
# ----------------------------------------------------------

@property
def summary(self) -> dict[str, Any]:
    """
    High-level summary for debugging and diagnostics.
    """

    return {
        "uuid": str(self.uuid),
        "name": self.name,
        "namespace": self.namespace,
        "type": self.metric_type,
        "unit": self.unit,
        "value": self.value,
        "health": self.health,
        "enabled": self.enabled,
        "frozen": self.frozen,
        "closed": self.closed,
        "updates": self.update_count,
        "labels": self.label_count,
        "attributes": self.attribute_count,
        "age": self.age,
    }


# ----------------------------------------------------------
# Dump
# ----------------------------------------------------------

def dump(self) -> dict[str, Any]:
    """
    Return a complete diagnostic dump.
    """

    return {
        "descriptor": self.descriptor.to_dict(),
        "metadata": self.metadata.to_dict(),
        "labels": dict(self.labels.items()),
        "attributes": dict(self.attributes.items()),
        "state": self.state.state,
        "statistics": self.statistics,
        "summary": self.summary,
    }              