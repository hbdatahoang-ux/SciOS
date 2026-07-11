"""
SciOS Runtime Plugin Tests
==========================

Validate RuntimePlugin lifecycle.

Tests
-----
- install()
- uninstall()
- start()
- stop()
- add_handle()
- handles
- status()
- __len__()
- __bool__()
- __repr__()
"""

from __future__ import annotations

from scios.runtime.engine import ExecutionEngine
from scios.runtime.plugin import RuntimePlugin


# ==========================================================
# Dummy Plugin
# ==========================================================


class DummyPlugin(RuntimePlugin):

    name = "dummy"

    version = "1.0"

    description = "Dummy Runtime Plugin"

    def install(self) -> None:

        handle = self.engine.hooks.register(
            "before_execute",
            lambda ctx: None,
        )

        self.add_handle(handle)


# ==========================================================
# Construction
# ==========================================================


def test_plugin_construct() -> None:

    engine = ExecutionEngine()

    plugin = DummyPlugin(engine)

    assert plugin.engine is engine

    assert plugin.installed is False

    assert plugin.running is False

    assert len(plugin) == 0


# ==========================================================
# Install
# ==========================================================


def test_install() -> None:

    engine = ExecutionEngine()

    plugin = DummyPlugin(engine)

    plugin.install()

    assert plugin.installed is True

    assert len(plugin.handles) == 1

    assert len(plugin) == 1


# ==========================================================
# Start
# ==========================================================


def test_start() -> None:

    engine = ExecutionEngine()

    plugin = DummyPlugin(engine)

    plugin.install()

    plugin.start()

    assert plugin.running is True

    assert bool(plugin) is True


# ==========================================================
# Stop
# ==========================================================


def test_stop() -> None:

    engine = ExecutionEngine()

    plugin = DummyPlugin(engine)

    plugin.install()

    plugin.start()

    plugin.stop()

    assert plugin.running is False

    assert bool(plugin) is False


# ==========================================================
# Uninstall
# ==========================================================


def test_uninstall() -> None:

    engine = ExecutionEngine()

    plugin = DummyPlugin(engine)

    plugin.install()

    plugin.uninstall()

    assert plugin.installed is False

    assert plugin.running is False

    assert len(plugin.handles) == 0

    assert len(plugin) == 0


# ==========================================================
# Handles
# ==========================================================


def test_handles_property() -> None:

    engine = ExecutionEngine()

    plugin = DummyPlugin(engine)

    plugin.install()

    handles = plugin.handles

    assert isinstance(handles, tuple)

    assert len(handles) == 1


# ==========================================================
# Status
# ==========================================================


def test_status() -> None:

    engine = ExecutionEngine()

    plugin = DummyPlugin(engine)

    plugin.install()

    status = plugin.status()

    assert status["name"] == "dummy"

    assert status["version"] == "1.0"

    assert status["installed"] is True

    assert status["hooks"] == 1


# ==========================================================
# Clear Handles
# ==========================================================


def test_clear_handles() -> None:

    engine = ExecutionEngine()

    plugin = DummyPlugin(engine)

    plugin.install()

    plugin.clear_handles()

    assert len(plugin.handles) == 0

    assert len(plugin) == 0


# ==========================================================
# Bool
# ==========================================================


def test_bool() -> None:

    engine = ExecutionEngine()

    plugin = DummyPlugin(engine)

    assert bool(plugin) is False

    plugin.install()

    plugin.start()

    assert bool(plugin) is True


# ==========================================================
# Repr
# ==========================================================


def test_repr() -> None:

    engine = ExecutionEngine()

    plugin = DummyPlugin(engine)

    text = repr(plugin)

    assert "DummyPlugin" in text

    assert "dummy" in text


# ==========================================================
# Multiple Install
# ==========================================================


def test_multiple_install() -> None:

    engine = ExecutionEngine()

    plugin = DummyPlugin(engine)

    plugin.install()

    plugin.install()

    assert len(plugin.handles) == 2


# ==========================================================
# Metadata
# ==========================================================


def test_metadata() -> None:

    engine = ExecutionEngine()

    plugin = DummyPlugin(engine)

    assert plugin.name == "dummy"

    assert plugin.version == "1.0"

    assert plugin.description == "Dummy Runtime Plugin"