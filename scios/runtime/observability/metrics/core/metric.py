# ==============================================================================
# Part 1. Imports
# ==============================================================================

from __future__ import annotations


import copy
import json
import time

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, TypeAlias


from .attributes import MetricAttributes
from .labels import MetricLabels
from .annotations import MetricAnnotations
from .tags import MetricTags
from .metric_hooks import MetricHooks
from .metric_snapshot import MetricSnapshot
from .metric_state import MetricState




# ==============================================================================
# Part 2. Constants
# ==============================================================================

METRIC_VERSION: str = "1.0.0"

DEFAULT_METRIC_NAME: str = "metric"

DEFAULT_METRIC_VALUE: float = 0.0

DEFAULT_TIMESTAMP: float = 0.0


# ==============================================================================
# Callable Metadata Container
# ==============================================================================

class CallableContainer:
    """
    Hybrid metadata API wrapper.

    Supports:

        metric.labels
        metric.labels()
        metric.labels["key"]
        metric.labels.add("key", "value")
        metric.labels.get("key")

        metric.attributes
        metric.attributes()
        metric.attributes["key"]
        metric.attributes.add("key", "value")
        metric.attributes.get("key")

        metric.annotations
        metric.annotations()
        metric.annotations["key"]
        metric.annotations.add("key", "value")
        metric.annotations.get("key")

        metric.tags
        metric.tags()
        metric.tags.add("value")
        "value" in metric.tags

        metric.hooks
        metric.hooks()
        metric.hooks.register(...)

    The wrapper preserves the real underlying metadata container.
    """

    __slots__ = (
        "_container",
    )

    # --------------------------------------------------------------------------
    # Constructor
    # --------------------------------------------------------------------------

    def __init__(
        self,
        container,
    ):
        object.__setattr__(
            self,
            "_container",
            container,
        )

    # --------------------------------------------------------------------------
    # Internal container access
    # --------------------------------------------------------------------------

    def _get_container(self):
        """
        Return the underlying metadata container.

        Safe during deepcopy / pickle reconstruction.
        """

        try:
            return object.__getattribute__(
                self,
                "_container",
            )

        except AttributeError:
            raise AttributeError(
                "CallableContainer is not initialized."
            ) from None

    # --------------------------------------------------------------------------
    # Internal storage access
    # --------------------------------------------------------------------------

    def _get_storage(self):
        """
        Return the underlying metadata storage.

        Supported container layouts:

            container.values
            container._values

        Current SciOS metadata containers use:

            MetricAnnotations.values -> dict
            MetricLabels.values      -> dict
            MetricAttributes.values  -> dict
            MetricTags.values        -> set
        """

        container = self._get_container()

        # ------------------------------------------------------------------
        # Preferred public storage
        # ------------------------------------------------------------------

        values = getattr(
            container,
            "values",
            None,
        )

        if values is not None:
            return values

        # ------------------------------------------------------------------
        # Backward-compatible private storage
        # ------------------------------------------------------------------

        values = getattr(
            container,
            "_values",
            None,
        )

        if values is not None:
            return values

        return None

    # --------------------------------------------------------------------------
    # Callable API
    # --------------------------------------------------------------------------

    def __call__(self):
        """
        Return this wrapper itself.

        Allows:

            metric.labels()
            metric.attributes()
            metric.annotations()
            metric.tags()
            metric.hooks()
        """

        return self

    # --------------------------------------------------------------------------
    # Attribute delegation
    # --------------------------------------------------------------------------

    def __getattr__(
        self,
        name,
    ):
        """
        Delegate unknown attributes to the underlying container.

        Explicit wrapper methods such as:

            add()
            get()
            clear()

        are resolved on CallableContainer itself.
        """

        container = self._get_container()

        return getattr(
            container,
            name,
        )

    # --------------------------------------------------------------------------
    # Item access
    # --------------------------------------------------------------------------

    def __getitem__(
        self,
        key,
    ):
        """
        Get metadata item.
        """

        container = self._get_container()

        try:
            return container[key]

        except (
            TypeError,
            AttributeError,
            KeyError,
        ):
            pass

        storage = self._get_storage()

        if storage is not None:
            return storage[key]

        raise KeyError(
            key,
        )

    # --------------------------------------------------------------------------
    # Item assignment
    # --------------------------------------------------------------------------

    def __setitem__(
        self,
        key,
        value,
    ):
        """
        Set metadata item.
        """

        container = self._get_container()

        try:
            container[key] = value
            return

        except (
            TypeError,
            AttributeError,
        ):
            pass

        storage = self._get_storage()

        if storage is not None:
            storage[key] = value
            return

        raise TypeError(
            f"{type(container).__name__} "
            "does not support item assignment."
        )

    # --------------------------------------------------------------------------
    # Membership
    # --------------------------------------------------------------------------

    def __contains__(
        self,
        item,
    ) -> bool:
        """
        Support:

            "production" in metric.tags
            "host" in metric.labels
        """

        container = self._get_container()

        try:
            return item in container

        except TypeError:
            pass

        storage = self._get_storage()

        if storage is not None:
            return item in storage

        return False

    # --------------------------------------------------------------------------
    # Iteration
    # --------------------------------------------------------------------------

    def __iter__(self):
        """
        Iterate over metadata.
        """

        container = self._get_container()

        try:
            return iter(container)

        except TypeError:
            pass

        storage = self._get_storage()

        if storage is not None:
            return iter(storage)

        return iter(())

    # --------------------------------------------------------------------------
    # Length
    # --------------------------------------------------------------------------

    def __len__(self) -> int:
        """
        Return metadata size.
        """

        container = self._get_container()

        try:
            return len(container)

        except TypeError:
            pass

        storage = self._get_storage()

        if storage is not None:
            return len(storage)

        return 0

    # --------------------------------------------------------------------------
    # Unified add API
    # --------------------------------------------------------------------------

    def add(
        self,
        *args,
    ):
        """
        Uniform metadata insertion API.

        Mapping-style:

            annotations.add(
                "description",
                "request counter",
            )

            labels.add(
                "host",
                "node01",
            )

            attributes.add(
                "region",
                "test",
            )

        Set-style:

            tags.add(
                "production",
            )
        """

        container = self._get_container()

        # ------------------------------------------------------------------
        # 1. Native container add()
        # ------------------------------------------------------------------

        native_add = getattr(
            container,
            "add",
            None,
        )

        if callable(native_add):
            return native_add(
                *args,
            )

        # ------------------------------------------------------------------
        # 2. Resolve actual storage
        # ------------------------------------------------------------------

        storage = self._get_storage()

        # ------------------------------------------------------------------
        # 3. Mapping-style add(key, value)
        # ------------------------------------------------------------------

        if len(args) == 2:

            key, value = args

            if storage is not None:

                if isinstance(
                    storage,
                    dict,
                ):
                    storage[key] = value
                    return value

                try:
                    storage[key] = value
                    return value

                except (
                    TypeError,
                    AttributeError,
                    KeyError,
                ):
                    pass

            # --------------------------------------------------------------
            # Generic container assignment
            # --------------------------------------------------------------

            try:
                container[key] = value
                return value

            except (
                TypeError,
                AttributeError,
                KeyError,
            ):
                pass

        # ------------------------------------------------------------------
        # 4. Set-style add(value)
        # ------------------------------------------------------------------

        if len(args) == 1:

            value = args[0]

            # --------------------------------------------------------------
            # Set storage
            # --------------------------------------------------------------

            if isinstance(
                storage,
                set,
            ):

                storage.add(
                    value,
                )

                return value

            # --------------------------------------------------------------
            # Generic storage exposing add()
            # --------------------------------------------------------------

            if storage is not None:

                storage_add = getattr(
                    storage,
                    "add",
                    None,
                )

                if callable(storage_add):

                    storage_add(
                        value,
                    )

                    return value

            # --------------------------------------------------------------
            # Generic container add()
            # --------------------------------------------------------------

            try:
                container[value] = value
                return value

            except (
                TypeError,
                AttributeError,
                KeyError,
            ):
                pass

        # ------------------------------------------------------------------
        # 5. Invalid operation
        # ------------------------------------------------------------------

        raise AttributeError(
            f"{type(container).__name__} "
            f"does not support add{args!r}"
        )

    # --------------------------------------------------------------------------
    # Get API
    # --------------------------------------------------------------------------

    def get(
        self,
        key,
        default=None,
    ):
        """
        Get metadata value.

        Mapping:

            metric.annotations.get(
                "description",
            )

        Tags:

            metric.tags.get(
                "production",
            )

        For tags, the returned value is the tag itself when present.
        """

        container = self._get_container()

        # ------------------------------------------------------------------
        # Native get()
        # ------------------------------------------------------------------

        native_get = getattr(
            container,
            "get",
            None,
        )

        if callable(native_get):

            try:
                return native_get(
                    key,
                    default,
                )

            except TypeError:
                return native_get(
                    key,
                )

        # ------------------------------------------------------------------
        # Actual storage
        # ------------------------------------------------------------------

        storage = self._get_storage()

        if storage is None:
            return default

        # ------------------------------------------------------------------
        # Mapping
        # ------------------------------------------------------------------

        if isinstance(
            storage,
            dict,
        ):
            return storage.get(
                key,
                default,
            )

        # ------------------------------------------------------------------
        # Set
        # ------------------------------------------------------------------

        if isinstance(
            storage,
            set,
        ):

            if key in storage:
                return key

            return default

        # ------------------------------------------------------------------
        # Generic mapping-like object
        # ------------------------------------------------------------------

        try:
            return storage.get(
                key,
                default,
            )

        except AttributeError:
            pass

        # ------------------------------------------------------------------
        # Generic item access
        # ------------------------------------------------------------------

        try:
            return storage[key]

        except (
            KeyError,
            TypeError,
            IndexError,
        ):
            return default

    # --------------------------------------------------------------------------
    # Clear API
    # --------------------------------------------------------------------------

    def clear(self):
        """
        Clear the underlying metadata container.
        """

        container = self._get_container()

        native_clear = getattr(
            container,
            "clear",
            None,
        )

        if callable(native_clear):
            return native_clear()

        storage = self._get_storage()

        if storage is not None:

            storage_clear = getattr(
                storage,
                "clear",
                None,
            )

            if callable(storage_clear):
                return storage_clear()

        raise AttributeError(
            f"{type(container).__name__} "
            "does not support clear()"
        )

    # --------------------------------------------------------------------------
    # Representation
    # --------------------------------------------------------------------------

    def __repr__(self):
        try:

            container = object.__getattribute__(
                self,
                "_container",
            )

        except AttributeError:

            return (
                "CallableContainer(<uninitialized>)"
            )

        return repr(
            container,
        )





