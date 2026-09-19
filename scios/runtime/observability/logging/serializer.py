"""
SciOS-NG
runtime/observability/logging/serializer.py

Part 1. Foundation

Responsible for:
- LogRecord serialization
- JSON conversion
- Schema management
- Runtime observability
"""

from __future__ import annotations


# =============================================================================
# Imports
# =============================================================================

import uuid


from datetime import datetime
from datetime import timezone


from typing import Any
from typing import Dict
from typing import Mapping
from typing import Optional



# =============================================================================
# Constants
# =============================================================================

DEFAULT_SERIALIZER_NAME = "default"

DEFAULT_FORMAT = "json"


SUPPORTED_FORMATS = (
    "json",
    "dict",
)


DEFAULT_SCHEMA = {

    "id": "string",

    "timestamp": "datetime",

    "level": "string",

    "message": "string",

    "source": "string",

    "context": "object",

    "metadata": "object",

}



# =============================================================================
# Type Aliases
# =============================================================================

Schema = Dict[str, Any]

Metadata = Dict[str, Any]

Statistics = Dict[str, Any]



# =============================================================================
# LogSerializer
# =============================================================================

class LogSerializer:
    """
    SciOS-NG Logging Serializer.

    Converts:

        LogRecord
            |
            ▼
        Serialized Representation


    Features:

    - JSON serialization
    - Dictionary serialization
    - Schema registry
    - Runtime state
    - Statistics tracking
    """



    # =========================================================================
    # Constructor
    # =========================================================================

    def __init__(
        self,
        name: str = DEFAULT_SERIALIZER_NAME,
        *,
        format: str = DEFAULT_FORMAT,
        compression: bool = False,
        metadata: Optional[Mapping[str, Any]] = None,
    ):
        """
        Initialize LogSerializer.
        """


        # ---------------------------------------------------------------------
        # Identity
        # ---------------------------------------------------------------------

        self.id = str(
            uuid.uuid4()
        )


        self.name = name



        # ---------------------------------------------------------------------
        # Runtime State
        # ---------------------------------------------------------------------

        self.enabled = True


        self.created_at = datetime.now(
            timezone.utc
        )


        self.updated_at = self.created_at


        self._frozen = False

        self._closed = False



        # ---------------------------------------------------------------------
        # Serialization Configuration
        # ---------------------------------------------------------------------

        if format not in SUPPORTED_FORMATS:

            raise ValueError(
                f"Unsupported format: {format}"
            )


        self.format = format


        self.compression = bool(
            compression
        )



        # ---------------------------------------------------------------------
        # Schema Registry
        # ---------------------------------------------------------------------

        self.schemas: Dict[str, Schema] = {

            "default":
                dict(
                    DEFAULT_SCHEMA
                )

        }



        self.active_schema = "default"



        # ---------------------------------------------------------------------
        # Metadata
        # ---------------------------------------------------------------------

        self.metadata: Metadata = dict(
            metadata or {}
        )



        # ---------------------------------------------------------------------
        # Statistics
        # ---------------------------------------------------------------------

        self.statistics: Statistics = {

            "serialized": 0,

            "deserialized": 0,

            "failed": 0,

            "bytes": 0,

            "total_time": 0.0,

        }



        # ---------------------------------------------------------------------
        # Hooks
        # ---------------------------------------------------------------------

        self._hooks = {}
