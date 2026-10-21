"""
SciOS-NG Runtime Observability

FlameGraph Dashboard
====================

High-performance flame graph implementation for:

    • Runtime profiling
    • CPU profiling
    • Memory profiling
    • Execution tracing
    • Timeline visualization

This module converts execution stacks into hierarchical
call trees and provides multiple rendering backends
(SVG, HTML, JSON, ASCII).
"""

from __future__ import annotations

# ==============================================================================
# Part 1.1 Imports
# ==============================================================================

import copy
import json
import math
import time
import uuid

from collections import defaultdict
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field

from enum import Enum
from enum import auto

from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import List
from typing import MutableMapping
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple
from typing import TypeAlias
from typing import Union

# ==============================================================================
# Part 1.2 Constants
# ==============================================================================

#
# Module Information
#

FLAMEGRAPH_NAME = "SciOS Runtime FlameGraph"

FLAMEGRAPH_VERSION = "0.1.0"

FLAMEGRAPH_AUTHOR = "SciOS-NG"

#
# Identity
#

DEFAULT_NAME = "Runtime FlameGraph"

DEFAULT_DESCRIPTION = (
    "Runtime profiling flame graph"
)

#
# Rendering
#

DEFAULT_RENDERER = "svg"

DEFAULT_RENDER_FORMAT = "svg"

DEFAULT_THEME = "hot"

DEFAULT_FONT = "monospace"

DEFAULT_FONT_SIZE = 11

DEFAULT_NODE_HEIGHT = 20

DEFAULT_NODE_PADDING = 2

DEFAULT_CANVAS_WIDTH = 1600

DEFAULT_CANVAS_HEIGHT = 900

#
# Profiling
#

DEFAULT_SAMPLE_RATE = 1000

DEFAULT_TIME_UNIT = "ms"

DEFAULT_MAX_DEPTH = 128

DEFAULT_MAX_STACK_DEPTH = 1024

DEFAULT_MAX_CHILDREN = 4096

#
# Runtime
#

DEFAULT_ENABLED = True

DEFAULT_FROZEN = False

DEFAULT_CLOSED = False

DEFAULT_AUTO_COMPACT = True

DEFAULT_AUTO_BUILD = True

DEFAULT_VALIDATE_ON_BUILD = True

#
# Events
#

DEFAULT_MAX_EVENTS = 1000

#
# Memory
#

DEFAULT_MAX_FRAMES = 100000

DEFAULT_MAX_NODES = 100000

DEFAULT_MAX_METADATA = 10000

#
# Colors
#

DEFAULT_ROOT_COLOR = "#ff9800"

DEFAULT_NODE_COLOR = "#ffb74d"

DEFAULT_TEXT_COLOR = "#000000"

DEFAULT_BACKGROUND_COLOR = "#ffffff"

#
# Export
#

DEFAULT_EXPORT_ENCODING = "utf-8"

DEFAULT_JSON_INDENT = 2

#
# Statistics
#

EMPTY_STATISTICS = {

    "frames": 0,

    "nodes": 0,

    "samples": 0,

    "depth": 0,

    "duration": 0.0,

}

#
# Hook Names
#

HOOK_BEFORE_BUILD = "before_build"

HOOK_AFTER_BUILD = "after_build"

HOOK_BEFORE_RENDER = "before_render"

HOOK_AFTER_RENDER = "after_render"

HOOK_BEFORE_EXPORT = "before_export"

HOOK_AFTER_EXPORT = "after_export"

SUPPORTED_HOOKS = (

    HOOK_BEFORE_BUILD,

    HOOK_AFTER_BUILD,

    HOOK_BEFORE_RENDER,

    HOOK_AFTER_RENDER,

    HOOK_BEFORE_EXPORT,

    HOOK_AFTER_EXPORT,

)

#
# Render Formats
#

SUPPORTED_RENDERERS = (

    "svg",

    "html",

    "json",

    "dict",

    "ascii",

)

#
# Time Units
#

SUPPORTED_TIME_UNITS = (

    "ns",

    "us",

    "ms",

    "s",

)

#
# File Extensions
#

SVG_EXTENSION = ".svg"

HTML_EXTENSION = ".html"

JSON_EXTENSION = ".json"

TXT_EXTENSION = ".txt"

#
# Miscellaneous
#

UNKNOWN_FUNCTION = "<unknown>"

ROOT_NODE_NAME = "root"

INVALID_NODE_ID = ""
# ==============================================================================
# Part 1.3 Enums
# ==============================================================================

class FlameNodeType(Enum):
    """
    Type of flame graph node.
    """

    ROOT = auto()
    FRAME = auto()
    FUNCTION = auto()
    METHOD = auto()
    MODULE = auto()
    CLASS = auto()
    THREAD = auto()
    PROCESS = auto()
    TASK = auto()
    SPAN = auto()
    EVENT = auto()
    CUSTOM = auto()

    def __str__(self) -> str:
        return self.name.lower()


# ------------------------------------------------------------------------------


class FlameRenderFormat(Enum):
    """
    Supported rendering formats.
    """

    DICT = "dict"
    JSON = "json"
    HTML = "html"
    SVG = "svg"
    ASCII = "ascii"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def values(cls) -> List[str]:
        """
        Return all supported format values.
        """
        return [item.value for item in cls]

    @classmethod
    def has_value(
        cls,
        value: str,
    ) -> bool:
        """
        Check whether a format is supported.
        """
        return value in cls.values()


# ------------------------------------------------------------------------------


class FlameColorScheme(Enum):
    """
    Built-in color schemes.
    """

    HOT = "hot"
    COOL = "cool"
    WARM = "warm"
    FIRE = "fire"
    OCEAN = "ocean"
    FOREST = "forest"
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    MONO = "mono"
    CUSTOM = "custom"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def values(cls) -> List[str]:
        return [item.value for item in cls]


# ------------------------------------------------------------------------------


class FlameGraphState(Enum):
    """
    Runtime lifecycle state of the FlameGraph.
    """

    CREATED = auto()
    INITIALIZED = auto()
    READY = auto()
    BUILDING = auto()
    BUILT = auto()
    RENDERING = auto()
    EXPORTED = auto()
    FROZEN = auto()
    DISABLED = auto()
    CLOSED = auto()
    ERROR = auto()

    @property
    def active(self) -> bool:
        """
        Whether the state allows runtime operations.
        """
        return self in {
            FlameGraphState.READY,
            FlameGraphState.BUILDING,
            FlameGraphState.BUILT,
            FlameGraphState.RENDERING,
        }

    @property
    def terminal(self) -> bool:
        """
        Whether the state is terminal.
        """
        return self in {
            FlameGraphState.CLOSED,
            FlameGraphState.ERROR,
        }

    def __str__(self) -> str:
        return self.name.lower()
