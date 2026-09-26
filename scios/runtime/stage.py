"""
SciOS Runtime Stage
===================

Base execution stage abstraction.

Python 3.11+
"""

from __future__ import annotations


from typing import Any


__all__ = [
    "Stage",
]



class Stage:
    """
    Runtime execution stage.

    A Stage represents one processing unit
    inside Pipeline.

    Lifecycle:

        initialize()
              |
              v
          execute()
              |
              v
            run()
              |
              v
          shutdown()

    """



    # ======================================================
    # Construction
    # ======================================================

    def __init__(
        self,
        name: str | None = None,
    ) -> None:
        """
        Create runtime stage.
        """


        self._name = (
            name
            or self.__class__.__name__
        )


        self.enabled: bool = True


        self.executions: int = 0


        self.errors: int = 0



        self.initialized: bool = False



    # ======================================================
    # Properties
    # ======================================================

    @property
    def name(self) -> str:
        """
        Stage name.
        """

        return self._name



    @name.setter
    def name(
        self,
        value: str,
    ) -> None:

        self._name = value



    @property
    def status(self) -> str:
        """
        Current stage status.
        """

        if not self.enabled:

            return "disabled"


        if self.initialized:

            return "ready"


        return "created"



    @property
    def healthy(self) -> bool:
        """
        Stage health state.
        """

        return self.errors == 0



    # ======================================================
    # Lifecycle
    # ======================================================

    def initialize(
        self,
    ) -> None:
        """
        Initialize stage.
        """

        self.initialized = True



    def shutdown(
        self,
    ) -> None:
        """
        Shutdown stage.
        """

        self.initialized = False



    def reset(
        self,
    ) -> None:
        """
        Reset runtime counters.
        """

        self.executions = 0

        self.errors = 0



    # ======================================================
    # Execution
    # ======================================================

    def run(
        self,
        context,
    ):
        """
        Override this method.

        Subclasses implement actual logic.
        """

        raise NotImplementedError(
            f"{self.__class__.__name__}.run() "
            "must be implemented"
        )



    def execute(
        self,
        context,
    ):
        """
        Execute stage safely.
        """


        if not self.enabled:

            return context



        try:

            self.executions += 1


            return self.run(
                context
            )


        except Exception:

            self.errors += 1

            raise



    # ======================================================
    # Enable / Disable
    # ======================================================

    def enable(
        self,
    ) -> None:

        self.enabled = True



    def disable(
        self,
    ) -> None:

        self.enabled = False



    # ======================================================
    # Diagnostics
    # ======================================================

    def status_dict(
        self,
    ) -> dict[str, Any]:
        """
        Runtime diagnostics.
        """

        return {

            "name":
                self.name,


            "status":
                self.status,


            "enabled":
                self.enabled,


            "initialized":
                self.initialized,


            "executions":
                self.executions,


            "errors":
                self.errors,


            "healthy":
                self.healthy,

        }



    def diagnostics(
        self,
    ) -> dict[str, Any]:

        return self.status_dict()



    # ======================================================
    # Protocols
    # ======================================================

    def __repr__(
        self,
    ) -> str:

        return (
            "Stage("
            f"name={self.name!r}, "
            f"enabled={self.enabled}, "
            f"executions={self.executions}"
            ")"
        )