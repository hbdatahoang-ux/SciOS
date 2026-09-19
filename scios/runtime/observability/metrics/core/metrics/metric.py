# ==============================================================================
# Part 1. Imports & Constants
# ==============================================================================

from __future__ import annotations

from typing import Any

from .core.attributes import MetricAttributes
from .core.descriptor import MetricDescriptor
from .core.labels import MetricLabels
from .core.metadata import MetricMetadata
from .metric_state import MetricState
from .metric_hooks import MetricHooks

__all__ = [
    "Metric",
]

DEFAULT_METRIC_TYPE = "gauge"
DEFAULT_VALUE_TYPE = float
DEFAULT_VALUE: Any = None

# ==============================================================================
# Part 2. Constructor
# ==============================================================================

class Metric:
    """
    High-level Metric abstraction.

    Composition:

        Metric
            ├── MetricDescriptor
            ├── MetricLabels
            ├── MetricAttributes
            ├── MetricState
            └── MetricHooks
    """

    def __init__(
        self,
        *,
        metadata: MetricMetadata,
        value: Any = DEFAULT_VALUE,
        metric_type: str = DEFAULT_METRIC_TYPE,
        value_type: type = DEFAULT_VALUE_TYPE,
    ) -> None:

        # --------------------------------------------------------------
        # Core Components
        # --------------------------------------------------------------

        self._descriptor = MetricDescriptor(
            metadata=metadata,
            metric_type=metric_type,
            value_type=value_type,
        )

        self._labels = MetricLabels()

        self._attributes = MetricAttributes()

        self._state = MetricState(
            value=value,
        )

        self._hooks = MetricHooks()

# ==============================================================================
# Part 3. Descriptor
# ==============================================================================

    @property
    def descriptor(self) -> MetricDescriptor:
        """
        Metric descriptor.
        """
        return self._descriptor


    @property
    def metadata(self) -> MetricMetadata:
        """
        Metric metadata.
        """
        return self._descriptor.metadata


    @property
    def name(self) -> str:
        """
        Metric name.
        """
        return self.metadata.name


    @property
    def namespace(self) -> str:
        """
        Metric namespace.
        """
        return self.metadata.namespace


    @property
    def description(self) -> str:
        """
        Metric description.
        """
        return self.metadata.description


    @property
    def unit(self) -> str:
        """
        Metric unit.
        """
        return self.metadata.unit


    @property
    def category(self) -> str:
        """
        Metric category.
        """
        return self.metadata.category


    @property
    def owner(self) -> str:
        """
        Metric owner.
        """
        return self.metadata.owner


    @property
    def version(self) -> str:
        """
        Metric version.
        """
        return self.metadata.version


    @property
    def tags(self):
        """
        Metric tags.
        """
        return self.metadata.tags


    @property
    def extras(self):
        """
        Extra metadata.
        """
        return self.metadata.extras


    @property
    def metric_type(self):
        """
        Metric type.
        """
        return self._descriptor.metric_type


    @property
    def value_type(self):
        """
        Value type.
        """
        return self._descriptor.value_type


    @property
    def aggregation(self):
        """
        Aggregation strategy.
        """
        return self._descriptor.aggregation


    @property
    def temporality(self):
        """
        Metric temporality.
        """
        return self._descriptor.temporality


    @property
    def monotonic(self):
        """
        Monotonic flag.
        """
        return self._descriptor.monotonic

# ==============================================================================
# Part 4. Metadata Properties
# ==============================================================================

    @property
    def fullname(self) -> str:
        """
        Fully-qualified metric name.
        """
        if self.namespace:
            return f"{self.namespace}.{self.name}"
        return self.name


    @property
    def metadata_dict(self) -> dict[str, Any]:
        """
        Metadata as dictionary.
        """
        return self.metadata.to_dict()


    def update_metadata(
        self,
        **kwargs: Any,
    ) -> "Metric":
        """
        Update metadata fields.
        """

        for key, value in kwargs.items():

            if hasattr(self.metadata, key):
                setattr(self.metadata, key, value)

        return self


