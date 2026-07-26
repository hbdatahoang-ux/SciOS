"""
SciOS Observability
===================

Metric metadata model.

This module provides metadata storage
for observability objects.

Metadata is used by:

- MetricDescriptor
- MetricRegistry
- Exporters
- Diagnostics
- Runtime inspection
- Distributed systems

Design goals:

- immutable friendly
- validation aware
- serialization ready
- thread safe
- exporter compatible
"""

from __future__ import annotations


import json
import uuid
import time

from copy import deepcopy
from threading import RLock

from typing import Any
from typing import Mapping
from typing import MutableMapping
from typing import Iterator


from .validation import MetricValidator


__all__ = [
    "MetricMetadata",
]


# ======================================================
# Constants
# ======================================================


_METADATA_VERSION = "1.0"

_MAX_METADATA_SIZE = 256


# ======================================================
# Type aliases
# ======================================================


MetadataDict = dict[str, Any]


# ======================================================
# MetricMetadata
# ======================================================


class MetricMetadata:
    """
    Metadata container for metrics.

    Example
    -------

    metadata = MetricMetadata(
        values={
            "owner": "SciOS",
            "domain": "physics",
        },
        tags=[
            "gpu",
            "distributed",
        ],
    )
    """

    # --------------------------------------------------
    # Construction
    # --------------------------------------------------

    def __init__(
        self,
        values: Mapping[str, Any] | None = None,
        *,
        tags: list[str] | tuple[str, ...] | None = None,
        annotations: Mapping[str, str] | None = None,
        owner: str | None = None,
        component: str | None = None,
        version: str | None = None,
    ):
        """
        Create metadata object.
        """


        self._lock = RLock()

        self._id = str(
            uuid.uuid4()
        )

        self._created_at = time.time()


        self._frozen = False


        self._values: MetadataDict = (
            MetricValidator.validate_metadata(
                values or {}
            )
        )


        self._tags = (
            MetricValidator.validate_tags(
                tags
            )
        )


        self._annotations = (
            MetricValidator.validate_annotations(
                annotations
            )
        )


        self._owner = owner

        self._component = component

        self._version = (
            version
            or
            _METADATA_VERSION
        )


    # --------------------------------------------------
    # Factory methods
    # --------------------------------------------------


    @classmethod
    def empty(
        cls,
    ) -> "MetricMetadata":
        """
        Create empty metadata.
        """

        return cls()



    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "MetricMetadata":
        """
        Create metadata from dictionary.
        """

        data = dict(data)


        return cls(
            values=data.get(
                "values",
                {},
            ),
            tags=data.get(
                "tags"
            ),
            annotations=data.get(
                "annotations"
            ),
            owner=data.get(
                "owner"
            ),
            component=data.get(
                "component"
            ),
            version=data.get(
                "version"
            ),
        )



    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "MetricMetadata":
        """
        Deserialize JSON.
        """

        return cls.from_dict(
            json.loads(payload)
        )


    # --------------------------------------------------
    # Basic properties
    # --------------------------------------------------


    @property
    def id(self) -> str:

        return self._id


    @property
    def values(self) -> Mapping[str, Any]:

        return dict(
            self._values
        )


    @property
    def tags(self) -> tuple[str, ...]:

        return self._tags


    @property
    def annotations(self) -> Mapping[str, str]:

        return dict(
            self._annotations
        )


    @property
    def owner(self) -> str | None:

        return self._owner


    @property
    def component(self) -> str | None:

        return self._component


    @property
    def version(self) -> str:

        return self._version


    @property
    def frozen(self) -> bool:

        return self._frozen
    # ==================================================
    # Part 2. CRUD API
    # ==================================================


    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get metadata value.

        Example
        -------

        metadata.get(
            "owner"
        )
        """

        key = MetricValidator.normalize_identifier(
            key,
            field="metadata_key",
        )


        with self._lock:

            return self._values.get(
                key,
                default,
            )



    def set(
        self,
        key: str,
        value: Any,
    ) -> "MetricMetadata":
        """
        Set metadata value.

        Raises
        ------

        MetricFrozenError
            If metadata is frozen.
        """

        self._ensure_mutable()


        key = MetricValidator.normalize_identifier(
            key,
            field="metadata_key",
        )


        value = MetricValidator.validate_metadata_value(
            value,
            field=f"metadata.{key}",
        )


        with self._lock:

            self._values[key] = value


        return self



    def update(
        self,
        values: Mapping[str, Any],
    ) -> "MetricMetadata":
        """
        Update multiple metadata entries.

        Example
        -------

        metadata.update(
            {
                "service": "kernel",
                "region": "asia"
            }
        )
        """

        self._ensure_mutable()


        validated = (
            MetricValidator.validate_metadata(
                values
            )
        )


        with self._lock:

            self._values.update(
                validated
            )


        return self



    def remove(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Remove metadata key.

        Returns removed value.
        """

        self._ensure_mutable()


        key = MetricValidator.normalize_identifier(
            key,
            field="metadata_key",
        )


        with self._lock:

            return self._values.pop(
                key,
                default,
            )



    def clear(
        self,
    ) -> "MetricMetadata":
        """
        Remove all metadata values.
        """

        self._ensure_mutable()


        with self._lock:

            self._values.clear()


        return self



    def contains(
        self,
        key: str,
    ) -> bool:
        """
        Check key existence.

        Equivalent to:

            key in metadata
        """

        key = MetricValidator.normalize_identifier(
            key,
            field="metadata_key",
        )


        with self._lock:

            return key in self._values



    def keys(
        self,
    ) -> tuple[str, ...]:
        """
        Return metadata keys.
        """

        with self._lock:

            return tuple(
                self._values.keys()
            )



    def items(
        self,
    ) -> tuple[tuple[str, Any], ...]:
        """
        Return metadata items.
        """

        with self._lock:

            return tuple(
                self._values.items()
            )
    # ==================================================
    # Part 3. Lifecycle API
    # ==================================================


    def freeze(
        self,
    ) -> "MetricMetadata":
        """
        Freeze metadata.

        After freezing:

        - set()
        - update()
        - remove()
        - clear()

        are disabled.

        Used for:

        - production descriptors
        - immutable snapshots
        - distributed sharing
        """

        with self._lock:

            self._frozen = True


        return self



    def unfreeze(
        self,
    ) -> "MetricMetadata":
        """
        Unfreeze metadata.

        Allows mutation again.
        """

        with self._lock:

            self._frozen = False


        return self



    def copy(
        self,
    ) -> "MetricMetadata":
        """
        Create shallow copy.

        Metadata values are copied,
        but nested objects are shared.
        """

        with self._lock:

            new = MetricMetadata(
                values=self._values,
                tags=self._tags,
                annotations=self._annotations,
                owner=self._owner,
                component=self._component,
                version=self._version,
            )


            new._frozen = self._frozen


        return new



    def clone(
        self,
    ) -> "MetricMetadata":
        """
        Create deep copy.

        Suitable for:

        - snapshots
        - checkpoints
        - distributed transfer
        """

        with self._lock:

            new = MetricMetadata(
                values=deepcopy(
                    self._values
                ),

                tags=deepcopy(
                    self._tags
                ),

                annotations=deepcopy(
                    self._annotations
                ),

                owner=self._owner,

                component=self._component,

                version=self._version,
            )


            new._created_at = (
                self._created_at
            )

            new._frozen = (
                self._frozen
            )


        return new
    # ==================================================
    # Part 4. Serialization API
    # ==================================================


    def to_dict(
        self,
        *,
        sanitize: bool = False,
    ) -> dict[str, Any]:
        """
        Serialize metadata into dictionary.

        Output schema:

        {
            "id": "...",
            "version": "...",
            "created_at": 123456789,

            "values": {},

            "tags": [],

            "annotations": {},

            "owner": "...",

            "component": "...",

            "frozen": false
        }

        """

        with self._lock:

            result = {

                "id": self._id,

                "version": self._version,

                "created_at":
                    self._created_at,

                "values":
                    deepcopy(
                        self._values
                    ),

                "tags":
                    list(
                        self._tags
                    ),

                "annotations":
                    deepcopy(
                        self._annotations
                    ),

                "owner":
                    self._owner,

                "component":
                    self._component,

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



    def to_json(
        self,
        *,
        indent: int | None = None,
        sanitize: bool = False,
    ) -> str:
        """
        Serialize metadata to JSON string.

        Compatible with:

        - REST API
        - logging
        - storage
        """

        return json.dumps(
            self.to_dict(
                sanitize=sanitize
            ),
            indent=indent,
            default=str,
            sort_keys=True,
        )



    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "MetricMetadata":
        """
        Restore metadata from JSON.

        """

        data = json.loads(
            payload
        )


        metadata = cls(
            values=data.get(
                "values",
                {},
            ),

            tags=data.get(
                "tags",
                (),
            ),

            annotations=data.get(
                "annotations",
                {},
            ),

            owner=data.get(
                "owner"
            ),

            component=data.get(
                "component"
            ),

            version=data.get(
                "version"
            ),
        )


        metadata._id = (
            data.get(
                "id",
                metadata._id,
            )
        )


        metadata._created_at = (
            data.get(
                "created_at",
                metadata._created_at,
            )
        )


        metadata._frozen = (
            data.get(
                "frozen",
                False,
            )
        )


        return metadata
    # ==================================================
    # Part 5. Diagnostics API
    # ==================================================


    def validate(
        self,
        *,
        strict: bool = True,
    ) -> bool:
        """
        Validate current metadata state.

        Returns
        -------

        bool

        Raises
        ------

        MetricValidationError
            If strict mode enabled.
        """


        try:

            MetricValidator.validate_metadata(
                self._values
            )


            MetricValidator.validate_tags(
                self._tags
            )


            MetricValidator.validate_annotations(
                self._annotations
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
        Return metadata statistics.

        Example output:

        {
            "keys": 5,
            "tags": 3,
            "annotations": 2,
            "size_bytes": 512,
            "frozen": False
        }

        """

        with self._lock:


            payload = self.to_json()


            return {

                "id":
                    self._id,


                "version":
                    self._version,


                "keys":
                    len(
                        self._values
                    ),


                "tags":
                    len(
                        self._tags
                    ),


                "annotations":
                    len(
                        self._annotations
                    ),


                "size_bytes":
                    len(
                        payload.encode(
                            "utf-8"
                        )
                    ),


                "frozen":
                    self._frozen,


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
        Human readable metadata dump.

        Used by:

        - CLI
        - debugging
        - logging
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

        return (

            "MetricMetadata("
            f"id={self._id!r}, "
            f"keys={len(self._values)}, "
            f"tags={len(self._tags)}, "
            f"frozen={self._frozen}"
            ")"

        )                                    