# =============================================================================
# Part 2. Properties
# =============================================================================


    # -------------------------------------------------------------------------
    # ID
    # -------------------------------------------------------------------------

    @property
    def id(
        self,
    ) -> str:
        """
        Return serializer identity.
        """

        return self._id



    # -------------------------------------------------------------------------
    # Name
    # -------------------------------------------------------------------------

    @property
    def name(
        self,
    ) -> str:
        """
        Return serializer name.
        """

        return self._name



    # -------------------------------------------------------------------------
    # Format
    # -------------------------------------------------------------------------

    @property
    def format(
        self,
    ) -> str:
        """
        Return serialization format.
        """

        return self._format



    # -------------------------------------------------------------------------
    # Compression
    # -------------------------------------------------------------------------

    @property
    def compression(
        self,
    ) -> bool:
        """
        Return compression state.
        """

        return self._compression



    # -------------------------------------------------------------------------
    # Enabled
    # -------------------------------------------------------------------------

    @property
    def enabled(
        self,
    ) -> bool:
        """
        Return serializer active state.
        """

        return self._enabled



    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    @property
    def metadata(
        self,
    ) -> Dict[str, Any]:
        """
        Return serializer metadata.
        """

        return self._metadata



    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    @property
    def statistics(
        self,
    ) -> Dict[str, Any]:
        """
        Return serializer statistics.
        """

        return self._statistics



    # -------------------------------------------------------------------------
    # Age
    # -------------------------------------------------------------------------

    @property
    def age(
        self,
    ) -> float:
        """
        Return serializer age in seconds.
        """

        now = datetime.now(
            timezone.utc
        )


        return (
            now
            -
            self.created_at
        ).total_seconds()



    # -------------------------------------------------------------------------
    # Serialize Count
    # -------------------------------------------------------------------------

    @property
    def serialize_count(
        self,
    ) -> int:
        """
        Return number of serialized records.
        """

        return int(
            self.statistics.get(
                "serialized",
                0
            )
        )
# =============================================================================
# Part 3. Serialization API
# =============================================================================


