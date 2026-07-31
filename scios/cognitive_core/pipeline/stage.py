"""
SciOS Cognitive Core Pipeline Stage
===================================

Base stage abstraction for Cognitive Pipeline execution.

Provides:
- BaseStage protocol
- Stage implementation
- PipelineStage backward compatibility alias
"""

from __future__ import annotations

from typing import (
    Any,
    Dict,
    Protocol,
    Callable,
)


__all__ = [
    "BaseStage",
    "Stage",
    "PipelineStage",
]


# ==========================================================
# Base Stage Protocol
# ==========================================================

class BaseStage(Protocol):
    """
    Standard interface for pipeline stages.

    A stage receives a dictionary payload,
    processes it, and returns updated payload.
    """

    name: str

    def process(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute stage processing.
        """
        ...


# ==========================================================
# Stage Implementation
# ==========================================================

class Stage:
    """
    Generic pipeline stage.

    Supports:

    - callable handlers
    - objects implementing process()

    Example
    -------
    >>> stage = Stage(
    ...     "normalize",
    ...     lambda x: x
    ... )
    """

    def __init__(
        self,
        name: str,
        handler: Any,
    ) -> None:

        self.name = name
        self.handler = handler


    # ------------------------------------------------------
    # Execution
    # ------------------------------------------------------

    def process(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute stage handler.
        """

        if callable(self.handler):

            result = self.handler(data)

        elif hasattr(
            self.handler,
            "process",
        ):

            result = self.handler.process(data)

        else:

            raise TypeError(
                f"Invalid handler for stage '{self.name}'"
            )


        if not isinstance(
            result,
            dict,
        ):

            raise TypeError(
                f"Stage '{self.name}' must return dict"
            )


        return result


    # ------------------------------------------------------
    # Metadata
    # ------------------------------------------------------

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return stage metadata.
        """

        return {

            "name":
                self.name,

            "handler":
                getattr(
                    self.handler,
                    "__name__",
                    type(
                        self.handler
                    ).__name__,
                ),

        }


    # ------------------------------------------------------
    # Python Protocol
    # ------------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return (
            f"Stage("
            f"name='{self.name}', "
            f"handler={self.handler!r})"
        )


# ==========================================================
# Backward Compatibility
# ==========================================================

"""
Legacy API compatibility.

Older SciOS tests/modules used:

    PipelineStage

New API uses:

    Stage
"""

PipelineStage = Stage