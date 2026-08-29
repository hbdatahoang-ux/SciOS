"""
ToolPolicy tests
================

Contract tests for SciOS Runtime ToolPolicy.

Covered contracts:
- default state
- enable / disable
- allow / deny tools
- tool access rules
- permissions
- execution limits
- call accounting
- validation
- compatibility API
- diagnostics
- serialization
"""


from scios.runtime.tools import ToolPolicy


# ==========================================================
# Construction
# ==========================================================


def test_default_policy():

    policy = ToolPolicy()

    assert policy.enabled is True
    assert policy.allowed_tools is None
    assert policy.denied_tools == set()
    assert policy.permissions == set()
    assert policy.max_calls is None
    assert policy.timeout_seconds == 30.0
    assert policy.calls == 0
    assert policy.remaining_calls is None
    assert policy.metadata == {}


# ==========================================================
# Enable / Disable
# ==========================================================


def test_disable_policy():

    policy = ToolPolicy()

    policy.disable()

    assert policy.enabled is False


def test_enable_policy():

    policy = ToolPolicy()

    policy.disable()
    policy.enable()

    assert policy.enabled is True


def test_disabled_policy_denies_execution():

    policy = ToolPolicy()

    policy.disable()

    assert policy.can_execute(
        "echo"
    ) is False

    assert policy.validate(
        "echo"
    ) is False


# ==========================================================
# Tool Access
# ==========================================================


def test_default_policy_allows_any_tool():

    policy = ToolPolicy()

    assert policy.can_execute(
        "echo"
    ) is True

    assert policy.can_execute(
        "calculator"
    ) is True


def test_allow_tool_creates_allow_list():

    policy = ToolPolicy()

    policy.allow_tool(
        "echo"
    )

    assert policy.allowed_tools == {
        "echo"
    }

    assert policy.can_execute(
        "echo"
    ) is True

    assert policy.can_execute(
        "calculator"
    ) is False


def test_allow_multiple_tools():

    policy = ToolPolicy()

    policy.allow_tool("echo")
    policy.allow_tool("calculator")

    assert policy.can_execute(
        "echo"
    ) is True

    assert policy.can_execute(
        "calculator"
    ) is True

    assert policy.can_execute(
        "unknown"
    ) is False


def test_deny_tool():

    policy = ToolPolicy()

    policy.deny_tool(
        "echo"
    )

    assert "echo" in policy.denied_tools

    assert policy.can_execute(
        "echo"
    ) is False


def test_deny_overrides_allow():

    policy = ToolPolicy()

    policy.allow_tool(
        "echo"
    )

    policy.deny_tool(
        "echo"
    )

    assert "echo" not in policy.allowed_tools
    assert "echo" in policy.denied_tools

    assert policy.can_execute(
        "echo"
    ) is False


def test_deny_unknown_tool_without_allow_list():

    policy = ToolPolicy()

    policy.deny_tool(
        "echo"
    )

    assert policy.can_execute(
        "echo"
    ) is False

    assert policy.can_execute(
        "calculator"
    ) is True


# ==========================================================
# Permissions
# ==========================================================


def test_default_has_no_permissions():

    policy = ToolPolicy()

    assert policy.has_permission(
        "read"
    ) is False


def test_grant_permission():

    policy = ToolPolicy()

    policy.grant(
        "read"
    )

    assert policy.has_permission(
        "read"
    ) is True

    assert "read" in policy.permissions


def test_grant_multiple_permissions():

    policy = ToolPolicy()

    policy.grant("read")
    policy.grant("write")

    assert policy.permissions == {
        "read",
        "write",
    }


def test_revoke_permission():

    policy = ToolPolicy()

    policy.grant(
        "read"
    )

    policy.revoke(
        "read"
    )

    assert policy.has_permission(
        "read"
    ) is False


def test_revoke_unknown_permission():

    policy = ToolPolicy()

    policy.revoke(
        "unknown"
    )

    assert policy.permissions == set()


# ==========================================================
# Validation
# ==========================================================


def test_validate_allowed_tool():

    policy = ToolPolicy()

    assert policy.validate(
        "echo"
    ) is True


