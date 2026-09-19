# ==============================================================================
# Part 1. Imports
# ==============================================================================

from __future__ import annotations

import json

from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from typing import Any, Final, TypeAlias


# ==============================================================================
# Part 2. Constants
# ==============================================================================

__version__: Final[str] = "0.1.0"

DEFAULT_ENABLED: Final[bool] = True
DEFAULT_ACTIVE: Final[bool] = True


# ==============================================================================
# Part 3. Enums
# ==============================================================================


class MetricLifecycle(str, Enum):
    """
    Metric lifecycle state.
    """

    CREATED = "created"
    ACTIVE = "active"
    DISABLED = "disabled"
    ARCHIVED = "archived"


class MetricHealth(str, Enum):
    """
    Metric health state.
    """

    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    STALE = "stale"


class MetricStatus(str, Enum):
    """
    Runtime metric status.
    """

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


# ==============================================================================
# Part 4. Exceptions
# ==============================================================================


class MetricStateError(RuntimeError):
    """
    Base metric-state exception.
    """


class MetricStateValidationError(
    MetricStateError,
    ValueError,
):
    """
    Raised when MetricState is invalid.
    """


# ==============================================================================
# Part 5. Type Aliases
# ==============================================================================

JsonDict: TypeAlias = dict[str, Any]


# ==============================================================================
# Part 6. Dataclass
# ==============================================================================


@dataclass(slots=True)
class MetricState:
    """
    Runtime state of a metric.

    This object stores only mutable execution state.
    Static information belongs to MetricDescriptor,
    MetricMetadata, MetricLabels and MetricAttributes.
    """

    enabled: bool = DEFAULT_ENABLED

    active: bool = DEFAULT_ACTIVE

    lifecycle: MetricLifecycle = MetricLifecycle.CREATED

    health: MetricHealth = MetricHealth.HEALTHY

    status: MetricStatus = MetricStatus.IDLE

# ==============================================================================
# Part 7. Constructor Validation
# ==============================================================================

    def __post_init__(self) -> None:
        """
        Validate constructor arguments.
        """

        if not isinstance(self.enabled, bool):
            raise TypeError("enabled must be bool.")

        if not isinstance(self.active, bool):
            raise TypeError("active must be bool.")

        if not isinstance(self.lifecycle, MetricLifecycle):
            try:
                self.lifecycle = MetricLifecycle(self.lifecycle)
            except Exception as exc:
                raise TypeError(
                    "Invalid MetricLifecycle."
                ) from exc

        if not isinstance(self.health, MetricHealth):
            try:
                self.health = MetricHealth(self.health)
            except Exception as exc:
                raise TypeError(
                    "Invalid MetricHealth."
                ) from exc

        if not isinstance(self.status, MetricStatus):
            try:
                self.status = MetricStatus(self.status)
            except Exception as exc:
                raise TypeError(
                    "Invalid MetricStatus."
                ) from exc


# ==============================================================================
# Part 8. Properties
# ==============================================================================

    @property
    def state(self) -> JsonDict:
        """
        Return current state.
        """

        return self.to_dict()


    # ------------------------------------------------------------------------------
    # Lifecycle state properties
    # ------------------------------------------------------------------------------

    @property
    def created(self) -> bool:
        """
        Whether the metric is in CREATED lifecycle state.
        """

        return self.lifecycle is MetricLifecycle.CREATED


    @property
    def active_lifecycle(self) -> bool:
        """
        Whether the metric lifecycle is ACTIVE.
        """

        return self.lifecycle is MetricLifecycle.ACTIVE


    @property
    def disabled(self) -> bool:
        """
        Whether the metric is disabled.
        """

        return self.lifecycle is MetricLifecycle.DISABLED


    @property
    def archived(self) -> bool:
        """
        Whether the metric is archived.
        """

        return self.lifecycle is MetricLifecycle.ARCHIVED


    # ------------------------------------------------------------------------------
    # Health properties
    # ------------------------------------------------------------------------------

    @property
    def healthy(self) -> bool:
        """
        Whether the metric is healthy.
        """

        return self.health is MetricHealth.HEALTHY


    @property
    def warning(self) -> bool:
        """
        Whether the metric is in warning state.
        """

        return self.health is MetricHealth.WARNING


    @property
    def error(self) -> bool:
        """
        Whether the metric is in error state.
        """

        return self.health is MetricHealth.ERROR


    @property
    def stale(self) -> bool:
        """
        Whether the metric is stale.
        """

        return self.health is MetricHealth.STALE



