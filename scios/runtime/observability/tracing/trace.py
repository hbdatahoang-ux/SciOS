"""
Trace entity.

Python 3.11+
"""

from __future__ import annotations


# ==============================================================================
# 1. Imports
# ==============================================================================

import copy
import json
import uuid

from datetime import (
    datetime,
    timezone,
)

from typing import (
    Any,
    Mapping,
    TypeAlias,
)

from uuid import uuid4

from .span import Span


# ==============================================================================
# Span
# ==============================================================================

#
# Span is imported explicitly because Trace owns the Span registry
# and is responsible for creating/restoring Span instances.
#
# Do not rely on package-level re-exports from __init__.py.
#

from .span import Span


# ==============================================================================
# 2. Public API
# ==============================================================================

__all__ = [

    # --------------------------------------------------------------------------
    # Constants
    # --------------------------------------------------------------------------

    "TRACE_VERSION",
    "TRACE_API_VERSION",

    "DEFAULT_TRACE_NAME",
    "DEFAULT_TRACE_VERSION",

    "DEFAULT_TRACE_AUTO_START",
    "DEFAULT_TRACE_AUTO_FINISH",

    "DEFAULT_SPAN_NAME",

    # --------------------------------------------------------------------------
    # Exceptions
    # --------------------------------------------------------------------------

    "TraceError",
    "TraceValidationError",
    "TraceStateError",

    "TraceClosedError",
    "TraceAlreadyStartedError",
    "TraceAlreadyFinishedError",

    "TraceNotStartedError",
    "TraceNotFinishedError",

    "TraceFrozenError",
    "TraceCancelledError",

    # --------------------------------------------------------------------------
    # Type aliases
    # --------------------------------------------------------------------------

    "TraceId",
    "TraceName",
    "TraceVersion",

    "TraceAttributeKey",
    "TraceAttributeValue",
    "TraceAttributes",

    "Timestamp",

    # --------------------------------------------------------------------------
    # Entity
    # --------------------------------------------------------------------------

    "Trace",
]


# ==============================================================================
# 3. Constants
# ==============================================================================

TRACE_VERSION = "1.0.0"

TRACE_API_VERSION = "1.0"

DEFAULT_TRACE_NAME = "Trace"

DEFAULT_TRACE_VERSION = TRACE_VERSION

DEFAULT_TRACE_AUTO_START = False

DEFAULT_TRACE_AUTO_FINISH = False

DEFAULT_SPAN_NAME = "Span"


# ==============================================================================
# 4. Type Aliases
# ==============================================================================

TraceId: TypeAlias = str

TraceName: TypeAlias = str

TraceVersion: TypeAlias = str

TraceAttributeKey: TypeAlias = str

TraceAttributeValue: TypeAlias = Any

TraceAttributes: TypeAlias = dict[
    TraceAttributeKey,
    TraceAttributeValue,
]

Timestamp: TypeAlias = datetime


# ==============================================================================
# 5. Exceptions
# ==============================================================================


class TraceError(Exception):
    """Base Trace exception."""


class TraceValidationError(TraceError):
    """Invalid Trace input or state."""


class TraceStateError(TraceError):
    """Invalid Trace lifecycle operation."""


class TraceClosedError(TraceStateError):
    """Trace is closed."""


class TraceAlreadyStartedError(TraceStateError):
    """Trace has already started."""


class TraceAlreadyFinishedError(TraceStateError):
    """Trace has already finished."""


class TraceNotStartedError(TraceStateError):
    """Trace has not started."""


class TraceNotFinishedError(TraceStateError):
    """Trace has not finished."""


class TraceFrozenError(TraceStateError):
    """Trace is frozen."""


class TraceCancelledError(TraceStateError):
    """Trace is cancelled."""


# ==============================================================================
# 6. Trace Entity
# ==============================================================================


