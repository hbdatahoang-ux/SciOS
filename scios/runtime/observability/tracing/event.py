"""
SciOS Runtime Observability
===========================

Atomic trace event model used by the tracing subsystem.

Responsibilities
----------------
- Represent a single runtime event.
- Store lifecycle state, timestamps, payload, tags, metadata, and attributes.
- Support serialization, snapshot/restore, cloning, and diagnostics.
- Provide a stable immutable public API.

Python 3.11+
"""

from __future__ import annotations

import copy
import json

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, TypeAlias
from uuid import uuid4

from .enums import (
    ExecutionPhase,
    Severity,
)

__all__: list[str]

# ==============================================================================
# Part 2. Constants & Type Aliases
# ==============================================================================

DEFAULT_EVENT_NAME = ""

DEFAULT_EVENT_PHASE = ExecutionPhase.CREATED

DEFAULT_EVENT_SEVERITY = Severity.INFO

DEFAULT_EVENT_ATTRIBUTES: dict[str, Any] = {}

DEFAULT_EVENT_METADATA: dict[str, Any] = {}

DEFAULT_EVENT_PAYLOAD: dict[str, Any] = {}

DEFAULT_EVENT_TAGS: dict[str, Any] = {}

EVENT_VERSION = "1.0.0"

EVENT_API_VERSION = "1"

EventAttributeMap: TypeAlias = dict[str, Any]

EventMetadataMap: TypeAlias = dict[str, Any]

EventPayloadMap: TypeAlias = dict[str, Any]

EventTagMap: TypeAlias = dict[str, Any]

EventJSON: TypeAlias = dict[str, Any]


def utcnow() -> datetime:
    """
    Return current UTC time.
    """
    return datetime.now(timezone.utc)


# ==============================================================================
# Part 3. Exceptions & Enums
# ==============================================================================

class EventError(Exception):
    """
    Base exception for Event operations.
    """


class EventValidationError(EventError):
    """
    Raised when an Event is invalid.
    """


class EventSerializationError(EventError):
    """
    Raised when serialization/deserialization fails.
    """


# ==============================================================================
# Part 4. Dataclass
# ==============================================================================

@dataclass(slots=True)
class Event:
    """
    Atomic runtime trace event.
    """

    event_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    name: str = DEFAULT_EVENT_NAME

    phase: ExecutionPhase = DEFAULT_EVENT_PHASE

    timestamp: datetime = field(
        default_factory=utcnow
    )

    severity: Severity = DEFAULT_EVENT_SEVERITY

    attributes: EventAttributeMap = field(
        default_factory=dict
    )

    metadata: EventMetadataMap = field(
        default_factory=dict
    )

    payload: EventPayloadMap = field(
        default_factory=dict
    )

    tags: EventTagMap = field(
        default_factory=dict
    )

    active: bool = False

    completed: bool = False

    failed: bool = False

    cancelled: bool = False

# ==============================================================================
# Part 5. Constructor & Properties
# ==============================================================================

    def __post_init__(self) -> None:
        """
        Validate and normalize the event.
        """
        if not isinstance(
            self.name,
            str,
        ):
            raise EventValidationError(
                "name must be a string."
            )

        self.name = self.name.strip()

        if not self.name:
            raise EventValidationError(
                "event name cannot be empty."
            )

        if not isinstance(
            self.phase,
            ExecutionPhase,
        ):
            raise EventValidationError(
                "phase must be an ExecutionPhase."
            )

        if not isinstance(
            self.severity,
            Severity,
        ):
            raise EventValidationError(
                "severity must be a Severity."
            )

        if not isinstance(
            self.timestamp,
            datetime,
        ):
            raise EventValidationError(
                "timestamp must be a datetime."
            )

        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(
                tzinfo=timezone.utc,
            )

        self.attributes = dict(
            self.attributes
        )

        self.payload = dict(
            self.payload
        )

        self.tags = dict(
            self.tags
        )

    @property
    def has_attributes(self) -> bool:
        """
        Return True if attributes exist.
        """
        return bool(self.attributes)

    @property
    def has_payload(self) -> bool:
        """
        Return True if payload exists.
        """
        return bool(self.payload)

    @property
    def has_tags(self) -> bool:
        """
        Return True if tags exist.
        """
        return bool(self.tags)

    @property
    def attribute_count(self) -> int:
        """
        Return attribute count.
        """
        return len(self.attributes)

    @property
    def payload_count(self) -> int:
        """
        Return payload count.
        """
        return len(self.payload)

    @property
    def tag_count(self) -> int:
        """
        Return tag count.
        """
        return len(self.tags)

    @property
    def is_finished(self) -> bool:
        """
        Return True if lifecycle has ended.
        """
        return (
            self.completed
            or self.failed
            or self.cancelled
        )

    @property
    def is_active(self) -> bool:
        """
        Return True if event is active.
        """
        return self.active
