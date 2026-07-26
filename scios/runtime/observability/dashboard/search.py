# ==============================================================================
# SciOS-NG
# Runtime Observability Dashboard
# Search Engine
#
# File: scios/runtime/observability/dashboard/search.py
# ==============================================================================

from __future__ import annotations

# ==============================================================================
# Part 1.1 Imports
# ==============================================================================

import copy
import json
import re
import time
import uuid

from dataclasses import (
    asdict,
    dataclass,
    field,
)

from enum import Enum

from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    MutableMapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeAlias,
    Union,
)

# ==============================================================================
# Part 1.2 Constants
# ==============================================================================

# ----------------------------------------------------------------------
# Version
# ----------------------------------------------------------------------

SEARCH_VERSION: str = "0.1.0"

# ----------------------------------------------------------------------
# Identity
# ----------------------------------------------------------------------

DEFAULT_NAME: str = "SearchEngine"

DEFAULT_DESCRIPTION: str = (
    "SciOS Runtime Observability Search Engine"
)

DEFAULT_INDEX_NAME: str = "default"

# ----------------------------------------------------------------------
# Search Defaults
# ----------------------------------------------------------------------

DEFAULT_MAX_RESULTS: int = 100

DEFAULT_CASE_SENSITIVE: bool = False

DEFAULT_REGEX: bool = False

DEFAULT_FUZZY: bool = False

DEFAULT_TIMEOUT: float = 5.0

# ----------------------------------------------------------------------
# Runtime Defaults
# ----------------------------------------------------------------------

DEFAULT_ENABLED: bool = True

DEFAULT_FROZEN: bool = False

DEFAULT_CLOSED: bool = False

# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

DEFAULT_JSON_INDENT: int = 4

DEFAULT_ENCODING: str = "utf-8"

# ----------------------------------------------------------------------
# Statistics
# ----------------------------------------------------------------------

DEFAULT_MAX_EVENTS: int = 1024

DEFAULT_CACHE_SIZE: int = 1024

# ----------------------------------------------------------------------
# Search
# ----------------------------------------------------------------------

DEFAULT_SCORE: float = 1.0

DEFAULT_LIMIT: int = 100

DEFAULT_OFFSET: int = 0

# ----------------------------------------------------------------------
# Time
# ----------------------------------------------------------------------

DEFAULT_TIMESTAMP: float = 0.0

# ----------------------------------------------------------------------
# Misc
# ----------------------------------------------------------------------

UNKNOWN: str = "unknown"

ALL: str = "*"

EMPTY_STRING: str = ""

EMPTY_DICT: Dict[str, Any] = {}

EMPTY_LIST: List[Any] = []

EMPTY_SET: Set[Any] = set()
# ==============================================================================
# Part 1.3 Enums
# ==============================================================================

class SearchState(Enum):
    """
    Runtime state of the SearchEngine.
    """

    CREATED = "created"
    READY = "ready"
    INDEXING = "indexing"
    SEARCHING = "searching"
    RENDERING = "rendering"
    FROZEN = "frozen"
    DISABLED = "disabled"
    CLOSED = "closed"
    ERROR = "error"


# ------------------------------------------------------------------------------


class SearchMode(Enum):
    """
    Search matching strategy.
    """

    EXACT = "exact"
    PREFIX = "prefix"
    SUFFIX = "suffix"
    CONTAINS = "contains"
    REGEX = "regex"
    FUZZY = "fuzzy"


# ------------------------------------------------------------------------------


class SearchScope(Enum):
    """
    Scope of the search.
    """

    CURRENT = "current"
    LOCAL = "local"
    GLOBAL = "global"
    RECURSIVE = "recursive"
    ALL = "all"


# ------------------------------------------------------------------------------


class SearchOperator(Enum):
    """
    Comparison operator used in filtering.
    """

    EQ = "eq"

    NE = "ne"

    GT = "gt"

    GTE = "gte"

    LT = "lt"

    LTE = "lte"

    CONTAINS = "contains"

    STARTSWITH = "startswith"

    ENDSWITH = "endswith"

    REGEX = "regex"

    IN = "in"

    NOT_IN = "not_in"


# ------------------------------------------------------------------------------


class SearchSortOrder(Enum):
    """
    Search result ordering.
    """

    NONE = "none"

    ASCENDING = "ascending"

    DESCENDING = "descending"

    SCORE = "score"

    NAME = "name"

    TIME = "time"

    DURATION = "duration"


# ------------------------------------------------------------------------------


class SearchTarget(Enum):
    """
    Search target object.
    """

    NODE = "node"

    FRAME = "frame"

    EVENT = "event"

    TRACE = "trace"

    SPAN = "span"

    METRIC = "metric"

    LOG = "log"

    TIMELINE = "timeline"

    FLAMEGRAPH = "flamegraph"

    ALL = "all"
# ==============================================================================
# Part 1.4 Type Aliases
# ==============================================================================

#
# ------------------------------------------------------------------------------
# Basic Identifiers
# ------------------------------------------------------------------------------

QueryID: TypeAlias = str

ResultID: TypeAlias = str

IndexID: TypeAlias = str

EventID: TypeAlias = str

#
# ------------------------------------------------------------------------------
# Search Values
# ------------------------------------------------------------------------------

SearchValue: TypeAlias = Union[
    str,
    int,
    float,
    bool,
]

SearchKey: TypeAlias = str

#
# ------------------------------------------------------------------------------
# Metadata
# ------------------------------------------------------------------------------

Metadata: TypeAlias = Dict[str, Any]

