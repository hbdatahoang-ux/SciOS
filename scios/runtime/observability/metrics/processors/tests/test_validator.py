"""
Tests for SciOS Runtime Metrics ValidatorProcessor.
"""

from __future__ import annotations

import pytest

from ..validator import ValidatorProcessor


# ==============================================================
# Fixtures
# ==============================================================


@pytest.fixture
def validator() -> ValidatorProcessor:
    return ValidatorProcessor()


# ==============================================================
# Construction
# ==============================================================


def test_default_construction(validator):
    assert validator.name == "ValidatorProcessor"
    assert len(validator) == 0
    assert validator.rules() == []
    assert validator.schema() == {}


def test_custom_construction():
    processor = ValidatorProcessor(
        name="custom",
        description="test",
    )

    assert processor.name == "custom"
    assert processor.description == "test"


# ==============================================================
# Transform
# ==============================================================


def test_transform_valid_metric(validator):
    metric = {"name": "requests", "value": 10}

    assert validator.transform(metric) is metric
    assert validator.statistics()["validated"] == 1
    assert validator.statistics()["invalid"] == 0


def test_transform_invalid_metric(validator):
    validator.require("name")

    metric = {"value": 10}

    assert validator.transform(metric) is None
    assert validator.statistics()["validated"] == 0
    assert validator.statistics()["invalid"] == 1
    assert "Missing required field: name" in validator.errors()


def test_transform_preserves_identity(validator):
    metric = {"value": 42}

    result = validator.transform(metric)

    assert result is metric


# ==============================================================
# Validation
# ==============================================================


def test_validate_without_rules(validator):
    valid, errors = validator.validate({"value": 1})

    assert valid is True
    assert errors == []


def test_custom_rule_true(validator):
    validator.add_rule(lambda metric: True)

    valid, errors = validator.validate({"value": 1})

    assert valid is True
    assert errors == []


def test_custom_rule_false(validator):
    validator.add_rule(lambda metric: False)

    valid, errors = validator.validate({"value": 1})

    assert valid is False
    assert errors == ["Rule validation failed"]


def test_custom_rule_string_error(validator):
    validator.add_rule(
        lambda metric: "invalid metric"
    )

    valid, errors = validator.validate({"value": 1})

    assert valid is False
    assert errors == ["invalid metric"]


def test_rule_exception_is_captured(validator):
    def rule(metric):
        raise RuntimeError("boom")

    validator.add_rule(rule)

    valid, errors = validator.validate({"value": 1})

    assert valid is False
    assert errors == ["boom"]


# ==============================================================
# Rule Management
# ==============================================================


def test_add_rule(validator):
    rule = lambda metric: True

    result = validator.add_rule(rule)

    assert result is validator
    assert validator.rules() == [rule]
    assert len(validator) == 1


def test_add_rule_requires_callable(validator):
    with pytest.raises(TypeError):
        validator.add_rule("not callable")


def test_remove_rule(validator):
    rule = lambda metric: True

    validator.add_rule(rule)
    validator.remove_rule(rule)

    assert len(validator) == 0


def test_remove_missing_rule_is_safe(validator):
    rule = lambda metric: True

    assert validator.remove_rule(rule) is validator


def test_clear_rules(validator):
    validator.add_rule(lambda metric: True)
    validator.add_rule(lambda metric: True)

    assert validator.clear_rules() is validator
    assert len(validator) == 0


def test_rules_returns_copy(validator):
    rule = lambda metric: True

    validator.add_rule(rule)

    rules = validator.rules()
    rules.clear()

    assert len(validator) == 1


# ==============================================================
# Schema
# ==============================================================


def test_define_field(validator):
    result = validator.define_field(
        "value",
        int,
    )

    assert result is validator
    assert validator.schema() == {"value": int}


def test_define_field_requires_name(validator):
    with pytest.raises(ValueError):
        validator.define_field("", int)


def test_define_field_requires_type(validator):
    with pytest.raises(TypeError):
        validator.define_field("value", "int")


def test_remove_field(validator):
    validator.define_field("value", int)

    assert validator.remove_field("value") is validator
    assert validator.schema() == {}


def test_remove_missing_field_is_safe(validator):
    assert validator.remove_field("missing") is validator


def test_schema_returns_copy(validator):
    validator.define_field("value", int)

    schema = validator.schema()
    schema.clear()

    assert validator.schema() == {"value": int}


def test_validate_schema_valid(validator):
    validator.define_field("value", int)

    assert validator.validate_schema(
        {"value": 10}
    ) == []


