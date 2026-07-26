"""
SciOS-NG Observability
======================

Metric Snapshot

Part 1 + Part 2
---------------

Foundation and Factory layer.

Responsibilities
-----------------

Part 1 Foundation
    - Immutable metric state
    - Snapshot identity
    - UUID
    - Timestamp
    - Versioning


Part 2 Factory
    - Create snapshot
    - Build from Metric
    - Restore from dictionary


Design Goals
------------

- Immutable
- Thread-safe
- Serializable
- Restore compatible
- Exporter friendly

"""

from __future__ import annotations


# ==========================================================
# Imports
# ==========================================================

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime
from datetime import timezone

from typing import Any
from typing import Mapping

from uuid import UUID
from uuid import uuid4


from .labels import MetricLabels
from .attributes import MetricAttributes
from .metadata import MetricMetadata


__all__ = [
    "MetricSnapshot",
]


# ==========================================================
# Constants
# ==========================================================


SNAPSHOT_VERSION = 1



# ==========================================================
# Helpers
# ==========================================================


def utc_now() -> datetime:
    """
    Return timezone aware UTC timestamp.
    """

    return datetime.now(
        timezone.utc
    )



def new_uuid() -> UUID:
    """
    Generate snapshot UUID.
    """

    return uuid4()



# ==========================================================
# Metric Snapshot
# ==========================================================


