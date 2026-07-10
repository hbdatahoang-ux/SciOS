# scios/cognitive_core/reflection/state.py

"""
SciOS Reflection State
======================

ReflectionState manages the current status of the reflection process.
It tracks whether reflection is idle, running, completed, or errored.
"""

from __future__ import annotations


class ReflectionState:
    """
    ReflectionState maintains the current state of reflection.
    """

    def __init__(self) -> None:
        self._state: str = "idle"

    def set_state(self, state: str) -> None:
        """
        Set the current reflection state.
        Allowed values: idle, reflecting, completed, error.
        """
        if state not in {"idle", "reflecting", "completed", "error"}:
            raise ValueError(f"Invalid reflection state: {state}")
        self._state = state

    def get_state(self) -> str:
        """
        Return the current reflection state.
        """
        return self._state

    def reset(self) -> None:
        """
        Reset reflection state to idle.
        """
        self._state = "idle"

    def is_idle(self) -> bool:
        """
        Check if reflection is idle.
        """
        return self._state == "idle"

    def is_reflecting(self) -> bool:
        """
        Check if reflection is in progress.
        """
        return self._state == "reflecting"

    def is_completed(self) -> bool:
        """
        Check if reflection has completed.
        """
        return self._state == "completed"

    def is_error(self) -> bool:
        """
        Check if reflection is in error state.
        """
        return self._state == "error"

    def __repr__(self) -> str:
        return f"<ReflectionState state={self._state}>"
