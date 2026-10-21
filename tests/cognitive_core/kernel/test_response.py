"""
Tests for scios.cognitive_core.kernel.response.
"""

from scios.cognitive_core.kernel.context import CognitiveContext
from scios.cognitive_core.kernel.request import CognitiveRequest
from scios.cognitive_core.kernel.response import CognitiveResponse


def make_context() -> CognitiveContext:
    request = CognitiveRequest(query="hello")
    return CognitiveContext(request)


def test_response_can_be_created():
    context = make_context()

    response = CognitiveResponse(
        status="success",
        context=context,
    )

    assert response.status == "success"
    assert response.context is context


def test_errors_default_to_empty_list():
    response = CognitiveResponse(
        status="success",
        context=make_context(),
    )

    assert response.errors == []


def test_warnings_default_to_empty_list():
    response = CognitiveResponse(
        status="success",
        context=make_context(),
    )

    assert response.warnings == []


def test_metadata_defaults_to_empty_dict():
    response = CognitiveResponse(
        status="success",
        context=make_context(),
    )

    assert response.metadata == {}


def test_errors_are_not_shared_between_instances():
    first = CognitiveResponse(
        status="success",
        context=make_context(),
    )
    second = CognitiveResponse(
        status="success",
        context=make_context(),
    )

    first.errors.append("error")

    assert first.errors == ["error"]
    assert second.errors == []


def test_warnings_are_not_shared_between_instances():
    first = CognitiveResponse(
        status="success",
        context=make_context(),
    )
    second = CognitiveResponse(
        status="success",
        context=make_context(),
    )

    first.warnings.append("warning")

    assert first.warnings == ["warning"]
    assert second.warnings == []


def test_metadata_is_not_shared_between_instances():
    first = CognitiveResponse(
        status="success",
        context=make_context(),
    )
    second = CognitiveResponse(
        status="success",
        context=make_context(),
    )

    first.metadata["source"] = "test"

    assert first.metadata == {"source": "test"}
    assert second.metadata == {}


def test_from_context():
    context = make_context()

    response = CognitiveResponse.from_context(context)

    assert response.status == "success"
    assert response.context is context
    assert response.errors == []
    assert response.warnings == []
    assert response.metadata == {}


def test_from_context_accepts_custom_status():
    context = make_context()

    response = CognitiveResponse.from_context(
        context,
        status="failed",
    )

    assert response.status == "failed"
    assert response.context is context


def test_to_dict_contains_expected_keys():
    response = CognitiveResponse(
        status="success",
        context=make_context(),
    )

    result = response.to_dict()

    assert set(result) == {
        "status",
        "context",
        "errors",
        "warnings",
        "metadata",
    }


def test_to_dict_preserves_status():
    response = CognitiveResponse(
        status="failed",
        context=make_context(),
    )

    result = response.to_dict()

    assert result["status"] == "failed"


def test_to_dict_serializes_context():
    context = make_context()
    context.set("answer", "world")

    response = CognitiveResponse(
        status="success",
        context=context,
    )

    result = response.to_dict()

    assert result["context"] == context.to_dict()


def test_to_dict_preserves_errors():
    response = CognitiveResponse(
        status="failed",
        context=make_context(),
        errors=["planning failed", "tool failed"],
    )

    result = response.to_dict()

    assert result["errors"] == [
        "planning failed",
        "tool failed",
    ]


def test_to_dict_preserves_warnings():
    response = CognitiveResponse(
        status="success",
        context=make_context(),
        warnings=["slow execution"],
    )

    result = response.to_dict()

    assert result["warnings"] == [
        "slow execution",
    ]


def test_to_dict_preserves_metadata():
    response = CognitiveResponse(
        status="success",
        context=make_context(),
        metadata={
            "stage": "reasoning",
            "duration": 1.2,
        },
    )

    result = response.to_dict()

    assert result["metadata"] == {
        "stage": "reasoning",
        "duration": 1.2,
    }


def test_to_dict_returns_independent_error_list():
    response = CognitiveResponse(
        status="failed",
        context=make_context(),
        errors=["error"],
    )

    result = response.to_dict()

    result["errors"].append("another")

    assert response.errors == [
        "error",
    ]


def test_to_dict_returns_independent_warning_list():
    response = CognitiveResponse(
        status="success",
        context=make_context(),
        warnings=["warning"],
    )

    result = response.to_dict()

    result["warnings"].append("another")

    assert response.warnings == [
        "warning",
    ]


def test_to_dict_returns_independent_metadata_dict():
    response = CognitiveResponse(
        status="success",
        context=make_context(),
        metadata={"source": "test"},
    )

    result = response.to_dict()

    result["metadata"]["source"] = "changed"

    assert response.metadata == {
        "source": "test",
    }


def test_repr_contains_status():
    response = CognitiveResponse(
        status="success",
        context=make_context(),
    )

    result = repr(response)

    assert "success" in result


def test_repr_contains_error_count():
    response = CognitiveResponse(
        status="failed",
        context=make_context(),
        errors=["one", "two"],
    )

    result = repr(response)

    assert "errors=2" in result


def test_response_accepts_empty_status():
    response = CognitiveResponse(
        status="",
        context=make_context(),
    )

    assert response.status == ""


def test_response_accepts_arbitrary_status():
    response = CognitiveResponse(
        status="custom",
        context=make_context(),
    )

    assert response.status == "custom"


def test_response_context_is_preserved():
    context = make_context()

    response = CognitiveResponse(
        status="success",
        context=context,
    )

    assert response.context is context


def test_response_to_dict_contains_context_state():
    context = make_context()
    context.set("result", 42)

    response = CognitiveResponse(
        status="success",
        context=context,
    )

    result = response.to_dict()

    assert result["context"]["state"]["result"] == 42


def test_response_to_dict_contains_context_metadata():
    context = make_context()
    context.metadata["component"] = "kernel"

    response = CognitiveResponse(
        status="success",
        context=context,
    )

    result = response.to_dict()

    assert result["context"]["metadata"]["component"] == "kernel"


def test_response_to_dict_contains_context_trace():
    context = make_context()
    context.set("result", 42)

    response = CognitiveResponse(
        status="success",
        context=context,
    )

    result = response.to_dict()

    assert result["context"]["trace"] == [
        {"result": 42},
    ]
