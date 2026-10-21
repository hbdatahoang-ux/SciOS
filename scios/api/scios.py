"""
SciOS Public API
================

Stable public facade for the Scientific Cognitive Operating System (SciOS).

This module exposes the primary entry point to the entire SciOS platform.
Applications should interact exclusively with :class:`SciOS` instead of
accessing kernel, runtime, or subsystem implementations directly.

Design Goals
------------
- Stable public API
- Thin facade over Kernel
- Backward compatible
- Production ready
- Easy to extend
"""

from __future__ import annotations

from typing import Any

from scios.kernel.kernel import Kernel

__all__ = [
    "SciOS",
]


class SciOS:
    """
    Public facade of the Scientific Cognitive Operating System.

    The facade intentionally exposes only a minimal set of stable APIs
    while hiding the internal architecture.

    Examples
    --------
    >>> from scios import SciOS
    >>> os = SciOS()
    >>> os.boot()
    >>> result = os.run("hello")
    >>> os.shutdown()
    """

    VERSION = "0.2.0"

    # ==========================================================
    # Construction
    # ==========================================================

    def __init__(self) -> None:
        """
        Create a new SciOS instance.
        """

        self._kernel = Kernel()

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def kernel(self) -> Kernel:
        """
        Read-only access to the underlying kernel.

        Primarily intended for debugging, testing,
        and advanced integrations.
        """

        return self._kernel

    @property
    def version(self) -> str:
        """
        Current SciOS version.
        """

        return self.VERSION

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def boot(self) -> bool:
        """
        Boot the operating system.

        Returns
        -------
        bool
            True if boot completed successfully.
        """

        self._kernel.boot()

        return True

    def shutdown(self) -> bool:
        """
        Shutdown the operating system.

        Returns
        -------
        bool
            True if shutdown completed successfully.
        """

        self._kernel.shutdown()

        return True

    def restart(self) -> bool:
        """
        Restart the operating system.

        Returns
        -------
        bool
            True if restart completed successfully.
        """

        self.shutdown()
        self.boot()

        return True

    # ==========================================================
    # Execution
    # ==========================================================

    def run(
        self,
        task: Any,
    ) -> Any:
        """
        Execute a task.

        Parameters
        ----------
        task:
            Arbitrary workload.

        Returns
        -------
        Any
            Execution result.
        """

        return self._kernel.run(task)

    # ==========================================================
    # Status
    # ==========================================================

    def status(self) -> dict[str, Any]:
        """
        Return a stable runtime status.

        The returned schema is considered part of the
        public SciOS API and should remain backward compatible.
        """

        status = dict(self._kernel.status())

        internal = status.get("state", "unknown")

        public_state = {
            "created": "created",
            "booting": "booting",
            "ready": "running",
            "running": "running",
            "stopping": "stopping",
            "stopped": "stopped",
        }.get(internal, internal)

        status["state"] = public_state
        status["booted"] = public_state == "running"
        status["version"] = self.version

        return status

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"version='{self.version}')"
        )

    def __str__(self) -> str:

        return f"SciOS {self.version}"
