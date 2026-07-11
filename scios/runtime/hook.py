"""
SciOS Runtime Hook System
=========================

Canonical hook abstractions for the SciOS Runtime.

Responsibilities
----------------
- Represent runtime hooks.
- Provide execution context.
- Manage hook lifecycle.
- Support plugin integration.
- Prepare for priority-based execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

__all__ = [
    "Hook",
    "HookContext",
    "HookHandle",
]


# ==========================================================
# Helpers
# ==========================================================


def _utc_now() -> str:
    """
    Return current UTC timestamp.
    """

    return datetime.now(
        timezone.utc,
    ).isoformat()


# ==========================================================
# Hook Context
# ==========================================================


@dataclass(slots=True)
class HookContext:
    """
    Runtime hook execution context.
    """

    name: str

    engine: Any | None = None

    context: Any | None = None

    result: Any | None = None

    error: BaseException | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    timestamp: str = field(
        default_factory=_utc_now,
    )

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.metadata[key] = value

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.metadata.get(
            key,
            default,
        )

    @property
    def succeeded(self) -> bool:

        return self.error is None

    @property
    def failed(self) -> bool:

        return self.error is not None

    def to_dict(self) -> dict[str, Any]:

        return {

            "name": self.name,

            "metadata": dict(self.metadata),

            "timestamp": self.timestamp,

            "error": (
                str(self.error)
                if self.error
                else None
            ),
        }

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r})"
        )


# ==========================================================
# Hook
# ==========================================================


@dataclass(slots=True)
class Hook:
    """
    Runtime hook descriptor.
    """

    name: str

    handler: Any

    priority: int = 100

    once: bool = False

    enabled: bool = True

    id: str = field(
        default_factory=lambda: str(uuid4()),
    )

    def __call__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        if not self.enabled:
            return None

        return self.handler(
            *args,
            **kwargs,
        )

    def enable(self) -> None:

        self.enabled = True

    def disable(self) -> None:

        self.enabled = False

    @property
    def callable(self) -> bool:

        return callable(
            self.handler,
        )

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"priority={self.priority}, "
            f"enabled={self.enabled})"
        )


# ==========================================================
# Hook Handle
# ==========================================================


@dataclass(slots=True)
class HookHandle:
    """
    Handle returned after hook registration.
    """

    registry: Any

    hook: Hook

    def unregister(self) -> None:
        """
        Remove the hook from its registry.
        """

        if self.registry is None:
            return

        self.registry.unregister(
            self.hook.name,
            self.hook.handler,
        )

    def enable(self) -> None:

        self.hook.enable()

    def disable(self) -> None:

        self.hook.disable()

    @property
    def enabled(self) -> bool:

        return self.hook.enabled

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"hook={self.hook.name!r}, "
            f"enabled={self.enabled})"
        )