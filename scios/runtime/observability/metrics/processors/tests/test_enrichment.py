"""
Tests for SciOS Runtime Metrics EnrichmentProcessor.
"""

from __future__ import annotations

import pytest

from ..enrichment import EnrichmentProcessor


# ==============================================================
# Fixtures
# ==============================================================


@pytest.fixture
def processor() -> EnrichmentProcessor:
    return EnrichmentProcessor()


# ==============================================================
# Construction
# ==============================================================


def test_default_construction(processor):
    assert processor.name == "EnrichmentProcessor"
    assert processor.fields() == {}
    assert processor.rules() == []
    assert len(processor) == 0


def test_custom_construction():
    processor = EnrichmentProcessor(
        name="custom",
        description="test",
        fields={"source": "runtime"},
    )

    assert processor.name == "custom"
    assert processor.description == "test"
    assert processor.fields() == {
        "source": "runtime"
    }


# ==============================================================
# Static Fields
# ==============================================================


def test_add_field(processor):
    assert processor.add_field(
        "source",
        "runtime",
    ) is processor

    assert processor.fields() == {
        "source": "runtime"
    }


def test_add_field_replaces_existing(processor):
    processor.add_field("source", "runtime")
    processor.add_field("source", "pipeline")

    assert processor.fields()["source"] == "pipeline"


def test_add_field_requires_name(processor):
    with pytest.raises(ValueError):
        processor.add_field("", "runtime")


def test_remove_field(processor):
    processor.add_field("source", "runtime")

    assert processor.remove_field("source") is processor
    assert processor.fields() == {}


def test_remove_missing_field_is_safe(processor):
    assert processor.remove_field("missing") is processor


def test_clear_fields(processor):
    processor.add_field("source", "runtime")
    processor.add_field("environment", "test")

    assert processor.clear_fields() is processor
    assert processor.fields() == {}


def test_fields_returns_copy(processor):
    processor.add_field("source", "runtime")

    fields = processor.fields()
    fields["other"] = "value"

    assert processor.fields() == {
        "source": "runtime"
    }


# ==============================================================
# Transform
# ==============================================================


def test_transform_adds_static_field(processor):
    processor.add_field("source", "runtime")

    metric = {
        "name": "requests",
        "value": 10,
    }

    result = processor.transform(metric)

    assert result == {
        "name": "requests",
        "value": 10,
        "source": "runtime",
    }


def test_transform_does_not_mutate_input(processor):
    processor.add_field("source", "runtime")

    metric = {
        "name": "requests",
    }

    result = processor.transform(metric)

    assert "source" not in metric
    assert result is not metric


def test_transform_preserves_metric_values(processor):
    processor.add_field("source", "runtime")

    metric = {
        "name": "requests",
        "value": 42,
    }

    result = processor.transform(metric)

    assert result["name"] == "requests"
    assert result["value"] == 42


def test_transform_dynamic_field(processor):
    processor.add_field(
        "source",
        lambda: "runtime",
    )

    result = processor.transform(
        {"name": "requests"}
    )

    assert result["source"] == "runtime"


def test_transform_deepcopies_field_value(processor):
    metadata = {
        "host": "node-1",
    }

    processor.add_field(
        "metadata",
        metadata,
    )

    result = processor.transform(
        {"name": "requests"}
    )

    result["metadata"]["host"] = "node-2"

    assert metadata["host"] == "node-1"


def test_transform_non_dict_passes_through(processor):
    metric = "metric"

    assert processor.transform(metric) == metric


# ==============================================================
# Rules
# ==============================================================


def test_add_rule(processor):
    rule = lambda metric: metric

    assert processor.add_rule(rule) is processor
    assert processor.rules() == [rule]


def test_add_rule_requires_callable(processor):
    with pytest.raises(TypeError):
        processor.add_rule("invalid")


def test_rule_can_modify_metric(processor):
    def rule(metric):
        metric["processed"] = True
        return metric

    processor.add_rule(rule)

    result = processor.transform(
        {"name": "requests"}
    )

    assert result["processed"] is True


def test_rule_returning_none_preserves_metric(processor):
    processor.add_rule(
        lambda metric: None
    )

    metric = {
        "name": "requests",
    }

    result = processor.transform(metric)

    assert result == metric