# ==============================================================================
# Part 1.4 Type Aliases
# ==============================================================================

#
# Basic Identifiers
#

NodeID: TypeAlias = str

FrameID: TypeAlias = str

GraphID: TypeAlias = str

EventID: TypeAlias = str

#
# Time
#

Timestamp: TypeAlias = float

Duration: TypeAlias = float

SampleCount: TypeAlias = int

Depth: TypeAlias = int

#
# Stack Representation
#

StackFrame: TypeAlias = str

StackTrace: TypeAlias = List[StackFrame]

CallPath: TypeAlias = List[NodeID]

#
# Metadata
#

Metadata: TypeAlias = Dict[str, Any]

Attributes: TypeAlias = Dict[str, Any]

Tags: TypeAlias = Dict[str, str]

Labels: TypeAlias = Dict[str, str]

#
# Graph Collections
#

NodeMap: TypeAlias = Dict[NodeID, "FlameNode"]

FrameMap: TypeAlias = Dict[FrameID, "FlameFrame"]

NodeList: TypeAlias = List["FlameNode"]

FrameList: TypeAlias = List["FlameFrame"]

#
# Runtime Structures
#

HookCallback: TypeAlias = Callable[..., Any]

HookRegistry: TypeAlias = Dict[
    str,
    List[HookCallback],
]

EventRecord: TypeAlias = Dict[str, Any]

EventHistory: TypeAlias = List[EventRecord]

#
# Rendering
#

RenderResult: TypeAlias = Union[
    str,
    Dict[str, Any],
]

RenderOptions: TypeAlias = Dict[str, Any]

#
# Serialization
#

JSONDict: TypeAlias = Dict[str, Any]

JSONObject: TypeAlias = Dict[str, Any]

JSONArray: TypeAlias = List[Any]

#
# Statistics
#

Statistics: TypeAlias = Dict[str, Any]

Summary: TypeAlias = Dict[str, Any]

#
# Export
#

FlamePayload: TypeAlias = Dict[str, Any]

ExportPayload: TypeAlias = Dict[str, Any]

Snapshot: TypeAlias = Dict[str, Any]

#
# Generic Runtime
#

FlameValue: TypeAlias = Union[
    int,
    float,
]

FlameData: TypeAlias = Union[
    Dict[str, Any],
    List[Any],
    str,
    int,
    float,
    bool,
    None,
]
# ==============================================================================
# Part 1.5 Dataclasses
# FlameFrame
# ==============================================================================

@dataclass(slots=True)
class FlameFrame:
    """
    Represents a single execution frame collected by the profiler.

    A FlameFrame is the atomic profiling record used to construct
    the hierarchical FlameGraph.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    id: FrameID = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    name: str = ""

    function: str = UNKNOWN_FUNCTION

    module: str = ""

    filename: str = ""

    line: int = 0

    qualified_name: str = ""

    # ------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------

    timestamp: Timestamp = field(
        default_factory=time.time
    )

    start_time: Timestamp = 0.0

    end_time: Timestamp = 0.0

    duration: Duration = 0.0

    self_time: Duration = 0.0

    total_time: Duration = 0.0

    # ------------------------------------------------------------------
    # Sampling
    # ------------------------------------------------------------------

    samples: SampleCount = 0

    weight: float = 1.0

    frequency: float = 0.0

    # ------------------------------------------------------------------
    # Execution Context
    # ------------------------------------------------------------------

    thread: str = ""

    process: str = ""

    task: str = ""

    trace_id: str = ""

    span_id: str = ""

    parent_frame: Optional[FrameID] = None

    stack_depth: Depth = 0

    stack_trace: StackTrace = field(
        default_factory=list
    )

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    node_type: FlameNodeType = (
        FlameNodeType.FRAME
    )

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    metadata: Metadata = field(
        default_factory=dict
    )

    attributes: Attributes = field(
        default_factory=dict
    )

    tags: Tags = field(
        default_factory=dict
    )

    labels: Labels = field(
        default_factory=dict
    )

    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    enabled: bool = True

    visible: bool = True

    collapsed: bool = False

    selected: bool = False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def is_root(self) -> bool:
        """
        Whether this frame is a root frame.
        """

        return self.parent_frame is None

    @property
    def is_leaf(self) -> bool:
        """
        Whether this frame has no stack trace.
        """

        return len(self.stack_trace) == 0

    @property
    def elapsed(self) -> Duration:
        """
        Elapsed execution time.
        """

        if self.duration > 0:
            return self.duration

        if self.end_time > self.start_time:
            return self.end_time - self.start_time

        return 0.0

    # ------------------------------------------------------------------

    def update_duration(
        self,
        duration: Duration,
    ) -> None:
        """
        Update execution duration.
        """

        self.duration = max(0.0, duration)
        self.total_time = self.duration

    # ------------------------------------------------------------------

    def increment_samples(
        self,
        count: int = 1,
    ) -> None:
        """
        Increment sample count.
        """

        self.samples += max(0, count)

    # ------------------------------------------------------------------

    def add_tag(
        self,
        key: str,
        value: str,
    ) -> None:
        """
        Add a tag.
        """

        self.tags[key] = value

    # ------------------------------------------------------------------

    def add_attribute(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Add an attribute.
        """

        self.attributes[key] = value

    # ------------------------------------------------------------------

    def add_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Add metadata.
        """

        self.metadata[key] = value

    # ------------------------------------------------------------------

    def reset(self) -> None:
        """
        Reset runtime statistics.
        """

        self.samples = 0
        self.duration = 0.0
        self.self_time = 0.0
        self.total_time = 0.0

    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.
        """

        return asdict(self)

    # ------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "FlameFrame":
        """
        Create a frame from dictionary.
        """

        return cls(**data)

    # ------------------------------------------------------------------

    def copy(self) -> "FlameFrame":
        """
        Return a deep copy.
        """

        return copy.deepcopy(self)

    # ------------------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"FlameFrame("
            f"name={self.function!r}, "
            f"duration={self.duration:.3f}, "
            f"samples={self.samples})"
        )
# ==============================================================================
# Part 1.5 Dataclasses
# FlameNode
# ==============================================================================

