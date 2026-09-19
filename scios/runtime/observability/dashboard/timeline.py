"""
SciOS-NG Observability Timeline Engine

Provides timeline data structures
for traces, events and runtime visualization.
"""


# ==============================================================================
# Imports
# ==============================================================================


from __future__ import annotations


import time

import uuid

import copy


from dataclasses import (
    dataclass,
    field,
)


from typing import (

    Any,

    Dict,

    List,

    Optional,

)



from enum import Enum



# ==============================================================================
# Constants
# ==============================================================================


TIMELINE_VERSION = (
    "0.3.0-alpha"
)


DEFAULT_TIMELINE_NAME = (
    "SciOS Timeline"
)


DEFAULT_MAX_EVENTS = 100000


DEFAULT_TIME_UNIT = (
    "seconds"
)



# ==============================================================================
# Timeline Event
# ==============================================================================


class EventType(Enum):

    """
    Timeline event categories.
    """

    TRACE = (
        "trace"
    )

    SPAN = (
        "span"
    )

    METRIC = (
        "metric"
    )

    LOG = (
        "log"
    )

    SYSTEM = (
        "system"
    )



@dataclass
class TimelineEvent:
    """
    Single timeline event.

    Represents:

        - trace span
        - runtime event
        - metric update
    """


    name: str


    timestamp: float = field(
        default_factory=time.time
    )


    duration: float = 0.0


    event_type: EventType = (
        EventType.SYSTEM
    )


    service: Optional[str] = None


    trace_id: Optional[str] = None


    span_id: Optional[str] = None


    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


    id: str = field(
        default_factory=lambda:
            str(uuid.uuid4())
    )



# ==============================================================================
# Timeline Node
# ==============================================================================


@dataclass
class TimelineNode:
    """
    Hierarchical timeline node.

    Used for:

        parent-child spans
        flamegraph conversion
    """


    name: str


    start_time: float


    duration: float = 0.0


    children: List[
        "TimelineNode"
    ] = field(
        default_factory=list
    )


    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


    parent: Optional[
        "TimelineNode"
    ] = None



    def add_child(
        self,
        node: "TimelineNode",
    ):

        node.parent = self

        self.children.append(
            node
        )



# ==============================================================================
# Timeline
# ==============================================================================


class Timeline:

    """
    Runtime timeline manager.

    Stores and manages:

        - events
        - nodes
        - traces
    """



    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------


    def __init__(
        self,
        name: str = DEFAULT_TIMELINE_NAME,
        max_events: int = DEFAULT_MAX_EVENTS,
    ):


        # --------------------------------------------------------------
        # Identity
        # --------------------------------------------------------------


        self._id = (
            str(uuid.uuid4())
        )


        self._name = name


        self._version = (
            TIMELINE_VERSION
        )


        # --------------------------------------------------------------
        # Configuration
        # --------------------------------------------------------------


        self._max_events = (
            max_events
        )


        self._time_unit = (
            DEFAULT_TIME_UNIT
        )


        self._enabled = True



        # --------------------------------------------------------------
        # Runtime State
        # --------------------------------------------------------------


        self._events: List[
            TimelineEvent
        ] = []


        self._nodes: List[
            TimelineNode
        ] = []


        self._created_at = (
            time.time()
        )


        self._updated_at = (
            self._created_at
        )



    # ==========================================================================
    # Identity Properties
    # ==========================================================================


    @property
    def id(
        self,
    ):

        return self._id



    @property
    def name(
        self,
    ):

        return self._name



    @property
    def version(
        self,
    ):

        return self._version



    # ==========================================================================
    # Configuration Properties
    # ==========================================================================


    @property
    def max_events(
        self,
    ):

        return self._max_events



    @property
    def enabled(
        self,
    ):

        return self._enabled



    # ==========================================================================
    # Runtime State
    # ==========================================================================


    @property
    def events(
        self,
    ):

        return self._events



    @property
    def nodes(
        self,
    ):

        return self._nodes



    @property
    def event_count(
        self,
    ):

        return len(
            self._events
        )
