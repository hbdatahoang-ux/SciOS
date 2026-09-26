import pytest

from scios.cognitive_core.tool_use.request import ToolRequest
from scios.cognitive_core.tool_use.validator import ToolValidator


@pytest.fixture
def validator():
    return ToolValidator()


def test_validator_accepts_valid_mapping(validator):
    request = {
        "tool": "calculator",
        "action": "calculate",
        "params": {"expression": "2+2"},
    }

    assert validator.validate(request) is True


def test_validator_accepts_valid_tool_request(validator):
    request = ToolRequest(
        tool="calculator",
        action="calculate",
        params={"expression": "2+2"},
    )

    assert validator.validate(request) is True


def test_validator_rejects_non_mapping_request(validator):
    assert validator.validate(None) is False
    assert validator.validate("invalid") is False
    assert validator.validate(42) is False
    assert validator.validate([]) is False


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"action": "calculate"},
        {"tool": ""},
        {"tool": "   "},
        {"tool": None},
    ],
)
def test_validator_rejects_missing_or_invalid_tool(validator, payload):
    assert validator.validate(payload) is False


@pytest.mark.parametrize(
    "payload",
    [
        {"tool": "calculator"},
        {"tool": "calculator", "action": ""},
        {"tool": "calculator", "action": "   "},
        {"tool": "calculator", "action": None},
    ],
)
def test_validator_rejects_missing_or_invalid_action(validator, payload):
    assert validator.validate(payload) is False


def test_validator_accepts_legacy_operation_mapping(validator):
    request = {
        "tool": "calculator",
        "operation": "calculate",
        "params": {"expression": "2+2"},
    }

    assert validator.validate(request) is True


def test_validator_prefers_action_over_operation(validator):
    request = {
        "tool": "calculator",
        "action": "calculate",
        "operation": "legacy",
    }

    assert validator.validate(request) is True


@pytest.mark.parametrize(
    "forbidden",
    [
        "__import__",
        "os.system",
        "subprocess",
        "eval",
        "exec",
    ],
)
def test_validator_rejects_forbidden_content(validator, forbidden):
    request = {
        "tool": "calculator",
        "action": "calculate",
        "params": {
            "expression": forbidden,
        },
    }

    assert validator.validate(request) is False


def test_validator_accepts_normal_parameters(validator):
    request = {
        "tool": "calculator",
        "action": "calculate",
        "params": {
            "a": 2,
            "b": 3,
        },
        "metadata": {
            "source": "test",
        },
    }

    assert validator.validate(request) is True


def test_validator_accepts_empty_params(validator):
    request = {
        "tool": "echo",
        "action": "say",
        "params": {},
    }

    assert validator.validate(request) is True


def test_validator_accepts_empty_metadata(validator):
    request = {
        "tool": "echo",
        "action": "say",
        "params": {
            "message": "hello",
        },
        "metadata": {},
    }

    assert validator.validate(request) is True


def test_validator_does_not_execute_request(validator):
    request = {
        "tool": "calculator",
        "action": "calculate",
        "params": {
            "expression": "2+2",
        },
    }

    result = validator.validate(request)

    assert result is True
    assert isinstance(result, bool)


def test_validator_has_no_runtime_execution_contract():
    validator = ToolValidator()

    assert not hasattr(validator, "execute")
    assert not hasattr(validator, "run")
    assert not hasattr(validator, "resolve")




