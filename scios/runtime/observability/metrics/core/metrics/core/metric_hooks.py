# ==========================================================
# Part 1. Imports
# ==========================================================

from __future__ import annotations

import copy as _copy
import json
from dataclasses import dataclass, field, replace as _replace
from typing import Any, Callable, TypeAlias


# ==========================================================
# Part 2. Constants & Type Aliases
# ==========================================================

Hook: TypeAlias = Callable[..., Any]
HookList: TypeAlias = list[Hook]

DEFAULT_VERSION: str = "1.0"

CALLBACK_REGISTRY: dict[str, Hook] = {}

__all__ = [
    "DEFAULT_VERSION",
    "CALLBACK_REGISTRY",
    "Hook",
    "HookList",
    "MetricHooks",
]

# ==========================================================
# Part 3. Dataclass / Core Container
# ==========================================================

@dataclass(slots=True, eq=False)
class MetricHooks:
    """
    Hook registry for the Metrics subsystem.
    """

    before_collect: HookList = field(default_factory=list)

    after_collect: HookList = field(default_factory=list)

    before_export: HookList = field(default_factory=list)

    after_export: HookList = field(default_factory=list)

    version: str = DEFAULT_VERSION

# ==========================================================
# Part 4. Validation
# ==========================================================

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """
        Validate hook registry.
        """

        collections = (
            self.before_collect,
            self.after_collect,
            self.before_export,
            self.after_export,
        )

        for hooks in collections:
            if not isinstance(hooks, list):
                raise TypeError("hook collection must be a list")

            for hook in hooks:
                if not callable(hook):
                    raise TypeError("all hooks must be callable")

        if not isinstance(self.version, str):
            raise TypeError("version must be str")

    def is_valid(self) -> bool:
        """
        Return True if registry is valid.
        """

        try:
            self.validate()
            return True
        except Exception:
            return False


# ==========================================================
# Part 5. Registration API
# ==========================================================

    def register_before_collect(
        self,
        hook: Hook,
    ) -> None:
        if not callable(hook):
            raise TypeError("hook must be callable")

        self.before_collect.append(hook)

    def register_after_collect(
        self,
        hook: Hook,
    ) -> None:
        if not callable(hook):
            raise TypeError("hook must be callable")

        self.after_collect.append(hook)

    def register_before_export(
        self,
        hook: Hook,
    ) -> None:
        if not callable(hook):
            raise TypeError("hook must be callable")

        self.before_export.append(hook)

    def register_after_export(
        self,
        hook: Hook,
    ) -> None:
        if not callable(hook):
            raise TypeError("hook must be callable")

        self.after_export.append(hook)


