"""Base contract for reasoning strategies."""

from abc import ABC

from ..core.base import ReasoningStrategy


class BaseReasoningStrategy(ReasoningStrategy, ABC):
    """Base class for all concrete reasoning strategies."""

    pass


__all__ = [
    "BaseReasoningStrategy",
]
