"""
Metric Registry Utilities
=========================

Shared helper utilities for metric registry.
"""

# ==============================================================================
# Part 1. Imports & Constants
# ==============================================================================

from __future__ import annotations

import hashlib
import json

from typing import (
    Any,
    Final,
    Iterable,
    Mapping,
    Sequence,
    TypeAlias,
)

DEFAULT_ENCODING: Final[str] = "utf-8"
DEFAULT_HASH: Final[str] = "sha256"
DEFAULT_INDENT: Final[int] = 2

JsonDict: TypeAlias = dict[str, Any]

# ==============================================================================
# Part 2. MetricUtils
# ==============================================================================


class MetricUtils:
    """
    Collection of metric registry utility helpers.
    """

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_name(
        name: str,
    ) -> str:
        """
        Normalize metric name.
        """

        return str(name).strip().lower()

    @staticmethod
    def normalize_tags(
        tags: Mapping[str, Any] | None,
    ) -> dict[str, str]:
        """
        Normalize tag dictionary.
        """

        if tags is None:
            return {}

        return {
            MetricUtils.normalize_name(k): str(v)
            for k, v in tags.items()
        }

    @staticmethod
    def normalize_labels(
        labels: Mapping[str, Any] | None,
    ) -> dict[str, str]:
        """
        Normalize label dictionary.
        """

        if labels is None:
            return {}

        return {
            MetricUtils.normalize_name(k): str(v)
            for k, v in labels.items()
        }

    # ------------------------------------------------------------------
    # Type Conversion
    # ------------------------------------------------------------------

    @staticmethod
    def ensure_mapping(
        value: Any,
    ) -> dict[str, Any]:
        """
        Ensure mapping.
        """

        if value is None:
            return {}

        if isinstance(
            value,
            Mapping,
        ):
            return dict(value)

        raise TypeError(
            "Expected mapping."
        )

    @staticmethod
    def ensure_sequence(
        value: Any,
    ) -> list[Any]:
        """
        Ensure sequence.
        """

        if value is None:
            return []

        if isinstance(
            value,
            (
                str,
                bytes,
            ),
        ):
            raise TypeError(
                "String is not a valid sequence."
            )

        if isinstance(
            value,
            Sequence,
        ):
            return list(value)

        if isinstance(
            value,
            Iterable,
        ):
            return list(value)

        raise TypeError(
            "Expected sequence."
        )

    @staticmethod
    def ensure_number(
        value: Any,
    ) -> float:
        """
        Ensure numeric value.
        """

        if isinstance(
            value,
            (
                int,
                float,
            ),
        ):
            return float(value)

        raise TypeError(
            "Expected numeric value."
        )

# ==============================================================================
# Part 3. Conversion Utilities
# ==============================================================================


    def to_dict(
        obj: Any,
    ) -> JsonDict:
        """
        Convert object to dictionary.
        """

        if isinstance(
            obj,
            Mapping,
        ):
            return dict(obj)

        if hasattr(
            obj,
            "to_dict",
        ):
            return obj.to_dict()

        if hasattr(
            obj,
            "__dict__",
        ):
            return dict(obj.__dict__)

        raise TypeError(
            "Cannot convert object to dict."
        )


    def from_dict(
        data: Mapping[str, Any],
    ) -> JsonDict:
        """
        Copy dictionary.
        """

        return dict(data)


    def to_tuple(
        data: Mapping[str, Any],
    ) -> tuple[tuple[str, Any], ...]:
        """
        Dictionary -> tuple.
        """

        return tuple(
            sorted(
                data.items(),
            )
        )


    def from_tuple(
        values: Sequence[
            tuple[str, Any]
        ],
    ) -> JsonDict:
        """
        Tuple -> dictionary.
        """

        return dict(values)


    def to_json(
        data: Any,
        *,
        indent: int = DEFAULT_INDENT,
    ) -> str:
        """
        Serialize object.
        """

        if not isinstance(
            data,
            (
                dict,
                list,
                tuple,
            ),
        ):
            data = to_dict(data)

        return json.dumps(
            data,
            indent=indent,
            sort_keys=True,
        )


    def from_json(
        text: str,
    ) -> Any:
        """
        Deserialize JSON.
        """

        return json.loads(text)


# ==============================================================================
# Part 4. Hash Utilities
# ==============================================================================


    def compute_hash(
        value: Any,
    ) -> str:
        """
        Compute SHA-256 hash.
        """

        payload = json.dumps(
            value,
            sort_keys=True,
            default=str,
        ).encode(
            DEFAULT_ENCODING,
        )

        return hashlib.sha256(
            payload,
        ).hexdigest()


    def stable_hash(
        value: Any,
    ) -> str:
        """
        Stable object hash.
        """

        return compute_hash(
            value,
        )


    def object_hash(
        obj: Any,
    ) -> str:
        """
        Hash object.
        """

        return compute_hash(
            to_dict(obj),
        )


    def compare_hash(
        left: Any,
        right: Any,
    ) -> bool:
        """
        Compare hashes.
        """

        return (
            compute_hash(left)
            == compute_hash(right)
        )


