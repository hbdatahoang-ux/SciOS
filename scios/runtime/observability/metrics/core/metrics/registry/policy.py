# ==============================================================================
# Part 1. Imports & Constants
# ==============================================================================

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from copy import deepcopy

__all__ = [
    "MetricPolicy",
]

PolicyState = dict[str, Any]
PolicyRules = dict[str, Any]

DEFAULT_NAME = ""
DEFAULT_ENABLED = True
DEFAULT_READ_ONLY = False
DEFAULT_ALLOW_OVERWRITE = True
DEFAULT_AUTO_CREATE = True
DEFAULT_VALIDATE_ON_REGISTER = True
DEFAULT_MAX_METRICS = 0

# ==============================================================================
# Part 2. MetricPolicy
# ==============================================================================

@dataclass(slots=True)
class MetricPolicy:
    """
    Registry policy configuration.
    """

    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------

    name: str = DEFAULT_NAME

    enabled: bool = DEFAULT_ENABLED

    read_only: bool = DEFAULT_READ_ONLY

    allow_overwrite: bool = DEFAULT_ALLOW_OVERWRITE

    auto_create: bool = DEFAULT_AUTO_CREATE

    validate_on_register: bool = DEFAULT_VALIDATE_ON_REGISTER

    max_metrics: int = DEFAULT_MAX_METRICS

    # ------------------------------------------------------------------
    # Policy data
    # ------------------------------------------------------------------

    limits: dict[str, Any] = field(
        default_factory=dict,
    )

    rules: PolicyRules = field(
        default_factory=dict,
    )

    state: PolicyState = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:

        self._normalize()
        self._validate()

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    def _normalize(self) -> None:

        if isinstance(self.name, str):
            self.name = self.name.strip().lower()

        if not isinstance(self.limits, dict):
            self.limits = {}

        if not isinstance(self.rules, dict):
            self.rules = {}

        if not isinstance(self.state, dict):
            self.state = {}

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self) -> None:

        if not isinstance(self.name, str):
            raise TypeError("name must be str.")

        if not isinstance(self.enabled, bool):
            raise TypeError("enabled must be bool.")

        if not isinstance(self.read_only, bool):
            raise TypeError("read_only must be bool.")

        if not isinstance(self.allow_overwrite, bool):
            raise TypeError("allow_overwrite must be bool.")

        if not isinstance(self.auto_create, bool):
            raise TypeError("auto_create must be bool.")

        if not isinstance(self.validate_on_register, bool):
            raise TypeError(
                "validate_on_register must be bool."
            )

        if not isinstance(self.max_metrics, int):
            raise TypeError("max_metrics must be int.")

        if not isinstance(self.limits, dict):
            raise TypeError("limits must be dict.")

        if not isinstance(self.rules, dict):
            raise TypeError("rules must be dict.")

        if not isinstance(self.state, dict):
            raise TypeError("state must be dict.")

    # ==========================================================================
    # Rule Operations
    # ==========================================================================

    def add_rule(
        self,
        name: str,
        value: Any,
    ) -> None:

        self.rules[str(name)] = value

    def remove_rule(
        self,
        name: str,
    ) -> Any:

        return self.rules.pop(str(name), None)

    def get_rule(
        self,
        name: str,
        default: Any = None,
    ) -> Any:

        return self.rules.get(str(name), default)

    def contains_rule(
        self,
        name: str,
    ) -> bool:

        return str(name) in self.rules

    def clear(self) -> None:

        self.rules.clear()

    def list_rules(self) -> list[str]:

        return sorted(self.rules)

    # ==========================================================================
    # Limit Operations
    # ==========================================================================

    def set_limit(
        self,
        name: str,
        value: Any,
    ) -> None:

        self.limits[str(name)] = value

    def get_limit(
        self,
        name: str,
        default: Any = None,
    ) -> Any:

        return self.limits.get(str(name), default)

    def remove_limit(
        self,
        name: str,
    ) -> Any:

        return self.limits.pop(str(name), None)

    def contains_limit(
        self,
        name: str,
    ) -> bool:

        return str(name) in self.limits

   

# ==============================================================================
# Part 3. Properties
# ==============================================================================

    @property
    def size(self) -> int:
        """
        Number of policy rules.
        """
        return len(
            self.rules
        )


    @property
    def active(self) -> bool:
        """
        Policy enabled.
        """
        return (
            self.enabled
        )


    @property
    def readonly(self) -> bool:
        """
        Read-only flag.
        """
        return (
            self.read_only
        )

