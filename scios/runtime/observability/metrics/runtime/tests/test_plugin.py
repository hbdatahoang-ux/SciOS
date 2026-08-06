"""
Tests for runtime.plugin
"""

# ==============================================================================
# Part 1. Imports
# ==============================================================================

import json

import pytest

from scios.runtime.observability.metrics.runtime.plugin import (
    DEFAULT_ENABLED,
    DEFAULT_NAME,
    RuntimePlugin,
)


# ==============================================================================
# Part 2. Helpers
# ==============================================================================


def create_plugin() -> RuntimePlugin:

    plugin = RuntimePlugin(
        name="demo",
    )

    plugin.set_config(
        "interval",
        1.0,
    )

    plugin.hooks["startup"] = lambda: None

    return plugin


# ==============================================================================
# Part 3. Constructor
# ==============================================================================


def test_default_constructor():

    plugin = RuntimePlugin()

    assert plugin.name == DEFAULT_NAME
    assert plugin.enabled is DEFAULT_ENABLED
    assert plugin.state == "idle"
    assert plugin.config == {}
    assert plugin.hooks == {}


def test_custom_constructor():

    plugin = RuntimePlugin(
        name="collector",
        enabled=False,
    )

    assert plugin.name == "collector"
    assert plugin.enabled is False
    assert plugin.state == "idle"


def test_slots():

    plugin = RuntimePlugin()

    assert hasattr(
        RuntimePlugin,
        "__slots__",
    )

    with pytest.raises(AttributeError):
        plugin.random = 123


# ==============================================================================
# Part 4. Properties
# ==============================================================================


def test_properties():

    plugin = create_plugin()

    assert plugin.name == "demo"
    assert plugin.enabled is True
    assert plugin.state == "idle"
    assert isinstance(plugin.config, dict)
    assert isinstance(plugin.hooks, dict)


def test_name_property():

    plugin = create_plugin()

    assert plugin.name == "demo"


def test_enabled_property():

    plugin = create_plugin()

    assert plugin.enabled is True


def test_state_property():

    plugin = create_plugin()

    assert plugin.state == "idle"

    plugin.start()

    assert plugin.state == "running"

    plugin.stop()

    assert plugin.state == "stopped"


def test_config_property():

    plugin = create_plugin()

    assert plugin.config["interval"] == 1.0


def test_hooks_property():

    plugin = create_plugin()

    assert "startup" in plugin.hooks


# ==============================================================================
# Part 5. Lifecycle
# ==============================================================================


def test_enable():

    plugin = RuntimePlugin(
        enabled=False,
    )

    plugin.enable()

    assert plugin.enabled is True


def test_disable():

    plugin = RuntimePlugin()

    plugin.disable()

    assert plugin.enabled is False


def test_start():

    plugin = create_plugin()

    plugin.start()

    assert plugin.state == "running"


def test_stop():

    plugin = create_plugin()

    plugin.start()
    plugin.stop()

    assert plugin.state == "stopped"


def test_reset():

    plugin = create_plugin()

    plugin.start()
    plugin.reset()

    assert plugin.state == "idle"
    assert plugin.enabled is DEFAULT_ENABLED


def test_enable_disable():

    plugin = RuntimePlugin()

    plugin.disable()

    assert plugin.enabled is False

    plugin.enable()

    assert plugin.enabled is True


# ==============================================================================
# Part 6. Config
# ==============================================================================


def test_set_config():

    plugin = RuntimePlugin()

    plugin.set_config(
        "a",
        10,
    )

    assert plugin.config["a"] == 10


def test_get_config():

    plugin = RuntimePlugin()

    plugin.set_config(
        "x",
        5,
    )

    assert plugin.get_config("x") == 5
    assert plugin.get_config("missing") is None


def test_update_config():

    plugin = RuntimePlugin()

    plugin.update_config(
        {
            "a": 1,
            "b": 2,
        }
    )

    assert plugin.config["a"] == 1
    assert plugin.config["b"] == 2


def test_clear_config():

    plugin = RuntimePlugin()

    plugin.update_config(
        {
            "a": 1,
            "b": 2,
        }
    )

    plugin.clear_config()

    assert plugin.config == {}


def test_config_copy():

    plugin = RuntimePlugin()

    plugin.set_config(
        "x",
        1,
    )

    copied = dict(plugin.config)

    copied["x"] = 999

    assert plugin.config["x"] == 1

# ==============================================================================
# Part 7. Hooks
# ==============================================================================


def test_add_hook():

    plugin = RuntimePlugin()

    fn = lambda: None

    plugin.add_hook(
        "startup",
        fn,
    )

    assert plugin.has_hook("startup")


def test_remove_hook():

    plugin = RuntimePlugin()

    fn = lambda: None

    plugin.add_hook(
        "startup",
        fn,
    )

    plugin.remove_hook("startup")

    assert not plugin.has_hook("startup")


def test_has_hook():

    plugin = RuntimePlugin()

    fn = lambda: None

    plugin.add_hook(
        "startup",
        fn,
    )

    assert plugin.has_hook("startup")
    assert not plugin.has_hook("shutdown")


