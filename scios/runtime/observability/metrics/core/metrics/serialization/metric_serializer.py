"""
SciOS-NG Metric Serializer
==========================

Serialization engine for Metrics subsystem.

Responsibilities:
- convert metrics into serializable data
- restore metrics from serialized data
- provide persistence helpers

Supported:
- dict
- JSON
- file storage
"""

from __future__ import annotations


import json

from threading import RLock
from typing import Any, Final


__all__ = [
    "MetricSerializer",
]


class MetricSerializer:
    """
    Thread-safe metric serialization engine.
    """


    VERSION: Final[str] = "1.0"



    # ==================================================
    # Constructor
    # ==================================================

    def __init__(
        self,
    ) -> None:


        #
        # Runtime
        #
        self._version = self.VERSION


        #
        # Thread safety
        #
        self._lock = RLock()



    # ==================================================
    # Properties
    # ==================================================

    @property
    def version(
        self,
    ) -> str:
        """
        Serializer version.
        """

        return self._version



    @property
    def lock(
        self,
    ) -> RLock:
        """
        Internal lock.
        """

        return self._lock



    # ==================================================
    # Internal Helpers
    # ==================================================

    def _base(
        self,
    ) -> dict[str, Any]:
        """
        Base serialization metadata.
        """

        return {

            "serializer":
                self.__class__.__name__,

            "version":
                self._version,

        }
# ==================================================
# Part 2. Serialization API
# ==================================================


# --------------------------------------------------
# Serialize Object
# --------------------------------------------------

def serialize(
    self,
    obj: Any,
) -> dict[str, Any]:
    """
    Serialize any supported metrics object.

    Supported:
    - Metric
    - Snapshot object
    - object with to_dict()
    - object with snapshot()
    """

    with self._lock:

        payload = self._base()


        if hasattr(
            obj,
            "to_dict",
        ):

            payload["data"] = (
                obj.to_dict()
            )


        elif hasattr(
            obj,
            "snapshot",
        ):

            payload["data"] = (
                obj.snapshot()
            )


        elif isinstance(
            obj,
            dict,
        ):

            payload["data"] = obj


        else:

            payload["data"] = {
                "value": str(obj)
            }


        return payload



# --------------------------------------------------
# Serialize Metric
# --------------------------------------------------

def serialize_metric(
    self,
    metric,
) -> dict[str, Any]:
    """
    Serialize Metric instance.
    """

    return self.serialize(
        metric
    )



# --------------------------------------------------
# To Dict
# --------------------------------------------------

def to_dict(
    self,
    obj: Any,
) -> dict[str, Any]:
    """
    Convert object to dictionary.
    """

    return self.serialize(
        obj
    )



# --------------------------------------------------
# To JSON
# --------------------------------------------------

def to_json(
    self,
    obj: Any,
    *,
    indent: int = 2,
) -> str:
    """
    Convert object to JSON string.
    """

    return json.dumps(
        self.serialize(obj),
        indent=indent,
        default=str,
    )



# --------------------------------------------------
# Serialize Many
# --------------------------------------------------

def serialize_many(
    self,
    objects: list[Any] | tuple[Any, ...],
) -> dict[str, Any]:
    """
    Serialize multiple objects.
    """

    with self._lock:

        return {

            **self._base(),

            "count":
                len(objects),

            "items":
                [
                    self.serialize(obj)
                    for obj in objects
                ],

        }
# ==================================================
# Part 3. Deserialization API
# ==================================================


# --------------------------------------------------
# Deserialize
# --------------------------------------------------

def deserialize(
    self,
    data: dict[str, Any],
    *,
    factory=None,
):
    """
    Deserialize serialized data.

    Parameters
    ----------
    data:
        Serialized dictionary.

    factory:
        Optional callable to recreate object.
    """

    with self._lock:

        payload = data.get(
            "data",
            data,
        )


        #
        # Custom object restore
        #
        if factory is not None:

            return factory(
                payload
            )


        #
        # Default
        #
        return payload



# --------------------------------------------------
# From Dict
# --------------------------------------------------

def from_dict(
    self,
    data: dict[str, Any],
    *,
    factory=None,
):
    """
    Restore object from dictionary.
    """

    return self.deserialize(
        data,
        factory=factory,
    )