def test_validate_denied_tool():

    policy = ToolPolicy()

    policy.deny_tool(
        "echo"
    )

    assert policy.validate(
        "echo"
    ) is False


def test_validate_required_permission():

    policy = ToolPolicy()

    policy.grant(
        "read"
    )

    assert policy.validate(
        "echo",
        permission="read",
    ) is True


def test_validate_missing_permission():

    policy = ToolPolicy()

    assert policy.validate(
        "echo",
        permission="read",
    ) is False


def test_validate_without_permission_requirement():

    policy = ToolPolicy()

    assert policy.validate(
        "echo"
    ) is True


# ==========================================================
# Compatibility API
# ==========================================================


def test_allow_check():

    policy = ToolPolicy()

    assert policy.allow(
        "echo"
    ) is True


def test_allow_respects_denied_tools():

    policy = ToolPolicy()

    policy.deny_tool(
        "echo"
    )

    assert policy.allow(
        "echo"
    ) is False


def test_allow_respects_disabled_policy():

    policy = ToolPolicy()

    policy.disable()

    assert policy.allow(
        "echo"
    ) is False


# ==========================================================
# Execution Limits
# ==========================================================


def test_unlimited_calls_by_default():

    policy = ToolPolicy()

    assert policy.check_limit() is True
    assert policy.remaining_calls is None


def test_max_calls():

    policy = ToolPolicy(
        max_calls=3
    )

    assert policy.check_limit() is True
    assert policy.remaining_calls == 3


def test_record_call():

    policy = ToolPolicy(
        max_calls=3
    )

    policy.record_call()

    assert policy.calls == 1
    assert policy.remaining_calls == 2


def test_max_calls_blocks_after_limit():

    policy = ToolPolicy(
        max_calls=2
    )

    policy.record_call()
    policy.record_call()

    assert policy.calls == 2
    assert policy.remaining_calls == 0
    assert policy.check_limit() is False


def test_validate_respects_max_calls():

    policy = ToolPolicy(
        max_calls=1
    )

    assert policy.validate(
        "echo"
    ) is True

    policy.record_call()

    assert policy.validate(
        "echo"
    ) is False


def test_reset_calls():

    policy = ToolPolicy(
        max_calls=3
    )

    policy.record_call()
    policy.record_call()

    assert policy.calls == 2

    policy.reset_calls()

    assert policy.calls == 0
    assert policy.remaining_calls == 3
    assert policy.check_limit() is True


# ==========================================================
# Diagnostics
# ==========================================================


def test_status():

    policy = ToolPolicy(
        allowed_tools={"echo"},
        denied_tools={"blocked"},
        permissions={"read"},
        max_calls=5,
        timeout_seconds=10.0,
    )

    policy.record_call()

    status = policy.status()

    assert status["enabled"] is True
    assert status["calls"] == 1
    assert status["remaining_calls"] == 4
    assert status["timeout_seconds"] == 10.0
    assert status["allowed_tools"] == ["echo"]
    assert status["denied_tools"] == ["blocked"]


def test_status_unrestricted_tools():

    policy = ToolPolicy()

    status = policy.status()

    assert status["allowed_tools"] is None
    assert status["denied_tools"] == []


# ==========================================================
# Serialization
# ==========================================================


def test_to_dict():

    policy = ToolPolicy(
        allowed_tools={"echo"},
        denied_tools={"blocked"},
        permissions={"read"},
        max_calls=5,
        timeout_seconds=10.0,
        metadata={"source": "test"},
    )

    policy.record_call()

    data = policy.to_dict()

    assert data["enabled"] is True
    assert data["calls"] == 1
    assert data["remaining_calls"] == 4
    assert data["timeout_seconds"] == 10.0
    assert data["allowed_tools"] == ["echo"]
    assert data["denied_tools"] == ["blocked"]
    assert data["permissions"] == ["read"]
    assert data["max_calls"] == 5
    assert data["metadata"] == {
        "source": "test"
    }


# ==========================================================
# Representation
# ==========================================================


def test_repr():

    policy = ToolPolicy()

    representation = repr(
        policy
    )

    assert "ToolPolicy" in representation
    assert "enabled=True" in representation
    assert "calls=0" in representation