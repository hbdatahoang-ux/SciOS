"""
SciOS Runtime ExecutionResult Contract Tests
=============================================

Canonical contract tests for:

    scios.runtime.result.ExecutionResult

Test location:

    tests/test_result.py

Python 3.11+
"""

from __future__ import annotations


from copy import deepcopy


import pytest


from scios.runtime.result import ExecutionResult


# ==========================================================
# Construction
# ==========================================================

def test_ok_factory_metadata_contract():
    result = ExecutionResult.ok(
        123,
        source="test",
        nested={
            "value": 123,
        },
    )

    assert result.metadata == {
        "source": "test",
        "nested": {
            "value": 123,
        },
    }

def test_default_construction():
    result = ExecutionResult()

    assert result.success is True
    assert result.value is None
    assert result.error is None
    assert result.message is None
    assert result.duration == 0.0
    assert result.metadata == {}
    assert isinstance(result.timestamp, str)


def test_ok_factory():
    result = ExecutionResult.ok(123)

    assert isinstance(result, ExecutionResult)
    assert result.success is True
    assert result.status == "success"
    assert result.value == 123
    assert result.result == 123
    assert result.error is None
    assert result.message is None


def test_fail_factory():
    error = ValueError("boom")

    result = ExecutionResult.fail(error)

    assert isinstance(result, ExecutionResult)
    assert result.success is False
    assert result.status == "error"
    assert result.failed is True
    assert result.error is error
    assert result.message == "boom"
    assert result.value is None


def test_from_value():
    result = ExecutionResult.from_value(42)

    assert isinstance(result, ExecutionResult)
    assert result.success is True
    assert result.value == 42


def test_from_error():
    error = RuntimeError("failure")

    result = ExecutionResult.from_error(error)

    assert isinstance(result, ExecutionResult)
    assert result.success is False
    assert result.error is error
    assert result.message == "failure"


# ==========================================================
# State API
# ==========================================================


@pytest.mark.parametrize(
    "result, expected",
    [
        (ExecutionResult.ok(1), True),
        (ExecutionResult.fail(ValueError("x")), False),
    ],
)
def test_succeeded(result, expected):
    assert result.succeeded is expected


@pytest.mark.parametrize(
    "result, expected",
    [
        (ExecutionResult.ok(1), False),
        (ExecutionResult.fail(ValueError("x")), True),
    ],
)
def test_failed(result, expected):
    assert result.failed is expected


@pytest.mark.parametrize(
    "result, expected",
    [
        (ExecutionResult.ok(1), True),
        (ExecutionResult.fail(ValueError("x")), False),
    ],
)
def test_is_success(result, expected):
    assert result.is_success is expected


def test_status_contract():
    assert ExecutionResult.ok(1).status == "success"
    assert ExecutionResult.fail(ValueError("x")).status == "error"


def test_result_is_value_alias():
    value = {"answer": 123}

    result = ExecutionResult.ok(value)

    assert result.result is value
    assert result.result == result.value


def test_has_value():
    assert ExecutionResult.ok(None).has_value is False
    assert ExecutionResult.ok(0).has_value is True
    assert ExecutionResult.ok(False).has_value is True
    assert ExecutionResult.ok("").has_value is True
    assert ExecutionResult.ok(123).has_value is True


# ==========================================================
# Metadata
# ==========================================================


def test_set_returns_self():
    result = ExecutionResult.ok(123)

    returned = result.set("source", "test")

    assert returned is result
    assert result.metadata["source"] == "test"


def test_get_metadata():
    result = ExecutionResult.ok(123)

    result.set("source", "test")

    assert result.get("source") == "test"
    assert result.get("missing") is None
    assert result.get("missing", "default") == "default"


def test_metadata_isolated_between_instances():
    first = ExecutionResult.ok(1)
    second = ExecutionResult.ok(2)

    first.set("x", 42)

    assert first.metadata == {"x": 42}
    assert second.metadata == {}


def test_factory_metadata():
    result = ExecutionResult.ok(
        123,
        source="test",
        stage="demo",
    )

    assert result.metadata == {
        "source": "test",
        "stage": "demo",
    }


def test_failure_factory_metadata():
    result = ExecutionResult.fail(
        ValueError("boom"),
        source="test",
        stage="demo",
    )

    assert result.metadata == {
        "source": "test",
        "stage": "demo",
    }


# ==========================================================
# Mapping compatibility
# ==========================================================