def test_list_hooks():

    plugin = RuntimePlugin()

    plugin.add_hook(
        "a",
        lambda: None,
    )

    plugin.add_hook(
        "b",
        lambda: None,
    )

    assert plugin.list_hooks() == [
        "a",
        "b",
    ]


def test_clear_hooks():

    plugin = RuntimePlugin()

    plugin.add_hook(
        "a",
        lambda: None,
    )

    plugin.clear_hooks()

    assert plugin.hooks == {}


def test_execute_hook():

    plugin = RuntimePlugin()

    executed = []

    def callback():

        executed.append(True)

    plugin.add_hook(
        "run",
        callback,
    )

    plugin.execute_hook("run")

    assert executed == [True]


# ==============================================================================
# Part 8. Operations
# ==============================================================================


def test_clone():

    plugin = create_plugin()

    cloned = plugin.clone()

    assert cloned == plugin
    assert cloned is not plugin


def test_copy():

    plugin = create_plugin()

    copied = plugin.copy()

    assert copied == plugin
    assert copied is not plugin


def test_merge():

    a = RuntimePlugin()

    b = RuntimePlugin()

    b.set_config(
        "interval",
        5,
    )

    a.merge(b)

    assert a.get_config("interval") == 5


def test_update():

    plugin = RuntimePlugin()

    plugin.update(
        {
            "interval": 2,
        }
    )

    assert plugin.get_config("interval") == 2


def test_snapshot():

    plugin = create_plugin()

    snapshot = plugin.snapshot()

    assert snapshot == plugin.to_dict()


def test_restore():

    plugin = RuntimePlugin()

    plugin.restore(
        create_plugin().snapshot()
    )

    assert plugin.name == "demo"
    assert plugin.get_config("interval") == 1.0


# ==============================================================================
# Part 9. Validation
# ==============================================================================


def test_validate_name():

    plugin = RuntimePlugin()

    assert plugin.validate_name()


def test_validate_config():

    plugin = RuntimePlugin()

    assert plugin.validate_config()


def test_validate_hooks():

    plugin = RuntimePlugin()

    assert plugin.validate_hooks()


def test_validate():

    plugin = RuntimePlugin()

    assert plugin.validate()


def test_normalize():

    plugin = RuntimePlugin(
        name=" demo "
    )

    plugin.normalize()

    assert plugin.name == "demo"


# ==============================================================================
# Part 10. Serialization
# ==============================================================================


def test_to_dict():

    plugin = create_plugin()

    data = plugin.to_dict()

    assert data["name"] == "demo"


def test_from_dict():

    plugin = RuntimePlugin.from_dict(
        create_plugin().to_dict()
    )

    assert plugin.name == "demo"


def test_to_tuple():

    plugin = create_plugin()

    assert isinstance(
        plugin.to_tuple(),
        tuple,
    )


def test_from_tuple():

    plugin = RuntimePlugin.from_tuple(
        create_plugin().to_tuple()
    )

    assert plugin.name == "demo"


def test_to_json():

    plugin = create_plugin()

    data = json.loads(
        plugin.to_json()
    )

    assert data["name"] == "demo"


def test_from_json():

    plugin = RuntimePlugin.from_json(
        create_plugin().to_json()
    )

    assert plugin.name == "demo"


# ==============================================================================
# Part 11. Diagnostics
# ==============================================================================


def test_summary():

    plugin = create_plugin()

    assert isinstance(
        plugin.summary(),
        dict,
    )


def test_diagnostics():

    plugin = create_plugin()

    assert isinstance(
        plugin.diagnostics(),
        dict,
    )


def test_report():

    plugin = create_plugin()

    assert isinstance(
        plugin.report(),
        dict,
    )


def test_status():

    plugin = RuntimePlugin()

    assert plugin.status() == "idle"

    plugin.start()

    assert plugin.status() == "running"


# ==============================================================================
# Part 12. Protocols
# ==============================================================================


def test_len():

    plugin = RuntimePlugin()

    plugin.set_config(
        "x",
        1,
    )

    assert len(plugin) == 1


def test_contains():

    plugin = RuntimePlugin()

    plugin.set_config(
        "x",
        1,
    )

    assert "x" in plugin


def test_iter():

    plugin = RuntimePlugin()

    plugin.set_config(
        "x",
        1,
    )

    assert list(iter(plugin))


def test_hash():

    plugin = RuntimePlugin()

    assert isinstance(
        hash(plugin),
        int,
    )


def test_eq():

    assert (
        RuntimePlugin()
        == RuntimePlugin()
    )


def test_repr():

    assert "RuntimePlugin" in repr(
        RuntimePlugin()
    )


def test_str():

    assert str(
        RuntimePlugin()
    ) == DEFAULT_NAME


def test_bool():

    assert bool(RuntimePlugin())

    plugin = RuntimePlugin(
        enabled=False,
    )

    assert not bool(plugin)    