# ==============================================================================
# Part 6. Core API
# ==============================================================================

    def rename(
        self,
        name: str,
    ) -> "Event":
        """
        Rename event.
        """
        name = str(name).strip()

        if not name:
            raise EventValidationError(
                "Event name cannot be empty."
            )

        self.name = name
        return self

    def set_phase(
        self,
        phase: ExecutionPhase,
    ) -> "Event":
        """
        Update execution phase.
        """
        if not isinstance(
            phase,
            ExecutionPhase,
        ):
            raise EventValidationError(
                "Invalid execution phase."
            )

        self.phase = phase
        return self

    def set_severity(
        self,
        severity: Severity,
    ) -> "Event":
        """
        Update event severity.
        """
        if not isinstance(
            severity,
            Severity,
        ):
            raise EventValidationError(
                "Invalid severity."
            )

        self.severity = severity
        return self

    def touch(self) -> "Event":
        """
        Refresh timestamp.
        """
        self.timestamp = utcnow()
        return self

    def activate(self) -> "Event":
        """
        Activate event.
        """
        self.active = True
        self.phase = ExecutionPhase.STARTED
        self.touch()
        return self

    def complete(self) -> "Event":
        """
        Mark event as completed.
        """
        self.completed = True
        self.active = False
        self.phase = ExecutionPhase.COMPLETED
        self.touch()
        return self

    def fail(
        self,
        message: str | None = None,
    ) -> "Event":
        """
        Mark event as failed.
        """
        self.failed = True
        self.active = False
        self.phase = ExecutionPhase.FAILED
        self.severity = Severity.ERROR

        if message:
            self.set_attribute(
                "error",
                str(message),
            )

        self.touch()
        return self

    def cancel(self) -> "Event":
        """
        Cancel event.
        """
        self.cancelled = True
        self.active = False
        self.phase = ExecutionPhase.CANCELLED
        self.touch()
        return self