def test_mapping_top_level_fields():
    result = ExecutionResult.ok(123)

    assert result["status"] == "success"
    assert result["success"] is True
    assert result["value"] == 123
    assert result["result"] == 123
    assert result["message"] is None
    assert result["error"] is None
    assert result["duration"] == 0.0
    assert result["metadata"] == {}
    assert isinstance(result["timestamp"], str)


def test_mapping_payload_fields():
    result = ExecutionResult.ok(
        {
            "answer": 123,
            "name": "demo",
        }
    )

    assert result["answer"] == 123
    assert result["name"] == "demo"


def test_mapping_metadata_fields():
    result = ExecutionResult.ok(
        123
    ).set(
        "source",
        "test",
    )

    assert result["source"] == "test"


def test_mapping_precedence_top_level_over_payload():
    result = ExecutionResult.ok(
        {
            "status": "payload-status",
            "success": "payload-success",
            "value": "payload-value",
        }
    )

    assert result["status"] == "success"
    assert result["success"] is True
    assert result["value"] == {
        "status": "payload-status",
        "success": "payload-success",
        "value": "payload-value",
    }


def test_mapping_precedence_metadata_over_payload():
    result = ExecutionResult.ok(
        {
            "x": "payload",
        }
    ).set(
        "x",
        "metadata",
    )

    assert result["x"] == "metadata"


def test_mapping_missing_key():
    result = ExecutionResult.ok(123)

    with pytest.raises(KeyError):
        _ = result["missing"]


def test_contains_top_level_key():
    result = ExecutionResult.ok(123)

    assert "status" in result
    assert "success" in result
    assert "value" in result
    assert "result" in result


def test_contains_payload_key():
    result = ExecutionResult.ok(
        {
            "answer": 123,
        }
    )

    assert "answer" in result


def test_contains_metadata_key():
    result = ExecutionResult.ok(123).set(
        "source",
        "test",
    )

    assert "source" in result


def test_keys_include_contract_and_dynamic_fields():
    result = ExecutionResult.ok(
        {
            "answer": 123,
        }
    ).set(
        "source",
        "test",
    )

    keys = result.keys()

    assert "status" in keys
    assert "success" in keys
    assert "value" in keys
    assert "result" in keys
    assert "metadata" in keys
    assert "timestamp" in keys
    assert "source" in keys
    assert "answer" in keys


def test_items_include_contract_and_dynamic_fields():
    result = ExecutionResult.ok(
        {
            "answer": 123,
        }
    ).set(
        "source",
        "test",
    )

    items = dict(result.items())

    assert items["status"] == "success"
    assert items["answer"] == 123
    assert items["source"] == "test"


def test_iteration_returns_keys():
    result = ExecutionResult.ok(
        {
            "answer": 123,
        }
    ).set(
        "source",
        "test",
    )

    keys = list(result)

    assert "status" in keys
    assert "answer" in keys
    assert "source" in keys


# ==========================================================
# Boolean / length protocol
# ==========================================================


def test_bool_success():
    assert bool(ExecutionResult.ok(123)) is True


def test_bool_failure():
    assert bool(
        ExecutionResult.fail(
            ValueError("boom")
        )
    ) is False


def test_len_for_dict_payload():
    result = ExecutionResult.ok(
        {
            "a": 1,
            "b": 2,
        }
    )

    assert len(result) == 2


def test_len_for_non_dict_payload():
    assert len(ExecutionResult.ok(123)) == 0
    assert len(ExecutionResult.ok("hello")) == 0
    assert len(ExecutionResult.ok(None)) == 0


# ==========================================================
# Serialization
# ==========================================================


def test_to_dict_success():
    result = ExecutionResult.ok(123)

    data = result.to_dict()

    assert data["status"] == "success"
    assert data["success"] is True
    assert data["value"] == 123
    assert data["result"] == 123
    assert data["message"] is None
    assert data["error"] is None
    assert data["duration"] == 0.0
    assert data["metadata"] == {}
    assert isinstance(data["timestamp"], str)


def test_to_dict_failure():
    error = ValueError("boom")

    result = ExecutionResult.fail(error)

    data = result.to_dict()

    assert data["status"] == "error"
    assert data["success"] is False
    assert data["value"] is None
    assert data["result"] is None
    assert data["message"] == "boom"
    assert data["error"] == "boom"


def test_to_dict_metadata_is_deep_copy():
    result = ExecutionResult.ok(
        1,
        nested={
            "value": 123,
        },
    )

    data = result.to_dict()

    data["metadata"]["nested"]["value"] = 999

    assert result.metadata["nested"]["value"] == 123