@dataclass(slots=True)
class FlameNode:
    """
    Represents a node in the FlameGraph call tree.

    A FlameNode aggregates one or more FlameFrame objects and forms
    the hierarchical structure used for rendering and analysis.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    id: NodeID = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    name: str = ""

    node_type: FlameNodeType = FlameNodeType.FUNCTION

    # ------------------------------------------------------------------
    # Hierarchy
    # ------------------------------------------------------------------

    parent: Optional[NodeID] = None

    children: List[NodeID] = field(
        default_factory=list
    )

    depth: Depth = 0

    level: int = 0

    order: int = 0

    # ------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------

    start_time: Timestamp = 0.0

    end_time: Timestamp = 0.0

    duration: Duration = 0.0

    self_time: Duration = 0.0

    total_time: Duration = 0.0

    # ------------------------------------------------------------------
    # Profiling
    # ------------------------------------------------------------------

    value: float = 0.0

    samples: SampleCount = 0

    weight: float = 1.0

    frequency: float = 0.0

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    color: str = DEFAULT_NODE_COLOR

    width: float = 0.0

    height: float = float(DEFAULT_NODE_HEIGHT)

    x: float = 0.0

    y: float = 0.0

    visible: bool = True

    collapsed: bool = False

    selected: bool = False

    highlighted: bool = False

    # ------------------------------------------------------------------
    # References
    # ------------------------------------------------------------------

    frame_ids: List[FrameID] = field(
        default_factory=list
    )

    stack_trace: StackTrace = field(
        default_factory=list
    )

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    metadata: Metadata = field(
        default_factory=dict
    )

    attributes: Attributes = field(
        default_factory=dict
    )

    tags: Tags = field(
        default_factory=dict
    )

    labels: Labels = field(
        default_factory=dict
    )

    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    enabled: bool = True

    expanded: bool = True

    dirty: bool = False

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_root(self) -> bool:
        """
        Whether this node is the graph root.
        """
        return self.parent is None

    @property
    def is_leaf(self) -> bool:
        """
        Whether this node has no children.
        """
        return len(self.children) == 0

    @property
    def child_count(self) -> int:
        """
        Number of child nodes.
        """
        return len(self.children)

    @property
    def has_frames(self) -> bool:
        """
        Whether the node references FlameFrame objects.
        """
        return bool(self.frame_ids)

    # ------------------------------------------------------------------
    # Hierarchy Helpers
    # ------------------------------------------------------------------

    def add_child(
        self,
        node_id: NodeID,
    ) -> None:
        """
        Add a child node reference.
        """
        if node_id not in self.children:
            self.children.append(node_id)

    # ------------------------------------------------------------------

    def remove_child(
        self,
        node_id: NodeID,
    ) -> None:
        """
        Remove a child node reference.
        """
        if node_id in self.children:
            self.children.remove(node_id)

    # ------------------------------------------------------------------

    def add_frame(
        self,
        frame_id: FrameID,
    ) -> None:
        """
        Associate a FlameFrame with this node.
        """
        if frame_id not in self.frame_ids:
            self.frame_ids.append(frame_id)

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def increment_samples(
        self,
        count: int = 1,
    ) -> None:
        """
        Increase sample count.
        """
        self.samples += max(0, count)

    # ------------------------------------------------------------------

    def update_duration(
        self,
        duration: Duration,
    ) -> None:
        """
        Update execution duration.
        """
        self.duration = max(0.0, duration)

    # ------------------------------------------------------------------

    def update_self_time(
        self,
        value: Duration,
    ) -> None:
        """
        Update exclusive execution time.
        """
        self.self_time = max(0.0, value)

    # ------------------------------------------------------------------

    def update_total_time(
        self,
        value: Duration,
    ) -> None:
        """
        Update inclusive execution time.
        """
        self.total_time = max(0.0, value)

    # ------------------------------------------------------------------
    # Metadata Helpers
    # ------------------------------------------------------------------

    def add_tag(
        self,
        key: str,
        value: str,
    ) -> None:
        self.tags[key] = value

    # ------------------------------------------------------------------

    def add_attribute(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.attributes[key] = value

    # ------------------------------------------------------------------

    def add_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.metadata[key] = value

    # ------------------------------------------------------------------
    # Runtime Helpers
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """
        Reset runtime profiling values.
        """
        self.samples = 0
        self.value = 0.0
        self.duration = 0.0
        self.self_time = 0.0
        self.total_time = 0.0

    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert node to dictionary.
        """
        return asdict(self)

    # ------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "FlameNode":
        """
        Create a node from a dictionary.
        """
        return cls(**data)

    # ------------------------------------------------------------------

    def copy(self) -> "FlameNode":
        """
        Create a deep copy.
        """
        return copy.deepcopy(self)

    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            "FlameNode("
            f"name={self.name!r}, "
            f"type={self.node_type.name}, "
            f"depth={self.depth}, "
            f"samples={self.samples}, "
            f"duration={self.duration:.3f})"
        )
# ==============================================================================
# Part 1.5 Dataclasses
# FlameGraphOptions
# ==============================================================================