# ==============================================================================
# Part 7. Payload / Tags / Attributes
# ==============================================================================

    # ------------------------------------------------------------------
    # Attributes
    # ------------------------------------------------------------------

    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> "Event":
        self.attributes[str(key)] = value
        return self

    def get_attribute(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self.attributes.get(
            key,
            default,
        )

    def remove_attribute(
        self,
        key: str,
    ) -> "Event":
        self.attributes.pop(
            key,
            None,
        )
        return self

    def clear_attributes(self) -> "Event":
        self.attributes.clear()
        return self

    # ------------------------------------------------------------------
    # Payload
    # ------------------------------------------------------------------

    def set_payload(
        self,
        key: str,
        value: Any,
    ) -> "Event":
        self.payload[str(key)] = value
        return self

    def update_payload(
        self,
        payload: dict[str, Any],
    ) -> "Event":
        self.payload.update(
            dict(payload)
        )
        return self

    def clear_payload(self) -> "Event":
        self.payload.clear()
        return self

    # ------------------------------------------------------------------
    # Tags
    # ------------------------------------------------------------------

    def set_tag(
        self,
        key: str,
        value: str,
    ) -> "Event":
        self.tags[str(key)] = str(value)
        return self

    def remove_tag(
        self,
        key: str,
    ) -> "Event":
        self.tags.pop(
            key,
            None,
        )
        return self

    def clear_tags(self) -> "Event":
        self.tags.clear()
        return self

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> "Event":
        self.metadata[str(key)] = value
        return self

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self.metadata.get(
            key,
            default,
        )

    def remove_metadata(
        self,
        key: str,
    ) -> "Event":
        self.metadata.pop(
            key,
            None,
        )
        return self

    def clear_metadata(self) -> "Event":
        self.metadata.clear()
        return self


# ==============================================================================
# Part 8. Serialization
# ==============================================================================

    def to_dict(self) -> EventJSON:
        """
        Serialize event.
        """
        return {
            "event_id": self.event_id,
            "name": self.name,
            "phase": self.phase.value,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.value,
            "attributes": dict(self.attributes),
            "metadata": dict(self.metadata),
            "payload": dict(self.payload),
            "tags": dict(self.tags),
            "active": self.active,
            "completed": self.completed,
            "failed": self.failed,
            "cancelled": self.cancelled,
        }

    def to_json(self) -> str:
        """
        Serialize event into JSON.
        """
        try:
            return json.dumps(
                self.to_dict(),
                ensure_ascii=False,
                default=str,
            )

        except Exception as exc:
            raise EventSerializationError(
                "Failed to serialize Event."
            ) from exc

    @classmethod
    def from_dict(
        cls,
        data: EventJSON,
    ) -> "Event":
        """
        Restore event from dictionary.
        """
        try:
            event = cls(
                event_id=data.get(
                    "event_id",
                    str(uuid4()),
                ),
                name=data.get(
                    "name",
                    DEFAULT_EVENT_NAME,
                ),
                phase=ExecutionPhase(
                    data.get(
                        "phase",
                        DEFAULT_EVENT_PHASE.value,
                    )
                ),
                timestamp=datetime.fromisoformat(
                    data.get(
                        "timestamp",
                        utcnow().isoformat(),
                    )
                ),
                severity=Severity(
                    data.get(
                        "severity",
                        DEFAULT_EVENT_SEVERITY.value,
                    )
                ),
                attributes=dict(
                    data.get(
                        "attributes",
                        {},
                    )
                ),
                metadata=dict(
                    data.get(
                        "metadata",
                        {},
                    )
                ),
                payload=dict(
                    data.get(
                        "payload",
                        {},
                    )
                ),
                tags=dict(
                    data.get(
                        "tags",
                        {},
                    )
                ),
                active=data.get(
                    "active",
                    False,
                ),
                completed=data.get(
                    "completed",
                    False,
                ),
                failed=data.get(
                    "failed",
                    False,
                ),
                cancelled=data.get(
                    "cancelled",
                    False,
                ),
            )

            return event

        except Exception as exc:
            raise EventSerializationError(
                "Failed to restore Event."
            ) from exc

    @classmethod
    def from_json(
        cls,
        value: str,
    ) -> "Event":
        """
        Restore event from JSON.
        """
        try:
            return cls.from_dict(
                json.loads(value)
            )

        except Exception as exc:
            raise EventSerializationError(
                "Failed to restore Event from JSON."
            ) from exc
# ==============================================================================
# Part 9. Snapshot / Clone
# ==============================================================================

    def snapshot(self) -> EventJSON:
        """
        Create a serializable snapshot.
        """
        return self.to_dict()

    @classmethod
    def restore(
        cls,
        snapshot: EventJSON,
    ) -> "Event":
        """
        Restore an event from snapshot.
        """
        return cls.from_dict(
            snapshot
        )

    def clone(self) -> "Event":
        """
        Create a deep clone.
        """
        return self.__class__.from_dict(
            copy.deepcopy(
                self.to_dict()
            )
        )

    def copy(self) -> "Event":
        """
        Create a shallow copy.
        """
        return copy.copy(
            self
        )


# ==============================================================================
# Part 10. Diagnostics
# ==============================================================================

    def validate(self) -> bool:
        """
        Validate event integrity.
        """
        if not isinstance(
            self.event_id,
            str,
        ):
            return False

        if (
            not isinstance(
                self.name,
                str,
            )
            or
            not self.name
        ):
            return False

        if not isinstance(
            self.phase,
            ExecutionPhase,
        ):
            return False

        if not isinstance(
            self.timestamp,
            datetime,
        ):
            return False

        if not isinstance(
            self.severity,
            Severity,
        ):
            return False

        if not isinstance(
            self.attributes,
            dict,
        ):
            return False

        if not isinstance(
            self.metadata,
            dict,
        ):
            return False

        if not isinstance(
            self.payload,
            dict,
        ):
            return False

        if not isinstance(
            self.tags,
            dict,
        ):
            return False

        return True

    def diagnostics(self) -> dict[str, Any]:
        """
        Return detailed diagnostics.
        """
        return {
            "valid": self.validate(),
            "event_id": self.event_id,
            "name": self.name,
            "phase": self.phase.value,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.value,
            "attribute_count": len(
                self.attributes
            ),
            "metadata_count": len(
                self.metadata
            ),
            "payload_count": len(
                self.payload
            ),
            "tag_count": len(
                self.tags
            ),
            "active": self.active,
            "completed": self.completed,
            "failed": self.failed,
            "cancelled": self.cancelled,
        }

    def summary(self) -> dict[str, Any]:
        """
        Return compact summary.
        """
        return {
            "event_id": self.event_id,
            "name": self.name,
            "phase": self.phase.value,
            "severity": self.severity.value,
        }


# ==============================================================================
# Part 11. Python Protocols
# ==============================================================================

    def __repr__(self) -> str:
        return (
            f"Event("
            f"event_id={self.event_id!r}, "
            f"name={self.name!r}, "
            f"phase={self.phase.value!r}, "
            f"severity={self.severity.value!r}"
            f")"
        )

    def __str__(self) -> str:
        return (
            f"[{self.timestamp.isoformat()}] "
            f"{self.phase.value}: "
            f"{self.name}"
        )

    def __len__(self) -> int:
        return (
            len(self.attributes)
            +
            len(self.metadata)
            +
            len(self.payload)
            +
            len(self.tags)
        )

    def __contains__(
        self,
        key: str,
    ) -> bool:
        return (
            key in self.attributes
            or
            key in self.metadata
            or
            key in self.payload
            or
            key in self.tags
        )

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        if key in self.attributes:
            return self.attributes[key]

        if key in self.metadata:
            return self.metadata[key]

        if key in self.payload:
            return self.payload[key]

        return self.tags[key]

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.attributes[key] = value

    def __eq__(
        self,
        other: object,
    ) -> bool:
        if not isinstance(
            other,
            Event,
        ):
            return NotImplemented

        return (
            self.event_id
            ==
            other.event_id
        )

    def __hash__(self) -> int:
        return hash(
            self.event_id
        )

    def __copy__(self) -> "Event":
        return self.__class__(
            event_id=self.event_id,
            name=self.name,
            phase=self.phase,
            timestamp=self.timestamp,
            severity=self.severity,
            attributes=dict(
                self.attributes
            ),
            metadata=dict(
                self.metadata
            ),
            payload=dict(
                self.payload
            ),
            tags=dict(
                self.tags
            ),
            active=self.active,
            completed=self.completed,
            failed=self.failed,
            cancelled=self.cancelled,
        )

    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ) -> "Event":
        result = self.__class__(
            event_id=copy.deepcopy(
                self.event_id,
                memo,
            ),
            name=copy.deepcopy(
                self.name,
                memo,
            ),
            phase=self.phase,
            timestamp=copy.deepcopy(
                self.timestamp,
                memo,
            ),
            severity=self.severity,
            attributes=copy.deepcopy(
                self.attributes,
                memo,
            ),
            metadata=copy.deepcopy(
                self.metadata,
                memo,
            ),
            payload=copy.deepcopy(
                self.payload,
                memo,
            ),
            tags=copy.deepcopy(
                self.tags,
                memo,
            ),
            active=self.active,
            completed=self.completed,
            failed=self.failed,
            cancelled=self.cancelled,
        )

        memo[id(self)] = result

        return result


# ==============================================================================
# Part 12. Public API
# ==============================================================================

__all__ = [

    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    "DEFAULT_EVENT_NAME",
    "DEFAULT_EVENT_PHASE",
    "DEFAULT_EVENT_SEVERITY",
    "DEFAULT_EVENT_ATTRIBUTES",
    "DEFAULT_EVENT_METADATA",
    "DEFAULT_EVENT_PAYLOAD",
    "DEFAULT_EVENT_TAGS",

    "EVENT_VERSION",
    "EVENT_API_VERSION",

    # ------------------------------------------------------------------
    # Type Aliases
    # ------------------------------------------------------------------

    "EventAttributeMap",
    "EventMetadataMap",
    "EventPayloadMap",
    "EventTagMap",
    "EventJSON",

    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    "EventError",
    "EventValidationError",
    "EventSerializationError",

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    "utcnow",

    # ------------------------------------------------------------------
    # Core Model
    # ------------------------------------------------------------------

    "Event",
]                                