# --------------------------------------------------
# From JSON
# --------------------------------------------------

def from_json(
    self,
    text: str,
    *,
    factory=None,
):
    """
    Restore object from JSON.
    """

    data = json.loads(
        text
    )


    return self.deserialize(
        data,
        factory=factory,
    )



# --------------------------------------------------
# Restore Object
# --------------------------------------------------

def restore_object(
    self,
    data: dict[str, Any],
    cls,
):
    """
    Restore object using class constructor.

    Requires:
        cls(**data)
    """

    payload = data.get(
        "data",
        data,
    )


    return cls(
        **payload
    )



# --------------------------------------------------
# Restore Many
# --------------------------------------------------

def deserialize_many(
    self,
    data: dict[str, Any],
    *,
    factory=None,
) -> list[Any]:
    """
    Restore multiple objects.
    """

    items = data.get(
        "items",
        [],
    )


    return [

        self.deserialize(
            item,
            factory=factory,
        )

        for item in items

    ]
# ==================================================
# Part 4. Snapshot API
# ==================================================


# --------------------------------------------------
# Create Snapshot
# --------------------------------------------------

def create_snapshot(
    self,
    obj: Any,
    *,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create a serializable snapshot.

    Parameters
    ----------
    obj:
        Runtime object.

    metadata:
        Extra snapshot metadata.
    """

    with self._lock:

        snapshot = {

            **self._base(),

            "type":
                obj.__class__.__name__,

            "snapshot":

                (
                    obj.snapshot()
                    if hasattr(
                        obj,
                        "snapshot",
                    )
                    else
                    self.serialize(obj)
                ),

        }


        if metadata:

            snapshot["metadata"] = (
                metadata
            )


        return snapshot



# --------------------------------------------------
# Serialize Snapshot
# --------------------------------------------------

def serialize_snapshot(
    self,
    snapshot: dict[str, Any],
) -> str:
    """
    Convert snapshot into JSON.
    """

    with self._lock:

        return json.dumps(
            snapshot,
            indent=2,
            default=str,
        )



# --------------------------------------------------
# Deserialize Snapshot
# --------------------------------------------------

def deserialize_snapshot(
    self,
    text: str,
) -> dict[str, Any]:
    """
    Restore snapshot dictionary.
    """

    with self._lock:

        return json.loads(
            text
        )



# --------------------------------------------------
# Restore Snapshot
# --------------------------------------------------

def restore_snapshot(
    self,
    snapshot: dict[str, Any],
    obj: Any,
) -> Any:
    """
    Restore object state from snapshot.
    """

    with self._lock:

        state = snapshot.get(
            "snapshot",
            snapshot,
        )


        if hasattr(
            obj,
            "restore",
        ):

            obj.restore(
                state
            )


        return obj



# --------------------------------------------------
# Snapshot Data
# --------------------------------------------------

def snapshot_data(
    self,
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    """
    Extract pure snapshot payload.
    """

    return snapshot.get(
        "snapshot",
        {},
    )



# --------------------------------------------------
# Clone Snapshot
# --------------------------------------------------

def clone_snapshot(
    self,
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    """
    Deep clone snapshot.

    Useful for:
    - backup
    - distributed transport
    """

    return json.loads(
        json.dumps(
            snapshot,
            default=str,
        )
    )
# ==================================================
# Part 5. Batch API
# ==================================================


# --------------------------------------------------
# Serialize Batch
# --------------------------------------------------

def serialize_batch(
    self,
    objects: list[Any] | tuple[Any, ...],
) -> dict[str, Any]:
    """
    Serialize multiple objects.

    Returns
    -------
    dict
        Batch serialized payload.
    """

    with self._lock:

        return {

            **self._base(),

            "type":
                "batch",

            "count":
                len(objects),

            "items":
                [
                    self.serialize(obj)
                    for obj in objects
                ],

        }



# --------------------------------------------------
# Deserialize Batch
# --------------------------------------------------

def deserialize_batch(
    self,
    data: dict[str, Any],
    *,
    factory=None,
) -> list[Any]:
    """
    Deserialize batch payload.
    """

    with self._lock:

        items = data.get(
            "items",
            [],
        )


        return [

            self.deserialize(
                item,
                factory=factory,
            )

            for item in items

        ]



# --------------------------------------------------
# Snapshot Batch
# --------------------------------------------------

def snapshot_batch(
    self,
    objects: list[Any] | tuple[Any, ...],
    *,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create batch snapshot.
    """

    with self._lock:

        payload = {

            **self._base(),

            "type":
                "snapshot_batch",

            "count":
                len(objects),

            "snapshots":
                [
                    self.create_snapshot(
                        obj
                    )
                    for obj in objects
                ],

        }


        if metadata:

            payload["metadata"] = (
                metadata
            )


        return payload



# --------------------------------------------------
# Restore Batch
# --------------------------------------------------

def restore_batch(
    self,
    snapshots: dict[str, Any],
    objects: list[Any],
) -> list[Any]:
    """
    Restore many objects from snapshots.

    Objects and snapshots must
    have same order.
    """

    with self._lock:

        states = snapshots.get(
            "snapshots",
            [],
        )


        restored = []


        for obj, snapshot in zip(
            objects,
            states,
        ):

            restored.append(

                self.restore_snapshot(
                    snapshot,
                    obj,
                )

            )


        return restored



# --------------------------------------------------
# Merge Batches
# --------------------------------------------------

def merge_batches(
    self,
    *batches: dict[str, Any],
) -> dict[str, Any]:
    """
    Merge multiple serialized batches.
    """

    items = []


    for batch in batches:

        items.extend(
            batch.get(
                "items",
                [],
            )
        )


    return {

        **self._base(),

        "type":
            "batch",

        "count":
            len(items),

        "items":
            items,

    }



# --------------------------------------------------
# Batch Size
# --------------------------------------------------

def batch_size(
    self,
    batch: dict[str, Any],
) -> int:
    """
    Return batch item count.
    """

    return batch.get(
        "count",
        0,
    )
# ==================================================
# Part 6. JSON API
# ==================================================


# --------------------------------------------------
# JSON Encode
# --------------------------------------------------

def encode_json(
    self,
    obj: Any,
    *,
    pretty: bool = False,
) -> str:
    """
    Encode object into JSON.

    Parameters
    ----------
    obj:
        Any serializable object.

    pretty:
        Enable formatted JSON.
    """

    with self._lock:

        payload = self.serialize(
            obj
        )

        return json.dumps(
            payload,
            indent=(
                2
                if pretty
                else None
            ),
            separators=(
                None
                if pretty
                else (
                    ",",
                    ":",
                )
            ),
            default=str,
        )



# --------------------------------------------------
# JSON Decode
# --------------------------------------------------

def decode_json(
    self,
    text: str,
) -> dict[str, Any]:
    """
    Decode JSON string.
    """

    with self._lock:

        return json.loads(
            text
        )



# --------------------------------------------------
# Compact JSON
# --------------------------------------------------

def compact_json(
    self,
    obj: Any,
) -> str:
    """
    Create compact JSON.

    Optimized for:
    - network
    - telemetry
    - edge transport
    """

    return self.encode_json(
        obj,
        pretty=False,
    )



# --------------------------------------------------
# Pretty JSON
# --------------------------------------------------

def pretty_json(
    self,
    obj: Any,
) -> str:
    """
    Create human readable JSON.

    Optimized for:
    - debugging
    - logs
    """

    return self.encode_json(
        obj,
        pretty=True,
    )



# --------------------------------------------------
# JSON Schema
# --------------------------------------------------

def json_schema(
    self,
) -> dict[str, Any]:
    """
    Return serializer JSON schema.
    """

    return {

        "serializer":
            self.__class__.__name__,

        "version":
            self._version,

        "format":
            "json",

        "encoding":
            "utf-8",

    }



# --------------------------------------------------
# Validate JSON
# --------------------------------------------------

def validate_json(
    self,
    text: str,
) -> bool:
    """
    Validate JSON payload.

    Returns
    -------
    bool
    """

    try:

        json.loads(
            text
        )

        return True


    except (
        ValueError,
        TypeError,
    ):

        return False



# --------------------------------------------------
# JSON Stream
# --------------------------------------------------

def stream_json(
    self,
    objects,
):
    """
    Generate JSON chunks.

    Useful for:
    - large metric batches
    - streaming telemetry
    """

    for obj in objects:

        yield self.compact_json(
            obj
        )
from pathlib import Path
import tempfile
import shutil
# ==================================================
# Part 8. Validation API
# ==================================================


# --------------------------------------------------
# Validate Generic Data
# --------------------------------------------------

def validate(
    self,
    data: Any,
) -> bool:
    """
    Validate generic serialized payload.
    """

    if data is None:
        return False


    if not isinstance(
        data,
        dict,
    ):
        return False


    return True



# --------------------------------------------------
# Validate Schema
# --------------------------------------------------

def validate_schema(
    self,
    data: dict[str, Any],
) -> bool:
    """
    Validate serializer schema.
    """

    if not self.validate(
        data
    ):
        return False


    required = (
        "serializer",
        "version",
    )


    for key in required:

        if key not in data:

            return False


    if (
        data["serializer"]
        != self.__class__.__name__
    ):

        return False


    return True



# --------------------------------------------------
# Validate Snapshot
# --------------------------------------------------

def validate_snapshot(
    self,
    snapshot: dict[str, Any],
) -> bool:
    """
    Validate snapshot payload.
    """

    if not self.validate(
        snapshot
    ):
        return False


    if "snapshot" not in snapshot:

        return False


    if "type" not in snapshot:

        return False


    return True



# --------------------------------------------------
# Validate Batch
# --------------------------------------------------

def validate_batch(
    self,
    batch: dict[str, Any],
) -> bool:
    """
    Validate batch payload.
    """

    if not self.validate(
        batch
    ):
        return False


    if batch.get(
        "type"
    ) != "batch":

        return False


    items = batch.get(
        "items"
    )


    if not isinstance(
        items,
        list,
    ):

        return False


    if batch.get(
        "count"
    ) != len(items):

        return False


    return True



# --------------------------------------------------
# Validate JSON Payload
# --------------------------------------------------

def validate_json_payload(
    self,
    text: str,
) -> bool:
    """
    Validate JSON string.

    Combines:
    - syntax validation
    - schema validation
    """

    try:

        data = json.loads(
            text
        )


    except (
        ValueError,
        TypeError,
    ):

        return False


    return self.validate_schema(
        data
    )



# --------------------------------------------------
# Validate File
# --------------------------------------------------

def validate_file(
    self,
    path: str | Path,
) -> bool:
    """
    Validate serialized file.
    """

    file_path = Path(
        path
    )


    if not file_path.exists():

        return False


    try:

        text = file_path.read_text(
            encoding="utf-8"
        )


        return self.validate_json_payload(
            text
        )


    except Exception:

        return False



# --------------------------------------------------
# Validation Report
# --------------------------------------------------

def validation_report(
    self,
    data: Any,
) -> dict[str, Any]:
    """
    Detailed validation result.
    """

    return {

        "valid":
            self.validate(data),

        "schema":
            (
                self.validate_schema(data)
                if isinstance(
                    data,
                    dict,
                )
                else False
            ),

        "snapshot":
            (
                self.validate_snapshot(data)
                if isinstance(
                    data,
                    dict,
                )
                else False
            ),

        "batch":
            (
                self.validate_batch(data)
                if isinstance(
                    data,
                    dict,
                )
                else False
            ),

    }
# ==================================================
# Part 9. Debug Helpers
# ==================================================


# --------------------------------------------------
# Initialize Debug Counters
# --------------------------------------------------

def _init_debug(
    self,
) -> None:
    """
    Initialize runtime statistics.
    """

    self._serialize_count = 0

    self._deserialize_count = 0

    self._snapshot_count = 0

    self._batch_count = 0

    self._error_count = 0



# --------------------------------------------------
# Info
# --------------------------------------------------

def info(
    self,
) -> dict[str, Any]:
    """
    Serializer information.
    """

    return {

        "name":
            self.__class__.__name__,

        "version":
            self._version,

        "format":
            "json",

        "thread_safe":
            True,

    }



# --------------------------------------------------
# Statistics
# --------------------------------------------------

def stats(
    self,
) -> dict[str, int]:
    """
    Runtime statistics.
    """

    return {

        "serialize":
            getattr(
                self,
                "_serialize_count",
                0,
            ),

        "deserialize":
            getattr(
                self,
                "_deserialize_count",
                0,
            ),

        "snapshot":
            getattr(
                self,
                "_snapshot_count",
                0,
            ),

        "batch":
            getattr(
                self,
                "_batch_count",
                0,
            ),

        "errors":
            getattr(
                self,
                "_error_count",
                0,
            ),

    }



# --------------------------------------------------
# Summary
# --------------------------------------------------

def summary(
    self,
) -> dict[str, Any]:
    """
    Human readable summary.
    """

    return {

        **self.info(),

        "statistics":
            self.stats(),

    }



# --------------------------------------------------
# Dump
# --------------------------------------------------

def dump(
    self,
) -> dict[str, Any]:
    """
    Full diagnostic dump.
    """

    return {

        "info":
            self.info(),

        "stats":
            self.stats(),

        "schema":
            self.json_schema(),

    }



# --------------------------------------------------
# Health Check
# --------------------------------------------------

def health(
    self,
) -> dict[str, Any]:
    """
    Serializer health status.
    """

    errors = (
        self.stats()
        .get(
            "errors",
            0,
        )
    )


    return {

        "status":
            (
                "healthy"
                if errors == 0
                else "degraded"
            ),

        "errors":
            errors,

        "version":
            self._version,

    }



# --------------------------------------------------
# Reset Statistics
# --------------------------------------------------

def reset_stats(
    self,
) -> None:
    """
    Reset debug counters.
    """

    self._serialize_count = 0

    self._deserialize_count = 0

    self._snapshot_count = 0

    self._batch_count = 0

    self._error_count = 0
# ==================================================
# Part 10. Thread Safety
# ==================================================


# --------------------------------------------------
# Acquire Lock
# --------------------------------------------------

def acquire(
    self,
    blocking: bool = True,
    timeout: float = -1,
) -> bool:
    """
    Acquire serializer lock.
    """

    return self._lock.acquire(
        blocking,
        timeout,
    )



# --------------------------------------------------
# Release Lock
# --------------------------------------------------

def release(
    self,
) -> None:
    """
    Release serializer lock.
    """

    self._lock.release()



# --------------------------------------------------
# Lock State
# --------------------------------------------------

@property
def locked(
    self,
) -> bool:
    """
    Check lock ownership.

    Debug purpose only.
    """

    checker = getattr(
        self._lock,
        "_is_owned",
        None,
    )


    if checker is None:

        return False


    return checker()



# --------------------------------------------------
# Context Manager
# --------------------------------------------------

def __enter__(
    self,
):
    """
    Enter synchronized block.
    """

    self.acquire()

    return self



def __exit__(
    self,
    exc_type,
    exc_value,
    traceback,
) -> bool:
    """
    Exit synchronized block.
    """

    self.release()

    return False



# --------------------------------------------------
# Thread Safe Execute
# --------------------------------------------------

def synchronized(
    self,
    func,
    *args,
    **kwargs,
):
    """
    Execute function under lock.
    """

    with self._lock:

        return func(
            *args,
            **kwargs,
        )



# --------------------------------------------------
# Safe Statistics Update
# --------------------------------------------------

def increment(
    self,
    counter: str,
    value: int = 1,
) -> None:
    """
    Thread safe counter increment.
    """

    with self._lock:

        current = getattr(
            self,
            counter,
            0,
        )

        setattr(
            self,
            counter,
            current + value,
        )



# --------------------------------------------------
# Safe Read
# --------------------------------------------------

def safe_stats(
    self,
) -> dict[str, Any]:
    """
    Thread safe statistics read.
    """

    with self._lock:

        return self.stats()



# --------------------------------------------------
# Safe Reset
# --------------------------------------------------

def safe_reset(
    self,
) -> None:
    """
    Thread safe reset.
    """

    with self._lock:

        self.reset_stats()



# --------------------------------------------------
# Thread Information
# --------------------------------------------------

def thread_info(
    self,
) -> dict[str, Any]:
    """
    Runtime thread diagnostic.
    """

    import threading


    return {

        "thread":
            threading.current_thread().name,

        "locked":
            self.locked,

        "daemon":
            threading.current_thread().daemon,

    }
                                                