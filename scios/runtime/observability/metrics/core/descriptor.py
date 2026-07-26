"""
SciOS Observability
===================

Metric descriptor model.

Defines immutable schema information
for observability metrics.

A descriptor describes:

- metric identity
- metric type
- value type
- unit
- labels
- attributes
- metadata

It does NOT store runtime values.

Compatible with:

- OpenTelemetry concepts
- Prometheus descriptors
- Distributed metric systems
"""


from __future__ import annotations


import json
import time
import uuid

from enum import Enum
from copy import deepcopy
from threading import RLock

from typing import Any
from typing import Mapping


from .validation import MetricValidator
from .metadata import MetricMetadata


__all__ = [
    "MetricType",
    "ValueType",
    "MetricDescriptor",
]



# ======================================================
# Constants
# ======================================================


DESCRIPTOR_VERSION = "1.0"



# ======================================================
# Enums
# ======================================================


class MetricType(str, Enum):

    COUNTER = "counter"

    UP_DOWN_COUNTER = (
        "up_down_counter"
    )

    GAUGE = "gauge"

    HISTOGRAM = "histogram"

    SUMMARY = "summary"

    TIMER = "timer"

    OBSERVABLE_COUNTER = (
        "observable_counter"
    )

    OBSERVABLE_GAUGE = (
        "observable_gauge"
    )



class ValueType(str, Enum):

    INTEGER = "integer"

    DOUBLE = "double"

    HISTOGRAM = "histogram"

    SUMMARY = "summary"



# ======================================================
# MetricDescriptor
# ======================================================


