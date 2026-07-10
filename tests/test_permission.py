# tests/test_permission.py

import pytest
from scios.cognitive_core.tool_use.permission import PermissionManager


def test_permission_grant_and_check():
    pm = PermissionManager()
    pm.grant("filesystem", "read")

    assert pm.check("filesystem", "read") is True
    assert pm.check("filesystem", "write") is False


def test_permission_revoke():
    pm = PermissionManager()
    pm.grant("network", "access")
    assert pm.check("network", "access") is True

    pm.revoke("network", "access")
    assert pm.check("network", "access") is False


def test_permission_multiple_actions():
    pm = PermissionManager()
    pm.grant("database", "read")
    pm.grant("database", "write")

    assert pm.check("database", "read") is True
    assert pm.check("database", "write") is True

    pm.revoke("database", "read")
    assert pm.check("database", "read") is False
    assert pm.check("database", "write") is True


def test_permission_list_permissions():
    pm = PermissionManager()
    pm.grant("api", "call")
    pm.grant("api", "delete")

    perms = pm.list_permissions("api")
    assert "call" in perms
    assert "delete" in perms
    assert len(perms) == 2


def test_permission_clear_all():
    pm = PermissionManager()
    pm.grant("toolA", "run")
    pm.grant("toolB", "execute")

    pm.clear()
    assert pm.check("toolA", "run") is False
    assert pm.check("toolB", "execute") is False
