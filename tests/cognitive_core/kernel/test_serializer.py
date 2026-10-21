"""
Contract tests for scios.cognitive_core.kernel.serializer.

These tests lock the public behavior of KernelSerializer.
"""

from __future__ import annotations

import json

import pytest

from scios.cognitive_core.kernel.context import CognitiveContext
from scios.cognitive_core.kernel.request import CognitiveRequest
from scios.cognitive_core.kernel.response import CognitiveResponse
from scios.cognitive_core.kernel.serializer import KernelSerializer


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def request_obj() -> CognitiveRequest:
    return CognitiveRequest(
        query="hello world",
        inputs={
            "temperature": 25,
            "pressure": 1.0,
        },
        metadata={
            "source": "test",
        },
    )


@pytest.fixture
def context(request_obj: CognitiveRequest) -> CognitiveContext:
    context = CognitiveContext(request_obj)

    context.state = {
        "result": "processed",
    }

    context.metadata = {
        "stage": "test",
    }

    context.trace = [
        "stage_a",
        "stage_b",
    ]

    return context


@pytest.fixture
def response(context: CognitiveContext) -> CognitiveResponse:
    return CognitiveResponse(
        status="success",
        context=context,
        errors=[],
        warnings=[],
        metadata={
            "source": "test",
        },
    )


# ============================================================
# Public API
# ============================================================


def test_serializer_is_available() -> None:
    assert KernelSerializer is not None


def test_serializer_to_dict_is_callable() -> None:
    assert callable(KernelSerializer.to_dict)


def test_serializer_to_json_is_callable() -> None:
    assert callable(KernelSerializer.to_json)


def test_serializer_from_json_request_is_callable() -> None:
    assert callable(KernelSerializer.from_json_request)


def test_serializer_from_json_response_is_callable() -> None:
    assert callable(KernelSerializer.from_json_response)


# ============================================================
# to_dict
# ============================================================


def test_to_dict_request(
    request_obj: CognitiveRequest,
) -> None:
    result = KernelSerializer.to_dict(request_obj)

    assert isinstance(result, dict)
    assert result["query"] == "hello world"
    assert result["inputs"]["temperature"] == 25
    assert result["metadata"]["source"] == "test"


def test_to_dict_context(
    context: CognitiveContext,
) -> None:
    result = KernelSerializer.to_dict(context)

    assert isinstance(result, dict)
    assert "request" in result
    assert result["state"]["result"] == "processed"
    assert result["metadata"]["stage"] == "test"
    assert result["trace"] == [
        "stage_a",
        "stage_b",
    ]


def test_to_dict_response(
    response: CognitiveResponse,
) -> None:
    result = KernelSerializer.to_dict(response)

    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert "context" in result


def test_to_dict_rejects_unsupported_object() -> None:
    with pytest.raises(TypeError):
        KernelSerializer.to_dict(object())


def test_to_dict_requires_dict_result() -> None:
    class InvalidObject:
        def to_dict(self):
            return "invalid"

    with pytest.raises(TypeError):
        KernelSerializer.to_dict(InvalidObject())


# ============================================================
# to_json
# ============================================================


def test_to_json_request(
    request_obj: CognitiveRequest,
) -> None:
    result = KernelSerializer.to_json(request_obj)

    assert isinstance(result, str)

    payload = json.loads(result)

    assert payload["query"] == "hello world"
    assert payload["inputs"]["pressure"] == 1.0


def test_to_json_context(
    context: CognitiveContext,
) -> None:
    result = KernelSerializer.to_json(context)

    payload = json.loads(result)

    assert payload["state"]["result"] == "processed"
    assert payload["trace"] == [
        "stage_a",
        "stage_b",
    ]


def test_to_json_response(
    response: CognitiveResponse,
) -> None:
    result = KernelSerializer.to_json(response)

    payload = json.loads(result)

    assert payload["status"] == "success"
    assert "context" in payload


def test_to_json_produces_pretty_json(
    request_obj: CognitiveRequest,
) -> None:
    result = KernelSerializer.to_json(request_obj)

    assert "\n" in result
    assert "  " in result


def test_to_json_preserves_unicode() -> None:
    request_obj = CognitiveRequest(
        query="Xin chào Việt Nam",
    )

    result = KernelSerializer.to_json(request_obj)

    assert "Xin chào Việt Nam" in result


# ============================================================
# from_json_request
# ============================================================


