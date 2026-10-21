from collections.abc import Callable
from typing import Any

from .ref import OperationRef


class OperationRegistry:
    """Registry mapping stable operation references to callables."""

    def __init__(self) -> None:
        self._operations: dict[OperationRef, Callable[..., Any]] = {}

    def register(
        self,
        ref: OperationRef,
        operation: Callable[..., Any],
    ) -> None:
        if not isinstance(ref, OperationRef):
            raise TypeError("ref must be an OperationRef")

        if not callable(operation):
            raise TypeError("operation must be callable")

        if ref in self._operations:
            raise ValueError(f"Operation already registered: {ref}")

        self._operations[ref] = operation

    def unregister(self, ref: OperationRef) -> None:
        self._operations.pop(ref, None)

    def get(
        self,
        ref: OperationRef,
    ) -> Callable[..., Any] | None:
        return self._operations.get(ref)

    def require(
        self,
        ref: OperationRef,
    ) -> Callable[..., Any]:
        operation = self.get(ref)
        if operation is None:
            raise KeyError(f"Operation not found: {ref}")
        return operation

    def exists(self, ref: OperationRef) -> bool:
        return ref in self._operations

    def list(self) -> tuple[OperationRef, ...]:
        return tuple(self._operations)

    def clear(self) -> None:
        self._operations.clear()
