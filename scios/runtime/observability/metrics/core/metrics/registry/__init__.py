"""
Metric registry package.
"""

from __future__ import annotations

# ==============================================================================
# Core registry types
# ==============================================================================

from .key import MetricKey
from .entry import MetricEntry
from .namespace import MetricNamespace
from .filter import MetricFilter
from .index import MetricIndex

# ==============================================================================
# Statistics
# ==============================================================================

from .statistics import (
    MetricStatistics,
    DEFAULT_NAME,
    DEFAULT_COUNT,
    DEFAULT_SUM,
    DEFAULT_MINIMUM,
    DEFAULT_MAXIMUM,
    DEFAULT_AVERAGE,
)

# ==============================================================================
# Utilities
# ==============================================================================

from .utils import (
    MetricUtils,

    DEFAULT_ENCODING,
    DEFAULT_HASH,
    DEFAULT_INDENT,

    normalize_name,
    normalize_tags,
    normalize_labels,

    ensure_mapping,
    ensure_sequence,
    ensure_number,

    to_dict,
    from_dict,
    to_tuple,
    from_tuple,
    to_json,
    from_json,

    compute_hash,
    stable_hash,
    object_hash,
    compare_hash,

    merge_dicts,
    merge_states,
    merge_labels,
    merge_tags,
    merge_statistics,

    validate_name,
    validate_mapping,
    validate_sequence,
    validate_number,
    validate_json,

    diagnostics,
    health,
    status,
    summary,
)

__all__ = [

    # ------------------------------------------------------------------
    # Registry
    # ------------------------------------------------------------------

    "MetricKey",
    "MetricEntry",
    "MetricNamespace",
    "MetricFilter",
    "MetricIndex",

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    "MetricStatistics",

    "DEFAULT_NAME",
    "DEFAULT_COUNT",
    "DEFAULT_SUM",
    "DEFAULT_MINIMUM",
    "DEFAULT_MAXIMUM",
    "DEFAULT_AVERAGE",

    # ------------------------------------------------------------------
    # Utils
    # ------------------------------------------------------------------

    "MetricUtils",

    "DEFAULT_ENCODING",
    "DEFAULT_HASH",
    "DEFAULT_INDENT",

    "normalize_name",
    "normalize_tags",
    "normalize_labels",

    "ensure_mapping",
    "ensure_sequence",
    "ensure_number",

    "to_dict",
    "from_dict",
    "to_tuple",
    "from_tuple",
    "to_json",
    "from_json",

    "compute_hash",
    "stable_hash",
    "object_hash",
    "compare_hash",

    "merge_dicts",
    "merge_states",
    "merge_labels",
    "merge_tags",
    "merge_statistics",

    "validate_name",
    "validate_mapping",
    "validate_sequence",
    "validate_number",
    "validate_json",

    "diagnostics",
    "health",
    "status",
    "summary",
]