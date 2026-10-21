"""
Tracing Span Entity.

Defines the foundational Span entity API, constants,
exceptions, and type aliases.

Dependency order:

    status.py
        â†“
    enums.py
        â†“
    attributes.py
        â†“
    baggage.py
        â†“
    context.py / link.py / event.py
        â†“
    span.py

Python 3.11+
"""

from __future__ import annotations


# ==============================================================================
# Standard Library
# ==============================================================================

import copy

from datetime import datetime

from typing import (
    Any,
    Mapping,
    MutableMapping,
    Sequence,
    TypeAlias,
)

from uuid import uuid4


# ==============================================================================
# Public API
# ==============================================================================

__all__ = [

    # --------------------------------------------------------------------------
    # Constants
    # --------------------------------------------------------------------------

    "SPAN_VERSION",
    "SPAN_API_VERSION",

    "DEFAULT_SPAN_NAME",
    "DEFAULT_SPAN_KIND",
    "DEFAULT_SPAN_STATUS",

    "DEFAULT_SPAN_AUTO_START",
    "DEFAULT_SPAN_AUTO_FINISH",

    # --------------------------------------------------------------------------
    # Exceptions
    # --------------------------------------------------------------------------

    "SpanError",
    "SpanValidationError",
    "SpanStateError",

    "SpanClosedError",
    "SpanAlreadyStartedError",
    "SpanAlreadyFinishedError",

    "SpanNotStartedError",
    "SpanNotFinishedError",

    "SpanFrozenError",
    "SpanCancelledError",

    # --------------------------------------------------------------------------
    # Type Aliases
    # --------------------------------------------------------------------------

    "SpanId",
    "TraceId",
    "ParentSpanId",
    "SpanName",

    "SpanAttributeKey",
    "SpanAttributeValue",
    "SpanAttributes",

    "Timestamp",
]


# ==============================================================================
# Part 1. Constants
# ==============================================================================

SPAN_VERSION = "1.0.0"

SPAN_API_VERSION = "1"


DEFAULT_SPAN_NAME = "Span"

DEFAULT_SPAN_KIND = "internal"

DEFAULT_SPAN_STATUS = "unset"


DEFAULT_SPAN_AUTO_START = False

DEFAULT_SPAN_AUTO_FINISH = True


# ==============================================================================
# Part 2. Exceptions
# ==============================================================================


class SpanError(RuntimeError):
    """
    Base exception for the Span subsystem.
    """


class SpanValidationError(SpanError):
    """
    Raised when Span configuration or input is invalid.
    """


class SpanStateError(SpanError):
    """
    Raised when an operation is incompatible with Span state.
    """


class SpanClosedError(SpanStateError):
    """
    Raised when an operation is attempted on a closed Span.
    """


class SpanAlreadyStartedError(SpanStateError):
    """
    Raised when a Span is started more than once.
    """


class SpanAlreadyFinishedError(SpanStateError):
    """
    Raised when a Span is finished more than once.
    """


class SpanNotStartedError(SpanStateError):
    """
    Raised when an operation requires a started Span.
    """


class SpanNotFinishedError(SpanStateError):
    """
    Raised when an operation requires a finished Span.
    """


class SpanFrozenError(SpanStateError):
    """
    Raised when mutation is attempted on a frozen Span.
    """


class SpanCancelledError(SpanStateError):
    """
    Raised when an operation is attempted on a cancelled Span.
    """


# ==============================================================================
# Part 3. Type Aliases
# ==============================================================================

SpanId: TypeAlias = str

TraceId: TypeAlias = str

ParentSpanId: TypeAlias = str | None

SpanName: TypeAlias = str


SpanAttributeKey: TypeAlias = str


SpanAttributeValue: TypeAlias = (
    str
    | int
    | float
    | bool
    | bytes
    | Sequence[Any]
    | Mapping[str, Any]
    | None
)


SpanAttributes: TypeAlias = dict[
    SpanAttributeKey,
    SpanAttributeValue,
]


Timestamp: TypeAlias = datetime

# ==============================================================================
# Part 4. Span
# ==============================================================================