# ==============================================================================
# Part 4. Policy Operations
# ==============================================================================

    def enable(
        self,
    ) -> "MetricPolicy":

        self.enabled = True

        return self


    def disable(
        self,
    ) -> "MetricPolicy":

        self.enabled = False

        return self


    def set_rule(
        self,
        key: str,
        value: Any,
    ) -> "MetricPolicy":

        self.rules[
            str(key)
        ] = value

        return self


    def get_rule(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.rules.get(
            key,
            default,
        )


    def remove_rule(
        self,
        key: str,
    ) -> "MetricPolicy":

        self.rules.pop(
            key,
            None,
        )

        return self


    def contains_rule(
        self,
        key: str,
    ) -> bool:

        return (
            key
            in self.rules
        )


    def clear_rules(
        self,
    ) -> "MetricPolicy":

        self.rules.clear()

        return self


    def normalize(
        self,
    ) -> "MetricPolicy":

        self._normalize()

        return self

    # ==============================================================================
    # Rule Operations
    # ==============================================================================

    def add_rule(self, name: str, value: Any) -> None:
        self.rules[str(name)] = value


    def remove_rule(self, name: str) -> Any:
        return self.rules.pop(str(name), None)


    def get_rule(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        return self.rules.get(str(name), default)


    def contains_rule(self, name: str) -> bool:
        return str(name) in self.rules


    def clear(self) -> None:
        self.rules.clear()


    def list_rules(self) -> list[str]:
        
        return sorted(self.rules) 

# ==============================================================================
# Part 5. Serialization
# ==============================================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "name": self.name,
            "enabled": self.enabled,
            "read_only": self.read_only,
            "allow_overwrite": self.allow_overwrite,
            "auto_create": self.auto_create,
            "validate_on_register": (
                self.validate_on_register
            ),
            "max_metrics": self.max_metrics,
            "rules": dict(
                self.rules
            ),
            "state": dict(
                self.state
            ),
        }


    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricPolicy":

        return cls(
            name=data.get(
                "name",
                DEFAULT_NAME,
            ),
            enabled=data.get(
                "enabled",
                DEFAULT_ENABLED,
            ),
            read_only=data.get(
                "read_only",
                DEFAULT_READ_ONLY,
            ),
            allow_overwrite=data.get(
                "allow_overwrite",
                DEFAULT_ALLOW_OVERWRITE,
            ),
            auto_create=data.get(
                "auto_create",
                DEFAULT_AUTO_CREATE,
            ),
            validate_on_register=data.get(
                "validate_on_register",
                DEFAULT_VALIDATE_ON_REGISTER,
            ),
            max_metrics=data.get(
                "max_metrics",
                DEFAULT_MAX_METRICS,
            ),
            rules=dict(
                data.get(
                    "rules",
                    {},
                )
            ),
            state=dict(
                data.get(
                    "state",
                    {},
                )
            ),
        )


    def to_tuple(
        self,
    ) -> tuple:

        return (
            self.name,
            self.enabled,
            self.read_only,
            self.allow_overwrite,
            self.auto_create,
            self.validate_on_register,
            self.max_metrics,
            dict(
                self.rules
            ),
            dict(
                self.state
            ),
        )


    @classmethod
    def from_tuple(
        cls,
        value: tuple,
    ) -> "MetricPolicy":

        (
            name,
            enabled,
            read_only,
            allow_overwrite,
            auto_create,
            validate_on_register,
            max_metrics,
            rules,
            state,
        ) = value

        return cls(
            name=name,
            enabled=enabled,
            read_only=read_only,
            allow_overwrite=allow_overwrite,
            auto_create=auto_create,
            validate_on_register=validate_on_register,
            max_metrics=max_metrics,
            rules=dict(
                rules,
            ),
            state=dict(
                state,
            ),
        )


    def snapshot(
        self,
    ) -> dict[str, Any]:

        return self.to_dict()


    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> "MetricPolicy":

        restored = self.from_dict(
            snapshot
        )

        self.name = restored.name
        self.enabled = restored.enabled
        self.read_only = restored.read_only
        self.allow_overwrite = (
            restored.allow_overwrite
        )
        self.auto_create = (
            restored.auto_create
        )
        self.validate_on_register = (
            restored.validate_on_register
        )
        self.max_metrics = (
            restored.max_metrics
        )
        self.rules = (
            restored.rules
        )
        self.state = (
            restored.state
        )

        return self

# ==============================================================================
# Part 6. Validation
# ==============================================================================

    @property
    def size(self) -> int:
        return len(self.rules)


    @classmethod
    def validate_name(cls, value: Any) -> bool:
        return isinstance(value, str)


    @classmethod
    def validate_enabled(cls, value: Any) -> bool:
        return isinstance(value, bool)


    @classmethod
    def validate_rules(cls, value: Any) -> bool:
        return isinstance(value, dict)


    @classmethod
    def validate_state(cls, value: Any) -> bool:
        return isinstance(value, dict)


    @classmethod
    def validate_policy(
        cls,
        policy: "MetricPolicy",
    ) -> bool:
        return (
            isinstance(policy, cls)
            and cls.validate_name(policy.name)
            and cls.validate_enabled(policy.enabled)
            and cls.validate_rules(policy.rules)
            and cls.validate_state(policy.state)
        )


    def validate(self) -> bool:
        return self.validate_policy(self)


# ==============================================================================
# Part 7. Utilities
# ==============================================================================

    def clone(self) -> "MetricPolicy":
        return deepcopy(self)


    def copy(self) -> "MetricPolicy":
        return self.clone()


    def merge(
        self,
        other: "MetricPolicy",
    ) -> "MetricPolicy":

        if not isinstance(other, MetricPolicy):
            return self

        self.rules.update(other.rules)
        self.state.update(other.state)

        return self


    def update(
        self,
        other: "MetricPolicy",
    ) -> "MetricPolicy":
        return self.merge(other)


    def reset(self) -> None:

        self.rules.clear()
        self.state.clear()


# ==============================================================================
# Part 8. Protocols
# ==============================================================================

    def __bool__(self) -> bool:
        return bool(self.rules)


    def __hash__(self) -> int:
        return hash(
            (
                self.name,
                self.enabled,
                tuple(sorted(self.rules.items())),
            )
        )


    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"enabled={self.enabled!r})"
        )


    def __str__(self) -> str:
        return self.__repr__()


# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================

    def summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "enabled": self.enabled,
            "rules": len(self.rules),
            "valid": self.validate(),
        }


    def diagnostics(self) -> dict[str, Any]:
        return {
            "valid": self.validate(),
            "summary": self.summary(),
        }


    def policy_report(self) -> dict[str, Any]:
        return {
            "summary": self.summary(),
            "diagnostics": self.diagnostics(),
        }


    def overall_status(self) -> str:
        return (
            "healthy"
            if self.validate()
            else "invalid"
        )


# ==============================================================================
# Part 10. Public API
# ==============================================================================

__all__ = [
    "MetricPolicy",
]                                    