Attributes: TypeAlias = Dict[str, Any]

Tags: TypeAlias = Dict[str, str]

Labels: TypeAlias = Dict[str, str]

#
# ------------------------------------------------------------------------------
# Query Types
# ------------------------------------------------------------------------------

SearchExpression: TypeAlias = str

SearchPattern: TypeAlias = str

SearchFilter: TypeAlias = Dict[str, Any]

SearchParameters: TypeAlias = Dict[str, Any]

#
# ------------------------------------------------------------------------------
# Index Types
# ------------------------------------------------------------------------------

SearchIndex: TypeAlias = Dict[
    str,
    Dict[str, Any],
]

IndexEntry: TypeAlias = Dict[str, Any]

IndexMap: TypeAlias = Dict[
    IndexID,
    IndexEntry,
]

#
# ------------------------------------------------------------------------------
# Results
# ------------------------------------------------------------------------------

SearchResultList: TypeAlias = List["SearchResult"]

SearchResultMap: TypeAlias = Dict[
    ResultID,
    "SearchResult",
]

#
# ------------------------------------------------------------------------------
# Collections
# ------------------------------------------------------------------------------

NodeCollection: TypeAlias = List[Any]

FrameCollection: TypeAlias = List[Any]

EventCollection: TypeAlias = List[Any]

TraceCollection: TypeAlias = List[Any]

SpanCollection: TypeAlias = List[Any]

#
# ------------------------------------------------------------------------------
# Hooks & Events
# ------------------------------------------------------------------------------

HookCallback: TypeAlias = Callable[..., Any]

HookRegistry: TypeAlias = Dict[
    str,
    List[HookCallback],
]

EventRecord: TypeAlias = Dict[str, Any]

EventHistory: TypeAlias = List[
    EventRecord
]

#
# ------------------------------------------------------------------------------
# Serialization
# ------------------------------------------------------------------------------

JSONObject: TypeAlias = Dict[str, Any]

JSONArray: TypeAlias = List[Any]

SearchPayload: TypeAlias = Dict[
    str,
    Any,
]

Snapshot: TypeAlias = Dict[
    str,
    Any,
]

#
# ------------------------------------------------------------------------------
# Rendering
# ------------------------------------------------------------------------------

RenderOutput: TypeAlias = Union[
    str,
    Dict[str, Any],
]

RenderOptions: TypeAlias = Dict[
    str,
    Any,
]

#
# ------------------------------------------------------------------------------
# Statistics
# ------------------------------------------------------------------------------

Statistics: TypeAlias = Dict[
    str,
    Any,
]

Summary: TypeAlias = Dict[
    str,
    Any,
]
# ==============================================================================
# Part 1.5 Dataclasses
# SearchQuery
# ==============================================================================

@dataclass(slots=True)
class SearchQuery:
    """
    Represents a search request executed by the SearchEngine.

    A SearchQuery encapsulates the query expression together with
    its execution context, filtering strategy and runtime options.
    """

    # ------------------------------------------------------------------
    # Identity & Query Definition
    # ------------------------------------------------------------------

    id: QueryID = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    expression: str = ""

    target: SearchTarget = SearchTarget.ALL

    scope: SearchScope = SearchScope.ALL

    mode: SearchMode = SearchMode.CONTAINS

    created_at: float = field(
        default_factory=time.time
    )

    # ------------------------------------------------------------------
    # Filtering & Search Options
    # ------------------------------------------------------------------

    operator: SearchOperator = (
        SearchOperator.CONTAINS
    )

    parameters: SearchParameters = field(
        default_factory=dict
    )

    case_sensitive: bool = (
        DEFAULT_CASE_SENSITIVE
    )

    regex: bool = DEFAULT_REGEX

    fuzzy: bool = DEFAULT_FUZZY

    max_results: int = (
        DEFAULT_MAX_RESULTS
    )

    timeout: float = DEFAULT_TIMEOUT

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_regex(self) -> bool:
        """
        Whether regex mode is enabled.
        """

        return self.regex

    # ------------------------------------------------------------------

    @property
    def is_fuzzy(self) -> bool:
        """
        Whether fuzzy matching is enabled.
        """

        return self.fuzzy

    # ------------------------------------------------------------------

    @property
    def has_expression(self) -> bool:
        """
        Whether the query contains a valid expression.
        """

        return bool(self.expression.strip())

    # ------------------------------------------------------------------

    @property
    def normalized_expression(self) -> str:
        """
        Return the normalized search expression.
        """

        if self.case_sensitive:
            return self.expression.strip()

        return self.expression.strip().lower()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def add_parameter(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Add or update a query parameter.
        """

        self.parameters[key] = value

    # ------------------------------------------------------------------

    def remove_parameter(
        self,
        key: str,
    ) -> None:
        """
        Remove a parameter if present.
        """

        self.parameters.pop(key, None)

    # ------------------------------------------------------------------

    def clear_parameters(self) -> None:
        """
        Remove all query parameters.
        """

        self.parameters.clear()

    # ------------------------------------------------------------------

    def update_expression(
        self,
        expression: str,
    ) -> None:
        """
        Update the search expression.
        """

        self.expression = expression

    # ------------------------------------------------------------------

    def update_mode(
        self,
        mode: SearchMode,
    ) -> None:
        """
        Update the search mode.
        """

        self.mode = mode

    # ------------------------------------------------------------------

    def update_target(
        self,
        target: SearchTarget,
    ) -> None:
        """
        Update the search target.
        """

        self.target = target

    # ------------------------------------------------------------------

    def update_scope(
        self,
        scope: SearchScope,
    ) -> None:
        """
        Update the search scope.
        """

        self.scope = scope

    # ------------------------------------------------------------------

    def reset(self) -> None:
        """
        Restore default runtime options while preserving identity.
        """

        self.parameters.clear()

        self.case_sensitive = DEFAULT_CASE_SENSITIVE

        self.regex = DEFAULT_REGEX

        self.fuzzy = DEFAULT_FUZZY

        self.max_results = DEFAULT_MAX_RESULTS

        self.timeout = DEFAULT_TIMEOUT

    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize this query into a dictionary.
        """

        return {
            "id": self.id,
            "expression": self.expression,
            "target": self.target.value,
            "scope": self.scope.value,
            "mode": self.mode.value,
            "operator": self.operator.value,
            "parameters": self.parameters,
            "case_sensitive": self.case_sensitive,
            "regex": self.regex,
            "fuzzy": self.fuzzy,
            "max_results": self.max_results,
            "timeout": self.timeout,
            "created_at": self.created_at,
        }

    # ------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "SearchQuery":
        """
        Create a SearchQuery from a dictionary.
        """

        return cls(
            id=data.get(
                "id",
                str(uuid.uuid4()),
            ),
            expression=data.get(
                "expression",
                "",
            ),
            target=SearchTarget(
                data.get(
                    "target",
                    SearchTarget.ALL.value,
                )
            ),
            scope=SearchScope(
                data.get(
                    "scope",
                    SearchScope.ALL.value,
                )
            ),
            mode=SearchMode(
                data.get(
                    "mode",
                    SearchMode.CONTAINS.value,
                )
            ),
            operator=SearchOperator(
                data.get(
                    "operator",
                    SearchOperator.CONTAINS.value,
                )
            ),
            parameters=data.get(
                "parameters",
                {},
            ),
            case_sensitive=data.get(
                "case_sensitive",
                DEFAULT_CASE_SENSITIVE,
            ),
            regex=data.get(
                "regex",
                DEFAULT_REGEX,
            ),
            fuzzy=data.get(
                "fuzzy",
                DEFAULT_FUZZY,
            ),
            max_results=data.get(
                "max_results",
                DEFAULT_MAX_RESULTS,
            ),
            timeout=data.get(
                "timeout",
                DEFAULT_TIMEOUT,
            ),
            created_at=data.get(
                "created_at",
                time.time(),
            ),
        )

    # ------------------------------------------------------------------

    def copy(self) -> "SearchQuery":
        """
        Return a deep copy of this query.
        """

        return copy.deepcopy(self)

    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            "SearchQuery("
            f"expression={self.expression!r}, "
            f"target={self.target.name}, "
            f"mode={self.mode.name}, "
            f"scope={self.scope.name})"
        )