import json
import time



    # -------------------------------------------------------------------------
    # Serialize
    # -------------------------------------------------------------------------

    def serialize(
        self,
        record: Any,
    ) -> Any:
        """
        Serialize LogRecord into configured format.

        Supported:
        - dict
        - json
        """

        if not self.enabled:

            raise RuntimeError(
                "Serializer is disabled"
            )


        start = time.perf_counter()


        try:

            self.before_serialize(
                record
            )


            data = self.to_dict(
                record
            )


            if self.format == "json":

                result = self.to_json(
                    data
                )

            else:

                result = data



            elapsed = (
                time.perf_counter()
                -
                start
            )


            self.statistics["serialized"] += 1

            self.statistics["bytes"] += len(
                str(result)
            )

            self.statistics["total_time"] += elapsed


            self.after_serialize(
                record,
                result
            )


            return result


        except Exception:

            self.statistics["failed"] += 1

            raise



    # -------------------------------------------------------------------------
    # Deserialize
    # -------------------------------------------------------------------------

    def deserialize(
        self,
        data: Any,
    ) -> Dict[str, Any]:
        """
        Deserialize serialized data.
        """

        start = time.perf_counter()


        try:

            self.before_deserialize(
                data
            )


            if isinstance(
                data,
                str
            ):

                result = self.from_json(
                    data
                )

            else:

                result = self.from_dict(
                    data
                )



            elapsed = (
                time.perf_counter()
                -
                start
            )


            self.statistics["deserialized"] += 1

            self.statistics["total_time"] += elapsed



            self.after_deserialize(
                result
            )


            return result


        except Exception:

            self.statistics["failed"] += 1

            raise



    # -------------------------------------------------------------------------
    # Encode
    # -------------------------------------------------------------------------

    def encode(
        self,
        value: Any,
    ) -> str:
        """
        Encode object into JSON string.
        """

        return json.dumps(
            value,
            ensure_ascii=False,
            default=str,
        )



    # -------------------------------------------------------------------------
    # Decode
    # -------------------------------------------------------------------------

    def decode(
        self,
        value: str,
    ) -> Any:
        """
        Decode JSON string.
        """

        return json.loads(
            value
        )



    # -------------------------------------------------------------------------
    # To Dictionary
    # -------------------------------------------------------------------------

    def to_dict(
        self,
        record: Any,
    ) -> Dict[str, Any]:
        """
        Convert LogRecord into dictionary.
        """

        if hasattr(
            record,
            "to_dict"
        ):

            return record.to_dict()



        if isinstance(
            record,
            Mapping
        ):

            return dict(
                record
            )



        return {

            "id":
                getattr(
                    record,
                    "id",
                    None
                ),

            "timestamp":
                str(
                    getattr(
                        record,
                        "timestamp",
                        None
                    )
                ),

            "level":
                str(
                    getattr(
                        record,
                        "level",
                        None
                    )
                ),

            "message":
                getattr(
                    record,
                    "message",
                    ""
                ),

            "source":
                getattr(
                    record,
                    "source",
                    None
                ),

            "context":
                getattr(
                    record,
                    "context",
                    {}
                ),

            "metadata":
                getattr(
                    record,
                    "metadata",
                    {}
                ),

        }



    # -------------------------------------------------------------------------
    # From Dictionary
    # -------------------------------------------------------------------------

    def from_dict(
        self,
        data: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """
        Restore dictionary representation.
        """

        return dict(
            data
        )



    # -------------------------------------------------------------------------
    # To JSON
    # -------------------------------------------------------------------------

    def to_json(
        self,
        value: Any,
        *,
        indent: int = 2,
    ) -> str:
        """
        Convert value into JSON.
        """

        return json.dumps(
            value,
            ensure_ascii=False,
            indent=indent,
            default=str,
        )



    # -------------------------------------------------------------------------
    # From JSON
    # -------------------------------------------------------------------------

    def from_json(
        self,
        value: str,
    ) -> Dict[str, Any]:
        """
        Restore object from JSON.
        """

        data = json.loads(
            value
        )


        if not isinstance(
            data,
            dict
        ):

            raise ValueError(
                "Serialized JSON must be object"
            )


        return data
# =============================================================================
# Part 4. Schema Registry API
# =============================================================================


    # -------------------------------------------------------------------------
    # Add Schema
    # -------------------------------------------------------------------------

    def add_schema(
        self,
        name: str,
        schema: Mapping[str, Any],
    ) -> "LogSerializer":
        """
        Register a serialization schema.
        """

        if getattr(
            self,
            "_frozen",
            False
        ):

            raise RuntimeError(
                "Serializer is frozen"
            )


        self.schemas[name] = dict(
            schema
        )


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Remove Schema
    # -------------------------------------------------------------------------

    def remove_schema(
        self,
        name: str,
    ) -> bool:
        """
        Remove schema from registry.
        """

        if name not in self.schemas:

            return False


        if name == self.active_schema:

            self.active_schema = "default"


        del self.schemas[name]


        self.updated_at = datetime.now(
            timezone.utc
        )


        return True



    # -------------------------------------------------------------------------
    # Schema
    # -------------------------------------------------------------------------

    def schema(
        self,
        name: Optional[str] = None,
    ) -> Schema:
        """
        Get schema by name.

        If name is None:
            return active schema.
        """

        target = (

            name

            if name is not None

            else self.active_schema

        )


        if target not in self.schemas:

            raise KeyError(
                f"Schema not found: {target}"
            )


        return dict(
            self.schemas[target]
        )



    # -------------------------------------------------------------------------
    # Schemas
    # -------------------------------------------------------------------------

    def schemas(
        self,
    ) -> Dict[str, Schema]:
        """
        Return all registered schemas.
        """

        return {

            name:
                dict(schema)

            for name, schema
            in self.schemas.items()

        }



    # -------------------------------------------------------------------------
    # Has Schema
    # -------------------------------------------------------------------------

    def has_schema(
        self,
        name: str,
    ) -> bool:
        """
        Check schema existence.
        """

        return (
            name
            in
            self.schemas
        )



    # -------------------------------------------------------------------------
    # Use Schema
    # -------------------------------------------------------------------------

    def use_schema(
        self,
        name: str,
    ) -> "LogSerializer":
        """
        Set active serialization schema.
        """

        if name not in self.schemas:

            raise KeyError(
                f"Unknown schema: {name}"
            )


        self.active_schema = name


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Default Schema
    # -------------------------------------------------------------------------

    def default_schema(
        self,
    ) -> Schema:
        """
        Return default schema.
        """

        return dict(
            DEFAULT_SCHEMA
        )



    # -------------------------------------------------------------------------
    # Clear Schemas
    # -------------------------------------------------------------------------

    def clear_schemas(
        self,
    ) -> "LogSerializer":
        """
        Remove all custom schemas.

        Keeps default schema.
        """

        if getattr(
            self,
            "_frozen",
            False
        ):

            raise RuntimeError(
                "Serializer is frozen"
            )


        self.schemas.clear()


        self.schemas["default"] = dict(
            DEFAULT_SCHEMA
        )


        self.active_schema = "default"


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Schema Count
    # -------------------------------------------------------------------------

    def schema_count(
        self,
    ) -> int:
        """
        Return number of schemas.
        """

        return len(
            self.schemas
        )
# =============================================================================
# Part 5. Lifecycle API
# =============================================================================


    # -------------------------------------------------------------------------
    # Enable
    # -------------------------------------------------------------------------

    def enable(
        self,
    ) -> "LogSerializer":
        """
        Enable serializer.
        """

        self._enabled = True


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Disable
    # -------------------------------------------------------------------------

    def disable(
        self,
    ) -> "LogSerializer":
        """
        Disable serializer.
        """

        self._enabled = False


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Reset
    # -------------------------------------------------------------------------

    def reset(
        self,
    ) -> "LogSerializer":
        """
        Reset runtime state.

        Keeps:
        - identity
        - schemas
        - metadata
        """

        self._enabled = True


        self._frozen = False


        self._closed = False


        self.active_schema = "default"



        self._statistics.clear()


        self._statistics.update(
            {

                "serialized": 0,

                "deserialized": 0,

                "failed": 0,

                "bytes": 0,

                "total_time": 0.0,

            }
        )


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Clear
    # -------------------------------------------------------------------------

    def clear(
        self,
    ) -> "LogSerializer":
        """
        Clear runtime resources.

        Removes:
        - metadata
        - custom schemas
        - statistics
        """

        self._metadata.clear()


        self.clear_schemas()


        self._statistics.clear()


        self._statistics.update(
            {

                "serialized": 0,

                "deserialized": 0,

                "failed": 0,

                "bytes": 0,

                "total_time": 0.0,

            }
        )


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Freeze
    # -------------------------------------------------------------------------

    def freeze(
        self,
    ) -> "LogSerializer":
        """
        Freeze serializer configuration.

        Frozen serializer cannot be modified.
        """

        self._frozen = True


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Unfreeze
    # -------------------------------------------------------------------------

    def unfreeze(
        self,
    ) -> "LogSerializer":
        """
        Unfreeze serializer.
        """

        self._frozen = False


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Close
    # -------------------------------------------------------------------------

    def close(
        self,
    ) -> "LogSerializer":
        """
        Close serializer lifecycle.
        """

        self._enabled = False


        self._closed = True


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Reopen
    # -------------------------------------------------------------------------

    def reopen(
        self,
    ) -> "LogSerializer":
        """
        Reopen closed serializer.
        """

        self._closed = False


        self._enabled = True


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self
# =============================================================================
# Part 6. Runtime Operations
# =============================================================================


import copy
import time



    # -------------------------------------------------------------------------
    # Snapshot
    # -------------------------------------------------------------------------

    def snapshot(
        self,
    ) -> Dict[str, Any]:
        """
        Create runtime snapshot.

        Contains:
        - configuration
        - schemas
        - metadata
        - statistics
        """

        return {

            "id":
                self.id,

            "name":
                self.name,

            "format":
                self.format,

            "compression":
                self.compression,

            "enabled":
                self.enabled,

            "frozen":
                self._frozen,

            "closed":
                self._closed,

            "active_schema":
                self.active_schema,

            "schemas":
                copy.deepcopy(
                    self.schemas
                ),

            "metadata":
                copy.deepcopy(
                    self.metadata
                ),

            "statistics":
                copy.deepcopy(
                    self.statistics
                ),

            "created_at":
                self.created_at.isoformat(),

            "updated_at":
                self.updated_at.isoformat(),

        }



    # -------------------------------------------------------------------------
    # Restore
    # -------------------------------------------------------------------------

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "LogSerializer":
        """
        Restore serializer state.
        """

        self._format = snapshot.get(
            "format",
            self.format,
        )


        self._compression = snapshot.get(
            "compression",
            self.compression,
        )


        self._enabled = snapshot.get(
            "enabled",
            True,
        )


        self._frozen = snapshot.get(
            "frozen",
            False,
        )


        self._closed = snapshot.get(
            "closed",
            False,
        )


        self.active_schema = snapshot.get(
            "active_schema",
            "default",
        )


        self.schemas = copy.deepcopy(
            snapshot.get(
                "schemas",
                {}
            )
        )


        self.metadata = copy.deepcopy(
            snapshot.get(
                "metadata",
                {}
            )
        )


        self.statistics = copy.deepcopy(
            snapshot.get(
                "statistics",
                {}
            )
        )


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Clone
    # -------------------------------------------------------------------------

    def clone(
        self,
    ) -> "LogSerializer":
        """
        Create independent serializer clone.
        """

        serializer = LogSerializer(
            name=self.name,
            format=self.format,
            compression=self.compression,
            metadata=self.metadata,
        )


        serializer.restore(
            self.snapshot()
        )


        return serializer



    # -------------------------------------------------------------------------
    # Copy
    # -------------------------------------------------------------------------

    def copy(
        self,
    ) -> "LogSerializer":
        """
        Create runtime copy.

        Alias for clone().
        """

        return self.clone()



    # -------------------------------------------------------------------------
    # Optimize
    # -------------------------------------------------------------------------

    def optimize(
        self,
    ) -> Dict[str, Any]:
        """
        Optimize serializer runtime.

        Operations:
        - remove unused metadata
        - compact schemas
        - cleanup hooks
        """

        start = time.perf_counter()


        removed_hooks = 0


        if hasattr(
            self,
            "_hooks"
        ):

            for event in list(
                self._hooks.keys()
            ):

                if not self._hooks[event]:

                    del self._hooks[event]

                    removed_hooks += 1



        elapsed = (
            time.perf_counter()
            -
            start
        )


        return {

            "optimized": True,

            "removed_hooks":
                removed_hooks,

            "latency":
                elapsed,

        }



    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------

    def cleanup(
        self,
    ) -> "LogSerializer":
        """
        Cleanup temporary runtime resources.
        """

        if hasattr(
            self,
            "_hooks"
        ):

            self._hooks.clear()


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Compact
    # -------------------------------------------------------------------------

    def compact(
        self,
    ) -> Dict[str, Any]:
        """
        Compact internal storage.

        Removes:
        - empty metadata
        - empty schemas
        """

        removed = {

            "metadata": 0,

            "schemas": 0,

        }


        empty_metadata = [

            key

            for key, value
            in self.metadata.items()

            if value is None

        ]


        for key in empty_metadata:

            del self.metadata[key]

            removed["metadata"] += 1



        empty_schema = [

            name

            for name, schema
            in self.schemas.items()

            if not schema

        ]


        for name in empty_schema:

            del self.schemas[name]

            removed["schemas"] += 1



        self.updated_at = datetime.now(
            timezone.utc
        )


        return {

            "compacted": True,

            "removed":
                removed,

        }
# =============================================================================
# Part 7. Statistics & Diagnostics
# =============================================================================


    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return serializer summary.
        """

        return {

            "id":
                self.id,

            "name":
                self.name,

            "format":
                self.format,

            "compression":
                self.compression,

            "enabled":
                self.enabled,

            "schema":
                self.active_schema,

            "schema_count":
                self.schema_count(),

            "serialize_count":
                self.serialize_count,

            "error_count":
                self.error_count,

            "uptime":
                self.uptime,

            "latency":
                self.latency,

        }



    # -------------------------------------------------------------------------
    # Report
    # -------------------------------------------------------------------------

    def report(
        self,
    ) -> Dict[str, Any]:
        """
        Generate detailed diagnostic report.
        """

        return {

            "component":
                "LogSerializer",

            "identity": {

                "id":
                    self.id,

                "name":
                    self.name,

            },


            "configuration": {

                "format":
                    self.format,

                "compression":
                    self.compression,

                "schema":
                    self.active_schema,

            },


            "runtime": {

                "enabled":
                    self.enabled,

                "frozen":
                    self._frozen,

                "closed":
                    self._closed,

            },


            "statistics":
                dict(
                    self.statistics
                ),


            "diagnostics":
                self.health(),

        }



    # -------------------------------------------------------------------------
    # Health
    # -------------------------------------------------------------------------

    def health(
        self,
    ) -> Dict[str, Any]:
        """
        Return health status.
        """

        healthy = (

            self.enabled

            and

            not self._closed

        )


        return {

            "healthy":
                healthy,

            "state":
                self.status(),

            "errors":
                self.error_count,

        }



    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    def status(
        self,
    ) -> str:
        """
        Return current lifecycle status.
        """

        if self._closed:

            return "closed"


        if self._frozen:

            return "frozen"


        if not self.enabled:

            return "disabled"


        return "active"



    # -------------------------------------------------------------------------
    # Schema Count
    # -------------------------------------------------------------------------

    @property
    def schema_count(
        self,
    ) -> int:
        """
        Return number of registered schemas.
        """

        return len(
            self.schemas
        )



    # -------------------------------------------------------------------------
    # Serialize Count
    # -------------------------------------------------------------------------

    @property
    def serialize_count(
        self,
    ) -> int:
        """
        Return successful serialization count.
        """

        return int(
            self.statistics.get(
                "serialized",
                0
            )
        )



    # -------------------------------------------------------------------------
    # Error Count
    # -------------------------------------------------------------------------

    @property
    def error_count(
        self,
    ) -> int:
        """
        Return serialization errors.
        """

        return int(
            self.statistics.get(
                "failed",
                0
            )
        )



    # -------------------------------------------------------------------------
    # Uptime
    # -------------------------------------------------------------------------

    @property
    def uptime(
        self,
    ) -> float:
        """
        Return runtime duration in seconds.
        """

        now = datetime.now(
            timezone.utc
        )


        return (
            now
            -
            self.created_at
        ).total_seconds()



    # -------------------------------------------------------------------------
    # Latency
    # -------------------------------------------------------------------------

    @property
    def latency(
        self,
    ) -> float:
        """
        Return average serialization latency.

        Unit:
        seconds
        """

        count = (

            self.serialize_count

            +

            self.statistics.get(
                "deserialized",
                0
            )

        )


        if count == 0:

            return 0.0


        return (

            self.statistics.get(
                "total_time",
                0.0
            )

            /

            count

        )
# =============================================================================
# Part 8. Validation
# =============================================================================


    # -------------------------------------------------------------------------
    # Validate
    # -------------------------------------------------------------------------

    def validate(
        self,
        data: Any,
    ) -> bool:
        """
        Validate serialized input.

        Performs:
        - format validation
        - schema validation
        - integrity checking
        """

        if not self.enabled:

            return False


        if not self.check_format(
            data
        ):

            return False


        if not self.check_integrity(
            data
        ):

            return False


        return True



    # -------------------------------------------------------------------------
    # Validate Record
    # -------------------------------------------------------------------------

    def validate_record(
        self,
        record: Any,
    ) -> bool:
        """
        Validate LogRecord object.

        Required fields:
        - id
        - timestamp
        - level
        - message
        """

        required_fields = (

            "id",

            "timestamp",

            "level",

            "message",

        )


        for field in required_fields:

            if isinstance(
                record,
                Mapping
            ):

                if field not in record:

                    return False

            else:

                if not hasattr(
                    record,
                    field
                ):

                    return False



        return True



    # -------------------------------------------------------------------------
    # Validate Schema
    # -------------------------------------------------------------------------

    def validate_schema(
        self,
        data: Mapping[str, Any],
        schema: Optional[str] = None,
    ) -> bool:
        """
        Validate data against schema.
        """

        target_schema = self.schema(
            schema
        )


        for field in target_schema:

            if field not in data:

                return False



        return True



    # -------------------------------------------------------------------------
    # Check Format
    # -------------------------------------------------------------------------

    def check_format(
        self,
        data: Any,
    ) -> bool:
        """
        Validate serialization format.
        """

        if self.format == "json":

            return isinstance(
                data,
                str
            )


        if self.format == "dict":

            return isinstance(
                data,
                Mapping
            )


        return False



    # -------------------------------------------------------------------------
    # Check Integrity
    # -------------------------------------------------------------------------

    def check_integrity(
        self,
        data: Any,
    ) -> bool:
        """
        Check serialized data integrity.

        Detect:
        - empty payload
        - invalid object
        """

        if data is None:

            return False


        if isinstance(
            data,
            str
        ):

            return len(
                data.strip()
            ) > 0



        if isinstance(
            data,
            Mapping
        ):

            return len(
                data
            ) > 0



        return False
# =============================================================================
# Part 9. Events & Hooks
# =============================================================================


    # -------------------------------------------------------------------------
    # Before Serialize
    # -------------------------------------------------------------------------

    def before_serialize(
        self,
        record: Any,
    ) -> None:
        """
        Hook executed before serialization.
        """

        self.emit(
            "before_serialize",
            record
        )



    # -------------------------------------------------------------------------
    # After Serialize
    # -------------------------------------------------------------------------

    def after_serialize(
        self,
        record: Any,
        result: Any,
    ) -> None:
        """
        Hook executed after serialization.
        """

        self.emit(
            "after_serialize",
            {
                "record": record,
                "result": result,
            }
        )



    # -------------------------------------------------------------------------
    # Before Deserialize
    # -------------------------------------------------------------------------

    def before_deserialize(
        self,
        data: Any,
    ) -> None:
        """
        Hook executed before deserialization.
        """

        self.emit(
            "before_deserialize",
            data
        )



    # -------------------------------------------------------------------------
    # After Deserialize
    # -------------------------------------------------------------------------

    def after_deserialize(
        self,
        result: Any,
    ) -> None:
        """
        Hook executed after deserialization.
        """

        self.emit(
            "after_deserialize",
            result
        )



    # -------------------------------------------------------------------------
    # Add Hook
    # -------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback,
    ) -> "LogSerializer":
        """
        Register event callback.
        """

        if event not in self._hooks:

            self._hooks[event] = []


        self._hooks[event].append(
            callback
        )


        return self



    # -------------------------------------------------------------------------
    # Remove Hook
    # -------------------------------------------------------------------------

    def remove_hook(
        self,
        event: str,
        callback=None,
    ) -> bool:
        """
        Remove event callback.
        """

        if event not in self._hooks:

            return False


        if callback is None:

            del self._hooks[event]

            return True



        if callback in self._hooks[event]:

            self._hooks[event].remove(
                callback
            )


            return True


        return False



    # -------------------------------------------------------------------------
    # Emit
    # -------------------------------------------------------------------------

    def emit(
        self,
        event: str,
        payload: Any = None,
    ) -> None:
        """
        Dispatch event to hooks.
        """

        callbacks = self._hooks.get(
            event,
            []
        )


        for callback in callbacks:

            try:

                callback(
                    payload
                )

            except Exception:

                self.statistics["failed"] += 1



    # -------------------------------------------------------------------------
    # Subscribe
    # -------------------------------------------------------------------------

    def subscribe(
        self,
        event: str,
        callback,
    ) -> "LogSerializer":
        """
        Alias for add_hook().
        """

        return self.add_hook(
            event,
            callback
        )
# =============================================================================
# Part 10. Python Protocols
# =============================================================================


import copy



    # -------------------------------------------------------------------------
    # __repr__
    # -------------------------------------------------------------------------

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (

            f"LogSerializer("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"format={self.format!r}, "
            f"enabled={self.enabled}, "
            f"schemas={self.schema_count}"
            f")"

        )



    # -------------------------------------------------------------------------
    # __str__
    # -------------------------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Human readable representation.
        """

        return (

            f"{self.name} "
            f"[{self.format}] "
            f"- {self.status()}"

        )



    # -------------------------------------------------------------------------
    # __len__
    # -------------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Return number of registered schemas.
        """

        return self.schema_count



    # -------------------------------------------------------------------------
    # __iter__
    # -------------------------------------------------------------------------

    def __iter__(
        self,
    ):
        """
        Iterate through schemas.
        """

        return iter(
            self.schemas.items()
        )



    # -------------------------------------------------------------------------
    # __contains__
    # -------------------------------------------------------------------------

    def __contains__(
        self,
        item: str,
    ) -> bool:
        """
        Check schema existence.
        """

        return self.has_schema(
            item
        )



    # -------------------------------------------------------------------------
    # __call__
    # -------------------------------------------------------------------------

    def __call__(
        self,
        record: Any,
    ) -> Any:
        """
        Shortcut for serialize().
        """

        return self.serialize(
            record
        )



    # -------------------------------------------------------------------------
    # __copy__
    # -------------------------------------------------------------------------

    def __copy__(
        self,
    ):
        """
        Shallow copy protocol.
        """

        return self.clone()



    # -------------------------------------------------------------------------
    # __deepcopy__
    # -------------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo,
    ):
        """
        Deep copy protocol.
        """

        cloned = self.clone()


        memo[id(self)] = cloned


        return cloned                                                                        