@dataclass(slots=True)
class FlameGraphOptions:
    """
    Configuration options for FlameGraph.

    This dataclass centralizes all runtime, rendering,
    profiling, validation, export and visualization settings.
    """

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    renderer: str = DEFAULT_RENDERER

    render_format: FlameRenderFormat = (
        FlameRenderFormat.SVG
    )

    theme: FlameColorScheme = (
        FlameColorScheme.HOT
    )

    font: str = DEFAULT_FONT

    font_size: int = DEFAULT_FONT_SIZE

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    canvas_width: int = DEFAULT_CANVAS_WIDTH

    canvas_height: int = DEFAULT_CANVAS_HEIGHT

    node_height: int = DEFAULT_NODE_HEIGHT

    node_padding: int = DEFAULT_NODE_PADDING

    max_depth: int = DEFAULT_MAX_DEPTH

    # ------------------------------------------------------------------
    # Profiling
    # ------------------------------------------------------------------

    sample_rate: int = DEFAULT_SAMPLE_RATE

    time_unit: str = DEFAULT_TIME_UNIT

    auto_build: bool = DEFAULT_AUTO_BUILD

    auto_compact: bool = DEFAULT_AUTO_COMPACT

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    validate_on_build: bool = (
        DEFAULT_VALIDATE_ON_BUILD
    )

    strict: bool = False

    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    enabled: bool = DEFAULT_ENABLED

    frozen: bool = DEFAULT_FROZEN

    closed: bool = DEFAULT_CLOSED

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    encoding: str = DEFAULT_EXPORT_ENCODING

    json_indent: int = DEFAULT_JSON_INDENT

    # ------------------------------------------------------------------
    # Visualization
    # ------------------------------------------------------------------

    show_labels: bool = True

    show_tooltips: bool = True

    show_grid: bool = False

    show_statistics: bool = True

    animate: bool = False

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    metadata: Metadata = field(
        default_factory=dict
    )

    attributes: Attributes = field(
        default_factory=dict
    )

    tags: Tags = field(
        default_factory=dict
    )

    labels: Labels = field(
        default_factory=dict
    )

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """
        Restore default configuration.
        """

        self.__dict__.update(
            FlameGraphOptions().__dict__
        )

    # ------------------------------------------------------------------

    def update(
        self,
        **kwargs: Any,
    ) -> None:
        """
        Update configuration values.

        Unknown keys are ignored.
        """

        for key, value in kwargs.items():

            if hasattr(self, key):

                setattr(self, key, value)

    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert options to dictionary.
        """

        return asdict(self)

    # ------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "FlameGraphOptions":
        """
        Create options from dictionary.
        """

        return cls(**data)

    # ------------------------------------------------------------------

    def copy(self) -> "FlameGraphOptions":
        """
        Return a deep copy.
        """

        return copy.deepcopy(self)

    # ------------------------------------------------------------------

    def __repr__(self) -> str:

        return (
            "FlameGraphOptions("
            f"renderer={self.renderer!r}, "
            f"format={self.render_format.value!r}, "
            f"theme={self.theme.value!r}, "
            f"sample_rate={self.sample_rate}, "
            f"max_depth={self.max_depth})"
        )
# ==============================================================================
# Part 1.5 Dataclasses
# FlameGraphStatistics
# ==============================================================================

@dataclass(slots=True)
class FlameGraphStatistics:
    """
    Runtime statistics for FlameGraph.

    Stores profiling, rendering, export and runtime metrics.
    """

    # ------------------------------------------------------------------
    # Graph Statistics
    # ------------------------------------------------------------------

    frame_count: int = 0

    node_count: int = 0

    root_count: int = 0

    leaf_count: int = 0

    max_depth: int = 0

    max_children: int = 0

    # ------------------------------------------------------------------
    # Profiling Statistics
    # ------------------------------------------------------------------

    total_samples: int = 0

    average_samples: float = 0.0

    total_duration: float = 0.0

    average_duration: float = 0.0

    max_duration: float = 0.0

    # ------------------------------------------------------------------
    # Rendering Statistics
    # ------------------------------------------------------------------

    build_count: int = 0

    render_count: int = 0

    export_count: int = 0

    last_build: float = 0.0

    last_render: float = 0.0

    last_export: float = 0.0

    # ------------------------------------------------------------------
    # Validation Statistics
    # ------------------------------------------------------------------

    validation_count: int = 0

    validation_errors: int = 0

    integrity_checks: int = 0

    # ------------------------------------------------------------------
    # Runtime Statistics
    # ------------------------------------------------------------------

    created_at: float = field(
        default_factory=time.time
    )

    updated_at: float = field(
        default_factory=time.time
    )

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    metadata: Metadata = field(
        default_factory=dict
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def touch(self) -> None:
        """
        Update modification timestamp.
        """

        self.updated_at = time.time()

    # ------------------------------------------------------------------

    def reset(self) -> None:
        """
        Reset all runtime statistics.
        """

        self.frame_count = 0
        self.node_count = 0
        self.root_count = 0
        self.leaf_count = 0

        self.max_depth = 0
        self.max_children = 0

        self.total_samples = 0
        self.average_samples = 0.0

        self.total_duration = 0.0
        self.average_duration = 0.0
        self.max_duration = 0.0

        self.build_count = 0
        self.render_count = 0
        self.export_count = 0

        self.last_build = 0.0
        self.last_render = 0.0
        self.last_export = 0.0

        self.validation_count = 0
        self.validation_errors = 0
        self.integrity_checks = 0

        self.metadata.clear()

        self.touch()

    # ------------------------------------------------------------------

    def report(self) -> Dict[str, Any]:
        """
        Return statistics report.
        """

        return asdict(self)

    # ------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """
        Return a compact summary.
        """

        return {
            "frames": self.frame_count,
            "nodes": self.node_count,
            "samples": self.total_samples,
            "duration": self.total_duration,
            "renders": self.render_count,
            "exports": self.export_count,
        }

    # ------------------------------------------------------------------

    def copy(self) -> "FlameGraphStatistics":
        """
        Return a deep copy.
        """

        return copy.deepcopy(self)

    # ------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "FlameGraphStatistics":
        """
        Create statistics from dictionary.
        """

        return cls(**data)

    # ------------------------------------------------------------------

    def __repr__(self) -> str:

        return (
            "FlameGraphStatistics("
            f"frames={self.frame_count}, "
            f"nodes={self.node_count}, "
            f"samples={self.total_samples}, "
            f"renders={self.render_count}, "
            f"exports={self.export_count})"
        )
# ==============================================================================
# FlameGraph
# ==============================================================================

class FlameGraph:
    """
    Runtime FlameGraph.

    Hierarchical execution graph used for profiling, visualization,
    performance analysis and observability.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        name: str = DEFAULT_NAME,
        options: Optional[FlameGraphOptions] = None,
    ) -> None:

        options = options or FlameGraphOptions()

        # ==============================================================
        # Identity
        # ==============================================================

        self._id: GraphID = str(uuid.uuid4())

        self._name: str = name

        self._description: str = DEFAULT_DESCRIPTION

        self._version: str = FLAMEGRAPH_VERSION

        self._author: str = FLAMEGRAPH_AUTHOR

        self._type: str = "flamegraph"

        # ==============================================================
        # Configuration
        # ==============================================================

        self._options: FlameGraphOptions = options

        self._renderer: str = options.renderer

        self._render_format: FlameRenderFormat = (
            options.render_format
        )

        self._theme: FlameColorScheme = (
            options.theme
        )

        self._sample_rate: int = (
            options.sample_rate
        )

        self._time_unit: str = (
            options.time_unit
        )

        self._canvas_width: int = (
            options.canvas_width
        )

        self._canvas_height: int = (
            options.canvas_height
        )

        self._max_depth: int = (
            options.max_depth
        )

        # ==============================================================
        # Runtime State
        # ==============================================================

        self._state: FlameGraphState = (
            FlameGraphState.CREATED
        )

        self._enabled: bool = options.enabled

        self._frozen: bool = options.frozen

        self._closed: bool = options.closed

        self._dirty: bool = False

        # ==============================================================
        # Graph Storage
        # ==============================================================

        self._root: Optional[NodeID] = None

        self._nodes: NodeMap = {}

        self._frames: FrameMap = {}

        self._graph: NodeList = []

        # ==============================================================
        # Statistics
        # ==============================================================

        self._statistics = (
            FlameGraphStatistics()
        )

        # ==============================================================
        # Events
        # ==============================================================

        self._events: EventHistory = []

        self._max_events: int = (
            DEFAULT_MAX_EVENTS
        )

        # ==============================================================
        # Hooks
        # ==============================================================

        self._hooks: HookRegistry = {

            HOOK_BEFORE_BUILD: [],

            HOOK_AFTER_BUILD: [],

            HOOK_BEFORE_RENDER: [],

            HOOK_AFTER_RENDER: [],

            HOOK_BEFORE_EXPORT: [],

            HOOK_AFTER_EXPORT: [],

        }

        # ==============================================================
        # Metadata
        # ==============================================================

        self._metadata: Metadata = {}

        self._attributes: Attributes = {}

        self._tags: Tags = {}

        self._labels: Labels = {}

        self._created_at: float = time.time()

        self._updated_at: float = (
            self._created_at
        )

        # ==============================================================
        # Initialize State
        # ==============================================================

        self._state = FlameGraphState.READY                                        
