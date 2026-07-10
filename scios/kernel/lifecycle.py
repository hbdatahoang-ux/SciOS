"""
SciOS Kernel Lifecycle
======================

Manages the lifecycle state of the Kernel.

Responsibilities
----------------
- Track Kernel state transitions.
- Provide lifecycle control methods (boot, stop, restart).
- Ensure valid state transitions.
"""

from __future__ import annotations
from typing import Optional

from .state import KernelState


__all__ = ["LifecycleManager"]


class LifecycleManager:
    """
    Lifecycle controller for the Kernel.
    """

    def __init__(self, kernel: "Kernel") -> None:
        self.kernel = kernel
        self._state: KernelState = KernelState.CREATED

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def state(self) -> KernelState:
        """Current lifecycle state."""
        return self._state

    # ==========================================================
    # Lifecycle operations
    # ==========================================================

    def boot(self) -> None:
        """Boot the kernel into RUNNING state."""
        if self._state not in {KernelState.CREATED, KernelState.STOPPED}:
            raise RuntimeError(f"Cannot boot from state {self._state}")
        self._state = KernelState.RUNNING

    def stop(self) -> None:
        """Stop the kernel."""
        if self._state != KernelState.RUNNING:
            raise RuntimeError(f"Cannot stop from state {self._state}")
        self._state = KernelState.STOPPED

    def restart(self) -> None:
        """Restart the kernel."""
        if self._state != KernelState.RUNNING:
            raise RuntimeError(f"Cannot restart from state {self._state}")
        self._state = KernelState.RESTARTING
        # transition back to RUNNING
        self._state = KernelState.RUNNING

    # ==========================================================
    # Utilities
    # ==========================================================

    def reset(self) -> None:
        """Reset lifecycle back to CREATED."""
        self._state = KernelState.CREATED

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __repr__(self) -> str:
        return f"LifecycleManager(state={self._state})"