# ==============================================================================
# Part 9. Lifecycle
# ==============================================================================

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False
        self.active = False
        self.lifecycle = MetricLifecycle.DISABLED

    def activate(self) -> None:
        if self.enabled:
            self.active = True
            self.lifecycle = MetricLifecycle.ACTIVE

    def deactivate(self) -> None:
        self.active = False

    def reset(self) -> None:
        self.enabled = DEFAULT_ENABLED
        self.active = DEFAULT_ACTIVE
        self.lifecycle = MetricLifecycle.CREATED
        self.health = MetricHealth.HEALTHY
        self.status = MetricStatus.IDLE

    def archive(self) -> None:
        self.active = False
        self.lifecycle = MetricLifecycle.ARCHIVED

    def restore(self) -> None:
        self.enabled = True
        self.active = True
        self.lifecycle = MetricLifecycle.ACTIVE


# ==============================================================================
# Part 10. Status
# ==============================================================================

    def mark_healthy(self) -> None:
        self.health = MetricHealth.HEALTHY

    def mark_warning(self) -> None:
        self.health = MetricHealth.WARNING

    def mark_error(self) -> None:
        self.health = MetricHealth.ERROR

    def mark_stale(self) -> None:
        self.health = MetricHealth.STALE

    def is_enabled(self) -> bool:
        return self.enabled

    def is_active(self) -> bool:
        return self.active

    def is_healthy(self) -> bool:
        return self.health is MetricHealth.HEALTHY

    def is_warning(self) -> bool:
        return self.health is MetricHealth.WARNING

    def is_error(self) -> bool:
        return self.health is MetricHealth.ERROR

    def is_stale(self) -> bool:
        return self.health is MetricHealth.STALE


# ==============================================================================
# Part 11. Validation
# ==============================================================================

    def validate(self) -> bool:
        """
        Validate current state.
        """

        if not isinstance(self.enabled, bool):
            return False

        if not isinstance(self.active, bool):
            return False

        if not isinstance(self.lifecycle, MetricLifecycle):
            return False

        if not isinstance(self.health, MetricHealth):
            return False

        if not isinstance(self.status, MetricStatus):
            return False

        return True

# ==============================================================================
# Part 12. Serialization
# ==============================================================================

    def to_dict(self) -> JsonDict:
        """
        Serialize to dictionary.
        """

        return {
            "enabled": self.enabled,
            "active": self.active,
            "lifecycle": self.lifecycle.value,
            "health": self.health.value,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(
        cls,
        data: JsonDict,
    ) -> "MetricState":
        """
        Create from dictionary.
        """

        return cls(
            enabled=data.get("enabled", DEFAULT_ENABLED),
            active=data.get("active", DEFAULT_ACTIVE),
            lifecycle=data.get(
                "lifecycle",
                MetricLifecycle.CREATED,
            ),
            health=data.get(
                "health",
                MetricHealth.HEALTHY,
            ),
            status=data.get(
                "status",
                MetricStatus.IDLE,
            ),
        )

    def to_json(
        self,
        **kwargs: Any,
    ) -> str:
        """
        Serialize to JSON.
        """

        return json.dumps(
            self.to_dict(),
            **kwargs,
        )

    @classmethod
    def from_json(
        cls,
        value: str,
    ) -> "MetricState":
        """
        Create from JSON.
        """

        return cls.from_dict(
            json.loads(value),
        )


# ==============================================================================
# Part 13. Copy
# ==============================================================================

    def copy(self) -> "MetricState":
        """
        Return a shallow copy.
        """

        return type(self).from_dict(
            self.to_dict(),
        )

    def clone(self) -> "MetricState":
        """
        Return a deep copy.
        """

        return deepcopy(self)


# ==============================================================================
# Part 14. Equality
# ==============================================================================

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(other, MetricState):
            return NotImplemented

        return self.to_dict() == other.to_dict()

    def __hash__(self) -> int:

        return hash(
            (
                self.enabled,
                self.active,
                self.lifecycle,
                self.health,
                self.status,
            )
        )


# ==============================================================================
# Part 15. Representation
# ==============================================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"enabled={self.enabled!r}, "
            f"active={self.active!r}, "
            f"lifecycle={self.lifecycle.value!r}, "
            f"health={self.health.value!r}, "
            f"status={self.status.value!r}"
            f")"
        )

    def __str__(self) -> str:

        return (
            f"{self.lifecycle.value}/"
            f"{self.health.value}/"
            f"{self.status.value}"
        )


# ==============================================================================
# Part 16. Public API
# ==============================================================================

__all__ = [
    "__version__",
    "MetricLifecycle",
    "MetricHealth",
    "MetricStatus",
    "MetricStateError",
    "MetricStateValidationError",
    "MetricState",
]            