# ==============================================================================
# Part 2. Graph API
# ==============================================================================

    def add_frame(
        self,
        frame: FlameFrame,
    ) -> FlameFrame:
        """
        Add a sampled execution frame.
        """

        if self._closed:
            raise RuntimeError("FlameGraph is closed.")

        if self._frozen:
            raise RuntimeError("FlameGraph is frozen.")

        self._frames.append(frame)

        self._updated_at = time.time()

        return frame

    # ------------------------------------------------------------------

    def add_node(
        self,
        node: FlameNode,
    ) -> FlameNode:
        """
        Add a node to the graph.
        """

        if self._closed:
            raise RuntimeError("FlameGraph is closed.")

        if self._frozen:
            raise RuntimeError("FlameGraph is frozen.")

        self._nodes.append(node)

        if self._root is None:
            self._root = node

        self._updated_at = time.time()

        return node

    # ------------------------------------------------------------------

    def add_stack(
        self,
        stack: List[str],
        *,
        value: float = 1.0,
        start_time: float = 0.0,
        duration: float = 0.0,
    ) -> Optional[FlameNode]:
        """
        Build a flame graph branch from a call stack.

        Example
        -------
        ["kernel", "scheduler", "worker", "execute"]
        """

        if not stack:
            return None

        parent: Optional[FlameNode] = None

        for depth, name in enumerate(stack):

            node = self.find_node(
                name=name,
                parent=parent.id if parent else None,
            )

            if node is None:

                node = FlameNode(
                    name=name,
                    value=value,
                    start_time=start_time,
                    duration=duration,
                    depth=depth,
                    parent=parent.id if parent else None,
                )

                self.add_node(node)

                if parent is not None:
                    parent.children.append(node.id)

            else:
                node.value += value
                node.duration += duration

            parent = node

        return parent

    # ------------------------------------------------------------------

    def remove_node(
        self,
        node_id: str,
    ) -> bool:
        """
        Remove a node by identifier.
        """

        node = self.find_node(node_id=node_id)

        if node is None:
            return False

        self._nodes.remove(node)

        if node.parent:

            parent = self.find_node(node_id=node.parent)

            if parent and node.id in parent.children:
                parent.children.remove(node.id)

        if self._root is node:
            self._root = None

        self._updated_at = time.time()

        return True

    # ------------------------------------------------------------------

    def find_node(
        self,
        *,
        node_id: Optional[str] = None,
        name: Optional[str] = None,
        parent: Optional[str] = None,
    ) -> Optional[FlameNode]:
        """
        Find a node by id or by (name,parent).
        """

        for node in self._nodes:

            if node_id is not None:

                if node.id == node_id:
                    return node

            else:

                if (
                    node.name == name
                    and node.parent == parent
                ):
                    return node

        return None

    # ------------------------------------------------------------------

    def merge(
        self,
        other: "FlameGraph",
    ) -> "FlameGraph":
        """
        Merge another flame graph into this graph.
        """

        if not isinstance(other, FlameGraph):
            raise TypeError(
                "other must be a FlameGraph"
            )

        for frame in other.frames:

            self.add_frame(
                copy.deepcopy(frame)
            )

        for node in other.nodes:

            existing = self.find_node(
                name=node.name,
                parent=node.parent,
            )

            if existing:

                existing.value += node.value
                existing.duration += node.duration

            else:

                self.add_node(
                    copy.deepcopy(node)
                )

        self._updated_at = time.time()

        return self

    # ------------------------------------------------------------------

    def build(
        self,
    ) -> "FlameGraph":
        """
        Build the flame graph from all frames.

        Frames are grouped into a hierarchical tree.
        """

        self._nodes.clear()

        self._root = None

        for frame in self._frames:

            stack = frame.metadata.get(
                "stack",
                [frame.function],
            )

            self.add_stack(
                stack=stack,
                value=frame.samples,
                start_time=frame.timestamp,
                duration=frame.duration,
            )

        self._updated_at = time.time()

        return self
# ==============================================================================
# Part 3. Rendering API
# ==============================================================================

    def render(
        self,
        format: str = "dict",
    ) -> Any:
        """
        Render the flame graph in the requested format.

        Supported formats:
            - dict
            - json
            - html
            - svg
            - ascii
        """

        format = format.lower()

        if format == "dict":
            return self.render_dict()

        if format == "json":
            return self.render_json()

        if format == "html":
            return self.render_html()

        if format == "svg":
            return self.render_svg()

        if format == "ascii":
            return self.render_ascii()

        raise ValueError(
            f"Unsupported render format: {format}"
        )

    # ------------------------------------------------------------------

    def render_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Render flame graph as a dictionary.
        """

        return {

            "id": self._id,

            "name": self._name,

            "version": self._version,

            "renderer": self._renderer,

            "frames": [

                {

                    "id": frame.id,

                    "function": frame.function,

                    "module": frame.module,

                    "duration": frame.duration,

                    "samples": frame.samples,

                }

                for frame in self._frames

            ],

            "nodes": [

                {

                    "id": node.id,

                    "name": node.name,

                    "value": node.value,

                    "depth": node.depth,

                    "parent": node.parent,

                    "children": node.children,

                    "duration": node.duration,

                }

                for node in self._nodes

            ],

        }

    # ------------------------------------------------------------------

    def render_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        """
        Render flame graph as JSON.
        """

        import json

        return json.dumps(

            self.render_dict(),

            indent=indent,

            ensure_ascii=False,

        )

    # ------------------------------------------------------------------

    def render_html(
        self,
    ) -> str:
        """
        Render flame graph as a minimal HTML page.
        """

        body = []

        for node in self._nodes:

            margin = node.depth * 24

            width = max(
                40,
                int(node.duration * 100),
            )

            body.append(

                f"""
<div style="
margin-left:{margin}px;
background:#ff914d;
margin-top:2px;
padding:4px;
width:{width}px;">
{node.name}
({node.duration:.3f} ms)
</div>
"""

            )

        return f"""
<html>

<head>

<title>{self._name}</title>

</head>

<body>

<h2>{self._name}</h2>

{''.join(body)}

</body>

