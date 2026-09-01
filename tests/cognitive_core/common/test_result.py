from scios.cognitive_core.common.result import CognitiveResult


def test_result_initialization():
    result = CognitiveResult("planner")

    assert result.stage == "planner"
    assert result.data == {}
    assert result.messages == []
    assert result.errors == []
    assert result.success is True


def test_add_data():
    result = CognitiveResult("planner")

    result.add_data("plan", {"steps": ["a", "b"]})

    assert result.data["plan"] == {"steps": ["a", "b"]}
    assert result["plan"] == {"steps": ["a", "b"]}
    assert "plan" in result


def test_add_multiple_data():
    result = CognitiveResult("planner")

    result.add_data("a", 1)
    result.add_data("b", 2)

    assert result.data == {
        "a": 1,
        "b": 2,
    }


def test_add_data_overwrites_existing_key():
    result = CognitiveResult("planner")

    result.add_data("value", 1)
    result.add_data("value", 2)

    assert result["value"] == 2


def test_add_message():
    result = CognitiveResult("reasoning")

    result.add_message("Reasoning started.")

    assert result.messages == ["Reasoning started."]
    assert result.success is True


def test_add_multiple_messages():
    result = CognitiveResult("reasoning")

    result.add_message("Step 1")
    result.add_message("Step 2")

    assert result.messages == [
        "Step 1",
        "Step 2",
    ]


def test_add_error_marks_result_unsuccessful():
    result = CognitiveResult("tool")

    result.add_error("Tool execution failed.")

    assert result.errors == ["Tool execution failed."]
    assert result.success is False


def test_add_multiple_errors():
    result = CognitiveResult("tool")

    result.add_error("Error 1")
    result.add_error("Error 2")

    assert result.errors == [
        "Error 1",
        "Error 2",
    ]
    assert result.success is False


def test_error_does_not_remove_existing_data():
    result = CognitiveResult("planner")

    result.add_data("plan", {"steps": 3})
    result.add_error("Planning failed.")

    assert result["plan"] == {"steps": 3}
    assert result.success is False


def test_getitem():
    result = CognitiveResult("planner")

    result.add_data("answer", 42)

    assert result["answer"] == 42


def test_getitem_missing_key_raises_key_error():
    result = CognitiveResult("planner")

    try:
        result["missing"]
        assert False
    except KeyError:
        pass


def test_contains():
    result = CognitiveResult("planner")

    result.add_data("answer", 42)

    assert "answer" in result
    assert "missing" not in result


def test_iter():
    result = CognitiveResult("planner")

    result.add_data("a", 1)
    result.add_data("b", 2)

    assert list(result) == ["a", "b"]


def test_items():
    result = CognitiveResult("planner")

    result.add_data("a", 1)
    result.add_data("b", 2)

    assert list(result.items()) == [
        ("a", 1),
        ("b", 2),
    ]


def test_keys():
    result = CognitiveResult("planner")

    result.add_data("a", 1)
    result.add_data("b", 2)

    assert list(result.keys()) == [
        "a",
        "b",
    ]


def test_values():
    result = CognitiveResult("planner")

    result.add_data("a", 1)
    result.add_data("b", 2)

    assert list(result.values()) == [
        1,
        2,
    ]


def test_repr_contains_stage():
    result = CognitiveResult("reasoning")

    representation = repr(result)

    assert "CognitiveResult" in representation
    assert "reasoning" in representation


def test_repr_contains_success_state():
    result = CognitiveResult("reasoning")

    representation = repr(result)

    assert "success=True" in representation


def test_repr_reflects_failure():
    result = CognitiveResult("reasoning")

    result.add_error("failure")

    representation = repr(result)

    assert "success=False" in representation


def test_data_is_independent_between_instances():
    first = CognitiveResult("planner")
    second = CognitiveResult("planner")

    first.add_data("value", 1)

    assert first.data == {"value": 1}
    assert second.data == {}


def test_messages_are_independent_between_instances():
    first = CognitiveResult("planner")
    second = CognitiveResult("planner")

    first.add_message("message")

    assert first.messages == ["message"]
    assert second.messages == []


def test_errors_are_independent_between_instances():
    first = CognitiveResult("planner")
    second = CognitiveResult("planner")

    first.add_error("error")

    assert first.errors == ["error"]
    assert second.errors == []
    assert second.success is True


def test_result_supports_mixed_operations():
    result = CognitiveResult("pipeline")

    result.add_data("input", 10)
    result.add_message("started")
    result.add_data("output", 20)
    result.add_message("completed")

    assert result.stage == "pipeline"
    assert result.data == {
        "input": 10,
        "output": 20,
    }
    assert result.messages == [
        "started",
        "completed",
    ]
    assert result.errors == []
    assert result.success is True