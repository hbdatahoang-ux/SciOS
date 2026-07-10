from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class VariableScope:
    """
    VariableScope = Compiler-style lexical scope for ExecutionContext.
    Immutable, copy-on-write.
    """

    variables: dict[str, Any] = field(default_factory=dict)
    parent: Optional["VariableScope"] = None

    # =========================================================
    # Copy-on-Write mutation API
    # =========================================================

    def fork(self, **overrides) -> "VariableScope":
        """
        Create new immutable scope snapshot.
        """
        data = self.variables.copy()
        data.update(overrides)
        return VariableScope(variables=data, parent=self.parent)

    def extend(self, new_vars: dict[str, Any]) -> "VariableScope":
        """
        Create child scope with new variables.
        """
        return VariableScope(variables=new_vars, parent=self)

    # =========================================================
    # Lookup API
    # =========================================================

    def resolve(self, key: str, default=None) -> Any:
        """
        Hierarchical lookup (lexical scope).
        """
        if key in self.variables:
            return self.variables[key]
        if self.parent:
            return self.parent.resolve(key, default)
        return default

    def contains(self, key: str) -> bool:
        """
        Check if variable exists in scope chain.
        """
        if key in self.variables:
            return True
        if self.parent:
            return self.parent.contains(key)
        return False

    # =========================================================
    # Serialization
    # =========================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Flatten scope chain into dict.
        """
        result = {}
        if self.parent:
            result.update(self.parent.to_dict())
        result.update(self.variables)
        return result