# ------------------------------------------------------------------
# Runtime & Metadata
# ------------------------------------------------------------------

#: Arbitrary metadata associated with this query.
#: Reserved for runtime, UI, plugins and serialization.
metadata: Metadata = field(
    default_factory=dict
)

#: Arbitrary runtime attributes.
#: Examples:
#:     {
#:         "source": "timeline",
#:         "user": "admin",
#:         "session": "...",
#:     }
attributes: Attributes = field(
    default_factory=dict
)

#: Lightweight searchable tags.
#: Used by SearchEngine.filter(), SearchEngine.by_tag(), etc.
#: Example:
#:     {
#:         "module": "runtime",
#:         "severity": "warning",
#:         "env": "production",
#:     }
tags: Tags = field(
    default_factory=dict
)

#: Human-readable labels.
#: Mainly intended for dashboard rendering.
#: Example:
#:     {
#:         "title": "CPU Profiling",
#:         "owner": "Runtime",
#:     }
labels: Labels = field(
    default_factory=dict
)

#: Whether this query is enabled.
#: Disabled queries are ignored by the SearchEngine.
enabled: bool = DEFAULT_ENABLED

#: Optional priority used by schedulers or query queues.
priority: int = 0

#: Number of times this query has been executed.
execution_count: int = 0

#: Timestamp of the last execution.
last_execution: float = 0.0

#: Last execution duration (seconds).
last_duration: float = 0.0

#: Cached number of matched results.
last_result_count: int = 0

#: Optional user-defined category.
category: str = ""

#: Optional textual description.
description: str = ""

#: Optional owner/component name.
owner: str = ""

#: Creation UUID of the originating engine/session.
session_id: str = ""

#: Runtime state cache.
state: SearchState = SearchState.CREATED

