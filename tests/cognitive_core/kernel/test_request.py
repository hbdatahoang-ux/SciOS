"""
Tests for scios.cognitive_core.kernel.request
"""

from datetime import datetime

from scios.cognitive_core.kernel.request import CognitiveRequest


# =========================================================
# Construction
# =========================================================

def test_default_request_can_be_created():
    request = CognitiveRequest()

    assert request is not None


def test_request_accepts_query():
    request = CognitiveRequest(query="hello")

    assert request.query == "hello"


def test_request_id_is_generated_automatically():
    request = CognitiveRequest(query="hello")

    assert request.request_id
    assert isinstance(request.request_id, str)


def test_each_request_gets_unique_id():
    first = CognitiveRequest(query="hello")
    second = CognitiveRequest(query="hello")

    assert first.request_id != second.request_id


def test_request_accepts_explicit_request_id():
    request = CognitiveRequest(
        query="hello",
        request_id="req-001",
    )

    assert request.request_id == "req-001"


def test_inputs_default_to_empty_dict():
    request = CognitiveRequest(query="hello")

    assert request.inputs == {}


def test_metadata_default_to_empty_dict():
    request = CognitiveRequest(query="hello")

    assert request.metadata == {}


def test_created_at_is_present():
    request = CognitiveRequest(query="hello")

    assert request.created_at is not None


def test_request_accepts_inputs():
    inputs = {
        "temperature": 0.5,
        "limit": 10,
    }

    request = CognitiveRequest(
        query="hello",
        inputs=inputs,
    )

    assert request.inputs == inputs


def test_request_accepts_metadata():
    metadata = {
        "source": "test",
        "version": 1,
    }

    request = CognitiveRequest(
        query="hello",
        metadata=metadata,
    )

    assert request.metadata == metadata


def test_request_accepts_created_at():
    created_at = datetime(2026, 1, 1, 12, 0, 0)

    request = CognitiveRequest(
        query="hello",
        created_at=created_at,
    )

    assert request.created_at == created_at


# =========================================================
# Dictionary serialization
# =========================================================

def test_to_dict_returns_dict():
    request = CognitiveRequest(query="hello")

    result = request.to_dict()

    assert isinstance(result, dict)


def test_to_dict_contains_request_id():
    request = CognitiveRequest(
        query="hello",
        request_id="req-001",
    )

    result = request.to_dict()

    assert result["request_id"] == "req-001"


def test_to_dict_contains_query():
    request = CognitiveRequest(query="hello")

    result = request.to_dict()

    assert result["query"] == "hello"


def test_to_dict_contains_inputs():
    inputs = {"x": 10}

    request = CognitiveRequest(
        query="hello",
        inputs=inputs,
    )

    result = request.to_dict()

    assert result["inputs"] == inputs


def test_to_dict_contains_metadata():
    metadata = {"source": "test"}

    request = CognitiveRequest(
        query="hello",
        metadata=metadata,
    )

    result = request.to_dict()

    assert result["metadata"] == metadata


def test_to_dict_contains_created_at():
    request = CognitiveRequest(query="hello")

    result = request.to_dict()

    assert "created_at" in result


def test_to_dict_contains_expected_keys():
    request = CognitiveRequest(query="hello")

    result = request.to_dict()

    assert set(result) == {
        "request_id",
        "query",
        "inputs",
        "metadata",
        "created_at",
    }


# =========================================================
# from_dict
# =========================================================

def test_from_dict_returns_request():
    data = {
        "request_id": "req-001",
        "query": "hello",
        "inputs": {"x": 1},
        "metadata": {"source": "test"},
    }

    request = CognitiveRequest.from_dict(data)

    assert isinstance(request, CognitiveRequest)


def test_from_dict_restores_request_id():
    data = {
        "request_id": "req-001",
        "query": "hello",
    }

    request = CognitiveRequest.from_dict(data)

    assert request.request_id == "req-001"


def test_from_dict_restores_query():
    data = {
        "request_id": "req-001",
        "query": "hello",
    }

    request = CognitiveRequest.from_dict(data)

    assert request.query == "hello"


def test_from_dict_restores_inputs():
    data = {
        "request_id": "req-001",
        "query": "hello",
        "inputs": {"x": 42},
    }

    request = CognitiveRequest.from_dict(data)

    assert request.inputs == {"x": 42}


def test_from_dict_restores_metadata():
    data = {
        "request_id": "req-001",
        "query": "hello",
        "metadata": {"source": "test"},
    }

    request = CognitiveRequest.from_dict(data)

    assert request.metadata == {"source": "test"}


def test_from_dict_missing_inputs_defaults_to_empty_dict():
    data = {
        "request_id": "req-001",
        "query": "hello",
    }

    request = CognitiveRequest.from_dict(data)

    assert request.inputs == {}


def test_from_dict_missing_metadata_defaults_to_empty_dict():
    data = {
        "request_id": "req-001",
        "query": "hello",
    }

    request = CognitiveRequest.from_dict(data)

    assert request.metadata == {}


def test_from_dict_generates_request_id_when_missing():
    data = {
        "query": "hello",
    }

    request = CognitiveRequest.from_dict(data)

    assert request.request_id
    assert isinstance(request.request_id, str)


# =========================================================
# Round trip
# =========================================================

def test_to_dict_from_dict_preserves_core_fields():
    request = CognitiveRequest(
        request_id="req-001",
        query="hello",
        inputs={"x": 1},
        metadata={"source": "test"},
    )

    restored = CognitiveRequest.from_dict(request.to_dict())

    assert restored.request_id == request.request_id
    assert restored.query == request.query
    assert restored.inputs == request.inputs
    assert restored.metadata == request.metadata


# =========================================================
# Representation
# =========================================================

def test_repr_contains_class_name():
    request = CognitiveRequest(query="hello")

    assert "CognitiveRequest" in repr(request)


def test_repr_contains_request_id():
    request = CognitiveRequest(
        request_id="req-001",
        query="hello",
    )

    result = repr(request)

    assert "req-001" in result


def test_repr_contains_query():
    request = CognitiveRequest(query="hello")

    result = repr(request)

    assert "hello" in result


def test_repr_has_expected_structure():
    request = CognitiveRequest(
        request_id="req-001",
        query="hello",
    )

    result = repr(request)

    assert result.startswith("CognitiveRequest(")
    assert "request_id=" in result
    assert "query=" in result
    assert result.endswith(")")


# =========================================================
# Isolation
# =========================================================

def test_inputs_are_not_shared_between_instances():
    first = CognitiveRequest(query="first")
    second = CognitiveRequest(query="second")

    first.inputs["x"] = 1

    assert second.inputs == {}


def test_metadata_are_not_shared_between_instances():
    first = CognitiveRequest(query="first")
    second = CognitiveRequest(query="second")

    first.metadata["source"] = "test"

    assert second.metadata == {}
