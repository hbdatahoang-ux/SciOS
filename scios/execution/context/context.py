from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
import copy


@dataclass(frozen=True)
class ExecutionContext:
    """
    ExecutionContext = Process Address Space of SciOS

    Immutable snapshot-based context.
    """

    # -------------------------
    # Identity Layer
    # -------------------------
    context_id: UUID = field(default_factory=uuid4)
    node_id: Optional[UUID] = None
    graph_id: Optional[UUID] = None
    parent_context_id: Optional[UUID] = None
    session_id: Optional[str] = None

    timestamp: datetime = field(default_factory=datetime.utcnow)

    # -------------------------
    # Goal Layer
    # -------------------------
    goal: Optional[str] = None
    subgoal: Optional[str] = None

    # -------------------------
    # Variable Scope (Compiler-style)
    # -------------------------
    variables: dict[str, Any] = field(default_factory=dict)

    # -------------------------
    # Memory Layer
    # -------------------------
    memory: dict[str, Any] = field(default_factory=dict)

    # -------------------------
    # Knowledge Layer
    # -------------------------
    knowledge: dict[str, Any] = field(default_factory=dict)

    # -------------------------
    # Resources Layer
    # -------------------------
    resources: dict[str, Any] = field(default_factory=dict)

    # -------------------------
    # Output Layer
    # -------------------------
    outputs: dict[str, Any] = field(default_factory=dict)

    # -------------------------
    # Metrics Layer
    # -------------------------
    metrics: dict[str, Any] = field(default_factory=dict)

    # -------------------------
    # Metadata (extensible ABI-safe)
    # -------------------------
    metadata: dict[str, Any] = field(default_factory=dict)

    # =========================================================
    # Copy-on-Write mutation API
    # =========================================================

    def fork(self, **overrides) -> "ExecutionContext":
        """
        Create new immutable context snapshot.
        """
        data = self.__dict__.copy()
        data.update(overrides)
        return ExecutionContext(**data)

    def update(self, **kwargs) -> "ExecutionContext":
        """
        Functional update (never mutates original).
        """
        return self.fork(**kwargs)

    # =========================================================
    # Scope resolution (compiler-style)
    # =========================================================

    def resolve(self, key: str, default=None) -> Any:
        """
        Hierarchical lookup (like lexical scope).
        """
        if key in self.variables:
            return self.variables[key]
        if key in self.memory:
            return self.memory[key]
        if key in self.knowledge:
            return self.knowledge[key]
        return default

    # =========================================================
    # Snapshot hash (for replay determinism)
    # =========================================================

    def hash(self) -> str:
        """
        Lightweight deterministic fingerprint.
        """
        return str(hash((
            self.context_id,
            frozenset(self.variables.items()),
            frozenset(self.memory.items()),
            frozenset(self.knowledge.items())
        )))
