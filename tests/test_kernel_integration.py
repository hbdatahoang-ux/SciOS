import pytest
from scios.kernel.plugins import PluginManager, PluginState


# ----------------------------------------------------------------------
# Dummy Plugin
# ----------------------------------------------------------------------

class DummyPlugin:
    def __init__(self, name="demo", version="1.0"):
        self.name = name
        self.version = version
        self.initialized = False
        self.shutdown_called = False

    def initialize(self, kernel=None):
        self.initialized = True

    def shutdown(self):
        self.shutdown_called = True


# ----------------------------------------------------------------------
# Phase A — Registration
# ----------------------------------------------------------------------

def test_register_and_get_plugin():
    manager = PluginManager()
    plugin = DummyPlugin()
    manager.register(plugin)

    info = manager.get(plugin.name)
    assert info.name == "demo"
    assert info.version == "1.0"
    assert info.state == PluginState.REGISTERED
    assert info.instance is plugin


def test_unregister_plugin():
    manager = PluginManager()
    plugin = DummyPlugin()
    manager.register(plugin)

    manager.unregister(plugin.name)
    assert not manager.contains(plugin.name)


# ----------------------------------------------------------------------
# Phase B — Lifecycle
# ----------------------------------------------------------------------

def test_enable_disable_plugin():
    manager = PluginManager()
    plugin = DummyPlugin()
    manager.register(plugin)

    manager.enable(plugin.name)
    assert manager.get(plugin.name).state == PluginState.ENABLED

    manager.disable(plugin.name)
    assert manager.get(plugin.name).state == PluginState.DISABLED


def test_initialize_and_shutdown_all():
    manager = PluginManager()
    plugin = DummyPlugin()
    manager.register(plugin)

    manager.initialize_all(kernel=None)
    assert plugin.initialized
    assert manager.get(plugin.name).state == PluginState.ENABLED

    manager.shutdown_all()
    assert plugin.shutdown_called
    assert manager.get(plugin.name).state == PluginState.DISABLED


# ----------------------------------------------------------------------
# Phase C — Inspection
# ----------------------------------------------------------------------

def test_names_and_count():
    manager = PluginManager()
    p1 = DummyPlugin(name="p1")
    p2 = DummyPlugin(name="p2")
    manager.register(p1)
    manager.register(p2)

    names = manager.names()
    assert "p1" in names and "p2" in names
    assert manager.count() == 2
    assert len(manager) == 2
