"""
Tests for SciOS Runtime Metrics Filter Processor.
"""

from __future__ import annotations

import pytest

from ..filter import FilterProcessor


# ==============================================================
# Construction
# ==============================================================


def test_default_construction():
    processor = FilterProcessor()

    assert processor.name == "FilterProcessor"
    assert len(processor) == 0
    assert processor.rules() == []


def test_custom_name_and_description():
    processor = FilterProcessor(
        name="custom",
        description="test",
    )

    assert processor.name == "custom"
    assert processor.description == "test"


def test_constructor_predicate():
    processor = FilterProcessor(
        predicate=lambda value: value > 10
    )

    assert len(processor) == 1
    assert processor.transform(20) == 20
    assert processor.transform(5) is None


# ==============================================================
# Rule Management
# ==============================================================


def test_add_rule():
    processor = FilterProcessor()

    rule = lambda value: value > 0

    result = processor.add_rule(rule)

    assert result is processor
    assert processor.rules() == [rule]


def test_add_rule_requires_callable():
    processor = FilterProcessor()

    with pytest.raises(TypeError):
        processor.add_rule("invalid")


def test_remove_rule():
    processor = FilterProcessor()

    rule = lambda value: True

    processor.add_rule(rule)
    processor.remove_rule(rule)

    assert len(processor) == 0


def test_remove_missing_rule_is_safe():
    processor = FilterProcessor()

    processor.remove_rule(lambda value: True)

    assert len(processor) == 0


def test_clear_rules():
    processor = FilterProcessor(
        predicate=lambda value: True
    )

    processor.add_rule(lambda value: True)
    processor.clear_rules()

    assert len(processor) == 0


def test_rules_returns_copy():
    processor = FilterProcessor(
        predicate=lambda value: True
    )

    rules = processor.rules()
    rules.clear()

    assert len(processor) == 1


# ==============================================================
# Processing
# ==============================================================


def test_empty_rules_accept_everything():
    processor = FilterProcessor()

    assert processor.transform("metric") == "metric"


def test_rule_accepts_metric():
    processor = FilterProcessor(
        predicate=lambda value: value > 10
    )

    assert processor.transform(20) == 20


def test_rule_rejects_metric():
    processor = FilterProcessor(
        predicate=lambda value: value > 10
    )

    assert processor.transform(5) is None


def test_multiple_rules_are_combined():
    processor = FilterProcessor()

    processor.add_rule(lambda value: value > 0)
    processor.add_rule(lambda value: value < 10)

    assert processor.transform(5) == 5
    assert processor.transform(20) is None
    assert processor.transform(-1) is None


def test_rule_exception_rejects_metric():
    def broken(_):
        raise RuntimeError("broken")

    processor = FilterProcessor(
        predicate=broken
    )

    assert processor.transform("metric") is None


def test_accepts_method():
    processor = FilterProcessor(
        predicate=lambda value: value == "ok"
    )

    assert processor.accepts("ok") is True
    assert processor.accepts("bad") is False


# ==============================================================
# Built-in Filters
# ==============================================================


def test_require_field():
    processor = FilterProcessor()

    processor.require_field("name")

    assert processor.transform(
        {"name": "requests"}
    ) == {"name": "requests"}

    assert processor.transform(
        {"value": 1}
    ) is None


def test_field_equals():
    processor = FilterProcessor()

    processor.field_equals(
        "type",
        "counter",
    )

    assert processor.transform(
        {"type": "counter"}
    ) == {"type": "counter"}

    assert processor.transform(
        {"type": "gauge"}
    ) is None


def test_field_in():
    processor = FilterProcessor()

    processor.field_in(
        "type",
        ["counter", "gauge"],
    )

    assert processor.transform(
        {"type": "counter"}
    ) is not None

    assert processor.transform(
        {"type": "gauge"}
    ) is not None

    assert processor.transform(
        {"type": "histogram"}
    ) is None


def test_builtin_filters_require_string_field():
    processor = FilterProcessor()

    with pytest.raises(TypeError):
        processor.require_field(123)


def test_field_equals_requires_string_field():
    processor = FilterProcessor()

    with pytest.raises(TypeError):
        processor.field_equals(123, "x")


# ==============================================================
# Statistics
# ==============================================================


def test_statistics():
    processor = FilterProcessor(
        predicate=lambda value: value > 0
    )

    processor.transform(10)
    processor.transform(-1)
    processor.transform(20)

    stats = processor.statistics()

    assert stats["total"] == 3
    assert stats["accepted"] == 2
    assert stats["rejected"] == 1
    assert stats["rules"] == 1
    assert stats["acceptance_rate"] == pytest.approx(2 / 3)
    assert stats["rejection_rate"] == pytest.approx(1 / 3)


def test_statistics_empty():
    processor = FilterProcessor()

    stats = processor.statistics()

    assert stats["total"] == 0
    assert stats["accepted"] == 0
    assert stats["rejected"] == 0
    assert stats["acceptance_rate"] == 0.0
    assert stats["rejection_rate"] == 0.0


# ==============================================================
# Reset
# ==============================================================


def test_reset_preserves_rules():
    processor = FilterProcessor(
        predicate=lambda value: value > 0
    )

    processor.transform(1)
    processor.transform(-1)

    processor.reset()

    stats = processor.statistics()

    assert stats["total"] == 0
    assert stats["accepted"] == 0
    assert stats["rejected"] == 0
    assert len(processor) == 1


def test_reset_returns_self():
    processor = FilterProcessor()

    assert processor.reset() is processor


# ==============================================================
# Representation
# ==============================================================


def test_repr():
    processor = FilterProcessor(
        predicate=lambda value: True
    )

    processor.transform(1)

    text = repr(processor)

    assert "FilterProcessor" in text
    assert "rules=1" in text
    assert "accepted=1" in text


def test_len():
    processor = FilterProcessor()

    assert len(processor) == 0

    processor.add_rule(lambda value: True)

    assert len(processor) == 1