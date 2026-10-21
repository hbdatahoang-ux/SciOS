"""Governance context model for SciOS runtime integration.

This module provides the GovernanceContext dataclass, which acts as an immutable
control-plane envelope carrying identity, authorization scope, and constraint
metadata across the execution boundary (Agent -> Router -> Executor).
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any


@dataclass(frozen=True, slots=True)
class GovernanceContext:
    """Immutable control-plane envelope for runtime governance execution."""

    request_id: str
    execution_id: str
    actor: str
    capabilities: frozenset[str] = field(default_factory=frozenset)
    policy_scope: Mapping[str, Any] = field(default_factory=dict)
    parent_execution_id: str | None = None
    source: str | None = None
    timeout: float | None = None
    execution_limits: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate structural integrity and freeze mutable inputs."""
        if not isinstance(self.request_id, str) or not self.request_id.strip():
            raise ValueError(
                "GovernanceContext 'request_id' must be a non-empty string"
            )

        if not isinstance(self.execution_id, str) or not self.execution_id.strip():
            raise ValueError(
                "GovernanceContext 'execution_id' must be a non-empty string"
            )

        if not isinstance(self.actor, str) or not self.actor.strip():
            raise ValueError(
                "GovernanceContext 'actor' must be a non-empty string"
            )

        if not isinstance(self.capabilities, (set, frozenset)):
            raise TypeError(
                "GovernanceContext 'capabilities' must be a set or frozenset of strings"
            )

        frozen_caps = frozenset(self.capabilities)
        for item in frozen_caps:
            if not isinstance(item, str):
                raise TypeError(
                    f"Capability item '{item!r}' must be a string"
                )
        object.__setattr__(self, "capabilities", frozen_caps)

        if not isinstance(self.policy_scope, Mapping):
            raise TypeError(
                "GovernanceContext 'policy_scope' must be a Mapping"
            )

        for key in self.policy_scope:
            if not isinstance(key, str):
                raise TypeError(
                    f"Policy scope key '{key!r}' must be a string"
                )

        object.__setattr__(
            self,
            "policy_scope",
            MappingProxyType(dict(self.policy_scope)),
        )

        if self.parent_execution_id is not None:
            if (
                not isinstance(self.parent_execution_id, str)
                or not self.parent_execution_id.strip()
            ):
                raise ValueError(
                    "GovernanceContext 'parent_execution_id', if provided, "
                    "must be a non-empty string"
                )

        if self.source is not None:
            if not isinstance(self.source, str) or not self.source.strip():
                raise ValueError(
                    "GovernanceContext 'source', if provided, "
                    "must be a non-empty string"
                )

        if self.timeout is not None:
            if (
                not isinstance(self.timeout, (int, float))
                or isinstance(self.timeout, bool)
                or self.timeout < 0
            ):
                raise ValueError(
                    "GovernanceContext 'timeout', if provided, "
                    "must be a non-negative number"
                )

        if not isinstance(self.execution_limits, Mapping):
            raise TypeError(
                "GovernanceContext 'execution_limits' must be a Mapping"
            )

        for key in self.execution_limits:
            if not isinstance(key, str):
                raise TypeError(
                    f"Execution limit key '{key!r}' must be a string"
                )

        object.__setattr__(
            self,
            "execution_limits",
            MappingProxyType(dict(self.execution_limits)),
        )