</html>
"""

    # ------------------------------------------------------------------

    def render_svg(
        self,
    ) -> str:
        """
        Render flame graph as SVG.
        """

        height = max(
            200,
            (len(self._nodes) + 2) * 22,
        )

        lines = [

            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="1200" height="{height}">'

        ]

        y = 20

        for node in self._nodes:

            x = node.depth * 30

            width = max(
                40,
                int(node.duration * 100),
            )

            lines.append(

                f'<rect '
                f'x="{x}" '
                f'y="{y}" '
                f'width="{width}" '
                f'height="18" '
                f'fill="orange"/>'

            )

            lines.append(

                f'<text '
                f'x="{x+4}" '
                f'y="{y+13}" '
                f'font-size="10">'
                f'{node.name}'
                f'</text>'

            )

            y += 22

        lines.append("</svg>")

        return "\n".join(lines)

    # ------------------------------------------------------------------

    def render_ascii(
        self,
    ) -> str:
        """
        Render flame graph as ASCII.
        """

        lines = []

        for node in self._nodes:

            indent = "  " * node.depth

            bar = "=" * max(
                1,
                int(node.duration),
            )

            lines.append(

                f"{indent}{bar} "

                f"{node.name} "

                f"({node.duration:.3f} ms)"

            )

        return "\n".join(lines)

    # ------------------------------------------------------------------

    def export(
        self,
        format: str = "json",
    ) -> Any:
        """
        Export flame graph.

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
        Create a complete snapshot of the FlameGraph state.
        """

        return {

            "id": self._id,

            "name": self._name,

            "version": self._version,

            "type": self._type,

            "configuration": {

                "renderer": self._renderer,

                "color_scheme": self._color_scheme,

                "sample_rate": self._sample_rate,

                "time_unit": self._time_unit,

                "max_depth": self._max_depth,

            },

            "runtime": {

                "enabled": self._enabled,

                "frozen": self._frozen,

                "closed": self._closed,

                "created_at": self._created_at,

                "updated_at": self._updated_at,

            },

            "frames": copy.deepcopy(
                self._frames
            ),

            "nodes": copy.deepcopy(
                self._nodes
            ),

            "root": copy.deepcopy(
                self._root
            ),

            "statistics": copy.deepcopy(
                self._statistics
            ),
        }

    # ------------------------------------------------------------------

    def restore(
        self,
        snapshot: Dict[str, Any],
    ) -> "FlameGraph":
        """
        Restore a previously created snapshot.
        """

        cfg = snapshot.get(
            "configuration",
            {},
        )

        runtime = snapshot.get(
            "runtime",
            {},
        )

        self._renderer = cfg.get(
            "renderer",
            self._renderer,
        )

        self._color_scheme = cfg.get(
            "color_scheme",
            self._color_scheme,
        )

        self._sample_rate = cfg.get(
            "sample_rate",
            self._sample_rate,
        )

        self._time_unit = cfg.get(
            "time_unit",
            self._time_unit,
        )

        self._max_depth = cfg.get(
            "max_depth",
            self._max_depth,
        )

        self._enabled = runtime.get(
            "enabled",
            True,
        )

        self._frozen = runtime.get(
            "frozen",
            False,
        )

        self._closed = runtime.get(
            "closed",
            False,
        )

        self._created_at = runtime.get(
            "created_at",
            self._created_at,
        )

        self._updated_at = runtime.get(
            "updated_at",
            time.time(),
        )

        self._frames = copy.deepcopy(
            snapshot.get("frames", [])
        )

        self._nodes = copy.deepcopy(
            snapshot.get("nodes", [])
        )

        self._root = copy.deepcopy(
            snapshot.get("root")
        )

        self._statistics = copy.deepcopy(
            snapshot.get(
                "statistics",
                {},
            )
        )

        return self

    # ------------------------------------------------------------------

    def clone(
        self,
    ) -> "FlameGraph":
        """
        Create a deep cloned FlameGraph.
        """

        cloned = self.__class__(

            name=self._name,

            options=copy.deepcopy(
                self._options
            ),

        )

        cloned.restore(
            self.snapshot()
        )

        return cloned

    # ------------------------------------------------------------------

    def copy(
        self,
    ) -> "FlameGraph":
        """
        Alias of clone().
        """

        return self.clone()

    # ------------------------------------------------------------------

    def cleanup(
        self,
    ) -> "FlameGraph":
        """
        Remove invalid and empty graph objects.
        """

        self._frames = [

            frame

            for frame in self._frames

            if frame.duration >= 0

        ]

        self._nodes = [

            node

            for node in self._nodes

            if node.duration >= 0

        ]

        self._updated_at = time.time()

        return self

    # ------------------------------------------------------------------

    def compact(
        self,
    ) -> "FlameGraph":
        """
        Compact the graph by merging duplicate nodes.
        """

        merged: Dict[
            tuple,
            FlameNode,
        ] = {}

        for node in self._nodes:

            key = (

                node.parent,

                node.name,

            )

            if key in merged:

                existing = merged[key]

                existing.value += node.value

                existing.duration += node.duration

                existing.children.extend(
                    child
                    for child in node.children
                    if child not in existing.children
                )

            else:

                merged[key] = copy.deepcopy(
                    node
                )

        self._nodes = list(
            merged.values()
        )

        self._updated_at = time.time()

        return self
# ==============================================================================
# Part 5. Statistics
# ==============================================================================

    @property
    def frame_count(
        self,
    ) -> int:
        """
        Number of frames.
        """

        return len(self._frames)

    # ------------------------------------------------------------------

    @property
    def node_count(
        self,
    ) -> int:
        """
        Number of graph nodes.
        """

        return len(self._nodes)

    # ------------------------------------------------------------------

    @property
    def max_depth(
        self,
    ) -> int:
        """
        Maximum depth of the flame graph.
        """

        if not self._nodes:
            return 0

        return max(
            node.depth
            for node in self._nodes
        )

    # ------------------------------------------------------------------

    @property
    def total_samples(
        self,
    ) -> int:
        """
        Total profiling samples.
        """

        return sum(
            frame.samples
            for frame in self._frames
        )

    # ------------------------------------------------------------------

    def report(
        self,
    ) -> Dict[str, Any]:
        """
        Generate a detailed statistics report.
        """

        total_duration = sum(
            frame.duration
            for frame in self._frames
        )

        average_duration = (
            total_duration / self.frame_count
            if self.frame_count
            else 0.0
        )

        total_node_value = sum(
            node.value
            for node in self._nodes
        )

        report = {

            "identity": {

                "id": self._id,

                "name": self._name,

                "version": self._version,

                "type": self._type,

            },

            "graph": {

                "frames": self.frame_count,

                "nodes": self.node_count,

                "root": (
                    self._root.name
                    if self._root
                    else None
                ),

                "max_depth": self.max_depth,

            },

            "profiling": {

                "total_samples": self.total_samples,

                "total_duration": total_duration,

                "average_duration": average_duration,

                "total_node_value": total_node_value,

            },

            "runtime": {

                "enabled": self._enabled,

                "frozen": self._frozen,

                "closed": self._closed,

                "created_at": self._created_at,

                "updated_at": self._updated_at,

            },

        }

        self._statistics = report

        return report

    # ------------------------------------------------------------------

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return a compact summary.
        """

        return {

            "frames": self.frame_count,

            "nodes": self.node_count,

            "max_depth": self.max_depth,

            "samples": self.total_samples,

            "enabled": self._enabled,

            "renderer": self._renderer,

        }