class Span:
    """
    Runtime tracing Span entity.

    A Span represents one unit of work inside a Trace.

    The Span is intentionally independent from TraceManager.
    Manager-level orchestration will be added later.
    """

    # ==========================================================================
    # 4.1 Constructor
    # ==========================================================================

    def __init__(
        self,
        name: str = DEFAULT_SPAN_NAME,
        *,
        span_id: SpanId | None = None,
        trace_id: TraceId | None = None,
        parent_id: ParentSpanId = None,
        component: str | None = None,
        task_id: str | None = None,
        kind: str = DEFAULT_SPAN_KIND,
        status: str = DEFAULT_SPAN_STATUS,
        auto_start: bool = DEFAULT_SPAN_AUTO_START,
        auto_finish: bool = DEFAULT_SPAN_AUTO_FINISH,
        attributes: Mapping[
            SpanAttributeKey,
            SpanAttributeValue,
        ] | None = None,
    ) -> None:
        """
        Initialize a Span entity.
        """

        # ----------------------------------------------------------------------
        # Validate name
        # ----------------------------------------------------------------------

        if not isinstance(name, str):
            raise SpanValidationError(
                "name must be a string"
            )

        name = name.strip()

        if not name:
            raise SpanValidationError(
                "name cannot be empty"
            )

        # ----------------------------------------------------------------------
        # Validate span_id
        # ----------------------------------------------------------------------

        if span_id is not None:

            if not isinstance(span_id, str):
                raise SpanValidationError(
                    "span_id must be a string or None"
                )

            span_id = span_id.strip()

            if not span_id:
                raise SpanValidationError(
                    "span_id cannot be empty"
                )

        # ----------------------------------------------------------------------
        # Validate trace_id
        # ----------------------------------------------------------------------

        if trace_id is not None:

            if not isinstance(trace_id, str):
                raise SpanValidationError(
                    "trace_id must be a string or None"
                )

            trace_id = trace_id.strip()

            if not trace_id:
                raise SpanValidationError(
                    "trace_id cannot be empty"
                )

        # ----------------------------------------------------------------------
        # Validate parent_id
        # ----------------------------------------------------------------------

        if parent_id is not None:

            if not isinstance(parent_id, str):
                raise SpanValidationError(
                    "parent_id must be a string or None"
                )

            parent_id = parent_id.strip()

            if not parent_id:
                raise SpanValidationError(
                    "parent_id cannot be empty"
                )

        # ----------------------------------------------------------------------
        # Validate component
        # ----------------------------------------------------------------------

        if component is not None:

            if not isinstance(component, str):
                raise SpanValidationError(
                    "component must be a string or None"
                )

            component = component.strip()

            if not component:
                raise SpanValidationError(
                    "component cannot be empty"
                )

        # ----------------------------------------------------------------------
        # Validate task_id
        # ----------------------------------------------------------------------

        if task_id is not None:

            if not isinstance(task_id, str):
                raise SpanValidationError(
                    "task_id must be a string or None"
                )

            task_id = task_id.strip()

            if not task_id:
                raise SpanValidationError(
                    "task_id cannot be empty"
                )

        # ----------------------------------------------------------------------
        # Validate configuration
        # ----------------------------------------------------------------------

        if not isinstance(kind, str):
            raise SpanValidationError(
                "kind must be a string"
            )

        if not isinstance(status, str):
            raise SpanValidationError(
                "status must be a string"
            )

        if not isinstance(auto_start, bool):
            raise SpanValidationError(
                "auto_start must be bool"
            )

        if not isinstance(auto_finish, bool):
            raise SpanValidationError(
                "auto_finish must be bool"
            )

        # ----------------------------------------------------------------------
        # Identity
        # ----------------------------------------------------------------------

        self._id: SpanId = (
            span_id
            if span_id is not None
            else self._generate_id()
        )

        self._trace_id: TraceId | None = trace_id

        self._parent_id: ParentSpanId = parent_id

        self._name: SpanName = name

        self._component: str | None = component

        self._task_id: str | None = task_id

        # ----------------------------------------------------------------------
        # Configuration
        # ----------------------------------------------------------------------

        self._kind: str = kind

        self._status: str = status

        self._auto_start: bool = auto_start

        self._auto_finish: bool = auto_finish

        # ----------------------------------------------------------------------
        # Lifecycle
        # ----------------------------------------------------------------------

        self._state: str = "created"

        self._started: bool = False

        self._finished: bool = False

        self._cancelled: bool = False

        self._closed: bool = False

        self._frozen: bool = False

        self._start_time: Timestamp | None = None

        self._end_time: Timestamp | None = None

        # ----------------------------------------------------------------------
        # Metadata
        # ----------------------------------------------------------------------

        self._attributes: SpanAttributes = dict(
            attributes
            if attributes is not None
            else {}
        )

        self._tags: dict[
            str,
            Any,
        ] = {}

        self._baggage: dict[
            str,
            Any,
        ] = {}

        # ----------------------------------------------------------------------
        # Child collections
        # ----------------------------------------------------------------------

        self._events: list[Any] = []

        self._links: list[Any] = []

        # ----------------------------------------------------------------------
        # Error / exception state
        # ----------------------------------------------------------------------

        self._exception: BaseException | None = None

        # ----------------------------------------------------------------------
        # Context
        # ----------------------------------------------------------------------

        self._context: Any | None = None

        self._context_id: str | None = None

        # ----------------------------------------------------------------------
        # Automatic lifecycle
        # ----------------------------------------------------------------------

        if self._auto_start:
            self.start()


    # ==========================================================================
    # 4.2 Identity
    # ==========================================================================

    @property
    def id(self) -> SpanId:
        return self._id


    @property
    def span_id(self) -> SpanId:
        return self._id


    @property
    def trace_id(self) -> TraceId | None:
        return self._trace_id


    @property
    def parent_id(self) -> ParentSpanId:
        return self._parent_id


    @property
    def parent_span_id(self) -> ParentSpanId:
        """Return the parent span identifier."""
        return self._parent_id


    @property
    def component(self) -> str | None:
        """Return the component associated with this span."""
        return self._component


    @property
    def task_id(self) -> str | None:
        """Return the task identifier associated with this span."""
        return self._task_id


    @property
    def name(self) -> SpanName:
        return self._name


    @property
    def kind(self) -> str:
        return self._kind


    # ==========================================================================
    # 4.3 Lifecycle
    # ==========================================================================

    def start(self) -> "Span":
        """
        Start the Span.
        """

        self._ensure_mutable()

        if self._started:
            raise SpanAlreadyStartedError(
                "Span has already been started"
            )

        if self._finished:
            raise SpanStateError(
                "Finished Span cannot be started"
            )

        if self._cancelled:
            raise SpanCancelledError(
                "Cancelled Span cannot be started"
            )

        self._start_time = self._now()
        self._started = True
        self._finished = False
        self._cancelled = False
        self._state = "running"

        return self

    def finish(
        self,
        *,
        end_time: Timestamp | None = None,
    ) -> "Span":
        """
        Finish the Span.
        """

        self._ensure_mutable()

        if not self._started:
            raise SpanNotStartedError(
                "Cannot finish a Span that has not started"
            )

        if self._finished:
            raise SpanAlreadyFinishedError(
                "Span has already been finished"
            )

        if self._cancelled:
            raise SpanCancelledError(
                "Cancelled Span cannot be finished"
            )

        if end_time is not None:
            if not isinstance(end_time, datetime):
                raise SpanValidationError(
                    "end_time must be datetime or None"
                )

            if (
                self._start_time is not None
                and end_time < self._start_time
            ):
                raise SpanValidationError(
                    "end_time cannot be before start_time"
                )

            self._end_time = end_time
        else:
            self._end_time = self._now()

        self._finished = True
        self._state = "finished"

        return self

    def reset(self) -> "Span":
        """
        Reset the Span to its initial lifecycle state.
        """

        self._ensure_mutable()

        self._state = "created"
        self._started = False
        self._finished = False
        self._cancelled = False
        self._closed = False

        self._start_time = None
        self._end_time = None
        self._exception = None

        return self

    def restart(self) -> "Span":
        """
        Reset and start the Span again.
        """

        self.reset()
        return self.start()

    def cancel(self) -> "Span":
        """
        Cancel the Span.
        """

        self._ensure_mutable()

        if not self._started:
            raise SpanNotStartedError(
                "Cannot cancel a Span that has not started"
            )

        if self._finished:
            raise SpanAlreadyFinishedError(
                "Finished Span cannot be cancelled"
            )

        self._cancelled = True
        self._state = "cancelled"
        self._end_time = self._now()

        return self

    def close(self) -> "Span":
        """
        Permanently close the Span.
        """

        if self._closed:
            return self

        if (
            self._started
            and not self._finished
            and not self._cancelled
            and self._auto_finish
        ):
            self.finish()

        self._closed = True
        self._state = "closed"
        self._frozen = True

        return self

    def freeze(self) -> "Span":
        """
        Freeze the Span against further mutation.
        """

        self._ensure_not_closed()
        self._frozen = True

        return self

    def unfreeze(self) -> "Span":
        """
        Unfreeze the Span.
        """

        self._ensure_not_closed()
        self._frozen = False

        return self

    # ==========================================================================
    # Internal Utilities
    # ==========================================================================

    @staticmethod
    def _generate_id() -> SpanId:
        """
        Generate a unique Span identifier.
        """

        return uuid4().hex

    @staticmethod
    def _now() -> Timestamp:
        """
        Return the current UTC timestamp.
        """

        return datetime.now().astimezone()

    def _ensure_not_closed(self) -> None:
        """
        Ensure the Span has not been permanently closed.
        """

        if self._closed:
            raise SpanClosedError(
                "Span is closed"
            )

    def _ensure_mutable(self) -> None:
        """
        Ensure that the Span can still be mutated.
        """

        self._ensure_not_closed()

        if self._frozen:
            raise SpanFrozenError(
                "Span is frozen"
            )

    def _ensure_started(self) -> None:
        """
        Ensure that the Span has been started.
        """

        self._ensure_not_closed()

        if not self._started:
            raise SpanNotStartedError(
                "Span has not been started"
            )



    # ==========================================================================
    # 4.4 State
    # ==========================================================================

    @property
    def status(self) -> str:
        return self._status

    def set_status(
        self,
        status: str,
        description: str | None = None,
    ) -> "Span":
        """
        Set the Span status.

        The public ``status`` property remains read-only;
        mutation is performed through this method so that
        Span lifecycle invariants are preserved.
        """

        self._ensure_mutable()

        if not isinstance(status, str):
            raise SpanValidationError(
                "status must be a string"
            )

        status = status.strip()

        if not status:
            raise SpanValidationError(
                "status cannot be empty"
            )

        self._status = status

        self._status_description: str | None = None

        if status.lower() in {
            "error",
            "failed",
            "failure",
        }:
            self._state = "error"

        # Keep the description optional and backward-compatible.
        if description is not None:
            if not isinstance(description, str):
                raise SpanValidationError(
                    "status description must be a string or None"
                )

            self._status_description = description

        return self

    @property
    def state(self) -> str:
        return self._state

    @property
    def started(self) -> bool:
        return self._started

    @property
    def finished(self) -> bool:
        return self._finished

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def frozen(self) -> bool:
        return self._frozen

    @property
    def active(self) -> bool:
        return (
            self._started
            and not self._finished
            and not self._cancelled
            and not self._closed
        )

    # ==========================================================================
    # 4.5 Timing
    # ==========================================================================

    @property
    def start_time(self) -> Timestamp | None:
        return self._start_time


    @property
    def end_time(self) -> Timestamp | None:
        return self._end_time


    @property
    def duration(self) -> float:
        """
        Return the completed Span duration in seconds.

        A Span that has not started or has been reset has
        zero duration.
        """

        if self._start_time is None:
            return 0.0

        if self._end_time is None:
            return 0.0

        return max(
            0.0,
            (
                self._end_time - self._start_time
            ).total_seconds(),
        )


    @property
    def elapsed(self) -> float:
        """
        Return elapsed Span time in seconds.

        A Span that has not started or has been reset
        has zero elapsed time.

        A running Span is measured until now.
        A finished Span is measured until end_time.
        """

        if self._start_time is None:
            return 0.0

        end_time = self._end_time

        if end_time is None:
            end_time = datetime.now(
                tz=self._start_time.tzinfo
            ) if self._start_time.tzinfo is not None else datetime.now()

        return max(
            0.0,
            (
                end_time - self._start_time
            ).total_seconds(),
        )


    # ==========================================================================
    # 4.6 Attributes
    # ==========================================================================

    @property
    def attributes(
        self,
    ) -> dict[
        SpanAttributeKey,
        SpanAttributeValue,
    ]:
        """
        Return a copy of Span attributes.
        """

        return dict(
            self._attributes,
        )


    def set_attribute(
        self,
        key: SpanAttributeKey,
        value: SpanAttributeValue,
    ) -> "Span":
        """
        Set a Span attribute.

        Returns:
            Span: self, enabling fluent mutation.
        """

        self._ensure_mutable()

        if not isinstance(
            key,
            str,
        ):
            raise SpanValidationError(
                "attribute key must be a string"
            )

        key = key.strip()

        if not key:
            raise SpanValidationError(
                "attribute key cannot be empty"
            )

        self._attributes[key] = value

        return self


    def get_attribute(
        self,
        key: SpanAttributeKey,
        default: Any = None,
    ) -> Any:
        """
        Return an attribute value.
        """

        return self._attributes.get(
            key,
            default,
        )


    def has_attribute(
        self,
        key: SpanAttributeKey,
    ) -> bool:
        """
        Return whether an attribute exists.
        """

        return key in self._attributes


    def remove_attribute(
        self,
        key: SpanAttributeKey,
    ) -> "Span":
        """
        Remove an attribute.

        Returns:
            Span: self, enabling fluent mutation.
        """

        self._ensure_mutable()

        self._attributes.pop(
            key,
            None,
        )

        return self


    def clear_attributes(
        self,
    ) -> "Span":
        """
        Remove all attributes.
        """

        self._ensure_mutable()

        self._attributes.clear()

        return self


    # ==========================================================================
    # 4.7 Tags
    # ==========================================================================

    @property
    def tags(self) -> dict[str, Any]:
        """
        Return a copy of Span tags.

        Tags are key/value metadata, consistent with attributes.
        """

        return dict(
            self._tags
        )


    def set_tag(
        self,
        key: str,
        value: Any = True,
    ) -> "Span":
        """
        Set a Span tag.

        Tags are represented as a dictionary.
        """

        self._ensure_mutable()

        if not isinstance(
            key,
            str,
        ):
            raise SpanValidationError(
                "tag key must be a string"
            )

        key = key.strip()

        if not key:
            raise SpanValidationError(
                "tag key cannot be empty"
            )

        self._tags[key] = value

        return self


    def get_tag(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Return a Span tag.
        """

        return self._tags.get(
            key,
            default,
        )


    def has_tag(
        self,
        key: str,
    ) -> bool:
        """
        Return whether a tag exists.
        """

        return key in self._tags


    def remove_tag(
        self,
        key: str,
    ) -> "Span":
        """
        Remove a Span tag.

        Mutation methods use fluent API semantics.
        """

        self._ensure_mutable()

        self._tags.pop(
            key,
            None,
        )

        return self


    def clear_tags(
        self,
    ) -> "Span":
        """
        Remove all Span tags.
        """

        self._ensure_mutable()

        self._tags.clear()

        return self


    # ==========================================================================
    # 4.8 Baggage
    # ==========================================================================

    @property
    def baggage(self) -> dict[str, Any]:
        """
        Return a copy of Span baggage.
        """

        return dict(
            self._baggage,
        )

    def set_baggage(
        self,
        key: str,
        value: Any,
    ) -> "Span":
        """
        Set a baggage item.
        """

        self._ensure_mutable()

        if not isinstance(
            key,
            str,
        ):
            raise SpanValidationError(
                "baggage key must be a string"
            )

        key = key.strip()

        if not key:
            raise SpanValidationError(
                "baggage key cannot be empty"
            )

        self._baggage[key] = value

        return self

    def get_baggage(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Return a baggage value.
        """

        return self._baggage.get(
            key,
            default,
        )

    def has_baggage(
        self,
        key: str,
    ) -> bool:
        """
        Return whether a baggage item exists.
        """

        return key in self._baggage

    def remove_baggage(
        self,
        key: str,
    ) -> "Span":
        """
        Remove a baggage item.

        Returns:
            Span: self, enabling fluent mutation.
        """

        self._ensure_mutable()

        self._baggage.pop(
            key,
            None,
        )

        return self

    def clear_baggage(
        self,
    ) -> "Span":
        """
        Remove all baggage.
        """

        self._ensure_mutable()

        self._baggage.clear()

        return self


    # ==========================================================================
    # 4.9 Events
    # ==========================================================================

    @property
    def events(self) -> list[Any]:
        """
        Return a copy of all Span events.
        """

        return list(
            self._events,
        )

    def add_event(
        self,
        event: Any,
        attributes: Mapping[str, Any] | None = None,
        timestamp: Timestamp | None = None,
    ) -> "Span":
        """
        Add an event to the Span.

        Supported forms:

            add_event("started")

            add_event(
                "started",
                attributes={"source": "test"},
            )

            add_event(existing_event)

        String event names are converted into a lightweight
        event object exposing:

            event.name
            event.attributes
            event.timestamp
        """

        self._ensure_mutable()

        if event is None:
            raise SpanValidationError(
                "event cannot be None"
            )

        if isinstance(
            event,
            str,
        ):
            from types import SimpleNamespace

            event = SimpleNamespace(
                name=event,
                attributes=dict(
                    attributes or {},
                ),
                timestamp=timestamp
                if timestamp is not None
                else datetime.now(),
            )

        elif attributes is not None:
            existing_attributes = getattr(
                event,
                "attributes",
                None,
            )

            if isinstance(
                existing_attributes,
                Mapping,
            ):
                existing_attributes.update(
                    attributes,
                )

            else:
                try:
                    setattr(
                        event,
                        "attributes",
                        dict(
                            attributes,
                        ),
                    )
                except Exception:
                    pass

        self._events.append(
            event,
        )

        return self

    def get_event(
        self,
        identifier: Any,
        default: Any = None,
    ) -> Any:
        """
        Return an event by index or event name.

        Supported forms:

            get_event(0)

            get_event("started")
        """

        if isinstance(
            identifier,
            int,
        ):
            try:
                return self._events[
                    identifier
                ]
            except IndexError:
                return default

        if isinstance(
            identifier,
            str,
        ):
            for event in self._events:
                event_name = getattr(
                    event,
                    "name",
                    None,
                )

                if event_name == identifier:
                    return event

            return default

        raise SpanValidationError(
            "event identifier must be an integer or string"
        )

    def clear_events(
        self,
    ) -> "Span":
        """
        Remove all events from the Span.
        """

        self._ensure_mutable()

        self._events.clear()

        return self


    # ==========================================================================
    # 4.10 Links
    # ==========================================================================

    @property
    def links(self) -> list[Any]:
        """
        Return a copy of all Span links.
        """

        return list(
            self._links,
        )

    def add_link(
        self,
        link: Any,
    ) -> "Span":
        """
        Add a link to the Span.
        """

        self._ensure_mutable()

        if link is None:
            raise SpanValidationError(
                "link cannot be None"
            )

        self._links.append(
            link,
        )

        return self

    def clear_links(
        self,
    ) -> "Span":
        """
        Remove all links from the Span.
        """

        self._ensure_mutable()

        self._links.clear()

        return self


    # ==========================================================================
    # 4.11 Context
    # ==========================================================================

    @property
    def context(
        self,
    ) -> Any | None:
        """
        Return the Span context.
        """

        return getattr(
            self,
            "_context",
            None,
        )


    @context.setter
    def context(
        self,
        value: Any | None,
    ) -> None:
        """
        Set the Span context.

        A context assignment also establishes
        a context_id when the supplied context
        does not already provide one.
        """

        self._ensure_mutable()

        self._context = value

        if value is None:
            self._context_id = None
            return

        context_id = getattr(
            value,
            "id",
            None,
        )

        if context_id is None:
            context_id = getattr(
                value,
                "context_id",
                None,
            )

        if context_id is None and isinstance(
            value,
            Mapping,
        ):
            context_id = value.get(
                "context_id",
            )

            if context_id is None:
                context_id = value.get(
                    "id",
                )

        if context_id is None:
            context_id = str(
                uuid4(),
            )

        self._context_id = str(
            context_id,
        )


    @property
    def context_id(
        self,
    ) -> str | None:
        """
        Return the context identifier.
        """

        context_id = getattr(
            self,
            "_context_id",
            None,
        )

        if context_id is not None:
            return str(
                context_id,
            )

        context = getattr(
            self,
            "_context",
            None,
        )

        if context is None:
            return None

        context_id = getattr(
            context,
            "id",
            None,
        )

        if context_id is not None:
            return str(
                context_id,
            )

        context_id = getattr(
            context,
            "context_id",
            None,
        )

        if context_id is not None:
            return str(
                context_id,
            )

        if isinstance(
            context,
            Mapping,
        ):
            context_id = context.get(
                "context_id",
            )

            if context_id is None:
                context_id = context.get(
                    "id",
                )

            if context_id is not None:
                return str(
                    context_id,
                )

        return None


    # ==========================================================================
    # 4.12 Parent / Children
    # ==========================================================================

    @property
    def parent(self) -> Any | None:
        """
        Return the parent Span.
        """

        return getattr(
            self,
            "_parent",
            None,
        )

    @parent.setter
    def parent(
        self,
        value: Any | None,
    ) -> None:
        """
        Set the parent Span.
        """

        self._ensure_mutable()

        self._parent = value

        if value is None:
            return

        parent_id = getattr(
            value,
            "id",
            None,
        )

        if parent_id is not None:
            self._parent_id = str(
                parent_id,
            )

    @property
    def children(self) -> list[Any]:
        """
        Return a copy of child Spans.
        """

        return list(
            getattr(
                self,
                "_children",
                [],
            ),
        )

    def add_child(
        self,
        child: Any,
    ) -> "Span":
        """
        Add a child Span and establish the
        parent/child relationship.
        """

        self._ensure_mutable()

        if child is None:
            raise SpanValidationError(
                "child cannot be None"
            )

        if child is self:
            raise SpanValidationError(
                "Span cannot be its own child"
            )

        if not hasattr(
            self,
            "_children",
        ):
            self._children = []

        if child not in self._children:
            self._children.append(
                child
            )

        if isinstance(
            child,
            Span,
        ):
            child.parent = self

        return self

    def remove_child(
        self,
        child: Any,
    ) -> "Span":
        """
        Remove a child Span and clear its parent
        when this Span is its parent.
        """

        self._ensure_mutable()

        children = getattr(
            self,
            "_children",
            [],
        )

        if child in children:
            children.remove(
                child
            )

        if isinstance(
            child,
            Span,
        ):
            if child.parent is self:
                child._parent = None
                child._parent_id = None

        return self

    @property
    def child_count(self) -> int:
        """
        Return the number of child Spans.
        """

        return len(
            getattr(
                self,
                "_children",
                [],
            ),
        )


    # ==========================================================================
    # 4.13 Error / Exception
    # ==========================================================================

    @property
    def exception(self) -> BaseException | None:
        """
        Return the attached exception.
        """

        return self._exception

    @property
    def error(self) -> bool:
        """
        Return whether the Span is in an error state.
        """

        return (
            self._exception is not None
            or self._status.lower()
            in {
                "error",
                "failed",
                "failure",
            }
        )

    @property
    def failed(self) -> bool:
        """
        Alias for error state.
        """

        return self.error

    def attach_exception(
        self,
        exception: BaseException,
    ) -> "Span":
        """
        Attach an exception to the Span
        and transition it into an error state.
        """

        self._ensure_mutable()

        if not isinstance(
            exception,
            BaseException,
        ):
            raise SpanValidationError(
                "exception must be BaseException"
            )

        self._exception = exception

        self._status = "error"

        self._state = "error"

        return self


    # ==========================================================================
    # 4.14 Diagnostics
    # ==========================================================================

    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Return a compact Span summary.
        """

        return {
            "span": self.__class__.__name__,
            "id": self.id,
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "kind": self.kind,
            "status": self.status,
            "state": self.state,
            "started": self.started,
            "finished": self.finished,
            "cancelled": self.cancelled,
            "closed": self.closed,
            "frozen": self.frozen,
            "active": self.active,
            "duration": self.duration,
            "elapsed": self.elapsed,
            "attribute_count": len(
                self._attributes,
            ),
            "tag_count": len(
                self._tags,
            ),
            "baggage_count": len(
                self._baggage,
            ),
            "event_count": len(
                self._events,
            ),
            "link_count": len(
                self._links,
            ),
            "child_count": self.child_count,
            "context_id": self.context_id,
            "has_exception": (
                self._exception is not None
            ),
            "error": self.error,
        }


    def diagnostics(
        self,
    ) -> dict[str, Any]:
        """
        Return detailed Span diagnostics.

        The returned structure is observational only and
        does not mutate the Span.
        """

        return {
            "summary": self.summary(),
            "attributes": self.attributes,
            "tags": self.tags,
            "baggage": self.baggage,
            "events": self.events,
            "links": self.links,
            "context_id": self.context_id,
            "exception": (
                repr(
                    self.exception,
                )
                if self.exception is not None
                else None
            ),
        }


    def validate(
        self,
    ) -> bool:
        try:
            if not isinstance(self._id, str) or not self._id.strip():
                return False

            if not isinstance(self._name, str) or not self._name.strip():
                return False

            if self._trace_id is not None and not isinstance(
                self._trace_id,
                str,
            ):
                return False

            if self._parent_id is not None and not isinstance(
                self._parent_id,
                str,
            ):
                return False

            if self._started and self._start_time is None:
                return False

            if self._finished and self._end_time is None:
                return False

            if (
                self._start_time is not None
                and self._end_time is not None
                and self._end_time < self._start_time
            ):
                return False

            if (
                self._closed
                and not self._finished
                and not self._cancelled
            ):
                return False

            if self._frozen and not self._closed:
                return False

            if not isinstance(self._attributes, dict):
                return False

            if not isinstance(self._tags, dict):
                return False

            if not isinstance(self._baggage, dict):
                return False

            if not isinstance(self._events, list):
                return False

            if not isinstance(self._links, list):
                return False

            return True

        except Exception:
            return False


    def health(
        self,
    ) -> bool:
        """
        Return whether the Span is internally healthy.
        """

        try:
            return self.validate()

        except Exception:
            return False


    # ==========================================================================
    # 4.15 Serialization
    # ==========================================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize the Span into a dictionary.
        """

        return {
            "id": self.id,
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_id": self.parent_id,

            "name": self.name,
            "kind": self.kind,
            "status": self.status,
            "state": self.state,

            "started": self.started,
            "finished": self.finished,
            "cancelled": self.cancelled,
            "closed": self.closed,
            "frozen": self.frozen,
            "active": self.active,

            "start_time": (
                self.start_time.isoformat()
                if self.start_time is not None
                else None
            ),

            "end_time": (
                self.end_time.isoformat()
                if self.end_time is not None
                else None
            ),

            "duration": self.duration,
            "elapsed": self.elapsed,

            "attributes": copy.deepcopy(
                self.attributes,
            ),

            "tags": copy.deepcopy(
                self._tags,
            ),

            "baggage": copy.deepcopy(
                self.baggage,
            ),

            "events": [
                {
                    "name": getattr(
                        event,
                        "name",
                        None,
                    ),
                    "attributes": copy.deepcopy(
                        getattr(
                            event,
                            "attributes",
                            {},
                        ),
                    ),
                    "timestamp": (
                        getattr(
                            event,
                            "timestamp",
                            None,
                        ).isoformat()
                        if getattr(
                            event,
                            "timestamp",
                            None,
                        ) is not None
                        else None
                    ),
                }
                if hasattr(
                    event,
                    "name",
                )
                else copy.deepcopy(
                    event,
                )
                for event in self._events
            ],

            "links": copy.deepcopy(
                self._links,
            ),

            "context_id": self.context_id,

            "child_count": self.child_count,

            "exception": (
                repr(
                    self.exception,
                )
                if self.exception is not None
                else None
            ),

            "error": self.error,
        }


    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Return an independent Span snapshot.
        """

        return copy.deepcopy(
            self.to_dict(),
        )


    @classmethod
    def from_snapshot(
        cls,
        snapshot: Mapping[str, Any],
    ) -> "Span":
        """
        Restore a Span from a serialized snapshot.
        """

        if not isinstance(
            snapshot,
            Mapping,
        ):
            raise SpanValidationError(
                "snapshot must be a mapping",
            )

        # ----------------------------------------------------------------------
        # Timestamps
        # ----------------------------------------------------------------------

        start_time = snapshot.get(
            "start_time",
        )

        end_time = snapshot.get(
            "end_time",
        )

        if isinstance(
            start_time,
            str,
        ):
            try:
                start_time = datetime.fromisoformat(
                    start_time,
                )
            except ValueError as exc:
                raise SpanValidationError(
                    "invalid start_time",
                ) from exc

        if isinstance(
            end_time,
            str,
        ):
            try:
                end_time = datetime.fromisoformat(
                    end_time,
                )
            except ValueError as exc:
                raise SpanValidationError(
                    "invalid end_time",
                ) from exc

        # ----------------------------------------------------------------------
        # Identity
        # ----------------------------------------------------------------------

        span_id = snapshot.get(
            "span_id",
            snapshot.get(
                "id",
            ),
        )

        # ----------------------------------------------------------------------
        # Construction
        # ----------------------------------------------------------------------

        restored = cls(
            name=snapshot.get(
                "name",
                DEFAULT_SPAN_NAME,
            ),

            span_id=span_id,

            trace_id=snapshot.get(
                "trace_id",
            ),

            parent_id=snapshot.get(
                "parent_id",
            ),

            kind=snapshot.get(
                "kind",
                DEFAULT_SPAN_KIND,
            ),

            status=snapshot.get(
                "status",
                DEFAULT_SPAN_STATUS,
            ),

            auto_start=False,

            auto_finish=snapshot.get(
                "auto_finish",
                DEFAULT_SPAN_AUTO_FINISH,
            ),

            attributes=copy.deepcopy(
                snapshot.get(
                    "attributes",
                    {},
                ),
            ),
        )

        # ----------------------------------------------------------------------
        # Identity fallback
        # ----------------------------------------------------------------------

        if span_id is not None:
            restored._id = str(
                span_id,
            )

        # ----------------------------------------------------------------------
        # Version
        # ----------------------------------------------------------------------

        if hasattr(
            restored,
            "_version",
        ):
            restored._version = snapshot.get(
                "version",
                restored._version,
            )

        # ----------------------------------------------------------------------
        # Lifecycle
        # ----------------------------------------------------------------------

        restored._state = snapshot.get(
            "state",
            "created",
        )

        restored._started = bool(
            snapshot.get(
                "started",
                False,
            ),
        )

        restored._finished = bool(
            snapshot.get(
                "finished",
                False,
            ),
        )

        restored._cancelled = bool(
            snapshot.get(
                "cancelled",
                False,
            ),
        )

        restored._closed = bool(
            snapshot.get(
                "closed",
                False,
            ),
        )

        restored._frozen = bool(
            snapshot.get(
                "frozen",
                False,
            ),
        )

        # ----------------------------------------------------------------------
        # Timing
        # ----------------------------------------------------------------------

        restored._start_time = start_time

        restored._end_time = end_time

        # ----------------------------------------------------------------------
        # Metadata
        # ----------------------------------------------------------------------

        restored._attributes = copy.deepcopy(
            snapshot.get(
                "attributes",
                {},
            ),
        )

        restored._tags = copy.deepcopy(
            snapshot.get(
                "tags",
                {},
            ),
        )

        restored._baggage = copy.deepcopy(
            snapshot.get(
                "baggage",
                {},
            ),
        )

        # ----------------------------------------------------------------------
        # Events
        # ----------------------------------------------------------------------

        restored._events = []

        for event_data in snapshot.get(
            "events",
            [],
        ):

            if isinstance(
                event_data,
                Mapping,
            ):
                from types import SimpleNamespace

                event_timestamp = event_data.get(
                    "timestamp",
                )

                if isinstance(
                    event_timestamp,
                    str,
                ):
                    try:
                        event_timestamp = datetime.fromisoformat(
                            event_timestamp,
                        )
                    except ValueError as exc:
                        raise SpanValidationError(
                            "invalid event timestamp",
                        ) from exc

                restored._events.append(
                    SimpleNamespace(
                        name=event_data.get(
                            "name",
                        ),
                        attributes=copy.deepcopy(
                            event_data.get(
                                "attributes",
                                {},
                            ),
                        ),
                        timestamp=event_timestamp,
                    ),
                )

            else:
                restored._events.append(
                    copy.deepcopy(
                        event_data,
                    ),
                )

        # ----------------------------------------------------------------------
        # Links
        # ----------------------------------------------------------------------

        restored._links = copy.deepcopy(
            snapshot.get(
                "links",
                [],
            ),
        )

        # ----------------------------------------------------------------------
        # Context
        # ----------------------------------------------------------------------

        restored._context_id = snapshot.get(
            "context_id",
        )

        restored._context = None

        # ----------------------------------------------------------------------
        # Hierarchy
        # ----------------------------------------------------------------------

        restored._parent = None

        restored._children = []

        # ----------------------------------------------------------------------
        # Error state
        # ----------------------------------------------------------------------

        restored._exception = None

        return restored


    @classmethod
    def restore(
        cls,
        snapshot: Mapping[str, Any],
    ) -> "Span":
        """
        Compatibility alias for from_snapshot().
        """

        return cls.from_snapshot(
            snapshot,
        )


    def clone(
        self,
    ) -> "Span":
        """
        Create an independent Span clone.
        """

        return self.__class__.from_snapshot(
            self.snapshot(),
        )


    # ==========================================================================
    # 4.16 Python Protocols
    # ==========================================================================

    def __repr__(
        self,
    ) -> str:
        return (
            f"Span("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"state={self.state!r}"
            f")"
        )


    def __str__(
        self,
    ) -> str:
        return (
            f"Span("
            f"{self.name}"
            f")"
        )


    def __bool__(
        self,
    ) -> bool:
        return self.health()


    def __eq__(
        self,
        other: Any,
    ) -> bool:

        if self is other:
            return True

        if not isinstance(
            other,
            Span,
        ):
            return NotImplemented

        return (
            self.id
            == other.id
        )


    def __hash__(
        self,
    ) -> int:
        return hash(
            self.id,
        )


    def __len__(
        self,
    ) -> int:
        """
        Return the logical size of the Span.

        The count represents the number of
        attached metadata collections.
        """

        return (
            len(self._attributes)
            + len(self._tags)
            + len(self._baggage)
            + len(self._events)
            + len(self._links)
        )


# ==========================================================================
# Part 5. Public API
# ==========================================================================

__all__ += [
    "Span",
]