@dataclass(
    frozen=True,
    slots=True,
)
class MetricSnapshot:
    """
    Immutable runtime snapshot.

    A snapshot represents the state of
    one metric at one point in time.

    It is safe for:

    - threads
    - exporters
    - storage
    - distributed transport
    """


    # ------------------------------------------------------
    # Identity
    # ------------------------------------------------------


    uuid: UUID = field(
        default_factory=new_uuid
    )


    timestamp: datetime = field(
        default_factory=utc_now
    )


    version: int = SNAPSHOT_VERSION



    # ------------------------------------------------------
    # Metric Core State
    # ------------------------------------------------------


    name: str = ""


    metric_type: str = "gauge"


    value: Any = None



    # ------------------------------------------------------
    # Context
    # ------------------------------------------------------


    labels: MetricLabels = field(
        default_factory=MetricLabels
    )


    attributes: MetricAttributes = field(
        default_factory=MetricAttributes
    )


    metadata: MetricMetadata = field(
        default_factory=MetricMetadata
    )



    # ======================================================
    # Immutable Validation
    # ======================================================


    def __post_init__(self):
        """
        Normalize immutable state.
        """


        if not isinstance(
            self.uuid,
            UUID,
        ):
            raise TypeError(
                "uuid must be UUID"
            )


        if self.timestamp.tzinfo is None:

            object.__setattr__(
                self,
                "timestamp",
                self.timestamp.replace(
                    tzinfo=timezone.utc
                )
            )


        if self.version < 1:

            raise ValueError(
                "version must be >= 1"
            )


        if not self.name:

            raise ValueError(
                "Metric name cannot be empty"
            )



        # Defensive copies

        if not isinstance(
            self.labels,
            MetricLabels,
        ):

            object.__setattr__(
                self,
                "labels",
                MetricLabels(
                    self.labels
                )
            )


        if not isinstance(
            self.attributes,
            MetricAttributes,
        ):

            object.__setattr__(
                self,
                "attributes",
                MetricAttributes(
                    self.attributes
                )
            )


        if not isinstance(
            self.metadata,
            MetricMetadata,
        ):

            object.__setattr__(
                self,
                "metadata",
                MetricMetadata(
                    self.metadata
                )
            )



    # ======================================================
    # Part 2 Factory
    # ======================================================


    @classmethod
    def create(
        cls,
        *,
        name: str,
        value: Any,
        metric_type: str = "gauge",
        labels: Mapping[str, Any] | None = None,
        attributes: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
        version: int = SNAPSHOT_VERSION,
    ) -> "MetricSnapshot":
        """
        Create snapshot from raw values.
        """


        return cls(

            name=name,

            value=value,

            metric_type=metric_type,

            version=version,

            labels=MetricLabels(
                labels or {}
            ),

            attributes=MetricAttributes(
                attributes or {}
            ),

            metadata=MetricMetadata(
                metadata or {}
            ),
        )



    @classmethod
    def from_metric(
        cls,
        metric,
    ) -> "MetricSnapshot":
        """
        Create snapshot from Metric object.

        Restore contract:
        Metric must expose:

        - name
        - value
        - metric_type
        - labels
        - attributes
        - metadata
        """


        return cls.create(

            name=metric.name,

            value=metric.value,

            metric_type=(
                metric.metric_type
                if hasattr(
                    metric,
                    "metric_type",
                )
                else metric.descriptor.kind
            ),


            labels=(
                metric.labels.to_dict()
                if hasattr(
                    metric.labels,
                    "to_dict",
                )
                else dict(metric.labels)
            ),


            attributes=(
                metric.attributes.to_dict()
                if hasattr(
                    metric.attributes,
                    "to_dict",
                )
                else dict(metric.attributes)
            ),


            metadata=(
                metric.metadata.to_dict()
                if hasattr(
                    metric.metadata,
                    "to_dict",
                )
                else dict(metric.metadata)
            ),

        )



    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "MetricSnapshot":
        """
        Restore snapshot from dictionary.
        """


        return cls(

            uuid=UUID(
                data["uuid"]
            )
            if "uuid" in data
            else new_uuid(),


            timestamp=datetime.fromisoformat(
                data["timestamp"]
            )
            if "timestamp" in data
            else utc_now(),


            version=int(
                data.get(
                    "version",
                    SNAPSHOT_VERSION,
                )
            ),


            name=data["name"],


            metric_type=data.get(
                "metric_type",
                "gauge",
            ),


            value=data.get(
                "value"
            ),


            labels=MetricLabels(
                data.get(
                    "labels",
                    {},
                )
            ),


            attributes=MetricAttributes(
                data.get(
                    "attributes",
                    {},
                )
            ),


            metadata=MetricMetadata(
                data.get(
                    "metadata",
                    {},
                )
            ),
        )
    # ======================================================
    # Part 3 Properties API
    # ======================================================


    @property
    def name(
        self,
    ) -> str:
        """
        Metric name.

        Immutable descriptor identity.
        """

        return self._name


    @property
    def value(
        self,
    ) -> Any:
        """
        Current metric value.

        Snapshot values are immutable.
        """

        return self._value


    @property
    def metric_type(
        self,
    ) -> str:
        """
        Metric type.

        Examples:

        - counter
        - gauge
        - histogram
        - summary
        - timer
        """

        return self._metric_type


    @property
    def labels(
        self,
    ) -> MetricLabels:
        """
        Metric labels.

        Labels are frozen context dimensions.
        """

        return self._labels


    @property
    def attributes(
        self,
    ) -> MetricAttributes:
        """
        Runtime attributes.

        Attributes are immutable
        inside snapshot state.
        """

        return self._attributes


    @property
    def metadata(
        self,
    ) -> MetricMetadata:
        """
        Metric metadata.

        Contains semantic information:

        - description
        - unit
        - namespace
        - tags
        """

        return self._metadata


    @property
    def version(
        self,
    ) -> int:
        """
        Snapshot schema/runtime version.

        Used for:

        - compatibility
        - distributed synchronization
        - restore validation
        """

        return self._version
    # ======================================================
    # Part 4 Comparison API
    # ======================================================


    def equal(
        self,
        other: "MetricSnapshot",
    ) -> bool:
        """
        Compare two snapshots.

        Equality means complete immutable
        state equivalence.

        Parameters
        ----------
        other:
            Another MetricSnapshot.

        Returns
        -------
        bool
        """

        if not isinstance(
            other,
            MetricSnapshot,
        ):
            return False


        return (

            self._name
            == other._name

            and

            self._metric_type
            == other._metric_type

            and

            self._value
            == other._value

            and

            self._labels
            == other._labels

            and

            self._attributes
            == other._attributes

            and

            self._metadata
            == other._metadata

            and

            self._version
            == other._version

        )



    def newer_than(
        self,
        other: "MetricSnapshot",
    ) -> bool:
        """
        Check whether this snapshot
        is newer than another snapshot.

        Priority:

        1. version
        2. timestamp

        Used for:

        - replication
        - synchronization
        - conflict resolution
        """


        if not isinstance(
            other,
            MetricSnapshot,
        ):
            raise TypeError(
                "other must be MetricSnapshot"
            )


        if self._version > other._version:

            return True


        if self._version < other._version:

            return False


        return (
            self._timestamp
            > other._timestamp
        )



    def older_than(
        self,
        other: "MetricSnapshot",
    ) -> bool:
        """
        Check whether this snapshot
        is older than another snapshot.
        """


        if not isinstance(
            other,
            MetricSnapshot,
        ):
            raise TypeError(
                "other must be MetricSnapshot"
            )


        if self._version < other._version:

            return True


        if self._version > other._version:

            return False


        return (
            self._timestamp
            < other._timestamp
        )



    def diff(
        self,
        other: "MetricSnapshot",
    ) -> dict[str, Any]:
        """
        Compute state differences.

        Returns
        -------
        dict

        Example
        -------

        {
            "value":
                {
                    "old": 10,
                    "new": 20
                }
        }

        """

        if not isinstance(
            other,
            MetricSnapshot,
        ):
            raise TypeError(
                "other must be MetricSnapshot"
            )


        changes: dict[str, Any] = {}



        if self._name != other._name:

            changes["name"] = {

                "old":
                    self._name,

                "new":
                    other._name,

            }



        if self._metric_type != other._metric_type:

            changes["metric_type"] = {

                "old":
                    self._metric_type,

                "new":
                    other._metric_type,

            }



        if self._value != other._value:

            changes["value"] = {

                "old":
                    self._value,

                "new":
                    other._value,

            }



        if self._labels != other._labels:

            changes["labels"] = {

                "old":
                    self._labels.to_dict(),

                "new":
                    other._labels.to_dict(),

            }



        if self._attributes != other._attributes:

            changes["attributes"] = {

                "old":
                    self._attributes.to_dict(),

                "new":
                    other._attributes.to_dict(),

            }



        if self._metadata != other._metadata:

            changes["metadata"] = {

                "old":
                    self._metadata.to_dict(),

                "new":
                    other._metadata.to_dict(),

            }



        if self._version != other._version:

            changes["version"] = {

                "old":
                    self._version,

                "new":
                    other._version,

            }



        if self._timestamp != other._timestamp:

            changes["timestamp"] = {

                "old":
                    self._timestamp,

                "new":
                    other._timestamp,

            }



        return changes
    # ======================================================
    # Part 5 Serialization API
    # ======================================================


    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize snapshot into dictionary.

        The returned object is fully JSON compatible.
        """

        return {

            "uuid":
                str(self._uuid),


            "timestamp":
                self._timestamp.isoformat(),


            "version":
                self._version,


            "name":
                self._name,


            "metric_type":
                self._metric_type,


            "value":
                self._value,


            "labels":
                self._labels.to_dict(),


            "attributes":
                self._attributes.to_dict(),


            "metadata":
                self._metadata.to_dict(),

        }



    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricSnapshot":
        """
        Restore snapshot from dictionary.

        Parameters
        ----------
        data:
            Serialized snapshot dictionary.

        Returns
        -------
        MetricSnapshot
        """


        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "Snapshot data must be dict."
            )



        timestamp = data.get(
            "timestamp"
        )


        if isinstance(
            timestamp,
            str,
        ):

            timestamp = datetime.fromisoformat(
                timestamp
            )


        return cls(

            _uuid=UUID(
                data["uuid"]
            ),


            _timestamp=timestamp,


            _version=int(
                data.get(
                    "version",
                    1,
                )
            ),


            _name=data["name"],


            _metric_type=data.get(
                "metric_type",
                "gauge",
            ),


            _value=data.get(
                "value"
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


            _metadata=MetricMetadata.from_dict(
                data.get(
                    "metadata",
                    {},
                )
            ),

        )



    def to_json(
        self,
        *,
        indent: int | None = None,
    ) -> str:
        """
        Serialize snapshot into JSON string.

        Suitable for:

        - API response
        - logging
        - message bus
        - storage
        """


        return json.dumps(

            self.to_dict(),

            indent=indent,

            ensure_ascii=False,

            sort_keys=True,

            default=str,

        )



    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "MetricSnapshot":
        """
        Restore snapshot from JSON string.
        """


        if not isinstance(
            payload,
            str,
        ):
            raise TypeError(
                "JSON payload must be string."
            )


        data = json.loads(
            payload
        )


        return cls.from_dict(
            data
        )
    # ======================================================
    # Part 6 Export API
    # ======================================================


    def prometheus(
        self,
    ) -> str:
        """
        Export snapshot in Prometheus exposition format.

        Example:

        cpu_usage{host="node1"} 0.75

        """

        labels = self._labels.to_dict()


        label_string = ""


        if labels:

            label_string = "{"

            label_string += ",".join(

                f'{key}="{value}"'

                for key, value
                in sorted(
                    labels.items()
                )

            )

            label_string += "}"



        return (

            f"{self._name}"

            f"{label_string}"

            f" "

            f"{self._value}"

        )



    def otel(
        self,
    ) -> dict[str, Any]:
        """
        Export snapshot into
        OpenTelemetry compatible format.

        This avoids importing OpenTelemetry SDK.

        Returns
        -------
        dict
        """

        return {

            "name":
                self._name,


            "type":
                self._metric_type,


            "value":
                self._value,


            "timestamp":
                int(
                    self._timestamp.timestamp()
                    *
                    1_000_000_000
                ),


            "unit":
                self._metadata.get(
                    "unit",
                    "",
                ),


            "description":
                self._metadata.get(
                    "description",
                    "",
                ),


            "attributes":
                self._attributes.to_dict(),


            "labels":
                self._labels.to_dict(),


            "metadata":
                self._metadata.to_dict(),

        }



    def csv(
        self,
    ) -> list[Any]:
        """
        Export snapshot as CSV row.

        Suitable for:

        - csv.writer
        - batch export
        - archival storage

        """

        return [

            str(self._uuid),


            self._timestamp.isoformat(),


            self._version,


            self._name,


            self._metric_type,


            self._value,


            json.dumps(

                self._labels.to_dict(),

                ensure_ascii=False,

            ),


            json.dumps(

                self._attributes.to_dict(),

                ensure_ascii=False,

            ),


            json.dumps(

                self._metadata.to_dict(),

                ensure_ascii=False,

            ),

        ]



    def dataframe(
        self,
    ) -> dict[str, Any]:
        """
        Export snapshot into
        Pandas DataFrame compatible row.

        No pandas dependency required.

        """

        row = {

            "uuid":
                str(self._uuid),


            "timestamp":
                self._timestamp,


            "version":
                self._version,


            "name":
                self._name,


            "metric_type":
                self._metric_type,


            "value":
                self._value,

        }



        for key, value in self._labels.items():

            row[
                f"label.{key}"
            ] = value



        for key, value in self._attributes.items():

            row[
                f"attribute.{key}"
            ] = value



        for key, value in self._metadata.items():

            row[
                f"metadata.{key}"
            ] = value



        return row
    # ======================================================
    # Part 7 Diagnostics API
    # ======================================================


    def validate(
        self,
    ) -> None:
        """
        Validate snapshot integrity.

        Raises
        ------
        ValueError
            If snapshot is invalid.

        TypeError
            If snapshot contains invalid types.
        """


        # ----------------------------------------------
        # Identity validation
        # ----------------------------------------------

        if not isinstance(
            self._uuid,
            UUID,
        ):
            raise TypeError(
                "Snapshot UUID must be UUID."
            )


        # ----------------------------------------------
        # Name validation
        # ----------------------------------------------

        if not isinstance(
            self._name,
            str,
        ):
            raise TypeError(
                "Metric name must be string."
            )


        if not self._name.strip():

            raise ValueError(
                "Metric name cannot be empty."
            )


        # ----------------------------------------------
        # Timestamp validation
        # ----------------------------------------------

        if not isinstance(
            self._timestamp,
            datetime,
        ):
            raise TypeError(
                "Timestamp must be datetime."
            )


        if self._timestamp.tzinfo is None:

            raise ValueError(
                "Timestamp must contain timezone."
            )


        # ----------------------------------------------
        # Version validation
        # ----------------------------------------------

        if not isinstance(
            self._version,
            int,
        ):
            raise TypeError(
                "Version must be integer."
            )


        if self._version < 1:

            raise ValueError(
                "Version must be >= 1."
            )


        # ----------------------------------------------
        # Metric type validation
        # ----------------------------------------------

        if not isinstance(
            self._metric_type,
            str,
        ):

            raise TypeError(
                "Metric type must be string."
            )


        if not self._metric_type:

            raise ValueError(
                "Metric type cannot be empty."
            )


        # ----------------------------------------------
        # Component validation
        # ----------------------------------------------

        self._labels.validate()

        self._attributes.validate()

        self._metadata.validate()



    @property
    def valid(
        self,
    ) -> bool:
        """
        Return validation status.

        Returns
        -------
        bool
        """

        try:

            self.validate()

            return True


        except Exception:

            return False



    def checksum(
        self,
    ) -> str:
        """
        Generate SHA-256 checksum.

        Used for:

        - integrity checking
        - storage verification
        - distributed synchronization
        """

        payload = json.dumps(

            self.to_dict(),

            sort_keys=True,

            ensure_ascii=False,

            default=str,

        )


        return hashlib.sha256(

            payload.encode(
                "utf-8"
            )

        ).hexdigest()



    def fingerprint(
        self,
    ) -> str:
        """
        Generate stable metric fingerprint.

        Timestamp and UUID are ignored.

        Two snapshots of the same metric schema
        have the same fingerprint.

        Useful for:

        - deduplication
        - indexing
        - registry lookup
        """


        payload = {

            "name":
                self._name,


            "metric_type":
                self._metric_type,


            "labels":
                self._labels.to_dict(),


            "attributes":
                self._attributes.to_dict(),

        }


        encoded = json.dumps(

            payload,

            sort_keys=True,

            ensure_ascii=False,

            default=str,

        )


        return hashlib.sha256(

            encoded.encode(
                "utf-8"
            )

        ).hexdigest()



    def inspect(
        self,
    ) -> dict[str, Any]:
        """
        Return production diagnostics.

        Designed for:

        - debugging
        - dashboards
        - health endpoints
        - logging
        """


        return {

            "identity": {

                "uuid":
                    str(self._uuid),

                "fingerprint":
                    self.fingerprint(),

            },


            "metric": {

                "name":
                    self._name,

                "type":
                    self._metric_type,

                "value_type":
                    type(
                        self._value
                    ).__name__,

            },


            "runtime": {

                "version":
                    self._version,

                "timestamp":
                    self._timestamp.isoformat(),

            },


            "collections": {

                "labels":
                    len(
                        self._labels
                    ),

                "attributes":
                    len(
                        self._attributes
                    ),

                "metadata":
                    len(
                        self._metadata
                    ),

            },


            "integrity": {

                "valid":
                    self.valid,

                "checksum":
                    self.checksum(),

            },

        }
    # ======================================================
    # Part 8. Utilities
    # ======================================================

    def clone(
        self,
        *,
        new_uuid: bool = False,
        new_timestamp: bool = False,
        version_bump: bool = False,
    ) -> "MetricSnapshot":
        """
        Clone this snapshot.

        Parameters
        ----------
        new_uuid
            Generate a new UUID.

        new_timestamp
            Use current UTC time.

        version_bump
            Increment version.

        Returns
        -------
        MetricSnapshot
        """

        return MetricSnapshot(

            _uuid=(
                uuid4()
                if new_uuid
                else self._uuid
            ),

            _timestamp=(
                datetime.now(timezone.utc)
                if new_timestamp
                else self._timestamp
            ),

            _version=(
                self._version + 1
                if version_bump
                else self._version
            ),

            _name=self._name,

            _metric_type=self._metric_type,

            _value=copy.deepcopy(
                self._value
            ),

            _labels=self._labels.copy(),

            _attributes=self._attributes.copy(),

            _metadata=self._metadata.copy(),
        )


    def copy(
        self,
    ) -> "MetricSnapshot":
        """
        Return an equivalent snapshot.

        Equivalent to clone().
        """

        return self.clone()


    def replace(
        self,
        *,
        name: str | None = None,
        value: Any = None,
        metric_type: str | None = None,
        labels: MetricLabels | None = None,
        attributes: MetricAttributes | None = None,
        metadata: MetricMetadata | None = None,
        timestamp: datetime | None = None,
        version: int | None = None,
        uuid: UUID | None = None,
    ) -> "MetricSnapshot":
        """
        Return a modified snapshot.

        Original snapshot remains unchanged.
        """

        return MetricSnapshot(

            _uuid=(
                uuid
                if uuid is not None
                else self._uuid
            ),

            _timestamp=(
                timestamp
                if timestamp is not None
                else self._timestamp
            ),

            _version=(
                version
                if version is not None
                else self._version
            ),

            _name=(
                name
                if name is not None
                else self._name
            ),

            _metric_type=(
                metric_type
                if metric_type is not None
                else self._metric_type
            ),

            _value=(
                self._value
                if value is None
                else value
            ),

            _labels=(
                labels.copy()
                if labels is not None
                else self._labels.copy()
            ),

            _attributes=(
                attributes.copy()
                if attributes is not None
                else self._attributes.copy()
            ),

            _metadata=(
                metadata.copy()
                if metadata is not None
                else self._metadata.copy()
            ),
        )


    def merge(
        self,
        other: "MetricSnapshot",
    ) -> "MetricSnapshot":
        """
        Merge another snapshot into this snapshot.

        The current snapshot keeps its identity.
        Runtime information is taken from 'other'.

        Parameters
        ----------
        other
            Snapshot to merge.

        Returns
        -------
        MetricSnapshot
        """

        if not isinstance(
            other,
            MetricSnapshot,
        ):
            raise TypeError(
                "other must be MetricSnapshot."
            )

        if self._name != other.name:
            raise ValueError(
                "Cannot merge snapshots with different names."
            )

        merged_labels = self._labels.copy()
        merged_labels.update(
            other.labels.to_dict()
        )

        merged_attributes = self._attributes.copy()
        merged_attributes.update(
            other.attributes.to_dict()
        )

        merged_metadata = self._metadata.copy()
        merged_metadata.update(
            other.metadata.to_dict()
        )

        return MetricSnapshot(

            _uuid=self._uuid,

            _timestamp=max(
                self._timestamp,
                other.timestamp,
            ),

            _version=max(
                self._version,
                other.version,
            ),

            _name=self._name,

            _metric_type=self._metric_type,

            _value=other.value,

            _labels=merged_labels,

            _attributes=merged_attributes,

            _metadata=merged_metadata,
        )                                                