# ==============================================================================
# Part 2. Timeline API
# ==============================================================================

    def add_event(
        self,
        event: TimelineEvent,
    ) -> TimelineEvent:
        """
        Add a timeline event.
        """

        if not self._enabled:
            raise RuntimeError("Timeline is disabled.")

        if not isinstance(event, TimelineEvent):
            raise TypeError("event must be TimelineEvent.")

        if len(self._events) >= self._max_events:
            self._events.pop(0)

        self._events.append(event)
        self._updated_at = time.time()

        return event

    # ------------------------------------------------------------------

    def add_span(
        self,
        name: str,
        start_time: Optional[float] = None,
        duration: float = 0.0,
        service: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TimelineEvent:
        """
        Create and add a span event.
        """

        event = TimelineEvent(
            name=name,
            timestamp=start_time or time.time(),
            duration=duration,
            event_type=EventType.SPAN,
            service=service,
            trace_id=trace_id,
            span_id=span_id,
            metadata=metadata or {},
        )

        return self.add_event(event)

    # ------------------------------------------------------------------

    def add_node(
        self,
        node: TimelineNode,
    ) -> TimelineNode:
        """
        Add a timeline node.
        """

        if not isinstance(node, TimelineNode):
            raise TypeError("node must be TimelineNode.")

        self._nodes.append(node)
        self._updated_at = time.time()

        return node

    # ------------------------------------------------------------------

    def get_event(
        self,
        event_id: str,
    ) -> Optional[TimelineEvent]:
        """
        Get event by identifier.
        """

        for event in self._events:
            if event.id == event_id:
                return event

        return None

    # ------------------------------------------------------------------

    def query(
        self,
        *,
        event_type: Optional[EventType] = None,
        service: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> List[TimelineEvent]:
        """
        Query timeline events.
        """

        results = []

        for event in self._events:

            if event_type is not None and event.event_type != event_type:
                continue

            if service is not None and event.service != service:
                continue

            if trace_id is not None and event.trace_id != trace_id:
                continue

            if span_id is not None and event.span_id != span_id:
                continue

            if name is not None and event.name != name:
                continue

            results.append(event)

        return results

    # ------------------------------------------------------------------

    def range(
        self,
        start: float,
        end: float,
    ) -> List[TimelineEvent]:
        """
        Return events inside a time range.
        """

        return [

            event

            for event in self._events

            if start <= event.timestamp <= end

        ]

    # ------------------------------------------------------------------

    def sort(
        self,
        reverse: bool = False,
    ) -> List[TimelineEvent]:
        """
        Sort timeline events by timestamp.
        """

        self._events.sort(
            key=lambda event: event.timestamp,
            reverse=reverse,
        )

        return self._events
# ==============================================================================
# Part 3. Rendering API
# ==============================================================================

    def render(
        self,
        format: str = "dict",
    ) -> Any:
        """
        Render timeline using the requested format.

        Supported formats:
            dict
            json
            ascii
            table
            html
        """

        format = format.lower()

        if format == "dict":
            return self.render_dict()

        if format == "json":
            return self.render_json()

        if format == "ascii":
            return self.render_ascii()

        if format == "table":
            return self.render_table()

        if format == "html":
            return self.render_html()

        raise ValueError(f"Unsupported render format: {format}")

    # ------------------------------------------------------------------

    def render_dict(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Render events as dictionaries.
        """

        return [
            {
                "id": event.id,
                "name": event.name,
                "timestamp": event.timestamp,
                "duration": event.duration,
                "event_type": event.event_type.value,
                "service": event.service,
                "trace_id": event.trace_id,
                "span_id": event.span_id,
                "metadata": dict(event.metadata),
            }
            for event in self._events
        ]

    # ------------------------------------------------------------------

    def render_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        """
        Render timeline as JSON.
        """

        import json

        return json.dumps(
            self.render_dict(),
            indent=indent,
            default=str,
        )

    # ------------------------------------------------------------------

    def render_ascii(
        self,
    ) -> str:
        """
        Render a simple ASCII timeline.
        """

        lines = []

        for event in self.sort():

            lines.append(
                f"[{event.timestamp:.6f}] "
                f"{event.event_type.value.upper():<8} "
                f"{event.name} "
                f"({event.duration:.6f}s)"
            )

        return "\n".join(lines)

    # ------------------------------------------------------------------

    def render_table(
        self,
    ) -> str:
        """
        Render events as a plain text table.
        """

        header = (
            f"{'Time':<18}"
            f"{'Type':<10}"
            f"{'Service':<16}"
            f"{'Duration':<12}"
            f"Name"
        )

        separator = "-" * len(header)

        rows = [header, separator]

        for event in self.sort():

            rows.append(
                f"{event.timestamp:<18.6f}"
                f"{event.event_type.value:<10}"
                f"{(event.service or '-'):16}"
                f"{event.duration:<12.6f}"
                f"{event.name}"
            )

        return "\n".join(rows)

    # ------------------------------------------------------------------

    def render_html(
        self,
    ) -> str:
        """
        Render events as a minimal HTML table.
        """

        rows = []

        for event in self.sort():

            rows.append(
                (
                    "<tr>"
                    f"<td>{event.timestamp:.6f}</td>"
                    f"<td>{event.event_type.value}</td>"
                    f"<td>{event.service or ''}</td>"
                    f"<td>{event.duration:.6f}</td>"
                    f"<td>{event.name}</td>"
                    "</tr>"
                )
            )

        return (
            "<table>"
            "<thead>"
            "<tr>"
            "<th>Time</th>"
            "<th>Type</th>"
            "<th>Service</th>"
            "<th>Duration</th>"
            "<th>Name</th>"
            "</tr>"
            "</thead>"
            "<tbody>"
            + "".join(rows)
            + "</tbody>"
            "</table>"
        )

    # ------------------------------------------------------------------

    def export(
        self,
        format: str = "json",
    ) -> Any:
        """
        Export timeline.

        Alias of render().
        """

        return self.render(format)
# ==============================================================================
# Part 4. Runtime Operations
# ==============================================================================

    def snapshot(
        self,
    ) -> Dict[str, Any]:
        """
        Create a serializable snapshot of the timeline state.
        """

        return {
            "id": self._id,
            "name": self._name,
            "version": self._version,
            "max_events": self._max_events,
            "time_unit": self._time_unit,
            "enabled": self._enabled,
            "created_at": self._created_at,
            "updated_at": self._updated_at,
            "events": copy.deepcopy(self._events),
            "nodes": copy.deepcopy(self._nodes),
        }

    # ------------------------------------------------------------------

    def restore(
        self,
        snapshot: Dict[str, Any],
    ) -> "Timeline":
        """
        Restore timeline from a snapshot.
        """

        self._id = snapshot["id"]
        self._name = snapshot["name"]
        self._version = snapshot["version"]

        self._max_events = snapshot["max_events"]
        self._time_unit = snapshot["time_unit"]
        self._enabled = snapshot["enabled"]

        self._created_at = snapshot["created_at"]
        self._updated_at = snapshot["updated_at"]

        self._events = copy.deepcopy(snapshot["events"])
        self._nodes = copy.deepcopy(snapshot["nodes"])

        return self

    # ------------------------------------------------------------------

    def clone(
        self,
    ) -> "Timeline":
        """
        Create a deep cloned timeline.
        """

        cloned = self.__class__(
            name=self._name,
            max_events=self._max_events,
        )

        cloned.restore(
            self.snapshot()
        )

        return cloned

    # ------------------------------------------------------------------

    def copy(
        self,
    ) -> "Timeline":
        """
        Create a shallow copy.
        """

        copied = self.__class__(
            name=self._name,
            max_events=self._max_events,
        )

        copied._events = list(self._events)
        copied._nodes = list(self._nodes)

        copied._enabled = self._enabled
        copied._time_unit = self._time_unit

        copied._created_at = self._created_at
        copied._updated_at = self._updated_at

        return copied

    # ------------------------------------------------------------------

    def cleanup(
        self,
    ) -> int:
        """
        Remove invalid timeline events and nodes.

        Returns
        -------
        int
            Number of removed objects.
        """

        removed = 0

        valid_events = []

        for event in self._events:

            if event is None:
                removed += 1
                continue

            valid_events.append(event)

        self._events = valid_events

        valid_nodes = []

        for node in self._nodes:

            if node is None:
                removed += 1
                continue

            valid_nodes.append(node)

        self._nodes = valid_nodes

        self._updated_at = time.time()

        return removed

    # ------------------------------------------------------------------

    def compact(
        self,
    ) -> int:
        """
        Compact timeline storage.

        Keeps only the newest max_events entries.

        Returns
        -------
        int
            Number of discarded events.
        """

        discarded = 0

        if len(self._events) > self._max_events:

            discarded = (
                len(self._events)
                - self._max_events
            )

            self._events = self._events[
                -self._max_events:
            ]

        self._updated_at = time.time()

        return discarded
# ==============================================================================
# Part 5. Statistics
# ==============================================================================

    @property
    def event_count(
        self,
    ) -> int:
        """
        Total number of events.
        """

        return len(self._events)

    # ------------------------------------------------------------------

    @property
    def span_count(
        self,
    ) -> int:
        """
        Number of span events.
        """

        return sum(
            1
            for event in self._events
            if event.event_type == EventType.SPAN
        )

    # ------------------------------------------------------------------

    @property
    def node_count(
        self,
    ) -> int:
        """
        Number of timeline nodes.
        """

        return len(self._nodes)

    # ------------------------------------------------------------------

    @property
    def total_duration(
        self,
    ) -> float:
        """
        Total duration of all events.
        """

        return sum(
            event.duration
            for event in self._events
        )

    # ------------------------------------------------------------------

    def report(
        self,
    ) -> Dict[str, Any]:
        """
        Detailed timeline report.
        """

        event_types = {}

        for event in self._events:

            key = event.event_type.value

            event_types[key] = (
                event_types.get(key, 0) + 1
            )

        return {

            "id": self._id,

            "name": self._name,

            "version": self._version,

            "enabled": self._enabled,

            "events": self.event_count,

            "spans": self.span_count,

            "nodes": self.node_count,

            "total_duration": self.total_duration,

            "created_at": self._created_at,

            "updated_at": self._updated_at,

            "event_types": event_types,

            "max_events": self._max_events,

            "time_unit": self._time_unit,

        }

    # ------------------------------------------------------------------

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Lightweight runtime summary.
        """

        return {

            "events": self.event_count,

            "spans": self.span_count,

            "nodes": self.node_count,

            "duration": self.total_duration,

        }
# ==============================================================================
# Part 6. Validation
# ==============================================================================

    def validate(
        self,
    ) -> bool:
        """
        Validate the entire timeline.
        """

        return (
            self.check_integrity()
            and all(
                self.validate_event(event)
                for event in self._events
            )
            and all(
                self.validate_node(node)
                for node in self._nodes
            )
        )

    # ------------------------------------------------------------------

    def validate_event(
        self,
        event: TimelineEvent,
    ) -> bool:
        """
        Validate a timeline event.
        """

        if not isinstance(event, TimelineEvent):
            return False

        if not event.id:
            return False

        if not event.name:
            return False

        if event.timestamp < 0:
            return False

        if event.duration < 0:
            return False

        if not isinstance(event.metadata, dict):
            return False

        return True

    # ------------------------------------------------------------------

    def validate_node(
        self,
        node: TimelineNode,
    ) -> bool:
        """
        Validate a timeline node.
        """

        if not isinstance(node, TimelineNode):
            return False

        if not node.name:
            return False

        if node.start_time < 0:
            return False

        if node.duration < 0:
            return False

        if not isinstance(node.children, list):
            return False

        return True

    # ------------------------------------------------------------------

    def validate_range(
        self,
        start: float,
        end: float,
    ) -> bool:
        """
        Validate a time range.
        """

        if start < 0:
            return False

        if end < 0:
            return False

        if start > end:
            return False

        return True

    # ------------------------------------------------------------------

    def check_integrity(
        self,
    ) -> bool:
        """
        Check internal timeline consistency.
        """

        if not isinstance(self._events, list):
            return False

        if not isinstance(self._nodes, list):
            return False

        if self._max_events <= 0:
            return False

        if self._created_at > self._updated_at:
            return False

        ids = set()

        for event in self._events:

            if event.id in ids:
                return False

            ids.add(event.id)

        return True
# ------------------------------------------------------------------
# Events & Hooks
# ------------------------------------------------------------------

self._hooks = {

    "before_add": [],

    "after_add": [],

    "before_render": [],

    "after_render": [],

    "before_export": [],

    "after_export": [],

}
# ==============================================================================
# Part 8. Python Protocols
# ==============================================================================

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"id={self._id!r}, "
            f"name={self._name!r}, "
            f"events={len(self._events)}, "
            f"nodes={len(self._nodes)})"
        )

    # ------------------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """

        return (
            f"{self._name} "
            f"[events={self.event_count}, "
            f"nodes={self.node_count}]"
        )

    # ------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Number of events.
        """

        return len(self._events)

    # ------------------------------------------------------------------

    def __iter__(
        self,
    ):
        """
        Iterate over timeline events.
        """

        return iter(self._events)

    # ------------------------------------------------------------------

    def __contains__(
        self,
        item,
    ) -> bool:
        """
        Membership test.
        """

        return item in self._events

    # ------------------------------------------------------------------

    def __getitem__(
        self,
        index,
    ):
        """
        Random access.
        """

        return self._events[index]

    # ------------------------------------------------------------------

    def __call__(
        self,
        *,
        format: str = "dict",
    ):
        """
        Shortcut for render().
        """

        return self.render(format)

    # ------------------------------------------------------------------

    def __copy__(
        self,
    ):
        """
        Shallow copy.
        """

        return self.copy()

    # ------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo,
    ):
        """
        Deep copy.
        """

        cloned = self.clone()

        memo[id(self)] = cloned

        return cloned
# ==============================================================================
# Part 9. Lifecycle Management
# ==============================================================================

    def enable(self) -> "Timeline":
        """
        Enable timeline.
        """

        if not self._closed:
            self._enabled = True

        return self

    # ------------------------------------------------------------------

    def disable(self) -> "Timeline":
        """
        Disable timeline.
        """

        self._enabled = False

        return self

    # ------------------------------------------------------------------

    def freeze(self) -> "Timeline":
        """
        Freeze timeline.

        Frozen timelines reject modifications
        but still allow read operations.
        """

        self._frozen = True

        return self

    # ------------------------------------------------------------------

    def unfreeze(self) -> "Timeline":
        """
        Unfreeze timeline.
        """

        if not self._closed:
            self._frozen = False

        return self

    # ------------------------------------------------------------------

    def close(self) -> "Timeline":
        """
        Close timeline permanently.
        """

        self._closed = True
        self._enabled = False

        return self

    # ------------------------------------------------------------------

    def reopen(self) -> "Timeline":
        """
        Reopen a previously closed timeline.
        """

        self._closed = False
        self._enabled = True
        self._frozen = False

        return self

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        """
        Whether timeline is enabled.
        """

        return self._enabled

    # ------------------------------------------------------------------

    @property
    def frozen(self) -> bool:
        """
        Whether timeline is frozen.
        """

        return self._frozen

    # ------------------------------------------------------------------

    @property
    def closed(self) -> bool:
        """
        Whether timeline has been closed.
        """

        return self._closed

    # ------------------------------------------------------------------

    @property
    def active(self) -> bool:
        """
        Timeline is active when enabled,
        not frozen and not closed.
        """

        return (
            self._enabled
            and not self._frozen
            and not self._closed
        )
# ==============================================================================
# Part 10. Utilities & Diagnostics
# ==============================================================================

    def find(
        self,
        name: str,
    ) -> Optional[TimelineEvent]:
        """
        Find the first event by name.
        """

        for event in self._events:
            if event.name == name:
                return event

        return None

    # ------------------------------------------------------------------

    def filter(
        self,
        predicate,
    ) -> List[TimelineEvent]:
        """
        Filter events using a predicate.
        """

        return [
            event
            for event in self._events
            if predicate(event)
        ]

    # ------------------------------------------------------------------

    def synchronize(
        self,
        offset: float,
    ) -> "Timeline":
        """
        Shift all timestamps by the given offset.
        """

        for event in self._events:
            event.timestamp += offset

        for node in self._nodes:
            node.start_time += offset

        self._updated_at = time.time()

        return self

    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> Dict[str, Any]:
        """
        Runtime diagnostic information.
        """

        return {

            "id": self._id,

            "name": self._name,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "active": self.active,

            "events": self.event_count,

            "nodes": self.node_count,

            "hooks": {
                name: len(callbacks)
                for name, callbacks
                in self._hooks.items()
            },

            "memory_events": len(self._events),

            "memory_nodes": len(self._nodes),

            "created_at": self._created_at,

            "updated_at": self._updated_at,
        }

    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> "Timeline":
        """
        Remove all events and nodes.
        """

        self._events.clear()
        self._nodes.clear()

        self._updated_at = time.time()

        return self

    # ------------------------------------------------------------------

    def reset(
        self,
    ) -> "Timeline":
        """
        Reset runtime state while preserving configuration.
        """

        self.clear()

        self._enabled = True
        self._frozen = False
        self._closed = False

        self._updated_at = time.time()

        return self

    # ------------------------------------------------------------------

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Convert timeline to a dictionary representation.
        """

        return {

            "id": self._id,

            "name": self._name,

            "version": self._version,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "events": self.render_dict(),

            "statistics": self.summary(),
        }                                                                