class MetricDescriptor:
    """
    Metric schema descriptor.

    Example
    -------

    descriptor = MetricDescriptor(
        name="cpu_usage",
        metric_type="gauge",
        unit="percent",
        description="CPU utilization",
    )

    """


    def __init__(
        self,
        name: str,
        metric_type: str | MetricType,
        *,
        value_type: str | ValueType | None = None,
        unit: str | None = None,
        description: str | None = None,
        labels: Mapping[str, Any] | None = None,
        attributes: Mapping[str, Any] | None = None,
        metadata: MetricMetadata | Mapping[str, Any] | None = None,
    ):
        """
        Create metric descriptor.
        """


        self._lock = RLock()


        self._id = str(
            uuid.uuid4()
        )


        self._created_at = time.time()


        self._version = (
            DESCRIPTOR_VERSION
        )


        self._frozen = False



        # --------------------------------
        # Validate identity
        # --------------------------------

        self._name = (
            MetricValidator.validate_name(
                name
            )
        )


        self._type = (
            MetricValidator.validate_metric_type(
                metric_type
            )
        )



        # --------------------------------
        # Value type
        # --------------------------------


        if value_type is None:

            value_type = (
                self._infer_value_type()
            )


        self._value_type = (
            MetricValidator.validate_value_type(
                value_type,
                metric_type=self._type,
            )
        )



        # --------------------------------
        # Optional schema
        # --------------------------------


        self._unit = (

            MetricValidator.validate_unit(
                unit
            )
            if unit
            else None

        )


        self._description = (

            MetricValidator.validate_description(
                description
            )
            if description
            else None

        )



        self._labels = (
            MetricValidator.validate_labels(
                labels
            )
        )


        self._attributes = (
            MetricValidator.validate_attributes(
                attributes
            )
        )



        if isinstance(
            metadata,
            MetricMetadata,
        ):

            self._metadata = (
                metadata
            )

        else:

            self._metadata = (
                MetricMetadata(
                    values=metadata or {}
                )
            )


    # ==================================================
    # Internal helpers
    # ==================================================


    def _infer_value_type(
        self,
    ) -> str:
        """
        Infer default value type.
        """

        defaults = {

            "counter":
                "integer",

            "up_down_counter":
                "integer",

            "gauge":
                "double",

            "histogram":
                "double",

            "summary":
                "double",

            "timer":
                "double",

            "observable_counter":
                "integer",

            "observable_gauge":
                "double",

        }


        return defaults.get(
            self._type,
            "double",
        )
    # ==================================================
    # Part 2B. Properties API
    # ==================================================


    @property
    def id(
        self,
    ) -> str:
        """
        Unique descriptor UUID.
        """

        return self._id



    @property
    def name(
        self,
    ) -> str:
        """
        Metric name.
        """

        return self._name



    @property
    def metric_type(
        self,
    ) -> MetricType:
        """
        Metric type.

        Example:

        counter
        gauge
        histogram
        """

        return self._type



    @property
    def value_type(
        self,
    ) -> ValueType:
        """
        Runtime value type.
        """

        return self._value_type



    @property
    def unit(
        self,
    ) -> str | None:
        """
        Metric unit.

        Example:

        seconds
        bytes
        percent
        """

        return self._unit



    @property
    def description(
        self,
    ) -> str | None:
        """
        Human readable description.
        """

        return self._description



    @property
    def labels(
        self,
    ) -> Mapping[str, Any]:
        """
        Metric labels.

        Returns copy to prevent
        accidental mutation.
        """

        return dict(
            self._labels
        )



    @property
    def attributes(
        self,
    ) -> Mapping[str, Any]:
        """
        Metric attributes.
        """

        return dict(
            self._attributes
        )



    @property
    def metadata(
        self,
    ) -> MetricMetadata:
        """
        Metric metadata object.
        """

        return self._metadata



    @property
    def frozen(
        self,
    ) -> bool:
        """
        Descriptor mutation state.
        """

        return self._frozen



    @property
    def version(
        self,
    ) -> str:
        """
        Descriptor schema version.
        """

        return self._version
    # ==================================================
    # Part 3. Metadata API
    # ==================================================


    def _ensure_mutable(
        self,
    ):
        """
        Ensure descriptor can be modified.
        """

        if self._frozen:

            from .exceptions import (
                MetricFrozenError
            )

            raise MetricFrozenError(
                "MetricDescriptor is frozen."
            )



    # --------------------------------------------------
    # Labels
    # --------------------------------------------------


    def set_label(
        self,
        key: str,
        value: Any,
    ) -> "MetricDescriptor":
        """
        Add or update metric label.

        Example
        -------

        descriptor.set_label(
            "region",
            "asia"
        )
        """

        self._ensure_mutable()


        validated = (
            MetricValidator.validate_label_key(
                key
            )
        )


        value = (
            MetricValidator.validate_label_value(
                value
            )
        )


        with self._lock:

            self._labels[validated] = value


        return self



    def remove_label(
        self,
        key: str,
    ) -> Any:
        """
        Remove metric label.
        """

        self._ensure_mutable()


        key = (
            MetricValidator.validate_label_key(
                key
            )
        )


        with self._lock:

            return self._labels.pop(
                key,
                None,
            )



    def has_label(
        self,
        key: str,
    ) -> bool:
        """
        Check label existence.
        """

        key = (
            MetricValidator.validate_label_key(
                key
            )
        )


        with self._lock:

            return key in self._labels



    def update_labels(
        self,
        labels: Mapping[str, Any],
    ) -> "MetricDescriptor":
        """
        Update multiple labels.
        """

        self._ensure_mutable()


        validated = (
            MetricValidator.validate_labels(
                labels
            )
        )


        with self._lock:

            self._labels.update(
                validated
            )


        return self



    # --------------------------------------------------
    # Attributes
    # --------------------------------------------------


    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> "MetricDescriptor":
        """
        Add or update attribute.
        """

        self._ensure_mutable()


        key = (
            MetricValidator.validate_attribute_key(
                key
            )
        )


        value = (
            MetricValidator.validate_attribute_value(
                value
            )
        )


        with self._lock:

            self._attributes[key] = value


        return self



    def remove_attribute(
        self,
        key: str,
    ) -> Any:
        """
        Remove attribute.
        """

        self._ensure_mutable()


        key = (
            MetricValidator.validate_attribute_key(
                key
            )
        )


        with self._lock:

            return self._attributes.pop(
                key,
                None,
            )



    def update_attributes(
        self,
        attributes: Mapping[str, Any],
    ) -> "MetricDescriptor":
        """
        Update multiple attributes.
        """

        self._ensure_mutable()


        validated = (
            MetricValidator.validate_attributes(
                attributes
            )
        )


        with self._lock:

            self._attributes.update(
                validated
            )


        return self



    # --------------------------------------------------
    # Metadata object
    # --------------------------------------------------


    def update_metadata(
        self,
        values: Mapping[str, Any],
    ) -> "MetricDescriptor":
        """
        Update attached MetricMetadata.
        """

        self._ensure_mutable()


        with self._lock:

            self._metadata.update(
                values
            )


        return self



    def replace_metadata(
        self,
        metadata: MetricMetadata | Mapping[str, Any],
    ) -> "MetricDescriptor":
        """
        Replace metadata object.
        """

        self._ensure_mutable()


        if isinstance(
            metadata,
            MetricMetadata,
        ):

            new_metadata = metadata


        else:

            new_metadata = MetricMetadata(
                values=metadata
            )


        with self._lock:

            self._metadata = new_metadata


        return self
    # ==================================================
    # Part 4. Lifecycle API
    # ==================================================


    def freeze(
        self,
    ) -> "MetricDescriptor":
        """
        Freeze descriptor schema.

        After freeze:

        - labels cannot change
        - attributes cannot change
        - metadata cannot change
        - schema is immutable

        Used by:

        - Registry
        - Exporter
        - Runtime
        """


        with self._lock:

            self._frozen = True


            # Freeze metadata too

            if self._metadata:

                self._metadata.freeze()


        return self



    def unfreeze(
        self,
    ) -> "MetricDescriptor":
        """
        Unfreeze descriptor.

        Allows schema mutation.
        """


        with self._lock:

            self._frozen = False


            if self._metadata:

                self._metadata.unfreeze()


        return self



    def copy(
        self,
    ) -> "MetricDescriptor":
        """
        Create shallow copy.

        Behaviour:

        - new descriptor UUID
        - shared nested references
        - same schema values

        Suitable for:
        - temporary modification
        """


        with self._lock:


            descriptor = MetricDescriptor(

                name=self._name,

                metric_type=self._type,

                value_type=self._value_type,

                unit=self._unit,

                description=self._description,

                labels=self._labels,

                attributes=self._attributes,

                metadata=self._metadata,

            )


            descriptor._version = (
                self._version
            )


            descriptor._frozen = (
                self._frozen
            )


        return descriptor



    def clone(
        self,
    ) -> "MetricDescriptor":
        """
        Create deep copy.

        Used for:

        - snapshots
        - distributed replication
        - checkpoint
        """


        with self._lock:


            descriptor = MetricDescriptor(

                name=self._name,

                metric_type=self._type,

                value_type=self._value_type,

                unit=self._unit,

                description=self._description,

                labels=deepcopy(
                    self._labels
                ),

                attributes=deepcopy(
                    self._attributes
                ),

                metadata=self._metadata.clone(),

            )


            descriptor._version = (
                self._version
            )


            descriptor._created_at = (
                self._created_at
            )


            descriptor._frozen = (
                self._frozen
            )


        return descriptor
    # ==================================================
    # Part 5. Serialization API
    # ==================================================


    def to_dict(
        self,
        *,
        sanitize: bool = False,
    ) -> dict[str, Any]:
        """
        Serialize descriptor into dictionary.

        Schema:

        {
            id,
            version,
            name,
            metric_type,
            value_type,
            unit,
            description,
            labels,
            attributes,
            metadata,
            frozen
        }
        """


        with self._lock:


            result = {

                "id":
                    self._id,


                "version":
                    self._version,


                "created_at":
                    self._created_at,


                "name":
                    self._name,


                "metric_type":
                    self._type.value
                    if isinstance(
                        self._type,
                        Enum
                    )
                    else self._type,


                "value_type":
                    self._value_type.value
                    if isinstance(
                        self._value_type,
                        Enum
                    )
                    else self._value_type,


                "unit":
                    self._unit,


                "description":
                    self._description,


                "labels":
                    deepcopy(
                        self._labels
                    ),


                "attributes":
                    deepcopy(
                        self._attributes
                    ),


                "metadata":
                    self._metadata.to_dict(),


                "frozen":
                    self._frozen,

            }



        if sanitize:

            result = (
                MetricValidator.sanitize(
                    result
                )
            )


        return result



    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "MetricDescriptor":
        """
        Restore descriptor from dictionary.
        """


        data = dict(
            data
        )


        descriptor = cls(

            name=data["name"],


            metric_type=(
                data.get(
                    "metric_type",
                    "gauge",
                )
            ),


            value_type=(
                data.get(
                    "value_type"
                )
            ),


            unit=data.get(
                "unit"
            ),


            description=data.get(
                "description"
            ),


            labels=data.get(
                "labels",
                {},
            ),


            attributes=data.get(
                "attributes",
                {},
            ),


            metadata=data.get(
                "metadata",
                {},
            ),

        )



        # Restore identity

        descriptor._id = (
            data.get(
                "id",
                descriptor._id,
            )
        )


        descriptor._version = (
            data.get(
                "version",
                descriptor._version,
            )
        )


        descriptor._created_at = (
            data.get(
                "created_at",
                descriptor._created_at,
            )
        )


        descriptor._frozen = (
            data.get(
                "frozen",
                False,
            )
        )


        return descriptor



    def to_json(
        self,
        *,
        indent: int | None = None,
        sanitize: bool = False,
    ) -> str:
        """
        Serialize descriptor to JSON.

        Used by:

        - API
        - storage
        - transport
        """


        return json.dumps(

            self.to_dict(
                sanitize=sanitize
            ),

            indent=indent,

            sort_keys=True,

            default=str,

        )



    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "MetricDescriptor":
        """
        Deserialize descriptor from JSON.
        """


        data = json.loads(
            payload
        )


        return cls.from_dict(
            data
        )
    # ==================================================
    # Part 6. Diagnostics API
    # ==================================================


    def validate(
        self,
        *,
        strict: bool = True,
    ) -> bool:
        """
        Validate descriptor schema.

        Checks:

        - metric name
        - metric type
        - value type
        - labels
        - attributes
        - metadata
        """


        try:

            MetricValidator.validate_name(
                self._name
            )


            MetricValidator.validate_metric_type(
                self._type
            )


            MetricValidator.validate_value_type(
                self._value_type,
                metric_type=self._type,
            )


            MetricValidator.validate_labels(
                self._labels
            )


            MetricValidator.validate_attributes(
                self._attributes
            )


            self._metadata.validate(
                strict=True
            )


            return True



        except Exception:


            if strict:

                raise


            return False



    def statistics(
        self,
    ) -> dict[str, Any]:
        """
        Return descriptor statistics.

        Example:

        {
            "name": "cpu_usage",
            "type": "gauge",
            "labels": 2,
            "attributes": 3,
            "frozen": True
        }

        """


        with self._lock:

            return {

                "id":
                    self._id,


                "name":
                    self._name,


                "metric_type":
                    (
                        self._type.value
                        if isinstance(
                            self._type,
                            Enum
                        )
                        else self._type
                    ),


                "value_type":
                    (
                        self._value_type.value
                        if isinstance(
                            self._value_type,
                            Enum
                        )
                        else self._value_type
                    ),


                "unit":
                    self._unit,


                "labels":
                    len(
                        self._labels
                    ),


                "attributes":
                    len(
                        self._attributes
                    ),


                "metadata":

                    self._metadata.statistics(),


                "frozen":
                    self._frozen,


                "version":
                    self._version,


                "created_at":
                    self._created_at,

            }



    def dump(
        self,
        *,
        pretty: bool = True,
        sanitize: bool = True,
    ) -> str:
        """
        Human readable descriptor dump.

        Used by:

        - CLI
        - logs
        - debugging
        """


        data = self.to_dict(
            sanitize=sanitize
        )


        if pretty:

            return json.dumps(
                data,
                indent=2,
                sort_keys=True,
                default=str,
            )


        return json.dumps(
            data,
            default=str,
        )



    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """


        metric_type = (

            self._type.value

            if isinstance(
                self._type,
                Enum
            )

            else self._type

        )


        return (

            "MetricDescriptor("
            f"name={self._name!r}, "
            f"type={metric_type!r}, "
            f"labels={len(self._labels)}, "
            f"attributes={len(self._attributes)}, "
            f"frozen={self._frozen}"
            ")"

        )                                        