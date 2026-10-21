"""
SciOS Runtime Metrics Plugin

Runtime plugin abstraction for the metrics runtime.

Python 3.11+
"""

# ==============================================================================
# Part 1. Header
# ==============================================================================

from __future__ import annotations

from typing import Any, TypeAlias


# ==============================================================================
# Part 2. Constants
# ==============================================================================

DEFAULT_NAME: str = "plugin"

DEFAULT_VERSION: str = "1.0.0"

DEFAULT_ENABLED: bool = True

DEFAULT_STARTED: bool = False

DEFAULT_PRIORITY: int = 0


__all__ = [
    "DEFAULT_NAME",
    "DEFAULT_VERSION",
    "DEFAULT_ENABLED",
    "DEFAULT_STARTED",
    "DEFAULT_PRIORITY",
    "PluginConfig",
    "PluginState",
    "RuntimePlugin",
]


# ==============================================================================
# Part 3. Type Aliases
# ==============================================================================

PluginConfig: TypeAlias = dict[str, Any]

PluginState: TypeAlias = dict[str, Any]


# ==============================================================================
# Part 4. RuntimePlugin
# ==============================================================================


class RuntimePlugin:
    """
    Runtime metrics plugin.
    """

    __slots__ = (
        "_name",
        "_version",
        "_enabled",
        "_state",
        "_priority",
        "_config",
        "_hooks",
    )

    def __init__(
        self,
        *,
        name: str = DEFAULT_NAME,
        version: str = DEFAULT_VERSION,
        enabled: bool = DEFAULT_ENABLED,
        priority: int = DEFAULT_PRIORITY,
        config: PluginConfig | None = None,
    ) -> None:

        self._name = str(name)

        self._version = str(version)

        self._enabled = bool(enabled)

        self._state = "idle"

        self._priority = int(priority)

        self._config: PluginConfig = dict(config or {})

        self._hooks: HookMap = {}

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:

        return self._name

    @property
    def version(self) -> str:

        return self._version

    @property
    def enabled(self) -> bool:

        return self._enabled

    @property
    def state(self) -> str:

        return self._state

    @property
    def started(self) -> bool:

        return self._state == "running"

    @property
    def priority(self) -> int:

        return self._priority

    @property
    def config(self) -> PluginConfig:

        return self._config

    @property
    def hooks(self) -> HookMap:

        return self._hooks


# ==============================================================================
# Part 5. Lifecycle
# ==============================================================================

    def start(self) -> None:

        self._state = "running"

    def stop(self) -> None:

        self._state = "stopped"

    def enable(self) -> None:

        self._enabled = True

    def disable(self) -> None:

        self._enabled = False

    def restart(self) -> None:

        self.stop()
        self.start()

    def reset(self) -> None:

        self._enabled = DEFAULT_ENABLED
        self._state = "idle"
        self._config.clear()
        self._hooks.clear()

