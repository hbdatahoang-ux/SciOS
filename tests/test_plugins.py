# tests/test_plugins.py

import pytest
from scios.cognitive_core.plugins.manager import PluginManager


class DummyPlugin:
    def __init__(self, name="dummy"):
        self.name = name

    def run(self, **kwargs):
        return f"Executed {self.name} with {kwargs}"


def test_plugin_manager_initialization():
    pm = PluginManager()
    assert pm.list_plugins() == []
    assert "plugins=0" in repr(pm)


def test_register_and_get_plugin():
    pm = PluginManager()
    plugin = DummyPlugin(name="alpha")
    pm.register("alpha", plugin)

    retrieved = pm.get("alpha")
    assert retrieved is plugin
    assert "alpha" in pm.list_plugins()


def test_execute_plugin_success():
    pm = PluginManager()
    plugin = DummyPlugin(name="beta")
    pm.register("beta", plugin)

    result = pm.execute("beta", param=123)
    assert "Executed beta" in result
    assert "param" in result


def test_execute_plugin_not_found():
    pm = PluginManager()
    with pytest.raises(KeyError):
        pm.execute("ghost", x=1)


def test_unregister_plugin():
    pm = PluginManager()
    plugin = DummyPlugin(name="gamma")
    pm.register("gamma", plugin)
    assert "gamma" in pm.list_plugins()

    pm.unregister("gamma")
    assert "gamma" not in pm.list_plugins()
    with pytest.raises(KeyError):
        pm.get("gamma")


def test_plugin_manager_repr_shows_count():
    pm = PluginManager()
    pm.register("delta", DummyPlugin(name="delta"))
    repr_str = repr(pm)
    assert "plugins=1" in repr_str
