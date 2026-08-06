"""
Tests for registry.utils
"""

from __future__ import annotations

import inspect

from scios.runtime.observability.metrics.core.metrics.registry import utils
from scios.runtime.observability.metrics.core.metrics.registry.utils import (
    __all__,
    MetricUtils,
    DEFAULT_ENCODING,
    DEFAULT_HASH,
    DEFAULT_INDENT,
)


# ==============================================================================
# Constructor / Constants
# ==============================================================================


def test_constants():

    assert DEFAULT_ENCODING == "utf-8"

    assert DEFAULT_HASH == "sha256"

    assert DEFAULT_INDENT == 2


def test_public_api():

    assert isinstance(__all__, list)
    
    assert "MetricUtils" in __all__


def test_class_exists():

    assert inspect.isclass(
        MetricUtils,
    )


# ==============================================================================
# Normalization
# ==============================================================================


def test_normalize_name():

    assert (
        MetricUtils.normalize_name(
            " Runtime "
        )
        == "runtime"
    )


def test_normalize_tags():

    tags = MetricUtils.normalize_tags(
        {
            "Host": "node1",
            "ENV": "prod",
        }
    )

    assert tags == {
        "host": "node1",
        "env": "prod",
    }


def test_normalize_labels():

    labels = MetricUtils.normalize_labels(
        {
            "Region": "EU",
            "Zone": "A",
        }
    )

    assert labels == {
        "region": "EU",
        "zone": "A",
    }


def test_ensure_mapping():

    mapping = MetricUtils.ensure_mapping(
        {
            "a": 1,
        }
    )

    assert mapping == {
        "a": 1,
    }


def test_ensure_sequence():

    sequence = MetricUtils.ensure_sequence(
        (
            1,
            2,
            3,
        )
    )

    assert sequence == [
        1,
        2,
        3,
    ]


def test_ensure_number():

    value = MetricUtils.ensure_number(
        10,
    )

    assert value == 10.0


# ==============================================================================
# Conversion
# ==============================================================================


def test_to_dict():

    data = {
        "a": 1,
        "b": 2,
    }

    assert (
        MetricUtils.to_dict(data)
        == data
    )


def test_from_dict():

    data = {
        "x": 5,
    }

    assert (
        MetricUtils.from_dict(data)
        == data
    )


def test_to_tuple():

    data = {
        "b": 2,
        "a": 1,
    }

    assert (
        MetricUtils.to_tuple(data)
        == (
            ("a", 1),
            ("b", 2),
        )
    )


def test_from_tuple():

    values = (
        ("x", 1),
        ("y", 2),
    )

    assert (
        MetricUtils.from_tuple(values)
        == {
            "x": 1,
            "y": 2,
        }
    )


def test_to_json():

    text = MetricUtils.to_json(
        {
            "a": 1,
        }
    )

    assert isinstance(
        text,
        str,
    )

    assert '"a"' in text


def test_from_json():

    data = MetricUtils.from_json(
        '{"a":1}'
    )

    assert data == {
        "a": 1,
    }


# ==============================================================================
# Hash
# ==============================================================================


def test_compute_hash():

    value = MetricUtils.compute_hash(
        {
            "a": 1,
        }
    )

    assert isinstance(
        value,
        str,
    )

    assert len(value) == 64


def test_stable_hash():

    left = MetricUtils.stable_hash(
        {
            "a": 1,
        }
    )

    right = MetricUtils.stable_hash(
        {
            "a": 1,
        }
    )

    assert left == right


def test_object_hash():

    value = MetricUtils.object_hash(
        {
            "a": 1,
        }
    )

    assert isinstance(
        value,
        str,
    )


def test_compare_hash():

    assert MetricUtils.compare_hash(
        {
            "a": 1,
        },
        {
            "a": 1,
        },
    )

    assert not MetricUtils.compare_hash(
        {
            "a": 1,
        },
        {
            "a": 2,
        },
    )

# ==============================================================================
# Merge
# ==============================================================================


def test_merge_dicts():

    result = MetricUtils.merge_dicts(
        {"a": 1},
        {"b": 2},
    )

    assert result == {
        "a": 1,
        "b": 2,
    }


def test_merge_states():

    result = MetricUtils.merge_states(
        {"count": 1},
        {"sum": 10},
    )

    assert result == {
        "count": 1,
        "sum": 10,
    }


def test_merge_labels():

    result = MetricUtils.merge_labels(
        {"env": "dev"},
        {"host": "node1"},
    )

    assert result == {
        "env": "dev",
        "host": "node1",
    }


def test_merge_tags():

    result = MetricUtils.merge_tags(
        {"service": "api"},
        {"version": "1.0"},
    )

    assert result == {
        "service": "api",
        "version": "1.0",
    }


def test_merge_statistics():

    left = {
        "count": 1,
        "sum": 10.0,
    }

    right = {
        "count": 2,
        "maximum": 8.0,
    }

    merged = MetricUtils.merge_statistics(
        left,
        right,
    )

    assert merged["count"] == 2

    assert merged["sum"] == 10.0

    assert merged["maximum"] == 8.0


# ==============================================================================
# Validation
# ==============================================================================


def test_validate_name():

    assert MetricUtils.validate_name(
        "runtime",
    )

    assert not MetricUtils.validate_name(
        "",
    )


def test_validate_mapping():

    assert MetricUtils.validate_mapping(
        {},
    )

    assert not MetricUtils.validate_mapping(
        [],
    )


def test_validate_sequence():

    assert MetricUtils.validate_sequence(
        [1, 2],
    )

    assert not MetricUtils.validate_sequence(
        10,
    )


def test_validate_number():

    assert MetricUtils.validate_number(
        1.5,
    )

    assert not MetricUtils.validate_number(
        "abc",
    )


def test_validate_json():

    assert MetricUtils.validate_json(
        '{"a":1}',
    )

    assert not MetricUtils.validate_json(
        "{",
    )


# ==============================================================================
# Diagnostics
# ==============================================================================


def test_diagnostics():

    diagnostics = MetricUtils.diagnostics()

    assert isinstance(
        diagnostics,
        dict,
    )

    assert "status" in diagnostics


def test_health():

    assert (
        MetricUtils.health()
        == "healthy"
    )


def test_status():

    assert (
        MetricUtils.status()
        == "ok"
    )


def test_summary():

    summary = MetricUtils.summary()

    assert isinstance(
        summary,
        dict,
    )


# ==============================================================================
# Public API
# ==============================================================================


def test_public_api_complete():
    expected = {
        "MetricUtils",
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
    }

    assert expected.issubset(set(__all__))