# ==============================================================================
# Part 3. Enums
# ==============================================================================

class MetricType(str, Enum):
    """Supported metric types."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    UNTYPED = "untyped"


class MetricUnit(str, Enum):
    """Supported metric units."""

    NONE = "none"

    COUNT = "count"

    BYTES = "bytes"

    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    MICROSECONDS = "microseconds"
    NANOSECONDS = "nanoseconds"

    PERCENT = "percent"

    CELSIUS = "celsius"

    VOLTS = "volts"
    AMPERES = "amperes"
    WATTS = "watts"

    HERTZ = "hertz"


# ==============================================================================
# Part 4. Exceptions
# ==============================================================================

class MetricError(Exception):
    """Base metric exception."""


class MetricValidationError(MetricError):
    """Raised when metric validation fails."""


# ==============================================================================
# Part 5. Type Aliases
# ==============================================================================

MetricValue: TypeAlias = int | float

MetricPayload: TypeAlias = dict[str, Any]



# ==============================================================================
# Part 6. Dataclass
# ==============================================================================

@dataclass(
    slots=True,
    eq=True,
    repr=False,
)
class Metric:
    """
    Runtime metric object.

    Public metadata API:

        metric.labels
        metric.labels()

        metric.attributes
        metric.attributes()

        metric.annotations
        metric.annotations()

        metric.tags
        metric.tags()

        metric.hooks
        metric.hooks()

    The private metadata fields always contain the real containers.
    CallableContainer objects are public API proxies only.
    """

    # ------------------------------------------------------------------
    # Core fields
    # ------------------------------------------------------------------

    name: str = DEFAULT_METRIC_NAME

    value: MetricValue = DEFAULT_METRIC_VALUE

    metric_type: MetricType = MetricType.GAUGE

    unit: MetricUnit = MetricUnit.NONE

    # ------------------------------------------------------------------
    # Runtime state
    # ------------------------------------------------------------------

    state: MetricState = field(
        default_factory=MetricState,
    )

    # ------------------------------------------------------------------
    # Real metadata containers
    #
    # IMPORTANT:
    # These MUST remain the actual container objects.
    #
    # Do NOT replace them with CallableContainer.
    # ------------------------------------------------------------------

    _labels: MetricLabels = field(
        default_factory=MetricLabels,
        repr=False,
    )

    _attributes: MetricAttributes = field(
        default_factory=MetricAttributes,
        repr=False,
    )

    _annotations: MetricAnnotations = field(
        default_factory=MetricAnnotations,
        repr=False,
    )

    _tags: MetricTags = field(
        default_factory=MetricTags,
        repr=False,
    )

    _hooks: MetricHooks = field(
        default_factory=MetricHooks,
        repr=False,
    )

    # ------------------------------------------------------------------
    # Public API proxies
    #
    # These are runtime helpers and must NOT participate in equality.
    # ------------------------------------------------------------------

    _labels_proxy: CallableContainer | None = field(
        default=None,
        init=False,
        repr=False,
        compare=False,
    )

    _attributes_proxy: CallableContainer | None = field(
        default=None,
        init=False,
        repr=False,
        compare=False,
    )

    _annotations_proxy: CallableContainer | None = field(
        default=None,
        init=False,
        repr=False,
        compare=False,
    )

    _tags_proxy: CallableContainer | None = field(
        default=None,
        init=False,
        repr=False,
        compare=False,
    )

    _hooks_proxy: CallableContainer | None = field(
        default=None,
        init=False,
        repr=False,
        compare=False,
    )

    # ------------------------------------------------------------------
    # Lifecycle timestamps
    # ------------------------------------------------------------------

    created_at: float = field(
        default_factory=time.time,
        init=False,
    )

    updated_at: float = field(
        default_factory=time.time,
        init=False,
    )

    # ------------------------------------------------------------------
    # Version
    # ------------------------------------------------------------------

    version: str = field(
        default=METRIC_VERSION,
        init=False,
        compare=False,
    )

    # ==========================================================================
    # Initialization / Validation
    # ==========================================================================

    def __post_init__(self) -> None:
        """
        Validate and initialize the metric.

        This is the single authoritative constructor hook.
        """

        # ------------------------------------------------------------------
        # Name
        # ------------------------------------------------------------------

        if not isinstance(
            self.name,
            str,
        ):
            raise MetricValidationError(
                "Metric name must be a string."
            )

        self.name = self.name.strip()

        if not self.name:
            raise MetricValidationError(
                "Metric name cannot be empty."
            )

        # ------------------------------------------------------------------
        # Value
        # ------------------------------------------------------------------

        if not isinstance(
            self.value,
            (int, float),
        ):
            raise MetricValidationError(
                "Metric value must be numeric."
            )

        if isinstance(
            self.value,
            bool,
        ):
            raise MetricValidationError(
                "Metric value cannot be boolean."
            )

        # ------------------------------------------------------------------
        # Metric type
        # ------------------------------------------------------------------

        if not isinstance(
            self.metric_type,
            MetricType,
        ):
            raise MetricValidationError(
                "Invalid metric type."
            )

        # ------------------------------------------------------------------
        # Unit
        # ------------------------------------------------------------------

        if not isinstance(
            self.unit,
            MetricUnit,
        ):
            raise MetricValidationError(
                "Invalid metric unit."
            )

        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------

        if not isinstance(
            self.state,
            MetricState,
        ):
            raise MetricValidationError(
                "state must be MetricState."
            )

        # ------------------------------------------------------------------
        # Metadata containers
        # ------------------------------------------------------------------

        metadata_fields = (
            (
                self._labels,
                MetricLabels,
                "labels",
            ),
            (
                self._attributes,
                MetricAttributes,
                "attributes",
            ),
            (
                self._annotations,
                MetricAnnotations,
                "annotations",
            ),
            (
                self._tags,
                MetricTags,
                "tags",
            ),
            (
                self._hooks,
                MetricHooks,
                "hooks",
            ),
        )

        for container, expected, name in metadata_fields:

            if not isinstance(
                container,
                expected,
            ):
                raise MetricValidationError(
                    f"{name} must be {expected.__name__}."
                )

        # ------------------------------------------------------------------
        # Timestamp normalization
        # ------------------------------------------------------------------

        now = time.time()

        if self.created_at <= DEFAULT_TIMESTAMP:
            self.created_at = now

        if self.updated_at <= DEFAULT_TIMESTAMP:
            self.updated_at = self.created_at

        if self.updated_at < self.created_at:
            self.updated_at = self.created_at

        # ------------------------------------------------------------------
        # Public metadata API
        # ------------------------------------------------------------------

        self._init_metadata_api()

    # ==========================================================================
    # Callable Metadata API
    # ==========================================================================

    def _init_metadata_api(self) -> None:
        """
        Rebuild public metadata proxies.

        The real containers remain untouched.

        _labels      -> MetricLabels
        _attributes  -> MetricAttributes
        _annotations -> MetricAnnotations
        _tags        -> MetricTags
        _hooks       -> MetricHooks
        """

        self._labels_proxy = CallableContainer(
            self._labels,
        )

        self._attributes_proxy = CallableContainer(
            self._attributes,
        )

        self._annotations_proxy = CallableContainer(
            self._annotations,
        )

        self._tags_proxy = CallableContainer(
            self._tags,
        )

        self._hooks_proxy = CallableContainer(
            self._hooks,
        )

    # ==========================================================================
    # Timestamp
    # ==========================================================================

    def touch(self) -> None:
        """
        Update modification timestamp.
        """

        self.updated_at = time.time()




    # ==============================================================================
    # Part 8. Properties
    # ==============================================================================


    # ------------------------------------------------------------------------------
    # Timestamp
    # ------------------------------------------------------------------------------


    @property
    def timestamp(self) -> float:
        """
        Latest update timestamp.
        """

        return self.updated_at


    @property
    def age(self) -> float:
        """
        Metric lifetime in seconds.
        """

        return max(
            0.0,
            time.time() - self.created_at,
        )


    # ------------------------------------------------------------------------------
    # Runtime state
    # ------------------------------------------------------------------------------


    @property
    def enabled(self) -> bool:
        """
        Whether counter is enabled.
        """

        return self.state.is_enabled()


    @property
    def active(self) -> bool:
        """
        Whether counter is active.
        """

        return self.state.is_active()


    @property
    def healthy(self) -> bool:
        """
        Whether counter is healthy.
        """

        return self.state.is_healthy()


    # ------------------------------------------------------------------------------
    # Metadata API
    #
    # IMPORTANT:
    #
    # Do NOT return:
    #
    #     self._annotations
    #     self._tags
    #
    # Those are the real metadata containers.
    #
    # The public API must return CallableContainer proxies.
    # ------------------------------------------------------------------------------


    @property
    def labels(self) -> CallableContainer:
        """
        Labels metadata API.

        Supports:

            counter.labels
            counter.labels()
            counter.labels["host"]
            counter.labels.add("host", "node01")
        """

        return self._labels_proxy


    @property
    def attributes(self) -> CallableContainer:
        """
        Attributes metadata API.

        Supports:

            counter.attributes
            counter.attributes()
            counter.attributes["region"]
            counter.attributes.add("region", "test")
        """

        return self._attributes_proxy


    @property
    def annotations(self) -> CallableContainer:
        """
        Annotations metadata API.

        Supports:

            counter.annotations
            counter.annotations()
            counter.annotations["description"]
            counter.annotations.add(
                "description",
                "request counter",
            )
        """

        return self._annotations_proxy


    @property
    def tags(self) -> CallableContainer:
        """
        Tags metadata API.

        Supports:

            counter.tags
            counter.tags()
            counter.tags.add("production")
        """

        return self._tags_proxy


    @property
    def hooks(self) -> CallableContainer:
        """
        Hooks metadata API.

        Supports:

            counter.hooks
            counter.hooks()
            counter.hooks.register(...)
        """

        return self._hooks_proxy






# ==============================================================================
# Part 9. Value Operations
# ==============================================================================


    def set_value(
        self,
        value: MetricValue,
    ) -> None:

        if not isinstance(value, (int, float)):
            raise MetricValidationError(
                "Metric value must be numeric."
            )


        self.value = value

        self.touch()



    def get_value(self) -> MetricValue:

        return self.value



    def increment(
        self,
        amount: MetricValue = 1,
    ) -> MetricValue:

        if not isinstance(amount, (int, float)):
            raise MetricValidationError(
                "Increment amount must be numeric."
            )


        self.value += amount

        self.touch()

        return self.value



    def decrement(
        self,
        amount: MetricValue = 1,
    ) -> MetricValue:

        if not isinstance(amount, (int, float)):
            raise MetricValidationError(
                "Decrement amount must be numeric."
            )


        self.value -= amount

        self.touch()

        return self.value



    def reset(self) -> None:

        self.value = DEFAULT_METRIC_VALUE

        self.touch()



    def update(
        self,
        value: MetricValue,
    ) -> None:

        self.set_value(value)



    def touch(self) -> None:

        self.updated_at = time.time()


# ==============================================================================
# Part 10. State Management
# ==============================================================================

    def enable(self) -> None:
        """
        Enable metric.
        """

        self.state.enable()
        self.touch()


    def disable(self) -> None:
        """
        Disable metric.
        """

        self.state.disable()
        self.touch()


    def activate(self) -> None:
        """
        Activate metric.
        """

        self.state.activate()
        self.touch()


    def deactivate(self) -> None:
        """
        Deactivate metric.
        """

        self.state.deactivate()
        self.touch()


    def archive(self) -> None:
        """
        Archive metric.
        """

        self.state.archive()
        self.touch()


    def restore(
        self,
        snapshot: MetricSnapshot | None = None,
    ) -> None:
        """
        Restore metric state or complete metric snapshot.

        Parameters
        ----------
        snapshot:
            None:
                Restore lifecycle state only.

            MetricSnapshot:
                Restore the complete metric state.
        """

        # ------------------------------------------------------------------
        # Lifecycle restore only
        # ------------------------------------------------------------------

        if snapshot is None:
            self.state.restore()
            self.touch()
            return

        # ------------------------------------------------------------------
        # Validate snapshot
        # ------------------------------------------------------------------

        if not isinstance(snapshot, MetricSnapshot):
            raise MetricValidationError(
                "snapshot must be a MetricSnapshot."
            )

        data = copy.deepcopy(snapshot.snapshot)

        # ------------------------------------------------------------------
        # Core fields
        # ------------------------------------------------------------------

        self.name = data["name"]

        self.value = data["value"]

        self.metric_type = MetricType(
            data["metric_type"]
        )

        self.unit = MetricUnit(
            data["unit"]
        )

        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------

        self.state = MetricState.from_dict(
            data.get(
                "state",
                {},
            )
        )

        # ------------------------------------------------------------------
        # Metadata containers
        #
        # IMPORTANT:
        # Keep the REAL metadata containers here.
        # CallableContainer is only the public API proxy.
        # ------------------------------------------------------------------

        self._labels = MetricLabels.from_dict(
            data.get(
                "labels",
                {},
            )
        )

        self._attributes = MetricAttributes.from_dict(
            data.get(
                "attributes",
                {},
            )
        )

        self._annotations = MetricAnnotations.from_dict(
            data.get(
                "annotations",
                {},
            )
        )

        self._tags = MetricTags.from_dict(
            data.get(
                "tags",
                [],
            )
        )

        self._hooks = MetricHooks.from_dict(
            data.get(
                "hooks",
                {},
            )
        )

        # ------------------------------------------------------------------
        # Lifecycle timestamps
        # ------------------------------------------------------------------

        self.created_at = data.get(
            "created_at",
            self.created_at,
        )

        self.updated_at = data.get(
            "updated_at",
            self.updated_at,
        )

        # ------------------------------------------------------------------
        # Version
        # ------------------------------------------------------------------

        if "version" in data:
            self.version = data["version"]

        # ------------------------------------------------------------------
        # Rebuild callable metadata proxies
        #
        # _labels / _annotations / _tags remain REAL containers.
        # ------------------------------------------------------------------

        self._init_metadata_api()


    def snapshot(self) -> MetricSnapshot:
        """
        Create an immutable metric snapshot.
        """

        return MetricSnapshot(
            snapshot=copy.deepcopy(
                self.to_dict()
            )
        )

# ==============================================================================
# Part 11. Metadata Access
# ==============================================================================


    def get_labels(self) -> MetricLabels:
        return self._labels



    def get_attributes(self) -> MetricAttributes:
        return self._attributes



    def get_annotations(self) -> MetricAnnotations:
        return self._annotations



    def get_tags(self) -> MetricTags:
        return self._tags



    def get_hooks(self) -> MetricHooks:
        return self._hooks



# ==============================================================================
# Part 12. Validation
# ==============================================================================


    def validate(self) -> bool:

        try:

            if not isinstance(self.name, str):
                return False


            if not self.name.strip():
                return False


            if not isinstance(
                self.value,
                (int, float),
            ):
                return False


            if not isinstance(
                self.metric_type,
                MetricType,
            ):
                return False


            if not isinstance(
                self.unit,
                MetricUnit,
            ):
                return False


            if not isinstance(
                self.state,
                MetricState,
            ):
                return False


            if not isinstance(
                self._labels,
                MetricLabels,
            ):
                return False


            if not isinstance(
                self._attributes,
                MetricAttributes,
            ):
                return False


            if not isinstance(
                self._annotations,
                MetricAnnotations,
            ):
                return False


            if not isinstance(
                self._tags,
                MetricTags,
            ):
                return False


            if not isinstance(
                self._hooks,
                MetricHooks,
            ):
                return False


            return True


        except Exception:

            return False



# ==============================================================================
# Part 13. Serialization
# ==============================================================================


    def to_dict(self) -> MetricPayload:

        return {

            "name": self.name,

            "value": self.value,

            "metric_type": self.metric_type.value,

            "unit": self.unit.value,

            "state": self.state.to_dict(),

            "labels": self._labels.to_dict(),

            "attributes": self._attributes.to_dict(),

            "annotations": self._annotations.to_dict(),

            "tags": self._tags.to_dict(),

            "hooks": self._hooks.to_dict(),


            "created_at": self.created_at,

            "updated_at": self.updated_at,

            "version": self.version,

        }



    @classmethod
    def from_dict(
        cls,
        data: MetricPayload,
    ) -> "Metric":

        return cls(

            name=data["name"],

            value=data["value"],

            metric_type=MetricType(
                data["metric_type"]
            ),

            unit=MetricUnit(
                data["unit"]
            ),

            state=MetricState.from_dict(
                data["state"]
            ),


            _labels=MetricLabels.from_dict(
                data.get(
                    "labels",
                    {},
                )
            ),


            _attributes=MetricAttributes.from_dict(
                data.get(
                    "attributes",
                    {},
                )
            ),


            _annotations=MetricAnnotations.from_dict(
                data.get(
                    "annotations",
                    {},
                )
            ),


            _tags=MetricTags.from_dict(
                data.get(
                    "tags",
                    [],
                )
            ),


            _hooks=MetricHooks.from_dict(
                data.get(
                    "hooks",
                    {},
                )
            ),


        )



    def to_json(self) -> str:

        return json.dumps(

            self.to_dict(),

            ensure_ascii=False,

            sort_keys=True,

        )



    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "Metric":

        return cls.from_dict(
            json.loads(payload)
        )



# ==============================================================================
# Part 14. Copy
# ==============================================================================


    def copy(self) -> "Metric":

        return self.clone()



    def clone(self) -> "Metric":

        return Metric(

            name=self.name,

            value=self.value,

            metric_type=self.metric_type,

            unit=self.unit,


            state=self.state.clone(),


            _labels=self._labels.clone(),

            _attributes=self._attributes.clone(),

            _annotations=self._annotations.clone(),

            _tags=self._tags.clone(),

            _hooks=self._hooks.clone(),

        )



# ==============================================================================
# Part 15. Equality
# ==============================================================================


    def __eq__(
        self,
        other: object,
    ) -> bool:


        if not isinstance(
            other,
            Metric,
        ):
            return NotImplemented


        return (

            self.name == other.name

            and self.value == other.value

            and self.metric_type == other.metric_type

            and self.unit == other.unit

            and self.state == other.state

            and self._labels == other._labels

            and self._attributes == other._attributes

            and self._annotations == other._annotations

            and self._tags == other._tags

            and self._hooks == other._hooks

        )



    def __hash__(self) -> int:

        return hash(

            (

                self.name,

                self.metric_type,

                self.unit,

                self.value,

            )

        )



# ==============================================================================
# Part 16. Representation
# ==============================================================================


    def __repr__(self) -> str:

        return (

            f"{self.__class__.__name__}("

            f"name={self.name!r}, "

            f"value={self.value!r}, "

            f"type={self.metric_type.value!r}, "

            f"unit={self.unit.value!r})"

        )



    def __str__(self) -> str:

        return (

            f"{self.name}"

            f"={self.value}"

            f" [{self.unit.value}]"

        )



# ==============================================================================
# Part 17. Public API
# ==============================================================================


__all__ = [

    "METRIC_VERSION",

    "DEFAULT_METRIC_NAME",

    "DEFAULT_METRIC_VALUE",

    "DEFAULT_TIMESTAMP",

    "MetricType",

    "MetricUnit",

    "MetricError",

    "MetricValidationError",

    "MetricValue",

    "MetricPayload",

    "Metric",

]