# ==============================================================================
# Part 6. Config
# ==============================================================================

    def set_config(
        self,
        key: str,
        value: Any,
    ) -> None:

        self._config[str(key)] = value

    def get_config(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self._config.get(
            str(key),
            default,
        )

    def has_config(
        self,
        key: str,
    ) -> bool:

        return str(key) in self._config

    def remove_config(
        self,
        key: str,
    ) -> Any:

        return self._config.pop(
            str(key),
            None,
        )

    def clear_config(self) -> None:

        self._config.clear()

    def update_config(
        self,
        config: PluginConfig,
    ) -> None:

        self._config.update(config)


# ==============================================================================
# Part 7. Hooks
# ==============================================================================

    def add_hook(
        self,
        name: str,
        callback: Any,
    ) -> None:

        self._hooks[str(name)] = callback

    def remove_hook(
        self,
        name: str,
    ) -> Any:

        return self._hooks.pop(
            str(name),
            None,
        )

    def has_hook(
        self,
        name: str,
    ) -> bool:

        return str(name) in self._hooks

    def list_hooks(self) -> list[str]:

        return sorted(self._hooks)

    def clear_hooks(self) -> None:

        self._hooks.clear()

    def execute_hook(
        self,
        name: str,
        *args,
        **kwargs,
    ) -> Any:

        callback = self._hooks.get(str(name))

        if callback is None:
            return None

        return callback(
            *args,
            **kwargs,
        )


# ==============================================================================
# Part 8. Operations
# ==============================================================================

    def clone(self) -> "RuntimePlugin":

        return self.from_dict(
            self.to_dict()
        )

    def copy(self) -> "RuntimePlugin":

        return self.clone()

    def merge(
        self,
        other: "RuntimePlugin",
    ) -> "RuntimePlugin":

        self._config.update(
            other.config
        )

        self._enabled = other.enabled
        self._priority = other.priority

        return self

    def update(
        self,
        config: PluginConfig,
    ) -> "RuntimePlugin":

        self.update_config(config)

        return self

    def snapshot(self) -> PluginState:

        return self.to_dict()

    def restore(
        self,
        state: PluginState,
    ) -> None:

        restored = self.from_dict(state)

        self._name = restored._name
        self._version = restored._version
        self._enabled = restored._enabled
        self._state = restored._state
        self._priority = restored._priority
        self._config = dict(restored._config)
        self._hooks = dict(restored._hooks)


# ==============================================================================
# Part 9. Validation
# ==============================================================================

    def validate_name(self) -> bool:

        return (
            isinstance(self._name, str)
            and bool(self._name.strip())
        )

    def validate_version(self) -> bool:

        return isinstance(
            self._version,
            str,
        )

    def validate_priority(self) -> bool:

        return isinstance(
            self._priority,
            int,
        )

    def validate_config(self) -> bool:

        return isinstance(
            self._config,
            dict,
        )

    def validate_hooks(self) -> bool:

        return isinstance(
            self._hooks,
            dict,
        )

    def validate(self) -> bool:

        return all(
            (
                self.validate_name(),
                self.validate_version(),
                self.validate_priority(),
                self.validate_config(),
                self.validate_hooks(),
            )
        )

    def normalize(self) -> "RuntimePlugin":

        self._name = self._name.strip()

        self._version = self._version.strip()

        return self


# ==============================================================================
# Part 10. Serialization
# ==============================================================================

    def to_dict(self) -> PluginState:

        return {
            "name": self._name,
            "version": self._version,
            "enabled": self._enabled,
            "state": self._state,
            "priority": self._priority,
            "config": dict(self._config),
        }

    @classmethod
    def from_dict(
        cls,
        data: PluginState,
    ) -> "RuntimePlugin":

        plugin = cls(
            name=data.get(
                "name",
                DEFAULT_NAME,
            ),
            version=data.get(
                "version",
                DEFAULT_VERSION,
            ),
            enabled=data.get(
                "enabled",
                DEFAULT_ENABLED,
            ),
            priority=data.get(
                "priority",
                DEFAULT_PRIORITY,
            ),
            config=data.get(
                "config",
                {},
            ),
        )

        plugin._state = data.get(
            "state",
            "idle",
        )

        return plugin

    def to_tuple(self) -> tuple[Any, ...]:

        return (
            self._name,
            self._version,
            self._enabled,
            self._state,
            self._priority,
            dict(self._config),
        )

    @classmethod
    def from_tuple(
        cls,
        data: tuple[Any, ...],
    ) -> "RuntimePlugin":

        plugin = cls(
            name=data[0],
            version=data[1],
            enabled=data[2],
            priority=data[4],
            config=data[5],
        )

        plugin._state = data[3]

        return plugin

    def to_json(self) -> str:

        import json

        return json.dumps(
            self.to_dict(),
            indent=2,
            sort_keys=True,
        )

    @classmethod
    def from_json(
        cls,
        text: str,
    ) -> "RuntimePlugin":

        import json

        return cls.from_dict(
            json.loads(text)
        )


# ==============================================================================
# Part 11. Diagnostics
# ==============================================================================

    def summary(self) -> dict[str, Any]:

        return {
            "name": self._name,
            "version": self._version,
            "enabled": self._enabled,
            "state": self._state,
            "priority": self._priority,
        }

    def diagnostics(self) -> dict[str, Any]:

        return {
            **self.summary(),
            "config_size": len(
                self._config
            ),
            "hook_count": len(
                self._hooks
            ),
            "valid": self.validate(),
        }

    def report(self) -> dict[str, Any]:

        return self.diagnostics()

    def status(self) -> str:

        if not self._enabled:
            return "disabled"

        return self._state


# ==============================================================================
# Part 12. Protocols
# ==============================================================================

    def __len__(self) -> int:

        return len(
            self._config
        )

    def __contains__(
        self,
        key: object,
    ) -> bool:

        return key in self._config

    def __iter__(self):

        return iter(
            self._config.items()
        )

    def __hash__(self) -> int:

        return hash(
            (
                self._name,
                self._version,
            )
        )

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(
            other,
            RuntimePlugin,
        ):
            return False

        return (
            self.to_dict()
            == other.to_dict()
        )

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"enabled={self._enabled}, "
            f"state={self._state!r})"
        )

    def __str__(self) -> str:

        return self._name

    def __bool__(self) -> bool:

        return self._enabled