# ==============================================================================
# Part 5. Merge Utilities
# ==============================================================================


    def merge_dicts(
        *mappings: Mapping[str, Any],
    ) -> JsonDict:
        """
        Merge dictionaries.
        """

        merged: JsonDict = {}

        for mapping in mappings:
            merged.update(
                dict(mapping),
            )

        return merged


    def merge_states(
        *states: Mapping[str, Any],
    ) -> JsonDict:
        """
        Merge state dictionaries.
        """

        return merge_dicts(
            *states,
        )


    def merge_labels(
        *labels: Mapping[str, Any],
    ) -> dict[str, str]:
        """
        Merge labels.
        """

        merged: dict[str, str] = {}

        for label in labels:
            merged.update(
                normalize_labels(
                    label,
                )
            )

        return merged


    def merge_tags(
        *tags: Mapping[str, Any],
    ) -> dict[str, str]:
        """
        Merge tags.
        """

        merged: dict[str, str] = {}

        for tag in tags:
            merged.update(
                normalize_tags(
                    tag,
                )
            )

        return merged


    def merge_statistics(
        *statistics: Mapping[str, Any],
    ) -> JsonDict:
        """
        Merge statistics dictionaries.
        """

        return merge_dicts(
            *statistics,
        )

# ==============================================================================
# Part 6. Validation
# ==============================================================================


    def validate_name(
        name: Any,
    ) -> bool:
        """
        Validate metric name.
        """

        return (
            isinstance(name, str)
            and bool(name.strip())
        )


    def validate_mapping(
        value: Any,
    ) -> bool:
        """
        Validate mapping.
        """

        return isinstance(
            value,
            Mapping,
        )


    def validate_sequence(
        value: Any,
    ) -> bool:
        """
        Validate sequence.
        """

        return (
            isinstance(
                value,
                Sequence,
            )
            and not isinstance(
                value,
                (
                    str,
                    bytes,
                ),
            )
        )


    def validate_number(
        value: Any,
    ) -> bool:
        """
        Validate numeric value.
        """

        return isinstance(
            value,
            (
                int,
                float,
            ),
        )


    def validate_json(
        value: str,
    ) -> bool:
        """
        Validate JSON string.
        """

        try:
            json.loads(value)
            return True

        except (
            TypeError,
            ValueError,
        ):
            return False


# ==============================================================================
# Part 7. Diagnostics
# ==============================================================================


    @staticmethod
    def diagnostics() -> dict[str, Any]:
        return {
            "status": "ok",
            "healthy": True,
            "encoding": DEFAULT_ENCODING,
            "hash": DEFAULT_HASH,
            "indent": DEFAULT_INDENT,
        }


    def health() -> str:
        """
        Health state.
        """

        return "healthy"


    def status() -> str:
        """
        Utility status.
        """

        return "ok"


    def summary() -> JsonDict:
        """
        Utility summary.
        """

        return {
            "encoding": DEFAULT_ENCODING,
            "hash": DEFAULT_HASH,
            "indent": DEFAULT_INDENT,
            "health": health(),
            "status": status(),
        }


# ==============================================================================
# Part 8. Public API
# ==============================================================================


# ==============================================================================
# Module aliases
# ==============================================================================

normalize_name = MetricUtils.normalize_name
normalize_tags = MetricUtils.normalize_tags
normalize_labels = MetricUtils.normalize_labels

ensure_mapping = MetricUtils.ensure_mapping
ensure_sequence = MetricUtils.ensure_sequence
ensure_number = MetricUtils.ensure_number

to_dict = MetricUtils.to_dict
from_dict = MetricUtils.from_dict
to_tuple = MetricUtils.to_tuple
from_tuple = MetricUtils.from_tuple
to_json = MetricUtils.to_json
from_json = MetricUtils.from_json

compute_hash = MetricUtils.compute_hash
stable_hash = MetricUtils.stable_hash
object_hash = MetricUtils.object_hash
compare_hash = MetricUtils.compare_hash

merge_dicts = MetricUtils.merge_dicts
merge_states = MetricUtils.merge_states
merge_labels = MetricUtils.merge_labels
merge_tags = MetricUtils.merge_tags
merge_statistics = MetricUtils.merge_statistics

validate_name = MetricUtils.validate_name
validate_mapping = MetricUtils.validate_mapping
validate_sequence = MetricUtils.validate_sequence
validate_number = MetricUtils.validate_number
validate_json = MetricUtils.validate_json

diagnostics = MetricUtils.diagnostics
health = MetricUtils.health
status = MetricUtils.status
summary = MetricUtils.summary

__all__ = [
    # constants
    "DEFAULT_ENCODING",
    "DEFAULT_HASH",
    "DEFAULT_INDENT",

    # class
    "MetricUtils",

    # aliases
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