# ==============================================================================
# Part 5. Labels
# ==============================================================================

    @property
    def labels(self) -> MetricLabels:
        """
        Metric labels.
        """
        return self._labels


    def set_label(
        self,
        key: str,
        value: Any,
    ) -> "Metric":

        self._labels[key] = value

        return self


    def get_label(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self._labels.get(
            key,
            default,
        )


    def remove_label(
        self,
        key: str,
    ) -> "Metric":

        self._labels.pop(
            key,
            None,
        )

        return self


    def clear_labels(self) -> "Metric":

        self._labels.clear()

        return self


# ==============================================================================
# Part 6. Attributes
# ==============================================================================

    @property
    def attributes(self) -> MetricAttributes:
        """
        Metric attributes.
        """
        return self._attributes


    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> "Metric":

        self._attributes[key] = value

        return self


    def get_attribute(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self._attributes.get(
            key,
            default,
        )


    def remove_attribute(
        self,
        key: str,
    ) -> "Metric":

        self._attributes.pop(
            key,
            None,
        )

        return self


    def clear_attributes(self) -> "Metric":

        self._attributes.clear()

        return self


# ==============================================================================
# Part 7. State
# ==============================================================================

    @property
    def state(self) -> MetricState:
        """
        Metric runtime state.
        """
        return self._state


    @property
    def value(self) -> Any:
        """
        Current metric value.
        """
        return self._state.value


    @value.setter
    def value(
        self,
        value: Any,
    ) -> None:

        self._state.value = value


    @property
    def timestamp(self):

        return self._state.timestamp


    @property
    def enabled(self):

        return self._state.enabled


# ==============================================================================
# Part 8. Value Operations
# ==============================================================================

    def set(
        self,
        value: Any,
    ) -> "Metric":

        self._state.value = value

        return self


    def get(self) -> Any:

        return self._state.value


    def reset(self) -> "Metric":

        self._state.reset()

        return self


    def increment(
        self,
        amount: int | float = 1,
    ) -> "Metric":

        self._state.value += amount

        return self


    def decrement(
        self,
        amount: int | float = 1,
    ) -> "Metric":

        self._state.value -= amount

        return self


    def update(
        self,
        value: Any,
    ) -> "Metric":

        self._state.value = value

        return self


# ==============================================================================
# Part 9. Hooks
# ==============================================================================

    @property
    def hooks(self) -> MetricHooks:
        """
        Metric hooks.
        """
        return self._hooks


    def add_hook(
        self,
        hook: Any,
    ) -> "Metric":

        self._hooks.add(hook)

        return self


    def remove_hook(
        self,
        hook: Any,
    ) -> "Metric":

        self._hooks.remove(hook)

        return self


    def clear_hooks(self) -> "Metric":

        self._hooks.clear()

        return self


    def emit_hooks(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> "Metric":

        self._hooks.emit(
            *args,
            **kwargs,
        )

        return self

# ==============================================================================
# Part 10. Serialization
# ==============================================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize metric.
        """
        return {
            "metadata": self.metadata.to_dict(),
            "descriptor": self.descriptor.to_dict(),
            "labels": self.labels.to_dict(),
            "attributes": self.attributes.to_dict(),
            "state": self.state.to_dict(),
        }


    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Metric":
        """
        Deserialize metric.
        """

        metadata = MetricMetadata.from_dict(
            data.get("metadata", {})
        )

        descriptor = data.get(
            "descriptor",
            {},
        )

        metric = cls(
            metadata=metadata,
            value=data.get("state", {}).get("value"),
            metric_type=descriptor.get(
                "metric_type",
                DEFAULT_METRIC_TYPE,
            ),
            value_type=eval(
                descriptor.get(
                    "value_type",
                    "float",
                )
            ),
        )

        metric.labels.update(
            data.get("labels", {})
        )

        metric.attributes.update(
            data.get("attributes", {})
        )

        metric.state.restore(
            data.get("state", {})
        )

        return metric


    def to_tuple(self) -> tuple:

        return (
            self.metadata.to_tuple(),
            self.descriptor.to_tuple(),
            self.labels.to_tuple(),
            self.attributes.to_tuple(),
            self.state.to_tuple(),
        )


    @classmethod
    def from_tuple(
        cls,
        value: tuple,
    ) -> "Metric":

        (
            metadata,
            descriptor,
            labels,
            attributes,
            state,
        ) = value

        metric = cls(
            metadata=MetricMetadata.from_tuple(
                metadata
            ),
            value=state[0],
            metric_type=descriptor[1],
            value_type=descriptor[2],
        )

        metric.labels.restore(labels)
        metric.attributes.restore(attributes)
        metric.state.restore(state)

        return metric


    def snapshot(self) -> dict[str, Any]:

        return self.to_dict()


    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> "Metric":

        restored = self.from_dict(
            snapshot
        )

        self.__dict__.update(
            restored.__dict__
        )

        return self


# ==============================================================================
# Part 11. Validation
# ==============================================================================

    @staticmethod
    def validate_metadata(
        metadata: MetricMetadata,
    ) -> bool:

        return isinstance(
            metadata,
            MetricMetadata,
        )


    @staticmethod
    def validate_descriptor(
        descriptor: MetricDescriptor,
    ) -> bool:

        return isinstance(
            descriptor,
            MetricDescriptor,
        )


    @staticmethod
    def validate_state(
        state: MetricState,
    ) -> bool:

        return isinstance(
            state,
            MetricState,
        )


    @classmethod
    def validate_metric(
        cls,
        metric: "Metric",
    ) -> bool:

        return isinstance(
            metric,
            cls,
        )


    def validate(self) -> bool:

        return all(
            (
                self.validate_metadata(
                    self.metadata,
                ),
                self.validate_descriptor(
                    self.descriptor,
                ),
                self.validate_state(
                    self.state,
                ),
            )
        )


# ==============================================================================
# Part 12. Utilities
# ==============================================================================

    def clone(self) -> "Metric":

        return self.from_dict(
            self.to_dict()
        )


    copy = clone


    def merge(
        self,
        other: "Metric",
    ) -> "Metric":

        if not isinstance(
            other,
            Metric,
        ):
            return self

        self.labels.update(
            other.labels
        )

        self.attributes.update(
            other.attributes
        )

        self.value = other.value

        return self


    def reset_all(self) -> "Metric":

        self.clear_labels()
        self.clear_attributes()
        self.reset()

        return self


# ==============================================================================
# Part 13. Protocols
# ==============================================================================

    def __hash__(self) -> int:

        return hash(
            self.fullname
        )


    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(
            other,
            Metric,
        ):
            return False

        return (
            self.fullname
            == other.fullname
        )


    def __repr__(self) -> str:

        return (
            f"Metric("
            f"name={self.fullname!r}, "
            f"value={self.value!r})"
        )


    __str__ = __repr__


    def __bool__(self) -> bool:

        return self.value is not None


# ==============================================================================
# Part 14. Diagnostics
# ==============================================================================

    def summary(self) -> dict[str, Any]:

        return {
            "name": self.fullname,
            "type": self.metric_type,
            "value": self.value,
        }


    def diagnostics(self) -> dict[str, Any]:

        return {
            "valid": self.validate(),
            "summary": self.summary(),
        }


    def metric_report(self) -> dict[str, Any]:

        return {
            "metadata": self.metadata.to_dict(),
            "diagnostics": self.diagnostics(),
        }


    def overall_status(self) -> str:

        return (
            "healthy"
            if self.validate()
            else "invalid"
        )


# ==============================================================================
# Part 15. Public API
# ==============================================================================

__all__ = [
    "Metric",
]                        