class Trace:
    """
    SciOS Trace entity.

    A Trace represents one logical execution and owns
    the Span instances belonging to that execution.
    """

    __slots__ = (
        # Identity
        "_id",
        "_name",
        "_version",

        # Lifecycle
        "_state",
        "_started",
        "_finished",
        "_cancelled",
        "_frozen",
        "_closed",

        # Lifecycle configuration
        "_auto_start",
        "_auto_finish",

        # Timing
        "_start_time",
        "_end_time",

        # Metadata
        "_attributes",
        "_tags",
        "_baggage",

        # Context
        "_context",
        "_context_id",

        # Events / Links
        "_events",
        "_links",

        # Exception
        "_exception",

        # Spans
        "_spans",
        "_span_stack",
    )

    # ==========================================================================
    # 6.1 Constructor
    # ==========================================================================

    def __init__(
        self,
        name: str = DEFAULT_TRACE_NAME,
        *,
        trace_id: TraceId | None = None,
        version: TraceVersion = TRACE_VERSION,
        auto_start: bool = DEFAULT_TRACE_AUTO_START,
        auto_finish: bool = DEFAULT_TRACE_AUTO_FINISH,
        attributes: Mapping[
            TraceAttributeKey,
            TraceAttributeValue,
        ] | None = None,
    ) -> None:

        # ----------------------------------------------------------------------
        # Validate constructor arguments
        # ----------------------------------------------------------------------

        if not isinstance(
            name,
            str,
        ):
            raise TraceValidationError(
                "name must be a string",
            )

        name = name.strip()

        if not name:
            raise TraceValidationError(
                "name cannot be empty",
            )

        if trace_id is not None:

            if not isinstance(
                trace_id,
                str,
            ):
                raise TraceValidationError(
                    "trace_id must be a string or None",
                )

            trace_id = trace_id.strip()

            if not trace_id:
                raise TraceValidationError(
                    "trace_id cannot be empty",
                )

        if not isinstance(
            version,
            str,
        ):
            raise TraceValidationError(
                "version must be a string",
            )

        version = version.strip()

        if not version:
            raise TraceValidationError(
                "version cannot be empty",
            )

        if not isinstance(
            auto_start,
            bool,
        ):
            raise TraceValidationError(
                "auto_start must be bool",
            )

        if not isinstance(
            auto_finish,
            bool,
        ):
            raise TraceValidationError(
                "auto_finish must be bool",
            )

        if attributes is not None and not isinstance(
            attributes,
            Mapping,
        ):
            raise TraceValidationError(
                "attributes must be a mapping or None",
            )

        # ----------------------------------------------------------------------
        # Identity
        # ----------------------------------------------------------------------

        self._id = (
            trace_id
            if trace_id is not None
            else self._generate_id()
        )

        self._name = name

        self._version = version

        # ----------------------------------------------------------------------
        # Lifecycle
        # ----------------------------------------------------------------------

        self._state = "created"

        self._started = False

        self._finished = False

        self._cancelled = False

        self._frozen = False

        self._closed = False

        # ----------------------------------------------------------------------
        # Configuration
        # ----------------------------------------------------------------------

        self._auto_start = auto_start

        self._auto_finish = auto_finish

        # ----------------------------------------------------------------------
        # Timing
        # ----------------------------------------------------------------------

        self._start_time = None

        self._end_time = None

        # ----------------------------------------------------------------------
        # Metadata
        # ----------------------------------------------------------------------

        self._attributes = copy.deepcopy(
            dict(
                attributes
                or {},
            ),
        )

        self._tags = {}

        self._baggage = {}

        # ----------------------------------------------------------------------
        # Context
        # ----------------------------------------------------------------------

        self._context = None

        self._context_id = None

        # ----------------------------------------------------------------------
        # Events / Links
        # ----------------------------------------------------------------------

        self._events = []

        self._links = []

        # ----------------------------------------------------------------------
        # Exception
        # ----------------------------------------------------------------------

        self._exception = None

        # ----------------------------------------------------------------------
        # Spans
        # ----------------------------------------------------------------------

        self._spans = {}

        self._span_stack = []

        # ----------------------------------------------------------------------
        # Automatic start
        # ----------------------------------------------------------------------

        if self._auto_start:
            self.start()

    # ==========================================================================
    # 6.2 Internal Utilities
    # ==========================================================================

    @staticmethod
    def _generate_id() -> TraceId:
        return uuid4().hex

    @staticmethod
    def _generate_id() -> TraceId:

        return uuid.uuid4().hex

    @staticmethod
    def _now() -> Timestamp:
        return datetime.now(
            timezone.utc,
        )

    def _ensure_not_closed(self) -> None:

        if self._closed:
            raise TraceClosedError(
                "Trace is closed",
            )

    def _ensure_mutable(self) -> None:

        self._ensure_not_closed()

        if self._frozen:
            raise TraceFrozenError(
                "Trace is frozen",
            )

        if self._cancelled:
            raise TraceCancelledError(
                "Trace is cancelled",
            )

    # ==========================================================================
    # 7. Identity
    # ==========================================================================

    @property
    def id(self) -> TraceId:
        return self._id

    @property
    def trace_id(self) -> TraceId:
        return self._id

    @property
    def name(self) -> TraceName:
        return self._name

    @name.setter
    def name(
        self,
        value: str,
    ) -> None:

        self._ensure_mutable()

        if not isinstance(
            value,
            str,
        ):
            raise TraceValidationError(
                "name must be a string",
            )

        value = value.strip()

        if not value:
            raise TraceValidationError(
                "name cannot be empty",
            )

        self._name = value

    @property
    def version(self) -> TraceVersion:
        return self._version

    @version.setter
    def version(
        self,
        value: str,
    ) -> None:

        self._ensure_mutable()

        if not isinstance(
            value,
            str,
        ):
            raise TraceValidationError(
                "version must be a string",
            )

        value = value.strip()

        if not value:
            raise TraceValidationError(
                "version cannot be empty",
            )

        self._version = value

    # ==========================================================================
    # 8. Lifecycle
    # ==========================================================================

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
    def frozen(self) -> bool:
        return self._frozen

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def active(self) -> bool:
        return (
            self._started
            and not self._finished
            and not self._cancelled
            and not self._closed
        )

    def start(self) -> "Trace":

        self._ensure_not_closed()

        if self._cancelled:
            raise TraceCancelledError(
                "Trace is cancelled",
            )

        if self._started:
            raise TraceAlreadyStartedError(
                "Trace has already started",
            )

        if self._finished:
            raise TraceAlreadyFinishedError(
                "Trace has already finished",
            )

        self._started = True

        self._finished = False

        self._cancelled = False

        self._start_time = self._now()

        self._end_time = None

        self._state = "running"

        return self

    def finish(self) -> "Trace":

        self._ensure_not_closed()

        if self._cancelled:
            raise TraceCancelledError(
                "Trace is cancelled",
            )

        if not self._started:
            raise TraceNotStartedError(
                "Trace has not been started",
            )

        if self._finished:
            raise TraceAlreadyFinishedError(
                "Trace has already finished",
            )

        self._finish_active_spans()

        self._end_time = self._now()

        self._finished = True

        self._state = "finished"

        if self._auto_finish:
            self._closed = True

        return self

    def cancel(self) -> "Trace":

        self._ensure_not_closed()

        if self._frozen:
            raise TraceFrozenError(
                "Trace is frozen",
            )

        if self._cancelled:
            raise TraceCancelledError(
                "Trace is already cancelled",
            )

        if self._finished:
            raise TraceAlreadyFinishedError(
                "Trace has already finished",
            )

        # Important:
        # cancellation is valid for a newly-created Trace as well.
        self._cancelled = True

        self._finished = False

        self._state = "cancelled"

        self._end_time = self._now()

        return self

    def reset(self) -> "Trace":

        self._ensure_not_closed()

        self._id = self._generate_id()

        self._state = "created"

        self._started = False

        self._finished = False

        self._cancelled = False

        self._frozen = False

        self._start_time = None

        self._end_time = None

        self._exception = None

        self._events.clear()

        self._links.clear()

        self._spans.clear()

        self._span_stack.clear()

        return self

    def restart(self) -> "Trace":

        self.reset()

        return self.start()

    def freeze(self) -> "Trace":

        self._ensure_not_closed()

        self._frozen = True

        self._state = "frozen"

        return self

    def unfreeze(self) -> "Trace":

        self._ensure_not_closed()

        self._frozen = False

        if self._cancelled:
            self._state = "cancelled"

        elif self._finished:
            self._state = "finished"

        elif self._started:
            self._state = "running"

        else:
            self._state = "created"

        return self

    def close(self) -> "Trace":

        if self._closed:
            return self

        if self._started and not self._finished and not self._cancelled:
            self._finish_active_spans()

            self._end_time = (
                self._end_time
                or self._now()
            )

            self._finished = True

        self._closed = True

        self._frozen = False

        self._state = "closed"

        return self

    # ==========================================================================
    # 9. Timing
    # ==========================================================================

    @property
    def start_time(self) -> Timestamp | None:
        return self._start_time

    @property
    def end_time(self) -> Timestamp | None:
        return self._end_time

    @property
    def duration(self) -> float | None:

        if (
            self._start_time is None
            or self._end_time is None
        ):
            return None

        return (
            self._end_time
            - self._start_time
        ).total_seconds()

    # ==========================================================================
    # 10. Attributes
    # ==========================================================================

    @property
    def attributes(self) -> dict[str, Any]:
        return copy.deepcopy(
            self._attributes,
        )

    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> "Trace":

        self._ensure_mutable()

        if not isinstance(
            key,
            str,
        ):
            raise TraceValidationError(
                "attribute key must be a string",
            )

        key = key.strip()

        if not key:
            raise TraceValidationError(
                "attribute key cannot be empty",
            )

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
    ) -> "Trace":

        self._ensure_mutable()

        self._attributes.pop(
            key,
            None,
        )

        return self

    def clear_attributes(self) -> "Trace":

        self._ensure_mutable()

        self._attributes.clear()

        return self

    # ==========================================================================
    # 11. Tags
    # ==========================================================================

    @property
    def tags(self) -> dict[str, Any]:
        return copy.deepcopy(
            self._tags,
        )

    def set_tag(
        self,
        key: str,
        value: Any = True,
    ) -> "Trace":

        self._ensure_mutable()

        if not isinstance(
            key,
            str,
        ) or not key.strip():
            raise TraceValidationError(
                "tag key must be a non-empty string",
            )

        self._tags[key.strip()] = value

        return self

    def get_tag(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self._tags.get(
            key,
            default,
        )

    def remove_tag(
        self,
        key: str,
    ) -> "Trace":

        self._ensure_mutable()

        self._tags.pop(
            key,
            None,
        )

        return self

    def clear_tags(self) -> "Trace":

        self._ensure_mutable()

        self._tags.clear()

        return self

    # ==========================================================================
    # 12. Baggage
    # ==========================================================================

    @property
    def baggage(self) -> dict[str, Any]:
        return copy.deepcopy(
            self._baggage,
        )

    def set_baggage(
        self,
        key: str,
        value: Any,
    ) -> "Trace":

        self._ensure_mutable()

        if not isinstance(
            key,
            str,
        ) or not key.strip():
            raise TraceValidationError(
                "baggage key must be a non-empty string",
            )

        self._baggage[key.strip()] = value

        return self

    def get_baggage(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self._baggage.get(
            key,
            default,
        )

    def remove_baggage(
        self,
        key: str,
    ) -> "Trace":

        self._ensure_mutable()

        self._baggage.pop(
            key,
            None,
        )

        return self

    def clear_baggage(self) -> "Trace":

        self._ensure_mutable()

        self._baggage.clear()

        return self

    # ==========================================================================
    # 13. Spans
    # ==========================================================================

    @property
    def spans(self) -> list[Span]:
        return list(
            self._spans.values(),
        )


    @property
    def span_count(self) -> int:
        return len(
            self._spans,
        )


    @property
    def current_span(self) -> Span | None:

        while self._span_stack:

            span = self._span_stack[-1]

            if self._span_is_active(span):
                return span

            self._span_stack.pop()

        return None


    @property
    def root_span(self) -> Span | None:

        if not self._spans:
            return None

        return next(
            iter(
                self._spans.values(),
            ),
        )


    @property
    def active_spans(self) -> list[Span]:

        return [
            span
            for span in self._spans.values()
            if self._span_is_active(span)
        ]


    @staticmethod
    def _span_is_active(
        span: Span,
    ) -> bool:

        active = getattr(
            span,
            "active",
            None,
        )

        if isinstance(
            active,
            bool,
        ):
            return active

        finished = getattr(
            span,
            "finished",
            None,
        )

        if isinstance(
            finished,
            bool,
        ):
            return not finished

        started = getattr(
            span,
            "started",
            None,
        )

        if isinstance(
            started,
            bool,
        ):
            return started

        return True


    def add_span(
        self,
        span: Span,
    ) -> "Trace":

        self._ensure_mutable()

        if span is None:
            raise TraceValidationError(
                "span cannot be None",
            )

        span_id = getattr(
            span,
            "id",
            None,
        )

        if span_id is None:
            span_id = getattr(
                span,
                "span_id",
                None,
            )

        if span_id is None:
            raise TraceValidationError(
                "span must have an id",
            )

        self._spans[
            str(span_id)
        ] = span

        return self


    def remove_span(
        self,
        span,
    ):
        if span is None:
            return self

        span_id = str(
            getattr(
                span,
                "id",
                getattr(
                    span,
                    "span_id",
                    span,
                ),
            ),
        )

        self._spans.pop(
            span_id,
            None,
        )

        self._span_stack = [
            item
            for item in self._span_stack
            if item is not span
            and str(
                getattr(
                    item,
                    "id",
                    getattr(
                        item,
                        "span_id",
                        "",
                    ),
                ),
            ) != span_id
        ]

        return self


    def get_span(
        self,
        span_id: str,
    ) -> Span | None:

        return self._spans.get(
            str(span_id),
        )


    def clear_spans(self) -> "Trace":

        self._ensure_mutable()

        self._spans.clear()
        self._span_stack.clear()

        return self


    def _finish_span_object(
        self,
        span: Span,
    ) -> Span:

        finish = getattr(
            span,
            "finish",
            None,
        )

        if callable(finish):
            finish()

        return span


    def finish_span(
        self,
    ) -> Span | None:

        self._ensure_mutable()

        span = self.current_span

        if span is None:
            return None

        finish = getattr(
            span,
            "finish",
            None,
        )

        if callable(finish):
            finish()

        if self._span_stack and self._span_stack[-1] is span:
            self._span_stack.pop()

        return span


    def _finish_active_spans(self) -> None:

        while self._span_stack:

            span = self._span_stack.pop()

            if not self._span_is_active(span):
                continue

            finish = getattr(
                span,
                "finish",
                None,
            )

            if callable(finish):
                finish()


    def start_span(
        self,
        name: str = DEFAULT_SPAN_NAME,
        **kwargs: Any,
    ) -> Span:

        self._ensure_mutable()

        # ------------------------------------------------------------------
        # Lazy trace start
        # ------------------------------------------------------------------

        if not self._started:
            self.start()

        if self._finished:
            raise TraceAlreadyFinishedError(
                "Trace has already finished",
            )

        if self._cancelled:
            raise TraceCancelledError(
                "Trace is cancelled",
            )

        # ------------------------------------------------------------------
        # Resolve parent
        # ------------------------------------------------------------------

        parent = self.current_span

        if parent is not None:

            parent_id = getattr(
                parent,
                "id",
                None,
            )

            if parent_id is None:
                parent_id = getattr(
                    parent,
                    "span_id",
                    None,
                )

        else:

            parent_id = self.id

        # User-supplied parent_id takes precedence.
        parent_id = kwargs.pop(
            "parent_id",
            parent_id,
        )

        # ------------------------------------------------------------------
        # Context propagation
        # ------------------------------------------------------------------

        span_context = None

        if self._context is not None:
            span_context = copy.deepcopy(
                self._context,
            )

        # Span does not necessarily accept context
        # through its constructor.
        kwargs.pop(
            "context",
            None,
        )

        # ------------------------------------------------------------------
        # Create Span
        # ------------------------------------------------------------------

        span = Span(
            name=name,
            trace_id=self.id,
            parent_id=parent_id,
            auto_start=True,
            auto_finish=False,
            **kwargs,
        )

        # ------------------------------------------------------------------
        # Propagate context after construction
        # ------------------------------------------------------------------

        if span_context is not None:

            try:
                span.context = span_context

            except (
                AttributeError,
                TypeError,
            ):
                pass

        # ------------------------------------------------------------------
        # Register
        # ------------------------------------------------------------------

        self._spans[
            str(span.id)
        ] = span

        self._span_stack.append(
            span,
        )

        return span
    # ==========================================================================
    # 14. Exceptions
    # ==========================================================================

    @property
    def exception(
        self,
    ) -> BaseException | None:
        return self._exception

    @property
    def has_exception(
        self,
    ) -> bool:
        return self._exception is not None

    def attach_exception(
        self,
        exception: BaseException | None,
    ) -> "Trace":

        self._ensure_mutable()

        if (
            exception is not None
            and not isinstance(
                exception,
                BaseException,
            )
        ):
            raise TraceValidationError(
                "exception must be a BaseException or None",
            )

        self._exception = exception

        return self

    # ==========================================================================
    # 15. Context
    # ==========================================================================

    @property
    def context(self) -> Any | None:
        return self._context

    @context.setter
    def context(
        self,
        value: Any | None,
    ) -> None:

        self._ensure_mutable()

        if value is None:
            self._context = None
            self._context_id = None
            return

        self._context = value

        context_id = getattr(
            value,
            "context_id",
            None,
        )

        if context_id is None:
            context_id = getattr(
                value,
                "id",
                None,
            )

        if (
            context_id is None
            and isinstance(
                value,
                Mapping,
            )
        ):
            context_id = value.get(
                "context_id",
            )

            if context_id is None:
                context_id = value.get(
                    "id",
                )

        if context_id is None:
            context_id = uuid4().hex

        self._context_id = str(
            context_id,
        )

    @property
    def context_id(self) -> str | None:
        return self._context_id

    # ==========================================================================
    # 16. Events
    # ==========================================================================

    @property
    def events(self) -> list[Any]:
        return copy.deepcopy(
            self._events,
        )

    @property
    def event_count(self) -> int:
        return len(
            self._events,
        )

    def add_event(
        self,
        event: Any,
    ) -> "Trace":

        self._ensure_mutable()

        if event is None:
            raise TraceValidationError(
                "event cannot be None",
            )

        self._events.append(
            copy.deepcopy(
                event,
            ),
        )

        return self

    def clear_events(self) -> "Trace":

        self._ensure_mutable()

        self._events.clear()

        return self

    # ==========================================================================
    # 17. Links
    # ==========================================================================

    @property
    def links(self) -> list[Any]:
        return copy.deepcopy(
            self._links,
        )

    @property
    def link_count(self) -> int:
        return len(
            self._links,
        )

    def add_link(
        self,
        link: Any,
    ) -> "Trace":

        self._ensure_mutable()

        if link is None:
            raise TraceValidationError(
                "link cannot be None",
            )

        self._links.append(
            copy.deepcopy(
                link,
            ),
        )

        return self

    def clear_links(self) -> "Trace":

        self._ensure_mutable()

        self._links.clear()

        return self

    # ==========================================================================
    # 18. Diagnostics
    # ==========================================================================

    def summary(self) -> dict[str, Any]:

        return {
            "trace": self.__class__.__name__,

            # Keep both keys for API compatibility.
            "id": self.id,
            "trace_id": self.trace_id,

            "name": self.name,
            "version": self.version,

            "state": self.state,

            "started": self.started,
            "finished": self.finished,
            "cancelled": self.cancelled,
            "frozen": self.frozen,
            "closed": self.closed,
            "active": self.active,

            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,

            "span_count": self.span_count,
            "active_span_count": len(
                self.active_spans,
            ),

            "event_count": self.event_count,
            "link_count": self.link_count,

            "has_exception": self.has_exception,

            "context_id": self.context_id,
        }

    def diagnostics(self) -> dict[str, Any]:

        return {
            "summary": self.summary(),

            "attributes": copy.deepcopy(
                self._attributes,
            ),

            "tags": copy.deepcopy(
                self._tags,
            ),

            "baggage": copy.deepcopy(
                self._baggage,
            ),

            "spans": copy.deepcopy(
                self.spans,
            ),

            "events": copy.deepcopy(
                self._events,
            ),

            "links": copy.deepcopy(
                self._links,
            ),

            "exception": (
                repr(
                    self.exception,
                )
                if self.exception is not None
                else None
            ),

            "context": copy.deepcopy(
                self.context,
            ),

            "context_id": self.context_id,
        }

    def validate(self) -> bool:

        try:

            if not isinstance(
                self._id,
                str,
            ) or not self._id:
                return False

            if not isinstance(
                self._name,
                str,
            ) or not self._name.strip():
                return False

            if not isinstance(
                self._version,
                str,
            ) or not self._version.strip():
                return False

            if self._started and self._start_time is None:
                return False

            if self._finished:

                if not self._started:
                    return False

                if self._end_time is None:
                    return False

            if self._cancelled:

                if self._finished:
                    return False

                if self._state != "cancelled":
                    return False

            if self._closed:
                if self._state != "closed":
                    return False

            if (
                self._start_time is not None
                and self._end_time is not None
                and self._end_time < self._start_time
            ):
                return False

            for span_id, span in self._spans.items():

                if not isinstance(
                    span_id,
                    str,
                ):
                    return False

                if span is None:
                    return False

            return True

        except Exception:
            return False

    def health(self) -> bool:
        return self.validate()

    # ==========================================================================
    # 19. Persistence
    # ==========================================================================

    @staticmethod
    def _serialize_span(
        span: Any,
    ) -> Any:

        serializer = getattr(
            span,
            "to_dict",
            None,
        )

        if callable(serializer):
            return serializer()

        return copy.deepcopy(
            span,
        )

    def to_dict(self) -> dict[str, Any]:

        return {
            "id": self.id,
            "trace_id": self.trace_id,

            "name": self.name,
            "version": self.version,

            "state": self.state,

            "started": self.started,
            "finished": self.finished,
            "cancelled": self.cancelled,
            "frozen": self.frozen,
            "closed": self.closed,

            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,

            "attributes": copy.deepcopy(
                self._attributes,
            ),

            "tags": copy.deepcopy(
                self._tags,
            ),

            "baggage": copy.deepcopy(
                self._baggage,
            ),

            "spans": [
                self._serialize_span(
                    span,
                )
                for span in self._spans.values()
            ],

            "events": copy.deepcopy(
                self._events,
            ),

            "links": copy.deepcopy(
                self._links,
            ),

            "exception": (
                repr(
                    self.exception,
                )
                if self.exception is not None
                else None
            ),

            "context": copy.deepcopy(
                self.context,
            ),

            "context_id": self.context_id,
        }

    def to_json(self) -> str:

        return json.dumps(
            self.to_dict(),
            default=str,
            sort_keys=True,
        )

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "Trace":

        return cls.restore(
            data,
        )

    @classmethod
    def from_json(
        cls,
        data: str,
    ) -> "Trace":

        if not isinstance(
            data,
            str,
        ):
            raise TraceValidationError(
                "data must be a string",
            )

        try:
            payload = json.loads(
                data,
            )
        except json.JSONDecodeError as exc:
            raise TraceValidationError(
                "invalid Trace JSON",
            ) from exc

        return cls.restore(
            payload,
        )



    def snapshot(self) -> dict[str, Any]:

        return copy.deepcopy(
            self.to_dict(),
        )

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "Trace":

        if not isinstance(
            snapshot,
            Mapping,
        ):
            raise TraceValidationError(
                "snapshot must be a mapping",
            )

        self._id = snapshot.get(
            "trace_id",
            snapshot.get("id"),
        )

        self._name = snapshot.get(
            "name",
            DEFAULT_TRACE_NAME,
        )

        self._version = snapshot.get(
            "version",
            TRACE_VERSION,
        )

        self._state = snapshot.get(
            "state",
            "created",
        )

        self._started = bool(
            snapshot.get(
                "started",
                False,
            )
        )

        self._finished = bool(
            snapshot.get(
                "finished",
                False,
            )
        )

        self._cancelled = bool(
            snapshot.get(
                "cancelled",
                False,
            )
        )

        self._frozen = bool(
            snapshot.get(
                "frozen",
                False,
            )
        )

        self._closed = bool(
            snapshot.get(
                "closed",
                False,
            )
        )

        self._start_time = snapshot.get(
            "start_time",
        )

        self._end_time = snapshot.get(
            "end_time",
        )

        self._attributes = copy.deepcopy(
            snapshot.get(
                "attributes",
                {},
            )
        )

        self._tags = set(
            copy.deepcopy(
                snapshot.get(
                    "tags",
                    [],
                )
            )
        )

        self._baggage = copy.deepcopy(
            snapshot.get(
                "baggage",
                {},
            )
        )

        self._events = copy.deepcopy(
            snapshot.get(
                "events",
                [],
            )
        )

        self._links = copy.deepcopy(
            snapshot.get(
                "links",
                [],
            )
        )

        self._context = copy.deepcopy(
            snapshot.get(
                "context",
            )
        )

        self._context_id = snapshot.get(
            "context_id",
        )

        self._exception = None

        self._spans.clear()
        self._span_stack.clear()

        for span_data in snapshot.get(
            "spans",
            [],
        ):
            if isinstance(
                span_data,
                Mapping,
            ):
                span = Span.restore(
                    span_data,
                )
            else:
                span = copy.deepcopy(
                    span_data,
                )

            self._spans[
                str(span.id)
            ] = span

        return self

    @staticmethod
    def _restore_timestamp(
        value: Any,
    ) -> Timestamp | None:

        if value is None:
            return None

        if isinstance(
            value,
            datetime,
        ):
            return value

        if isinstance(
            value,
            str,
        ):

            try:
                return datetime.fromisoformat(
                    value,
                )
            except ValueError:
                return None

        return None

    def clone(
        self,
    ) -> "Trace":

        clone = self.__class__(
            name=self.name,
            trace_id=self.id,
            version=self.version,
            auto_start=False,
            auto_finish=False,
            attributes=copy.deepcopy(
                self._attributes,
            ),
        )

        return clone.restore(
            self.snapshot(),
        )

    def copy(self) -> "Trace":

        return self.clone()

    # ==========================================================================
    # 20. Protocol
    # ==========================================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"state={self.state!r}, "
            f"span_count={self.span_count!r}"
            f")"
        )

    def __str__(self) -> str:

        return (
            f"{self.name}"
            f"({self.id})"
        )

    def __bool__(self) -> bool:

        return bool(
            self.health()
            and not self.closed,
            # Cancelled Trace is intentionally false.
        ) and not self.cancelled

    def __len__(self) -> int:

        return self.span_count

    def __contains__(
        self,
        key: str,
    ) -> bool:

        return str(key) in self._spans

    def __getitem__(
        self,
        key: int | str,
    ) -> Span:

        if isinstance(
            key,
            int,
        ):
            return list(
                self._spans.values(),
            )[key]

        if isinstance(
            key,
            str,
        ):

            span = self.get_span(
                key,
            )

            if span is None:
                raise KeyError(
                    key,
                )

            return span

        raise TypeError(
            "Trace indices must be integers or span ids",
        )

    def __setitem__(
        self,
        key: int | str,
        value: Span,
    ) -> None:

        self._ensure_mutable()

        if isinstance(
            key,
            int,
        ):
            spans = list(
                self._spans.items(),
            )

            try:
                span_id = spans[key][0]
            except IndexError as exc:
                raise IndexError(
                    key,
                ) from exc

            self._spans[
                span_id
            ] = value

            return

        if isinstance(
            key,
            str,
        ):

            self._spans[
                key
            ] = value

            return

        raise TypeError(
            "Trace indices must be integers or span ids",
        )

    def __iter__(self):

        return iter(
            self._spans.values(),
        )

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if self is other:
            return True

        if not isinstance(
            other,
            Trace,
        ):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:

        return hash(
            self.id,
        )

# ==========================================================================
# 15. Public API
# ==========================================================================

__all__ = [
    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    "TRACE_VERSION",
    "TRACE_API_VERSION",

    "DEFAULT_TRACE_NAME",
    "DEFAULT_TRACE_VERSION",

    "DEFAULT_TRACE_AUTO_START",
    "DEFAULT_TRACE_AUTO_FINISH",

    "DEFAULT_SPAN_NAME",

    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    "TraceError",
    "TraceValidationError",
    "TraceStateError",

    "TraceClosedError",
    "TraceAlreadyStartedError",
    "TraceAlreadyFinishedError",

    "TraceNotStartedError",
    "TraceNotFinishedError",

    "TraceFrozenError",
    "TraceCancelledError",

    # ------------------------------------------------------------------
    # Type Aliases
    # ------------------------------------------------------------------

    "TraceId",
    "TraceName",
    "TraceVersion",
    "Timestamp",

    "TraceAttributeKey",
    "TraceAttributeValue",
    "TraceAttributes",

    # ------------------------------------------------------------------
    # Entities
    # ------------------------------------------------------------------

    "Trace",
    "Span",
]