# ==========================================================
# Part 6. Execution API
# ==========================================================

    def run_before_collect(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        for hook in self.before_collect:
            hook(*args, **kwargs)

    def run_after_collect(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        for hook in self.after_collect:
            hook(*args, **kwargs)

    def run_before_export(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        for hook in self.before_export:
            hook(*args, **kwargs)

    def run_after_export(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        for hook in self.after_export:
            hook(*args, **kwargs)

# ==========================================================
# Part 7. Serialization
# ==========================================================

    @classmethod
    def register_callback(
        cls,
        name: str,
        callback: Hook,
    ) -> None:
        """
        Register callback for serialization.
        """
        CALLBACK_REGISTRY[name] = callback

    @classmethod
    def unregister_callback(
        cls,
        name: str,
    ) -> None:
        """
        Remove callback from registry.
        """
        CALLBACK_REGISTRY.pop(name, None)

    @staticmethod
    def _callback_name(
        callback: Hook,
    ) -> str:
        """
        Resolve callback -> registry name.

        Automatically register callbacks that are not yet present.
        """

        for name, fn in CALLBACK_REGISTRY.items():
            if fn is callback:
                return name

        name = getattr(
            callback,
            "__qualname__",
            getattr(
                callback,
                "__name__",
                repr(callback),
            ),
        )

        CALLBACK_REGISTRY[name] = callback

        return name

    @staticmethod
    def _callback_from_name(
        name: str,
    ) -> Hook:
        """
        Resolve registry name -> callback.
        """
        try:
            return CALLBACK_REGISTRY[name]
        except KeyError as exc:
            raise KeyError(
                f"Unknown callback: {name}"
            ) from exc

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize hook registry.
        """

        return {
            "before_collect": [
                self._callback_name(cb)
                for cb in self.before_collect
            ],
            "after_collect": [
                self._callback_name(cb)
                for cb in self.after_collect
            ],
            "before_export": [
                self._callback_name(cb)
                for cb in self.before_export
            ],
            "after_export": [
                self._callback_name(cb)
                for cb in self.after_export
            ],
            "version": self.version,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricHooks":
        """
        Deserialize hook registry.
        """

        hooks = cls(
            version=data.get(
                "version",
                DEFAULT_VERSION,
            ),
        )

        hooks.before_collect = [
            cls._callback_from_name(name)
            for name in data.get(
                "before_collect",
                [],
            )
        ]

        hooks.after_collect = [
            cls._callback_from_name(name)
            for name in data.get(
                "after_collect",
                [],
            )
        ]

        hooks.before_export = [
            cls._callback_from_name(name)
            for name in data.get(
                "before_export",
                [],
            )
        ]

        hooks.after_export = [
            cls._callback_from_name(name)
            for name in data.get(
                "after_export",
                [],
            )
        ]

        return hooks

    def to_json(self) -> str:
        """
        Serialize registry to JSON.
        """

        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
        )

    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "MetricHooks":
        """
        Deserialize registry from JSON.
        """

        return cls.from_dict(
            json.loads(payload),
        )


# ==========================================================
# Part 8. Copy API
# ==========================================================

    def copy(self) -> "MetricHooks":
        """
        Return a shallow copy.
        """

        return MetricHooks(
            before_collect=list(self.before_collect),
            after_collect=list(self.after_collect),
            before_export=list(self.before_export),
            after_export=list(self.after_export),
            version=self.version,
        )

    def clone(self) -> "MetricHooks":
        """
        Alias of copy().
        """

        return self.copy()

    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ) -> "MetricHooks":
        """
        Deep copy preserving callbacks.
        """

        obj = MetricHooks(
            before_collect=list(self.before_collect),
            after_collect=list(self.after_collect),
            before_export=list(self.before_export),
            after_export=list(self.after_export),
            version=self.version,
        )

        memo[id(self)] = obj
        return obj

    def deepcopy(self) -> "MetricHooks":
        """
        Public deep-copy API.
        """

        return self.__deepcopy__({})

    def replace(
        self,
        **changes: Any,
    ) -> "MetricHooks":
        """
        Dataclass replace().
        """

        return _replace(self, **changes)


# ==========================================================
# Pickle Support
# ==========================================================

    def __getstate__(self) -> dict[str, Any]:
        """
        Return object state for pickle.
        """

        return {
            "before_collect": self.before_collect,
            "after_collect": self.after_collect,
            "before_export": self.before_export,
            "after_export": self.after_export,
            "version": self.version,
        }

    def __setstate__(
        self,
        state: dict[str, Any],
    ) -> None:
        """
        Restore pickle state.
        """

        self.before_collect = list(state["before_collect"])
        self.after_collect = list(state["after_collect"])
        self.before_export = list(state["before_export"])
        self.after_export = list(state["after_export"])
        self.version = state["version"]


# ==========================================================
# Part 9. Comparison
# ==========================================================

    def __eq__(
        self,
        other: object,
    ) -> bool:
        if not isinstance(other, MetricHooks):
            return NotImplemented

        return (
            self.before_collect == other.before_collect
            and self.after_collect == other.after_collect
            and self.before_export == other.before_export
            and self.after_export == other.after_export
            and self.version == other.version
        )

    def __hash__(self) -> int:
        return hash(
            (
                tuple(self.before_collect),
                tuple(self.after_collect),
                tuple(self.before_export),
                tuple(self.after_export),
                self.version,
            )
        )

# ==========================================================
# Part 10. Python Protocols
# ==========================================================

    def items(self):
        return {
            "before_collect": self.before_collect,
            "after_collect": self.after_collect,
            "before_export": self.before_export,
            "after_export": self.after_export,
            "version": self.version,
        }.items()

    def keys(self):
        return {
            "before_collect": None,
            "after_collect": None,
            "before_export": None,
            "after_export": None,
            "version": None,
        }.keys()

    def values(self):
        return {
            "before_collect": self.before_collect,
            "after_collect": self.after_collect,
            "before_export": self.before_export,
            "after_export": self.after_export,
            "version": self.version,
        }.values()

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return {
            "before_collect": self.before_collect,
            "after_collect": self.after_collect,
            "before_export": self.before_export,
            "after_export": self.after_export,
            "version": self.version,
        }.get(key, default)

    def clear(self) -> None:
        self.before_collect.clear()
        self.after_collect.clear()
        self.before_export.clear()
        self.after_export.clear()

    def __repr__(self) -> str:
        return (
            "MetricHooks("
            f"before_collect={len(self.before_collect)}, "
            f"after_collect={len(self.after_collect)}, "
            f"before_export={len(self.before_export)}, "
            f"after_export={len(self.after_export)}, "
            f"version={self.version!r})"
        )

    def __str__(self) -> str:
        return repr(self)

    def __bool__(self) -> bool:
        return any(
            (
                self.before_collect,
                self.after_collect,
                self.before_export,
                self.after_export,
            )
        )

    def __len__(self) -> int:
        return (
            len(self.before_collect)
            + len(self.after_collect)
            + len(self.before_export)
            + len(self.after_export)
        )

    def __iter__(self):
        return iter(self.items())

    def __contains__(
        self,
        item: object,
    ) -> bool:
        return item in self.items()

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        if key == "before_collect":
            return self.before_collect
        if key == "after_collect":
            return self.after_collect
        if key == "before_export":
            return self.before_export
        if key == "after_export":
            return self.after_export
        if key == "version":
            return self.version

        raise KeyError(key)

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        if key == "before_collect":
            self.before_collect = list(value)
        elif key == "after_collect":
            self.after_collect = list(value)
        elif key == "before_export":
            self.before_export = list(value)
        elif key == "after_export":
            self.after_export = list(value)
        elif key == "version":
            self.version = str(value)
        else:
            raise KeyError(key)

    def __delitem__(
        self,
        key: str,
    ) -> None:
        if key == "before_collect":
            self.before_collect.clear()
        elif key == "after_collect":
            self.after_collect.clear()
        elif key == "before_export":
            self.before_export.clear()
        elif key == "after_export":
            self.after_export.clear()
        else:
            raise KeyError(key)


# ==========================================================
# Part 11. Public API
# ==========================================================

__all__ = [
    "DEFAULT_VERSION",
    "Hook",
    "HookList",
    "MetricHooks",
]                        