def test_multiple_rules(processor):
    processor.add_rule(
        lambda metric: {
            **metric,
            "a": 1,
        }
    )

    processor.add_rule(
        lambda metric: {
            **metric,
            "b": 2,
        }
    )

    result = processor.transform(
        {"name": "requests"}
    )

    assert result == {
        "name": "requests",
        "a": 1,
        "b": 2,
    }


def test_remove_rule(processor):
    rule = lambda metric: metric

    processor.add_rule(rule)

    assert processor.remove_rule(rule) is processor
    assert processor.rules() == []


def test_remove_missing_rule_is_safe(processor):
    rule = lambda metric: metric

    assert processor.remove_rule(rule) is processor


def test_clear_rules(processor):
    processor.add_rule(lambda metric: metric)
    processor.add_rule(lambda metric: metric)

    assert processor.clear_rules() is processor
    assert processor.rules() == []


def test_rules_returns_copy(processor):
    rule = lambda metric: metric

    processor.add_rule(rule)

    rules = processor.rules()
    rules.clear()

    assert len(processor.rules()) == 1


# ==============================================================
# Rule Errors
# ==============================================================


def test_rule_exception_returns_none(processor):
    def rule(metric):
        raise RuntimeError("boom")

    processor.add_rule(rule)

    assert processor.transform(
        {"name": "requests"}
    ) is None

    assert processor.errors() == ["boom"]


def test_rule_exception_increments_skipped(processor):
    processor.add_rule(
        lambda metric: 1 / 0
    )

    processor.transform(
        {"name": "requests"}
    )

    assert processor.statistics()["skipped"] == 1


# ==============================================================
# Temporary Enrichment
# ==============================================================


def test_enrich(processor):
    metric = {
        "name": "requests",
    }

    result = processor.enrich(
        metric,
        source="runtime",
        environment="test",
    )

    assert result == {
        "name": "requests",
        "source": "runtime",
        "environment": "test",
    }


def test_enrich_does_not_mutate_input(processor):
    metric = {
        "name": "requests",
    }

    result = processor.enrich(
        metric,
        source="runtime",
    )

    assert "source" not in metric
    assert result is not metric


def test_enrich_dynamic_value(processor):
    result = processor.enrich(
        {"name": "requests"},
        timestamp=lambda: 123,
    )

    assert result["timestamp"] == 123


def test_enrich_non_dict(processor):
    metric = "metric"

    assert processor.enrich(
        metric,
        source="runtime",
    ) == metric


# ==============================================================
# Diagnostics
# ==============================================================


def test_errors_returns_copy(processor):
    processor.add_rule(
        lambda metric: 1 / 0
    )

    processor.transform({})

    errors = processor.errors()
    errors.clear()

    assert processor.errors() == ["division by zero"]


def test_clear_errors(processor):
    processor.add_rule(
        lambda metric: 1 / 0
    )

    processor.transform({})

    assert processor.clear_errors() is processor
    assert processor.errors() == []


# ==============================================================
# Statistics
# ==============================================================


def test_statistics(processor):
    processor.add_field(
        "source",
        "runtime",
    )

    processor.add_rule(
        lambda metric: metric
    )

    processor.transform(
        {"name": "requests"}
    )

    stats = processor.statistics()

    assert stats["enriched"] == 1
    assert stats["skipped"] == 0
    assert stats["fields"] == 1
    assert stats["rules"] == 1
    assert stats["errors"] == 0


def test_statistics_after_error(processor):
    processor.add_rule(
        lambda metric: 1 / 0
    )

    processor.transform({})

    stats = processor.statistics()

    assert stats["enriched"] == 0
    assert stats["skipped"] == 1
    assert stats["errors"] == 1


# ==============================================================
# Reset
# ==============================================================


def test_reset(processor):
    processor.add_field(
        "source",
        "runtime",
    )

    processor.add_rule(
        lambda metric: 1 / 0
    )

    processor.transform({})

    assert processor.statistics()["skipped"] == 1
    assert processor.errors()

    assert processor.reset() is processor

    stats = processor.statistics()

    assert stats["enriched"] == 0
    assert stats["skipped"] == 0
    assert stats["errors"] == 0

    # Configuration survives reset.
    assert len(processor.fields()) == 1
    assert len(processor.rules()) == 1


# ==============================================================
# Representation
# ==============================================================


def test_repr(processor):
    text = repr(processor)

    assert text.startswith(
        "EnrichmentProcessor("
    )
    assert "fields=0" in text
    assert "rules=0" in text
    assert "enriched=0" in text
    assert "skipped=0" in text