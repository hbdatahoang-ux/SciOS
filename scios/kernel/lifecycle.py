"""
SciOS Kernel Lifecycle
======================

Kernel lifecycle state machine.

Responsibilities
----------------
- Kernel state transitions
- Transition validation
- Idempotent lifecycle management
- Runtime status reporting
"""

from __future__ import annotations

from enum import Enum

__all__ = [
    "KernelState",
    "LifecycleManager",
]


class KernelState(str, Enum):
    """
    Kernel lifecycle states.
    """

    STOPPED = "stopped"

    BOOTING = "booting"

    READY = "running"

    STOPPING = "stopping"


class LifecycleManager:
    """
    Finite-state machine for the SciOS kernel.

    State Diagram
    -------------

        STOPPED
            │
            ▼
        BOOTING
            │
            ▼
        READY
            │
            ▼
        STOPPING
            │
            ▼
        STOPPED
    """

    _ALLOWED = {

        KernelState.STOPPED: {
            KernelState.BOOTING,
        },

        KernelState.BOOTING: {
            KernelState.READY,
            KernelState.STOPPED,
        },

        KernelState.READY: {
            KernelState.STOPPING,
        },

        KernelState.STOPPING: {
            KernelState.STOPPED,
        },
    }

    def __init__(self) -> None:

        self._state = KernelState.STOPPED

    # =====================================================
    # Properties
    # =====================================================

    @property
    def state(self) -> KernelState:
        return self._state

    @property
    def running(self) -> bool:
        return self._state is KernelState.READY

    @property
    def booted(self) -> bool:
        return self.running

    # =====================================================
    # Transition
    # =====================================================

    def transition(
        self,
        state: KernelState,
    ) -> None:
        """
        Perform a validated lifecycle transition.
        """

        if state is self._state:
            return

        allowed = self._ALLOWED[self._state]

        if state not in allowed:

            raise RuntimeError(
                f"Illegal lifecycle transition: "
                f"{self._state.value} -> {state.value}"
            )

        self._state = state

    # =====================================================
    # Force
    # =====================================================

    def force(
        self,
        state: KernelState,
    ) -> None:
        """
        Force lifecycle state.

        Intended only for emergency recovery
        during failed boot sequences.
        """

        self._state = state

    # =====================================================
    # Helpers
    # =====================================================

    def reset(self) -> None:
        """
        Reset lifecycle.
        """

        self._state = KernelState.STOPPED

    # =====================================================
    # Status
    # =====================================================

    def status(self) -> dict[str, object]:

        return {
            "state": self._state.value,
            "booted": self.booted,
            "running": self.running,
        }

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:

        return (
            "LifecycleManager("
            f"state='{self._state.value}')"
        )