def test_validate_schema_missing_field(validator):
    validator.define_field("value", int)

    errors = validator.validate_schema({})

    assert errors == ["Missing field: value"]


def test_validate_schema_invalid_type(validator):
    validator.define_field("value", int)

    errors = validator.validate_schema(
        {"value": "10"}
    )

    assert errors == ["Invalid type for value"]


def test_validate_schema_requires_dict(validator):
    validator.define_field("value", int)

    assert validator.validate_schema(10) == [
        "Metric must be dictionary"
    ]


def test_schema_is_combined_with_rules(validator):
    validator.define_field("value", int)
    validator.require("name")

    valid, errors = validator.validate(
        {"value": "bad"}
    )

    assert valid is False
    assert "Missing required field: name" in errors
    assert "Invalid type for value" in errors


# ==============================================================
# Built-in Validators
# ==============================================================


def test_require_valid(validator):
    validator.require("name", "value")

    valid, errors = validator.validate(
        {
            "name": "requests",
            "value": 1,
        }
    )

    assert valid is True
    assert errors == []


def test_require_missing_field(validator):
    validator.require("name", "value")

    valid, errors = validator.validate(
        {"name": "requests"}
    )

    assert valid is False
    assert errors == ["Missing required field: value"]


def test_require_non_dict(validator):
    validator.require("name")

    valid, errors = validator.validate("metric")

    assert valid is False
    assert errors == ["Rule validation failed"]


def test_range_minimum(validator):
    validator.range(
        "value",
        minimum=0,
    )

    valid, errors = validator.validate(
        {"value": 5}
    )

    assert valid is True
    assert errors == []


def test_range_below_minimum(validator):
    validator.range(
        "value",
        minimum=0,
    )

    valid, errors = validator.validate(
        {"value": -1}
    )

    assert valid is False
    assert errors == ["value below minimum"]


def test_range_maximum(validator):
    validator.range(
        "value",
        maximum=10,
    )

    valid, errors = validator.validate(
        {"value": 5}
    )

    assert valid is True
    assert errors == []


def test_range_above_maximum(validator):
    validator.range(
        "value",
        maximum=10,
    )

    valid, errors = validator.validate(
        {"value": 11}
    )

    assert valid is False
    assert errors == ["value above maximum"]


def test_range_missing_field(validator):
    validator.range(
        "value",
        minimum=0,
    )

    valid, errors = validator.validate({})

    assert valid is False
    assert errors == ["Missing field: value"]


def test_range_invalid_value(validator):
    validator.range(
        "value",
        minimum=0,
    )

    valid, errors = validator.validate(
        {"value": "invalid"}
    )

    assert valid is False
    assert errors == ["Invalid value for value"]


def test_range_requires_boundary(validator):
    with pytest.raises(ValueError):
        validator.range("value")


# ==============================================================
# Diagnostics
# ==============================================================


def test_errors_returns_copy(validator):
    validator.require("name")
    validator.transform({})

    errors = validator.errors()
    errors.clear()

    assert validator.errors() == [
        "Missing required field: name"
    ]


def test_clear_errors(validator):
    validator.require("name")
    validator.transform({})

    assert validator.clear_errors() is validator
    assert validator.errors() == []


# ==============================================================
# Statistics
# ==============================================================


def test_statistics(validator):
    validator.require("name")
    validator.transform({"name": "x"})
    validator.transform({})

    stats = validator.statistics()

    assert stats["validated"] == 1
    assert stats["invalid"] == 1
    assert stats["rules"] == 1
    assert stats["schema_fields"] == 0


def test_statistics_schema(validator):
    validator.define_field("value", int)

    stats = validator.statistics()

    assert stats["schema_fields"] == 1


# ==============================================================
# Reset
# ==============================================================


def test_reset(validator):
    validator.require("name")

    validator.transform({"name": "x"})
    validator.transform({})

    assert validator.statistics()["validated"] == 1
    assert validator.statistics()["invalid"] == 1
    assert validator.errors()

    assert validator.reset() is validator

    assert validator.statistics()["validated"] == 0
    assert validator.statistics()["invalid"] == 0
    assert validator.errors() == []

    # Configuration survives reset.
    assert len(validator) == 1


# ==============================================================
# Representation
# ==============================================================


def test_repr(validator):
    text = repr(validator)

    assert text.startswith("ValidatorProcessor(")
    assert "rules=0" in text
    assert "validated=0" in text
    assert "invalid=0" in text