# ==============================================================================
# Part 6. Validation
# ==============================================================================

    def validate(self) -> bool:
        """
        Validate the entire FlameGraph.

        Returns
        -------
        bool
            True if the graph is valid.
        """

        return (
            self.validate_graph()
            and all(self.validate_frame(f) for f in self._frames)
            and all(self.validate_node(n) for n in self._nodes)
            and self.check_integrity()
        )

    # ------------------------------------------------------------------

    def validate_node(
        self,
        node: FlameNode,
    ) -> bool:
        """
        Validate a FlameNode.
        """

        if not isinstance(node, FlameNode):
            return False

        if not node.id:
            return False

        if not node.name:
            return False

        if node.depth < 0:
            return False

        if node.duration < 0:
            return False

        if node.value < 0:
            return False

        if not isinstance(node.children, list):
            return False

        return True

    # ------------------------------------------------------------------

    def validate_frame(
        self,
        frame: FlameFrame,
    ) -> bool:
        """
        Validate a FlameFrame.
        """

        if not isinstance(frame, FlameFrame):
            return False

        if not frame.id:
            return False

        if not frame.function:
            return False

        if frame.duration < 0:
            return False

        if frame.samples < 0:
            return False

        if frame.line < 0:
            return False

        return True

    # ------------------------------------------------------------------

    def validate_graph(self) -> bool:
        """
        Validate graph-level configuration.
        """

        if self._max_depth <= 0:
            return False

        if self._sample_rate <= 0:
            return False

        if not self._renderer:
            return False

        if not self._time_unit:
            return False

        return True

    # ------------------------------------------------------------------

    def check_integrity(self) -> bool:
        """
        Check structural integrity of the graph.

        Verifies:

        - unique node ids
        - parent references
        - child references
        - root consistency
        """

        node_map = {
            node.id: node
            for node in self._nodes
        }

        # --------------------------------------------------------------
        # Unique IDs
        # --------------------------------------------------------------

        if len(node_map) != len(self._nodes):
            return False

        # --------------------------------------------------------------
        # Parent references
        # --------------------------------------------------------------

        for node in self._nodes:

            if (
                node.parent is not None
                and node.parent not in node_map
            ):
                return False

        # --------------------------------------------------------------
        # Child references
        # --------------------------------------------------------------

        for node in self._nodes:

            for child in node.children:

                if child not in node_map:
                    return False

        # --------------------------------------------------------------
        # Root consistency
        # --------------------------------------------------------------

        if self._root is not None:

            if self._root.id not in node_map:
                return False

            if self._root.parent is not None:
                return False

        return True
# ==============================================================================
# Part 7. Events & Hooks
# ==============================================================================

    def before_build(
        self,
        callback,
    ) -> "FlameGraph":
        """
        Register a callback executed before build().
        """

        self._hooks["before_build"].append(callback)

        return self

    # ------------------------------------------------------------------

    def after_build(
        self,
        callback,
    ) -> "FlameGraph":
        """
        Register a callback executed after build().
        """

        self._hooks["after_build"].append(callback)

        return self

    # ------------------------------------------------------------------

    def before_render(
        self,
        callback,
    ) -> "FlameGraph":
        """
        Register a callback executed before render().
        """

        self._hooks["before_render"].append(callback)

        return self

    # ------------------------------------------------------------------

    def after_render(
        self,
        callback,
    ) -> "FlameGraph":
        """
        Register a callback executed after render().
        """

        self._hooks["after_render"].append(callback)

        return self

    # ------------------------------------------------------------------

    def before_export(
        self,
        callback,
    ) -> "FlameGraph":
        """
        Register a callback executed before export().
        """

        self._hooks["before_export"].append(callback)

        return self

    # ------------------------------------------------------------------

    def after_export(
        self,
        callback,
    ) -> "FlameGraph":
        """
        Register a callback executed after export().
        """

        self._hooks["after_export"].append(callback)

        return self

    # ------------------------------------------------------------------

    def emit_event(
        self,
        event: str,
        **payload: Any,
    ) -> None:
        """
        Emit an internal event and execute registered hooks.
        """

        record = {

            "timestamp": time.time(),

            "event": event,

            "source": self._id,

            "payload": payload,

        }

        self._events.append(record)

        callbacks = self._hooks.get(event, [])

        for callback in callbacks:

            try:

                callback(self, payload)

            except Exception:

                #
                # Hook failures should never stop runtime execution.
                #
                pass   
