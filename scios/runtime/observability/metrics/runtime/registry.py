"""
SciOS Runtime Metrics Registry

Central runtime registry for metric recorders, collectors, and plugins.

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

DEFAULT_NAME: str = "runtime"

DEFAULT_ENABLED: bool = True

DEFAULT_LOCKED: bool = False

DEFAULT_MAX_RECORDERS: int = 1024

DEFAULT_MAX_COLLECTORS: int = 1024

DEFAULT_MAX_PLUGINS: int = 256


__all__ = [
    # constants
    "DEFAULT_NAME",
    "DEFAULT_ENABLED",
    "DEFAULT_LOCKED",
    "DEFAULT_MAX_RECORDERS",
    "DEFAULT_MAX_COLLECTORS",
    "DEFAULT_MAX_PLUGINS",
    # aliases
    "RecorderMap",
    "CollectorMap",
    "PluginMap",
    "RegistryState",
    # classes
    "RuntimeRegistry",
]


# ==============================================================================
# Part 3. Type Aliases
# ==============================================================================

RecorderMap: TypeAlias = dict[str, Any]

CollectorMap: TypeAlias = dict[str, Any]

PluginMap: TypeAlias = dict[str, Any]

RegistryState: TypeAlias = dict[str, Any]


# ==============================================================================
# Part 4. RuntimeRegistry
# ==============================================================================


class RuntimeRegistry:
    """
    Runtime metrics registry.

    Manages runtime metric recorders, collectors, and plugins.
    """

    __slots__ = (
        "_name",
        "_recorders",
        "_collectors",
        "_plugins",
        "_enabled",
        "_locked",
    )

    def __init__(
        self,
        *,
        name: str = DEFAULT_NAME,
        enabled: bool = DEFAULT_ENABLED,
        locked: bool = DEFAULT_LOCKED,
    ) -> None:

        self._name = str(name)

        self._recorders: RecorderMap = {}

        self._collectors: CollectorMap = {}

        self._plugins: PluginMap = {}

        self._enabled = bool(enabled)

        self._locked = bool(locked)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:

        return self._name

    @property
    def recorders(self) -> RecorderMap:

        return self._recorders

    @property
    def collectors(self) -> CollectorMap:

        return self._collectors

    @property
    def plugins(self) -> PluginMap:

        return self._plugins

    @property
    def enabled(self) -> bool:

        return self._enabled

    @property
    def locked(self) -> bool:

        return self._locked

    @property
    def size(self) -> int:

        return (
            len(self._recorders)
            + len(self._collectors)
            + len(self._plugins)
        )

    # ==============================================================================
    # Part 5. Recorder API
    # ==============================================================================

    def register_recorder(
        self,
        name: str,
        recorder: Any,
    ) -> Any:

        if self._locked:
            raise RuntimeError("registry is locked")

        if len(self._recorders) >= DEFAULT_MAX_RECORDERS:
            raise RuntimeError("maximum recorder capacity exceeded")

        self._recorders[str(name)] = recorder

        return recorder

    def unregister_recorder(
        self,
        name: str,
    ) -> Any | None:

        if self._locked:
            raise RuntimeError("registry is locked")

        return self._recorders.pop(
            str(name),
            None,
        )

    def get_recorder(
        self,
        name: str,
        default: Any = None,
    ) -> Any:

        return self._recorders.get(
            str(name),
            default,
        )

    def has_recorder(
        self,
        name: str,
    ) -> bool:

        return str(name) in self._recorders

    def list_recorders(self) -> list[str]:

        return sorted(self._recorders)

    def clear_recorders(self) -> None:

        if self._locked:
            raise RuntimeError("registry is locked")

        self._recorders.clear()

# ==============================================================================
# Part 6. Collector API
# ==============================================================================

    def register_collector(
        self,
        name: str,
        collector: Any,
    ) -> Any:

        if self._locked:
            raise RuntimeError("registry is locked")

        if len(self._collectors) >= DEFAULT_MAX_COLLECTORS:
            raise RuntimeError("maximum collector capacity exceeded")

        self._collectors[str(name)] = collector
        return collector

    def unregister_collector(
        self,
        name: str,
    ) -> Any | None:

        if self._locked:
            raise RuntimeError("registry is locked")

        return self._collectors.pop(str(name), None)

    def get_collector(
        self,
        name: str,
        default: Any = None,
    ) -> Any:

        return self._collectors.get(str(name), default)

    def has_collector(
        self,
        name: str,
    ) -> bool:

        return str(name) in self._collectors

    def list_collectors(self) -> list[str]:

        return sorted(self._collectors)

    def clear_collectors(self) -> None:

        if self._locked:
            raise RuntimeError("registry is locked")

        self._collectors.clear()


# ==============================================================================
# Part 7. Plugin API
# ==============================================================================

    def register_plugin(
        self,
        name: str,
        plugin: Any,
    ) -> Any:

        if self._locked:
            raise RuntimeError("registry is locked")

        if len(self._plugins) >= DEFAULT_MAX_PLUGINS:
            raise RuntimeError("maximum plugin capacity exceeded")

        self._plugins[str(name)] = plugin
        return plugin

    def unregister_plugin(
        self,
        name: str,
    ) -> Any | None:

        if self._locked:
            raise RuntimeError("registry is locked")

        return self._plugins.pop(str(name), None)

    def get_plugin(
        self,
        name: str,
        default: Any = None,
    ) -> Any:

        return self._plugins.get(str(name), default)

    def has_plugin(
        self,
        name: str,
    ) -> bool:

        return str(name) in self._plugins

    def list_plugins(self) -> list[str]:

        return sorted(self._plugins)

    def clear_plugins(self) -> None:

        if self._locked:
            raise RuntimeError("registry is locked")

        self._plugins.clear()


# ==============================================================================
# Part 8. Registry Operations
# ==============================================================================

    def clear(self) -> None:

        self.clear_recorders()
        self.clear_collectors()
        self.clear_plugins()

    def reset(self) -> None:

        self.clear()

        self._enabled = DEFAULT_ENABLED
        self._locked = DEFAULT_LOCKED

    def clone(self) -> "RuntimeRegistry":

        return self.from_dict(
            self.to_dict()
        )

    def copy(self) -> "RuntimeRegistry":

        return self.clone()

    def merge(
        self,
        other: "RuntimeRegistry",
    ) -> "RuntimeRegistry":

        self._recorders.update(
            other.recorders
        )

        self._collectors.update(
            other.collectors
        )

        self._plugins.update(
            other.plugins
        )

        return self

    def update(
        self,
        state: RegistryState,
    ) -> "RuntimeRegistry":

        self.restore(state)

        return self

    def snapshot(self) -> RegistryState:

        return self.to_dict()

    def restore(
        self,
        state: RegistryState,
    ) -> None:

        restored = self.from_dict(state)

        self._name = restored._name
        self._enabled = restored._enabled
        self._locked = restored._locked

        self._recorders = restored._recorders
        self._collectors = restored._collectors
        self._plugins = restored._plugins


# ==============================================================================
# Part 9. Validation
# ==============================================================================

    def validate_name(self) -> bool:

        return (
            isinstance(
                self._name,
                str,
            )
            and
            bool(
                self._name.strip()
            )
        )

    def validate_recorders(self) -> bool:

        return isinstance(
            self._recorders,
            dict,
        )

    def validate_collectors(self) -> bool:

        return isinstance(
            self._collectors,
            dict,
        )

    def validate_plugins(self) -> bool:

        return isinstance(
            self._plugins,
            dict,
        )

    def validate(self) -> bool:

        return all(
            (
                self.validate_name(),
                self.validate_recorders(),
                self.validate_collectors(),
                self.validate_plugins(),
            )
        )

    def normalize(self) -> "RuntimeRegistry":

        self._name = self._name.strip()

        return self


# ==============================================================================
# Part 10. Serialization
# ==============================================================================

    def to_dict(self) -> RegistryState:

        return {
            "name": self._name,
            "enabled": self._enabled,
            "locked": self._locked,

            "recorders": tuple(
                sorted(
                    self._recorders.keys()
                )
            ),

            "collectors": tuple(
                sorted(
                    self._collectors.keys()
                )
            ),

            "plugins": tuple(
                sorted(
                    self._plugins.keys()
                )
            ),
        }

    @classmethod
    def from_dict(
        cls,
        data: RegistryState,
    ) -> "RuntimeRegistry":

        registry = cls(
            name=data.get(
                "name",
                DEFAULT_NAME,
            ),
            enabled=data.get(
                "enabled",
                DEFAULT_ENABLED,
            ),
            locked=data.get(
                "locked",
                DEFAULT_LOCKED,
            ),
        )

        for name in data.get(
            "recorders",
            (),
        ):
            registry._recorders[name] = None

        for name in data.get(
            "collectors",
            (),
        ):
            registry._collectors[name] = None

        for name in data.get(
            "plugins",
            (),
        ):
            registry._plugins[name] = None

        return registry

    def to_tuple(self) -> tuple[Any, ...]:

        return (
            self._name,
            self._enabled,
            self._locked,

            tuple(
                sorted(
                    self._recorders
                )
            ),

            tuple(
                sorted(
                    self._collectors
                )
            ),

            tuple(
                sorted(
                    self._plugins
                )
            ),
        )

    @classmethod
    def from_tuple(
        cls,
        data: tuple[Any, ...],
    ) -> "RuntimeRegistry":

        registry = cls(
            name=data[0],
            enabled=data[1],
            locked=data[2],
        )

        for name in data[3]:
            registry._recorders[name] = None

        for name in data[4]:
            registry._collectors[name] = None

        for name in data[5]:
            registry._plugins[name] = None

        return registry

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
    ) -> "RuntimeRegistry":

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
            "size": self.size,
            "enabled": self._enabled,
            "locked": self._locked,
        }

    def diagnostics(self) -> dict[str, Any]:

        return {
            "valid": self.validate(),
            **self.summary(),
        }

    def report(self) -> dict[str, Any]:

        return self.to_dict()

    def status(self) -> str:

        if self._locked:
            return "locked"

        if not self._enabled:
            return "disabled"

        return "ready"


# ==============================================================================
# Part 12. Protocols
# ==============================================================================

    def __len__(self) -> int:

        return self.size

    def __contains__(
        self,
        item: str,
    ) -> bool:

        return (
            item in self._recorders
            or item in self._collectors
            or item in self._plugins
        )

    def __iter__(self):

        yield from self._recorders.items()
        yield from self._collectors.items()
        yield from self._plugins.items()

    def __hash__(self) -> int:

        return hash(
            (
                self._name,
                self.size,
            )
        )

    def __eq__(
        self,
        other: object,
    ) -> bool:

        return (
            isinstance(other, RuntimeRegistry)
            and self.to_dict() == other.to_dict()
        )

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"size={self.size})"
        )

    def __str__(self) -> str:

        return f"{self._name} ({self.size})"

    def __bool__(self) -> bool:

        return self.size > 0        