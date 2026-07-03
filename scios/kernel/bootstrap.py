"""
SciOS Bootstrap
===============

Kernel bootstrap manager.

Responsible for bootstrapping and shutting down all
core kernel subsystems in a deterministic order.

Boot Order
----------
Lifecycle
    ↓
Context
    ↓
Registry
    ↓
EventBus
    ↓
Runtime
    ↓
READY

Shutdown Order
--------------
Runtime
    ↓
EventBus
    ↓
Registry
    ↓
Context
    ↓
STOPPED
"""

from __future__ import annotations

import logging

from .lifecycle import KernelState

__all__ = [
    "Bootstrap",
]

_LOG = logging.getLogger("SciOS.Bootstrap")


class Bootstrap:
    """
    SciOS kernel bootstrap manager.

    This class owns the initialization and shutdown
    sequence of every core subsystem.

    The operations are fully idempotent.
    """

    # ==========================================================
    # Boot
    # ==========================================================

    def boot(self, kernel) -> bool:
        """
        Boot the SciOS kernel.

        Returns
        -------
        bool
            True if the kernel is running.
        """

        if kernel.lifecycle.state is KernelState.READY:
            return True

        _LOG.info("Bootstrapping SciOS...")

        try:

            kernel.lifecycle.transition(
                KernelState.BOOTING
            )

            # --------------------------------------------------
            # Reset execution context
            # --------------------------------------------------

            kernel.context.reset()

            # --------------------------------------------------
            # Register core services
            # --------------------------------------------------

            kernel.registry.register(
                "runtime",
                kernel.runtime,
                overwrite=True,
            )

            kernel.registry.register(
                "eventbus",
                kernel.eventbus,
                overwrite=True,
            )

            kernel.registry.register(
                "context",
                kernel.context,
                overwrite=True,
            )

            # --------------------------------------------------
            # Boot runtime
            # --------------------------------------------------

            kernel.runtime.boot()

            # --------------------------------------------------
            # Ready
            # --------------------------------------------------

            kernel.lifecycle.transition(
                KernelState.READY
            )

            _LOG.info("SciOS boot completed.")

            return True

        except Exception:

            _LOG.exception(
                "Kernel boot failed."
            )

            # rollback
            try:
                kernel.runtime.shutdown()
            except Exception:
                pass

            try:
                kernel.registry.clear()
            except Exception:
                pass

            try:
                kernel.eventbus.clear()
            except Exception:
                pass

            try:
                kernel.context.reset()
            except Exception:
                pass

            kernel.lifecycle.force(
                KernelState.STOPPED
            )

            raise

    # ==========================================================
    # Shutdown
    # ==========================================================

    def shutdown(self, kernel) -> bool:
        """
        Shutdown the kernel.

        Returns
        -------
        bool
            True if shutdown succeeds.
        """

        if kernel.lifecycle.state is KernelState.STOPPED:
            return True

        _LOG.info("Shutting down SciOS...")

        kernel.lifecycle.transition(
            KernelState.STOPPING
        )

        # --------------------------------------------------
        # Runtime
        # --------------------------------------------------

        kernel.runtime.shutdown()

        # --------------------------------------------------
        # EventBus
        # --------------------------------------------------

        kernel.eventbus.clear()

        # --------------------------------------------------
        # Registry
        # --------------------------------------------------

        kernel.registry.clear()

        # --------------------------------------------------
        # Context
        # --------------------------------------------------

        kernel.context.reset()

        # --------------------------------------------------
        # Lifecycle
        # --------------------------------------------------

        kernel.lifecycle.transition(
            KernelState.STOPPED
        )

        _LOG.info("SciOS shutdown completed.")

        return True