def test_from_json_request(
    request_obj: CognitiveRequest,
) -> None:
    data = KernelSerializer.to_json(request_obj)

    result = KernelSerializer.from_json_request(data)

    assert isinstance(result, CognitiveRequest)
    assert result.query == request_obj.query
    assert result.inputs == request_obj.inputs
    assert result.metadata == request_obj.metadata


def test_from_json_request_preserves_request_id(
    request_obj: CognitiveRequest,
) -> None:
    data = KernelSerializer.to_json(request_obj)

    result = KernelSerializer.from_json_request(data)

    assert result.request_id == request_obj.request_id


def test_from_json_request_rejects_non_string() -> None:
    with pytest.raises(TypeError):
        KernelSerializer.from_json_request({})  # type: ignore[arg-type]


def test_from_json_request_rejects_non_object_json() -> None:
    with pytest.raises(TypeError):
        KernelSerializer.from_json_request("[]")


def test_from_json_request_invalid_json() -> None:
    with pytest.raises(json.JSONDecodeError):
        KernelSerializer.from_json_request("{invalid json}")


def test_from_json_request_requires_query() -> None:
    data = json.dumps(
        {
            "request_id": "test",
        }
    )

    with pytest.raises(KeyError):
        KernelSerializer.from_json_request(data)


def test_from_json_request_requires_request_id() -> None:
    data = json.dumps(
        {
            "query": "hello",
        }
    )

    with pytest.raises(KeyError):
        KernelSerializer.from_json_request(data)


# ============================================================
# from_json_response
# ============================================================


def test_from_json_response(
    response: CognitiveResponse,
) -> None:
    data = KernelSerializer.to_json(response)

    result = KernelSerializer.from_json_response(data)

    assert isinstance(result, CognitiveResponse)
    assert result.status == response.status


def test_from_json_response_restores_context(
    response: CognitiveResponse,
) -> None:
    data = KernelSerializer.to_json(response)

    result = KernelSerializer.from_json_response(data)

    assert result.context.state == {
        "result": "processed",
    }

    assert result.context.metadata == {
        "stage": "test",
    }

    assert result.context.trace == [
        "stage_a",
        "stage_b",
    ]


def test_from_json_response_restores_request(
    response: CognitiveResponse,
) -> None:
    data = KernelSerializer.to_json(response)

    result = KernelSerializer.from_json_response(data)

    assert result.context.request.query == "hello world"
    assert result.context.request.inputs == {
        "temperature": 25,
        "pressure": 1.0,
    }


def test_from_json_response_restores_errors_and_warnings() -> None:
    request_obj = CognitiveRequest(
        query="test",
    )

    context = CognitiveContext(request_obj)

    response = CognitiveResponse(
        status="error",
        context=context,
        errors=["failure"],
        warnings=["warning"],
        metadata={
            "source": "test",
        },
    )

    data = KernelSerializer.to_json(response)

    result = KernelSerializer.from_json_response(data)

    assert result.errors == ["failure"]
    assert result.warnings == ["warning"]
    assert result.metadata == {
        "source": "test",
    }


def test_from_json_response_rejects_non_string() -> None:
    with pytest.raises(TypeError):
        KernelSerializer.from_json_response({})  # type: ignore[arg-type]


def test_from_json_response_rejects_non_object_json() -> None:
    with pytest.raises(TypeError):
        KernelSerializer.from_json_response("[]")


def test_from_json_response_requires_context() -> None:
    data = json.dumps(
        {
            "status": "success",
        }
    )

    with pytest.raises(KeyError):
        KernelSerializer.from_json_response(data)


def test_from_json_response_requires_status() -> None:
    data = json.dumps(
        {
            "context": {},
        }
    )

    with pytest.raises(KeyError):
        KernelSerializer.from_json_response(data)


# ============================================================
# Round-trip contracts
# ============================================================


def test_request_json_round_trip(
    request_obj: CognitiveRequest,
) -> None:
    serialized = KernelSerializer.to_json(request_obj)
    restored = KernelSerializer.from_json_request(serialized)

    assert restored.query == request_obj.query
    assert restored.inputs == request_obj.inputs
    assert restored.metadata == request_obj.metadata
    assert restored.request_id == request_obj.request_id


def test_response_json_round_trip(
    response: CognitiveResponse,
) -> None:
    serialized = KernelSerializer.to_json(response)
    restored = KernelSerializer.from_json_response(serialized)

    assert restored.status == response.status
    assert restored.context.state == response.context.state
    assert restored.context.metadata == response.context.metadata
    assert restored.context.trace == response.context.trace
    assert restored.context.request.query == (
        response.context.request.query
    )