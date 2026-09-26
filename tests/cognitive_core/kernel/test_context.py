"""
Tests for scios.cognitive_core.kernel.context
"""

from scios.cognitive_core.kernel.context import CognitiveContext
from scios.cognitive_core.kernel.request import CognitiveRequest


def make_context():
    request = CognitiveRequest(query="hello")
    return CognitiveContext(request)


def test_context_initializes_with_request():
    request = CognitiveRequest(query="hello")
    context = CognitiveContext(request)

    assert context.request is request


def test_context_initial_state_is_empty():
    context = make_context()

    assert context.state == {}


def test_context_initial_metadata_is_empty():
    context = make_context()

    assert context.metadata == {}


def test_context_initial_trace_is_empty():
    context = make_context()

    assert context.trace == []


def test_set_stores_value():
    context = make_context()

    context.set("answer", 42)

    assert context.state["answer"] == 42


def test_get_returns_stored_value():
    context = make_context()

    context.set("answer", 42)

    assert context.get("answer") == 42


def test_get_missing_key_returns_none():
    context = make_context()

    assert context.get("missing") is None


def test_set_appends_trace():
    context = make_context()

    context.set("answer", 42)

    assert context.trace == [{"answer": 42}]


def test_multiple_sets_append_trace_in_order():
    context = make_context()

    context.set("first", 1)
    context.set("second", 2)

    assert context.trace == [
        {"first": 1},
        {"second": 2},
    ]


def test_set_overwrites_existing_state_value():
    context = make_context()

    context.set("answer", 1)
    context.set("answer", 2)

    assert context.state["answer"] == 2


def test_overwrite_still_records_trace():
    context = make_context()

    context.set("answer", 1)
    context.set("answer", 2)

    assert context.trace == [
        {"answer": 1},
        {"answer": 2},
    ]


def test_metadata_can_be_written_directly():
    context = make_context()

    context.metadata["source"] = "test"

    assert context.metadata["source"] == "test"


def test_to_dict_contains_request():
    context = make_context()

    result = context.to_dict()

    assert "request" in result
    assert result["request"] == context.request.to_dict()


def test_to_dict_contains_state():
    context = make_context()

    context.set("answer", 42)

    result = context.to_dict()

    assert result["state"] == {"answer": 42}


def test_to_dict_contains_metadata():
    context = make_context()

    context.metadata["source"] = "test"

    result = context.to_dict()

    assert result["metadata"] == {"source": "test"}


def test_to_dict_contains_trace():
    context = make_context()

    context.set("answer", 42)

    result = context.to_dict()

    assert result["trace"] == [{"answer": 42}]


def test_to_dict_contains_all_required_keys():
    context = make_context()

    result = context.to_dict()

    assert set(result) == {
        "request",
        "state",
        "metadata",
        "trace",
    }


def test_to_dict_returns_current_state():
    context = make_context()

    context.set("a", 1)
    context.metadata["m"] = 2

    result = context.to_dict()

    assert result["state"] == {"a": 1}
    assert result["metadata"] == {"m": 2}
    assert result["trace"] == [{"a": 1}]


def test_repr_contains_class_name():
    context = make_context()

    assert "CognitiveContext" in repr(context)


def test_repr_contains_state_keys():
    context = make_context()

    context.set("answer", 42)

    result = repr(context)

    assert "answer" in result


def test_repr_empty_context():
    context = make_context()

    assert repr(context) == "<CognitiveContext state_keys=[]>"


def test_repr_multiple_state_keys():
    context = make_context()

    context.set("first", 1)
    context.set("second", 2)

    result = repr(context)

    assert "first" in result
    assert "second" in result


def test_context_accepts_arbitrary_value_types():
    context = make_context()

    value = {
        "items": [1, 2, 3],
        "nested": {"enabled": True},
    }

    context.set("payload", value)

    assert context.get("payload") == value


def test_context_preserves_request_identity():
    request = CognitiveRequest(query="test")
    context = CognitiveContext(request)

    assert context.request is request


def test_to_dict_reflects_changes_after_initial_call():
    context = make_context()

    first = context.to_dict()

    context.set("answer", 42)

    second = context.to_dict()

    assert first["state"] == {}
    assert second["state"] == {"answer": 42}