def test_from_dict_success():
    data = {
        "status": "success",
        "success": True,
        "value": 123,
        "result": 123,
        "message": None,
        "error": None,
        "duration": 1.5,
        "metadata": {
            "source": "test",
        },
        "timestamp": "2026-01-01T00:00:00+00:00",
    }

    result = ExecutionResult.from_dict(data)

    assert result.success is True
    assert result.status == "success"
    assert result.value == 123
    assert result.duration == 1.5
    assert result.metadata == {
        "source": "test",
    }
    assert result.timestamp == data["timestamp"]


def test_from_dict_failure():
    data = {
        "status": "error",
        "success": False,
        "value": None,
        "message": "boom",
        "error": "boom",
    }

    result = ExecutionResult.from_dict(data)

    assert result.success is False
    assert result.status == "error"
    assert result.value is None
    assert result.message == "boom"
    assert isinstance(result.error, RuntimeError)
    assert str(result.error) == "boom"


def test_from_dict_prefers_value_over_result():
    result = ExecutionResult.from_dict(
        {
            "value": "value",
            "result": "result",
        }
    )

    assert result.value == "value"


def test_from_dict_uses_result_when_value_missing():
    result = ExecutionResult.from_dict(
        {
            "result": 123,
        }
    )

    assert result.value == 123


def test_round_trip():
    original = ExecutionResult.ok(
        {
            "answer": 123,
        },
        message="done",
        duration=1.25,
        source="test",
    )

    restored = ExecutionResult.from_dict(
        original.to_dict()
    )

    assert restored.success == original.success
    assert restored.value == original.value
    assert restored.message == original.message
    assert restored.duration == original.duration
    assert restored.metadata == original.metadata
    assert restored.timestamp == original.timestamp


# ==========================================================
# Copy
# ==========================================================


def test_copy_returns_independent_result():
    original = ExecutionResult.ok(
        {
            "nested": {
                "value": 123,
            }
        }
    )

    copied = original.copy()

    assert copied is not original
    assert copied.value == original.value
    assert copied.metadata == original.metadata

    copied.value["nested"]["value"] = 999

    assert original.value["nested"]["value"] == 123


def test_copy_metadata_is_independent():
    original = ExecutionResult.ok(
        123,
        source="test",
    )

    copied = original.copy()

    copied.metadata["source"] = "changed"

    assert original.metadata["source"] == "test"


# ==========================================================
# Duration / diagnostics
# ==========================================================


def test_duration_is_preserved():
    result = ExecutionResult.ok(
        123,
        duration=2.5,
    )

    assert result.duration == 2.5


def test_failure_duration_is_preserved():
    result = ExecutionResult.fail(
        ValueError("boom"),
        duration=3.25,
    )

    assert result.duration == 3.25


def test_failure_message_defaults_to_error_string():
    error = RuntimeError("boom")

    result = ExecutionResult.fail(error)

    assert result.message == "boom"


def test_explicit_failure_message_overrides_error_string():
    error = RuntimeError("internal")

    result = ExecutionResult.fail(
        error,
        message="public message",
    )

    assert result.message == "public message"
    assert result.error is error


# ==========================================================
# Regression contracts
# ==========================================================


def test_set_does_not_modify_payload():
    payload = {
        "answer": 123,
    }

    result = ExecutionResult.ok(payload)

    result.set(
        "source",
        "test",
    )

    assert result.value == {
        "answer": 123,
    }


def test_set_does_not_modify_metadata_identity_contract():
    result = ExecutionResult.ok(123)

    metadata_before = result.metadata

    result.set(
        "source",
        "test",
    )

    assert result.metadata is metadata_before


def test_error_identity_is_preserved():
    error = ValueError("boom")

    result = ExecutionResult.fail(error)

    assert result.error is error


def test_success_result_has_no_error():
    result = ExecutionResult.ok(123)

    assert result.error is None


def test_failure_result_has_no_success():
    result = ExecutionResult.fail(
        ValueError("boom")
    )

    assert result.success is False
    assert result.succeeded is False
    assert result.is_success is False


def test_deepcopy_does_not_share_metadata():
    result = ExecutionResult.ok(
        123,
        nested={
            "x": 1,
        },
    )

    copied = deepcopy(result)

    copied.metadata["nested"]["x"] = 99

    assert result.metadata["nested"]["x"] == 1
