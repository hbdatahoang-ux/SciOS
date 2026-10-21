from collections.abc import Callable
from typing import Any

from .ref import OperationRef
from .registry import OperationRegistry


class OperationResolver:
    """Resolves an OperationRef to a registered callable."""

    def __init__(self, registry: OperationRegistry) -> None:
        self._registry = registry

    def resolve(
        self,
        ref: OperationRef,
    ) -> Callable[..., Any]:
        return self._registry.require(ref)

    def exists(self, ref: OperationRef) -> bool:
        return self._registry.exists(ref)