# ==============================================================================
# Part 8. Python Protocols
# ==============================================================================

    def __repr__(self) -> str:
        """
        Official string representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"id={self._id!r}, "
            f"name={self._name!r}, "
            f"nodes={len(self._nodes)}, "
            f"frames={len(self._frames)}, "
            f"state={self._state.name})"
        )

    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return (
            f"{self._name} "
            f"(nodes={len(self._nodes)}, "
            f"frames={len(self._frames)})"
        )

    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """
        Return the number of nodes.
        """

        return len(self._nodes)

    # ------------------------------------------------------------------

    def __iter__(self) -> Iterator[FlameNode]:
        """
        Iterate over graph nodes.
        """

        return iter(self._nodes.values())

    # ------------------------------------------------------------------

    def __contains__(
        self,
        node_id: object,
    ) -> bool:
        """
        Check whether a node exists.
        """

        if not isinstance(node_id, str):
            return False

        return node_id in self._nodes

    # ------------------------------------------------------------------

    def __getitem__(
        self,
        node_id: NodeID,
    ) -> FlameNode:
        """
        Return a node by its identifier.
        """

        return self._nodes[node_id]

    # ------------------------------------------------------------------

    def __call__(self) -> Dict[str, Any]:
        """
        Return a dictionary representation.
        """

        return self.render_dict()

    # ------------------------------------------------------------------

    def __copy__(self) -> "FlameGraph":
        """
        Return a shallow copy.
        """

        cls = self.__class__

        result = cls(
            name=self._name,
            options=copy.copy(self._options),
        )

        result._root = self._root
        result._nodes = self._nodes.copy()
        result._frames = self._frames.copy()
        result._statistics = copy.copy(
            self._statistics
        )

        result._metadata = self._metadata.copy()
        result._attributes = self._attributes.copy()
        result._tags = self._tags.copy()
        result._labels = self._labels.copy()

        return result

    # ------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo: Optional[Dict[int, Any]] = None,
    ) -> "FlameGraph":
        """
        Return a deep copy.
        """

        memo = memo or {}

        cls = self.__class__

        result = cls(
            name=self._name,
            options=copy.deepcopy(
                self._options,
                memo,
            ),
        )

        memo[id(self)] = result

        result._root = copy.deepcopy(
            self._root,
            memo,
        )

        result._nodes = copy.deepcopy(
            self._nodes,
            memo,
        )

        result._frames = copy.deepcopy(
            self._frames,
            memo,
        )

        result._statistics = copy.deepcopy(
            self._statistics,
            memo,
        )

        result._events = copy.deepcopy(
            self._events,
            memo,
        )

        result._hooks = copy.deepcopy(
            self._hooks,
            memo,
        )

        result._metadata = copy.deepcopy(
            self._metadata,
            memo,
        )

        result._attributes = copy.deepcopy(
            self._attributes,
            memo,
        )

        result._tags = copy.deepcopy(
            self._tags,
            memo,
        )

        result._labels = copy.deepcopy(
            self._labels,
            memo,
        )

        return result
# ==============================================================================
# Part 9. Lifecycle Management
# ==============================================================================

    # ------------------------------------------------------------------
    # Lifecycle Operations
    # ------------------------------------------------------------------

    def enable(self) -> None:
        """
        Enable the flame graph.
        """

        if self._closed:
            raise RuntimeError(
                "Cannot enable a closed FlameGraph."
            )

        self._enabled = True
        self._state = FlameGraphState.READY
        self._updated_at = time.time()

    # ------------------------------------------------------------------

    def disable(self) -> None:
        """
        Disable the flame graph.
        """

        self._enabled = False
        self._state = FlameGraphState.DISABLED
        self._updated_at = time.time()

    # ------------------------------------------------------------------

    def freeze(self) -> None:
        """
        Freeze the flame graph.

        While frozen, no modifications should be made.
        """

        if self._closed:
            raise RuntimeError(
                "Cannot freeze a closed FlameGraph."
            )

        self._frozen = True
        self._state = FlameGraphState.FROZEN
        self._updated_at = time.time()

    # ------------------------------------------------------------------

    def unfreeze(self) -> None:
        """
        Unfreeze the flame graph.
        """

        if self._closed:
            raise RuntimeError(
                "Cannot unfreeze a closed FlameGraph."
            )

        self._frozen = False

        if self._enabled:
            self._state = FlameGraphState.READY
        else:
            self._state = FlameGraphState.DISABLED

        self._updated_at = time.time()

    # ------------------------------------------------------------------

    def close(self) -> None:
        """
        Close the flame graph permanently.
        """

        self._closed = True
        self._enabled = False
        self._frozen = False

        self._state = FlameGraphState.CLOSED
        self._updated_at = time.time()

    # ------------------------------------------------------------------

    def reopen(self) -> None:
        """
        Reopen a previously closed flame graph.
        """

        self._closed = False
        self._enabled = True
        self._frozen = False

        self._state = FlameGraphState.READY
        self._updated_at = time.time()

    # ------------------------------------------------------------------
    # Lifecycle Properties
    # ------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        """
        Whether the flame graph is enabled.
        """

        return self._enabled

    # ------------------------------------------------------------------

    @property
    def frozen(self) -> bool:
        """
        Whether the flame graph is frozen.
        """

        return self._frozen

    # ------------------------------------------------------------------

    @property
    def closed(self) -> bool:
        """
        Whether the flame graph has been closed.
        """

        return self._closed

    # ------------------------------------------------------------------

    @property
    def active(self) -> bool:
        """
        Whether the flame graph is active.

        A FlameGraph is active only if it is enabled,
        not frozen, and not closed.
        """

        return (
            self._enabled
            and not self._frozen
            and not self._closed
        )
# ==============================================================================
# Part 10. Utilities & Diagnostics
# ==============================================================================

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """
        Remove all nodes, frames, events and reset runtime state.

        Configuration is preserved.
        """

        self._root = None

        self._nodes.clear()

        self._frames.clear()

        self._events.clear()

        self._statistics.reset()

        self._dirty = False

        self._updated_at = time.time()

    # ------------------------------------------------------------------

    def reset(self) -> None:
        """
        Reset the FlameGraph to its initial runtime state.

        Both graph data and configuration are restored.
        """

        self.clear()

        self._options = FlameGraphOptions()

        self._renderer = self._options.renderer

        self._render_format = self._options.render_format

        self._theme = self._options.theme

        self._sample_rate = self._options.sample_rate

        self._time_unit = self._options.time_unit

        self._canvas_width = self._options.canvas_width

        self._canvas_height = self._options.canvas_height

        self._max_depth = self._options.max_depth

        self._enabled = True

        self._frozen = False

        self._closed = False

        self._state = FlameGraphState.READY

    # ------------------------------------------------------------------

    def synchronize(self) -> None:
        """
        Synchronize runtime statistics with current graph state.
        """

        self._statistics.node_count = len(self._nodes)

        self._statistics.frame_count = len(self._frames)

        self._statistics.root_count = sum(
            1
            for node in self._nodes.values()
            if node.parent is None
        )

        self._statistics.leaf_count = sum(
            1
            for node in self._nodes.values()
            if not node.children
        )

        self._updated_at = time.time()

    # ------------------------------------------------------------------

    def diagnostics(self) -> Dict[str, Any]:
        """
        Return runtime diagnostics.
        """

        return {

            "id": self._id,

            "name": self._name,

            "state": self._state.name,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "dirty": self._dirty,

            "nodes": len(self._nodes),

            "frames": len(self._frames),

            "events": len(self._events),

            "created_at": self._created_at,

            "updated_at": self._updated_at,

        }

    # ------------------------------------------------------------------

    def find(
        self,
        name: str,
    ) -> Optional[FlameNode]:
        """
        Find the first node matching the given name.
        """

        for node in self._nodes.values():

            if node.name == name:

                return node

        return None

    # ------------------------------------------------------------------

    def filter(
        self,
        predicate: Callable[[FlameNode], bool],
    ) -> List[FlameNode]:
        """
        Return all nodes satisfying the predicate.
        """

        return [

            node

            for node in self._nodes.values()

            if predicate(node)

        ]

    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the complete FlameGraph into a dictionary.
        """

        return {

            "id": self._id,

            "name": self._name,

            "description": self._description,

            "version": self._version,

            "state": self._state.name,

            "options": self._options.to_dict(),

            "statistics": self._statistics.report(),

            "nodes": {

                node_id: node.to_dict()

                for node_id, node in self._nodes.items()

            },

            "frames": {

                frame_id: frame.to_dict()

                for frame_id, frame in self._frames.items()

            },

            "metadata": self._metadata,

            "attributes": self._attributes,

            "tags": self._tags,

            "labels": self._labels,

            "created_at": self._created_at,

            "updated_at": self._updated_at,

        }                                                                         