#: Reserved extension payload.
extra: Dict[str, Any] = field(
    default_factory=dict
)
    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this SearchQuery into a serializable dictionary.
        """

        return {
            "id": self.id,
            "expression": self.expression,
            "target": self.target.value,
            "scope": self.scope.value,
            "mode": self.mode.value,
            "operator": self.operator.value,
            "parameters": copy.deepcopy(self.parameters),
            "case_sensitive": self.case_sensitive,
            "regex": self.regex,
            "fuzzy": self.fuzzy,
            "max_results": self.max_results,
            "timeout": self.timeout,
            "metadata": copy.deepcopy(self.metadata),
            "attributes": copy.deepcopy(self.attributes),
            "tags": copy.deepcopy(self.tags),
            "labels": copy.deepcopy(self.labels),
            "enabled": self.enabled,
            "priority": self.priority,
            "execution_count": self.execution_count,
            "last_execution": self.last_execution,
            "last_duration": self.last_duration,
            "last_result_count": self.last_result_count,
            "category": self.category,
            "description": self.description,
            "owner": self.owner,
            "session_id": self.session_id,
            "state": self.state.value,
            "extra": copy.deepcopy(self.extra),
            "created_at": self.created_at,
        }

    # ------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "SearchQuery":
        """
        Create a SearchQuery from a dictionary.
        """

        return cls(
            id=data.get(
                "id",
                str(uuid.uuid4()),
            ),
            expression=data.get(
                "expression",
                "",
            ),
            target=SearchTarget(
                data.get(
                    "target",
                    SearchTarget.ALL.value,
                )
            ),
            scope=SearchScope(
                data.get(
                    "scope",
                    SearchScope.ALL.value,
                )
            ),
            mode=SearchMode(
                data.get(
                    "mode",
                    SearchMode.CONTAINS.value,
                )
            ),
            operator=SearchOperator(
                data.get(
                    "operator",
                    SearchOperator.CONTAINS.value,
                )
            ),
            parameters=copy.deepcopy(
                data.get("parameters", {})
            ),
            case_sensitive=data.get(
                "case_sensitive",
                DEFAULT_CASE_SENSITIVE,
            ),
            regex=data.get(
                "regex",
                DEFAULT_REGEX,
            ),
            fuzzy=data.get(
                "fuzzy",
                DEFAULT_FUZZY,
            ),
            max_results=data.get(
                "max_results",
                DEFAULT_MAX_RESULTS,
            ),
            timeout=data.get(
                "timeout",
                DEFAULT_TIMEOUT,
            ),
            metadata=copy.deepcopy(
                data.get("metadata", {})
            ),
            attributes=copy.deepcopy(
                data.get("attributes", {})
            ),
            tags=copy.deepcopy(
                data.get("tags", {})
            ),
            labels=copy.deepcopy(
                data.get("labels", {})
            ),
            enabled=data.get(
                "enabled",
                DEFAULT_ENABLED,
            ),
            priority=data.get(
                "priority",
                0,
            ),
            execution_count=data.get(
                "execution_count",
                0,
            ),
            last_execution=data.get(
                "last_execution",
                0.0,
            ),
            last_duration=data.get(
                "last_duration",
                0.0,
            ),
            last_result_count=data.get(
                "last_result_count",
                0,
            ),
            category=data.get(
                "category",
                "",
            ),
            description=data.get(
                "description",
                "",
            ),
            owner=data.get(
                "owner",
                "",
            ),
            session_id=data.get(
                "session_id",
                "",
            ),
            state=SearchState(
                data.get(
                    "state",
                    SearchState.CREATED.value,
                )
            ),
            extra=copy.deepcopy(
                data.get("extra", {})
            ),
            created_at=data.get(
                "created_at",
                time.time(),
            ),
        )

    # ------------------------------------------------------------------

    def copy(self) -> "SearchQuery":
        """
        Return a deep copy.
        """

        return copy.deepcopy(self)

    # ------------------------------------------------------------------

    def update(
        self,
        **kwargs: Any,
    ) -> None:
        """
        Update existing fields.

        Unknown keys are ignored.
        """

        for key, value in kwargs.items():

            if hasattr(self, key):

                setattr(
                    self,
                    key,
                    value,
                )

    # ------------------------------------------------------------------

    def matches(
        self,
        text: str,
    ) -> bool:
        """
        Check whether the supplied text satisfies this query.
        """

        if not self.enabled:

            return False

        if not self.expression:

            return False

        candidate = text
        query = self.expression

        if not self.case_sensitive:

            candidate = candidate.lower()
            query = query.lower()

        #
        # Regular expression
        #

        if self.regex:

            try:

                return re.search(
                    query,
                    candidate,
                ) is not None

            except re.error:

                return False

        #
        # Matching mode
        #

        if self.mode == SearchMode.EXACT:

            return candidate == query

        if self.mode == SearchMode.PREFIX:

            return candidate.startswith(query)

        if self.mode == SearchMode.SUFFIX:

            return candidate.endswith(query)

        if self.mode == SearchMode.CONTAINS:

            return query in candidate

        #
        # Placeholder fuzzy search.
        # Can later be replaced with RapidFuzz.
        #

        if self.mode == SearchMode.FUZZY:

            return query in candidate

        return False

    # ------------------------------------------------------------------

    def reset(self) -> None:
        """
        Reset runtime information while preserving identity
        and query definition.
        """

        self.parameters.clear()

        self.metadata.clear()

        self.attributes.clear()

        self.tags.clear()

        self.labels.clear()

        self.extra.clear()

        self.enabled = DEFAULT_ENABLED

        self.priority = 0

        self.execution_count = 0

        self.last_execution = 0.0

        self.last_duration = 0.0

        self.last_result_count = 0

        self.state = SearchState.CREATED

    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            "SearchQuery("
            f"id={self.id!r}, "
            f"expression={self.expression!r}, "
            f"target={self.target.name}, "
            f"scope={self.scope.name}, "
            f"mode={self.mode.name}, "
            f"enabled={self.enabled})"
        )
# ==============================================================================
# Part 1.5 Dataclasses
# SearchResult
# ==============================================================================

@dataclass(slots=True)
class SearchResult:
    """
    Represents a single search result produced by SearchEngine.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    id: ResultID = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    query_id: QueryID = ""

    target: SearchTarget = SearchTarget.ALL

    # ------------------------------------------------------------------
    # Result
    # ------------------------------------------------------------------

    object_id: str = ""

    object_type: str = ""

    object_ref: Optional[Any] = None

    name: str = ""

    score: float = 0.0

    matched: bool = False

    # ------------------------------------------------------------------
    # Location
    # ------------------------------------------------------------------

    path: str = ""

    index: int = -1

    depth: int = 0

    line: int = -1

    column: int = -1

    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    created_at: float = field(
        default_factory=time.time
    )

    execution_time: float = 0.0

    enabled: bool = True

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

    extra: Dict[str, Any] = field(
        default_factory=dict
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def valid(self) -> bool:
        """
        Whether this search result is valid.
        """

        return self.matched and self.object_ref is not None

    # ------------------------------------------------------------------

    @property
    def has_metadata(self) -> bool:
        """
        Whether metadata exists.
        """

        return bool(self.metadata)

    # ------------------------------------------------------------------

    @property
    def has_tags(self) -> bool:
        """
        Whether tags exist.
        """

        return bool(self.tags)

    # ------------------------------------------------------------------

    @property
    def has_labels(self) -> bool:
        """
        Whether labels exist.
        """

        return bool(self.labels)
# ==============================================================================
# Part 1.5 Dataclasses
# SearchOptions
# ==============================================================================

@dataclass(slots=True)
class SearchOptions:
    """
    Configuration options for SearchEngine.
    """

    # ------------------------------------------------------------------
    # Search Configuration
    # ------------------------------------------------------------------

    mode: SearchMode = SearchMode.CONTAINS

    scope: SearchScope = SearchScope.ALL

    operator: SearchOperator = SearchOperator.CONTAINS

    sort_order: SearchSortOrder = SearchSortOrder.SCORE

    target: SearchTarget = SearchTarget.ALL

    # ------------------------------------------------------------------
    # Matching Options
    # ------------------------------------------------------------------

    case_sensitive: bool = DEFAULT_CASE_SENSITIVE

    regex: bool = DEFAULT_REGEX

    fuzzy: bool = DEFAULT_FUZZY

    partial_match: bool = True

    whole_word: bool = False

    # ------------------------------------------------------------------
    # Result Options
    # ------------------------------------------------------------------

    max_results: int = DEFAULT_MAX_RESULTS

    timeout: float = DEFAULT_TIMEOUT

    minimum_score: float = 0.0

    include_metadata: bool = True

    include_attributes: bool = True

    include_tags: bool = True

    include_labels: bool = True

    # ------------------------------------------------------------------
    # Index Options
    # ------------------------------------------------------------------

    auto_index: bool = True

    cache_enabled: bool = True

    cache_size: int = DEFAULT_CACHE_SIZE

    rebuild_on_update: bool = False

    # ------------------------------------------------------------------
    # Rendering Options
    # ------------------------------------------------------------------

    pretty: bool = True

    indent: int = DEFAULT_JSON_INDENT

    encoding: str = DEFAULT_ENCODING

    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    enabled: bool = DEFAULT_ENABLED

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
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert SearchOptions into a dictionary.
        """

        return {
            "mode": self.mode.value,
            "scope": self.scope.value,
            "operator": self.operator.value,
            "sort_order": self.sort_order.value,
            "target": self.target.value,
            "case_sensitive": self.case_sensitive,
            "regex": self.regex,
            "fuzzy": self.fuzzy,
            "partial_match": self.partial_match,
            "whole_word": self.whole_word,
            "max_results": self.max_results,
            "timeout": self.timeout,
            "minimum_score": self.minimum_score,
            "include_metadata": self.include_metadata,
            "include_attributes": self.include_attributes,
            "include_tags": self.include_tags,
            "include_labels": self.include_labels,
            "auto_index": self.auto_index,
            "cache_enabled": self.cache_enabled,
            "cache_size": self.cache_size,
            "rebuild_on_update": self.rebuild_on_update,
            "pretty": self.pretty,
            "indent": self.indent,
            "encoding": self.encoding,
            "enabled": self.enabled,
            "metadata": copy.deepcopy(self.metadata),
            "attributes": copy.deepcopy(self.attributes),
            "tags": copy.deepcopy(self.tags),
            "labels": copy.deepcopy(self.labels),
        }

    # ------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "SearchOptions":
        """
        Create SearchOptions from a dictionary.
        """

        return cls(
            mode=SearchMode(
                data.get(
                    "mode",
                    SearchMode.CONTAINS.value,
                )
            ),
            scope=SearchScope(
                data.get(
                    "scope",
                    SearchScope.ALL.value,
                )
            ),
            operator=SearchOperator(
                data.get(
                    "operator",
                    SearchOperator.CONTAINS.value,
                )
            ),
            sort_order=SearchSortOrder(
                data.get(
                    "sort_order",
                    SearchSortOrder.SCORE.value,
                )
            ),
            target=SearchTarget(
                data.get(
                    "target",
                    SearchTarget.ALL.value,
                )
            ),
            case_sensitive=data.get(
                "case_sensitive",
                DEFAULT_CASE_SENSITIVE,
            ),
            regex=data.get(
                "regex",
                DEFAULT_REGEX,
            ),
            fuzzy=data.get(
                "fuzzy",
                DEFAULT_FUZZY,
            ),
            partial_match=data.get(
                "partial_match",
                True,
            ),
            whole_word=data.get(
                "whole_word",
                False,
            ),
            max_results=data.get(
                "max_results",
                DEFAULT_MAX_RESULTS,
            ),
            timeout=data.get(
                "timeout",
                DEFAULT_TIMEOUT,
            ),
            minimum_score=data.get(
                "minimum_score",
                0.0,
            ),
            include_metadata=data.get(
                "include_metadata",
                True,
            ),
            include_attributes=data.get(
                "include_attributes",
                True,
            ),
            include_tags=data.get(
                "include_tags",
                True,
            ),
            include_labels=data.get(
                "include_labels",
                True,
            ),
            auto_index=data.get(
                "auto_index",
                True,
            ),
            cache_enabled=data.get(
                "cache_enabled",
                True,
            ),
            cache_size=data.get(
                "cache_size",
                DEFAULT_CACHE_SIZE,
            ),
            rebuild_on_update=data.get(
                "rebuild_on_update",
                False,
            ),
            pretty=data.get(
                "pretty",
                True,
            ),
            indent=data.get(
                "indent",
                DEFAULT_JSON_INDENT,
            ),
            encoding=data.get(
                "encoding",
                DEFAULT_ENCODING,
            ),
            enabled=data.get(
                "enabled",
                DEFAULT_ENABLED,
            ),
            metadata=copy.deepcopy(
                data.get("metadata", {})
            ),
            attributes=copy.deepcopy(
                data.get("attributes", {})
            ),
            tags=copy.deepcopy(
                data.get("tags", {})
            ),
            labels=copy.deepcopy(
                data.get("labels", {})
            ),
        )

    # ------------------------------------------------------------------

    def copy(self) -> "SearchOptions":
        """
        Return a deep copy.
        """

        return copy.deepcopy(self)

    # ------------------------------------------------------------------

    def update(
        self,
        **kwargs: Any,
    ) -> None:
        """
        Update existing option fields.
        """

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    # ------------------------------------------------------------------

    def reset(self) -> None:
        """
        Reset to default configuration.
        """

        self.__dict__.update(SearchOptions().__dict__)

    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            "SearchOptions("
            f"mode={self.mode.name}, "
            f"scope={self.scope.name}, "
            f"target={self.target.name}, "
            f"max_results={self.max_results}, "
            f"enabled={self.enabled})"
        )
# ==============================================================================
# Part 1.5 Dataclasses
# SearchStatistics
# ==============================================================================

@dataclass(slots=True)
class SearchStatistics:
    """
    Runtime statistics for SearchEngine.
    """

    # ------------------------------------------------------------------
    # Query Statistics
    # ------------------------------------------------------------------

    query_count: int = 0

    successful_queries: int = 0

    failed_queries: int = 0

    hit_count: int = 0

    miss_count: int = 0

    # ------------------------------------------------------------------
    # Index Statistics
    # ------------------------------------------------------------------

    indexed_nodes: int = 0

    indexed_frames: int = 0

    indexed_events: int = 0

    indexed_traces: int = 0

    indexed_spans: int = 0

    indexed_metrics: int = 0

    indexed_logs: int = 0

    # ------------------------------------------------------------------
    # Performance Statistics
    # ------------------------------------------------------------------

    total_execution_time: float = 0.0

    average_latency: float = 0.0

    minimum_latency: float = 0.0

    maximum_latency: float = 0.0

    last_latency: float = 0.0

    # ------------------------------------------------------------------
    # Cache Statistics
    # ------------------------------------------------------------------

    cache_hits: int = 0

    cache_misses: int = 0

    cache_size: int = 0

    # ------------------------------------------------------------------
    # Runtime
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
    # Properties
    # ------------------------------------------------------------------

    @property
    def success_rate(self) -> float:
        """
        Successful query ratio.
        """

        if self.query_count == 0:
            return 0.0

        return self.successful_queries / self.query_count

    # ------------------------------------------------------------------

    @property
    def hit_rate(self) -> float:
        """
        Cache/Search hit ratio.
        """

        total = self.hit_count + self.miss_count

        if total == 0:
            return 0.0

        return self.hit_count / total

    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    def update(
        self,
        latency: float,
        hits: int = 0,
    ) -> None:
        """
        Update runtime statistics.
        """

        self.query_count += 1

        self.successful_queries += 1

        self.hit_count += hits

        self.total_execution_time += latency

        self.last_latency = latency

        self.updated_at = time.time()

        self.average_latency = (
            self.total_execution_time
            / self.query_count
        )

        if (
            self.minimum_latency == 0.0
            or latency < self.minimum_latency
        ):
            self.minimum_latency = latency

        if latency > self.maximum_latency:
            self.maximum_latency = latency

    # ------------------------------------------------------------------

    def record_failure(self) -> None:
        """
        Record a failed search.
        """

        self.query_count += 1

        self.failed_queries += 1

        self.updated_at = time.time()

    # ------------------------------------------------------------------

    def reset(self) -> None:
        """
        Reset all runtime statistics.
        """

        self.query_count = 0

        self.successful_queries = 0

        self.failed_queries = 0

        self.hit_count = 0

        self.miss_count = 0

        self.total_execution_time = 0.0

        self.average_latency = 0.0

        self.minimum_latency = 0.0

        self.maximum_latency = 0.0

        self.last_latency = 0.0

        self.cache_hits = 0

        self.cache_misses = 0

        self.cache_size = 0

        self.updated_at = time.time()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize statistics.
        """

        return {
            "query_count": self.query_count,
            "successful_queries": self.successful_queries,
            "failed_queries": self.failed_queries,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "indexed_nodes": self.indexed_nodes,
            "indexed_frames": self.indexed_frames,
            "indexed_events": self.indexed_events,
            "indexed_traces": self.indexed_traces,
            "indexed_spans": self.indexed_spans,
            "indexed_metrics": self.indexed_metrics,
            "indexed_logs": self.indexed_logs,
            "total_execution_time": self.total_execution_time,
            "average_latency": self.average_latency,
            "minimum_latency": self.minimum_latency,
            "maximum_latency": self.maximum_latency,
            "last_latency": self.last_latency,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_size": self.cache_size,
            "success_rate": self.success_rate,
            "hit_rate": self.hit_rate,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": copy.deepcopy(self.metadata),
        }

    # ------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "SearchStatistics":
        """
        Deserialize statistics.
        """

        return cls(**copy.deepcopy(data))

    # ------------------------------------------------------------------

    def copy(self) -> "SearchStatistics":
        """
        Deep copy.
        """

        return copy.deepcopy(self)

    # ------------------------------------------------------------------

    def report(self) -> Dict[str, Any]:
        """
        Runtime report.
        """

        return self.to_dict()

    # ------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """
        Compact summary.
        """

        return {
            "queries": self.query_count,
            "hits": self.hit_count,
            "misses": self.miss_count,
            "avg_latency": self.average_latency,
            "success_rate": self.success_rate,
        }

    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            "SearchStatistics("
            f"queries={self.query_count}, "
            f"hits={self.hit_count}, "
            f"avg_latency={self.average_latency:.6f}s)"
        )
"""
SciOS-NG
Runtime Observability Dashboard
Search Engine
"""

from __future__ import annotations

import time
import uuid

from typing import Any
from typing import Callable


class SearchEngine:
    """
    Base Search Engine.

    Provides searching, indexing, filtering and rendering support
    for runtime dashboard components.
    """

    VERSION = "0.1.0"

    # ==========================================================
    # Constructor
    # ==========================================================

    def __init__(
        self,
        name: str = "SearchEngine",
        *,
        engine_type: str = "generic",
    ) -> None:

        # ------------------------------------------------------
        # Identity
        # ------------------------------------------------------

        self.id: str = str(uuid.uuid4())
        self.name: str = name
        self.version: str = self.VERSION
        self.description: str = ""
        self.engine_type: str = engine_type

        # ------------------------------------------------------
        # Configuration
        # ------------------------------------------------------

        self.options: dict[str, Any] = {}

        self.max_results: int = 100

        self.case_sensitive: bool = False

        self.regex: bool = False

        self.fuzzy: bool = False

        self.timeout: float | None = None

        # ------------------------------------------------------
        # Runtime State
        # ------------------------------------------------------

        self.enabled: bool = True
        self.frozen: bool = False
        self.closed: bool = False

        self.state: str = "ready"

        self.dirty: bool = False

        self.index: dict[str, Any] = {}

        self.statistics: dict[str, Any] = {
            "searches": 0,
            "matches": 0,
            "indexed": 0,
            "rendered": 0,
            "errors": 0,
        }

        # ------------------------------------------------------
        # Events
        # ------------------------------------------------------

        self.events: list[dict[str, Any]] = []

        self.max_events: int = 500

        # ------------------------------------------------------
        # Hooks
        # ------------------------------------------------------

        self.before_search: Callable[..., Any] | None = None
        self.after_search: Callable[..., Any] | None = None

        self.before_index: Callable[..., Any] | None = None
        self.after_index: Callable[..., Any] | None = None

        self.before_render: Callable[..., Any] | None = None
        self.after_render: Callable[..., Any] | None = None

        # ------------------------------------------------------
        # Metadata
        # ------------------------------------------------------

        self.metadata: dict[str, Any] = {}

        self.attributes: dict[str, Any] = {}

        self.tags: set[str] = set()

        self.labels: dict[str, str] = {}

        now = time.time()

        self.created_at: float = now
        self.updated_at: float = now
# ==========================================================
# Part 2. Search API
# ==========================================================

def search(
    self,
    query: Any,
    *,
    limit: int | None = None,
) -> list[Any]:
    """
    Execute a generic search.
    """


def find(
    self,
    query: Any,
) -> Any | None:
    """
    Return the first matching object.
    """


def filter(
    self,
    items: list[Any],
    predicate: Callable[[Any], bool],
) -> list[Any]:
    """
    Filter a collection.
    """


def match(
    self,
    item: Any,
    query: Any,
) -> bool:
    """
    Determine whether an item matches a query.
    """


def query(
    self,
    search_query: SearchQuery,
) -> SearchResult:
    """
    Execute a structured SearchQuery.
    """


def locate(
    self,
    identifier: str,
) -> Any | None:
    """
    Locate an object by id, path, name or label.
    """


def search_frames(
    self,
    text: str,
) -> list[Any]:
    """
    Search profiling frames.
    """


def search_nodes(
    self,
    text: str,
) -> list[Any]:
    """
    Search graph/tree nodes.
    """


def search_events(
    self,
    text: str,
) -> list[Any]:
    """
    Search runtime events.
    """
# ==========================================================
# Part 3. Index API
# ==========================================================


def build_index(
    self,
    items: list[Any] | None = None,
) -> dict[str, Any]:
    """
    Build search index from source data.
    """

    if self.closed:
        raise RuntimeError(
            "SearchEngine is closed"
        )

    if self.frozen:
        raise RuntimeError(
            "SearchEngine is frozen"
        )

    if self.before_index:
        self.before_index(items)


    self.index.clear()


    if items:

        for item in items:

            key = self._index_key(item)

            self.index[key] = item


    self.statistics["indexed"] = len(
        self.index
    )


    self.dirty = False

    self.updated_at = time.time()


    self._emit_event(
        "index_built",
        {
            "size": len(self.index)
        }
    )


    if self.after_index:
        self.after_index(self.index)


    return self.index
# ==========================================================
# Part 4. Query API
# ==========================================================


def by_name(
    self,
    name: str,
) -> list[Any]:
    """
    Query objects by name.
    """

    results = []

    for item in self.index.values():

        item_name = self._get_value(
            item,
            "name"
        )

        if item_name == name:
            results.append(item)


    return results
# ==========================================================
# Part 5. Rendering API
# ==========================================================


def render(
    self,
    data: Any,
    *,
    format: str = "dict",
) -> Any:
    """
    Generic rendering entry point.
    """

    if self.closed:
        raise RuntimeError(
            "SearchEngine is closed"
        )


    if self.before_render:
        self.before_render(data)


    handlers = {
        "dict": self.render_dict,
        "json": self.render_json,
        "table": self.render_table,
        "html": self.render_html,
    }


    renderer = handlers.get(
        format
    )


    if renderer is None:
        raise ValueError(
            f"Unsupported format: {format}"
        )


    result = renderer(data)


    self.statistics["rendered"] += 1


    self.updated_at = time.time()


    self._emit_event(
        "render",
        {
            "format": format
        }
    )


    if self.after_render:
        self.after_render(result)


    return result
# ==========================================================
# Part 6. Runtime Operations
# ==========================================================


def snapshot(
    self,
) -> dict[str, Any]:
    """
    Create runtime snapshot.
    """

    state = {
        "identity": {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "engine_type": self.engine_type,
        },

        "configuration": {
            "options": self.options.copy(),
            "max_results": self.max_results,
            "case_sensitive": self.case_sensitive,
            "regex": self.regex,
            "fuzzy": self.fuzzy,
            "timeout": self.timeout,
        },

        "runtime": {
            "enabled": self.enabled,
            "frozen": self.frozen,
            "closed": self.closed,
            "state": self.state,
            "dirty": self.dirty,
        },

        "index": self.index.copy(),

        "statistics": self.statistics.copy(),

        "metadata": {
            "metadata": self.metadata.copy(),
            "attributes": self.attributes.copy(),
            "tags": list(self.tags),
            "labels": self.labels.copy(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        },
    }


    self._emit_event(
        "snapshot_created"
    )


    return state
# ==========================================================
# Part 7. Statistics API
# ==========================================================


# ----------------------------------------------------------
# Statistics Properties
# ----------------------------------------------------------

@property
def query_count(
    self,
) -> int:
    """
    Total executed queries.
    """

    return self.statistics.get(
        "query_count",
        0
    )


@property
def hit_count(
    self,
) -> int:
    """
    Number of successful queries.
    """

    return self.statistics.get(
        "hit_count",
        0
    )


@property
def miss_count(
    self,
) -> int:
    """
    Number of failed queries.
    """

    return self.statistics.get(
        "miss_count",
        0
    )


@property
def indexed_nodes(
    self,
) -> int:
    """
    Number of indexed runtime nodes.
    """

    return self.statistics.get(
        "indexed_nodes",
        0
    )


@property
def indexed_frames(
    self,
) -> int:
    """
    Number of indexed profiling frames.
    """

    return self.statistics.get(
        "indexed_frames",
        0
    )
# ==========================================================
# Part 8. Validation API
# ==========================================================


# ----------------------------------------------------------
# General Validation
# ----------------------------------------------------------

def validate(
    self,
) -> bool:
    """
    Validate complete SearchEngine state.
    """

    checks = [

        self.validate_index(),

        self.check_integrity(),

    ]


    return all(checks)
# ==========================================================
# Part 9. Events & Hooks API
# ==========================================================


# ----------------------------------------------------------
# Search Hooks
# ----------------------------------------------------------

def before_search(
    self,
    query: Any,
) -> None:
    """
    Hook executed before search.
    """

    if callable(
        self._hooks.get(
            "before_search"
        )
    ):

        self._hooks[
            "before_search"
        ](query)


    self.emit_event(
        "before_search",
        {
            "query": str(query)
        }
    )
# ==========================================================
# Part 10. Python Protocols API
# ==========================================================


# ----------------------------------------------------------
# Representation Protocols
# ----------------------------------------------------------

def __repr__(
    self,
) -> str:
    """
    Developer representation.
    """

    return (
        f"{self.__class__.__name__}("
        f"id={self.id!r}, "
        f"name={self.name!r}, "
        f"state={self.state!r}, "
        f"index={len(self.index)}"
        f")"
    )
# ==========================================================
# Part 11. Lifecycle Management API
# ==========================================================


# ----------------------------------------------------------
# Enable / Disable
# ----------------------------------------------------------

def enable(
    self,
) -> None:
    """
    Enable search engine.
    """

    if self.closed:
        raise RuntimeError(
            "Cannot enable closed engine"
        )


    self.enabled = True

    self.state = "enabled"

    self.updated_at = time.time()


    self.emit_event(
        "engine_enabled"
    )
# ==========================================================
# Part 12. Utilities & Diagnostics API
# ==========================================================


# ----------------------------------------------------------
# Clear Runtime Data
# ----------------------------------------------------------

def clear(
    self,
) -> None:
    """
    Clear runtime data but keep configuration.
    """

    self._ensure_not_closed()


    self.index.clear()

    self.events.clear()


    self.statistics.update(
        {
            "query_count": 0,
            "hit_count": 0,
            "miss_count": 0,
            "indexed_nodes": 0,
            "indexed_frames": 0,
        }
    )


    self.dirty = True

    self.updated_at = time.time()


    self.emit_event(
        "engine_cleared"
    )                                                                                            