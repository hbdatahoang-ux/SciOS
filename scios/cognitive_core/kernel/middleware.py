"""
SciOS Cognitive Middleware
==========================

Middleware layer for CognitivePipeline.

Responsibilities:
- Before stage interception
- After stage interception
- Runtime context transformation
- Extensible pipeline hooks
- Lifecycle management
- Diagnostics

Python 3.11+
"""

from __future__ import annotations


from typing import (
    Any,
    Callable,
)


__all__ = [
    "MiddlewareManager",
]



Middleware = Callable[[Any], Any]



class MiddlewareManager:
    """
    Middleware execution manager.

    Pipeline flow:

        before middleware
                |
                v
              Stage
                |
                v
        after middleware


    Middleware contract:

        def middleware(context):
            ...
            return context

    Returning None keeps current context.
    Returning object replaces context.
    """



    # ======================================================
    # Construction
    # ======================================================

    def __init__(
        self,
    ) -> None:


        self._before: list[Middleware] = []

        self._after: list[Middleware] = []


        self._executions: int = 0

        self._state: str = "created"



    # ======================================================
    # Registration
    # ======================================================

    def add_before(
        self,
        middleware: Middleware,
    ) -> None:
        """
        Register before-stage middleware.
        """

        if middleware not in self._before:

            self._before.append(
                middleware
            )



    def add_after(
        self,
        middleware: Middleware,
    ) -> None:
        """
        Register after-stage middleware.
        """

        if middleware not in self._after:

            self._after.append(
                middleware
            )



    def remove_before(
        self,
        middleware: Middleware,
    ) -> None:


        if middleware in self._before:

            self._before.remove(
                middleware
            )



    def remove_after(
        self,
        middleware: Middleware,
    ) -> None:


        if middleware in self._after:

            self._after.remove(
                middleware
            )



    def clear(
        self,
    ) -> None:
        """
        Remove all middleware.
        """

        self._before.clear()

        self._after.clear()



    # ======================================================
    # Lifecycle
    # ======================================================

    def reset(
        self,
    ) -> None:
        """
        Reset runtime state.

        IMPORTANT:
            Keep middleware registration.

        Used by:
            CognitivePipeline.reset()
        """

        self._executions = 0

        self._state = "created"



    # ======================================================
    # Runtime Execution
    # ======================================================

    def before_stage(
        self,
        stage,
        context,
    ):
        """
        Execute before-stage middleware.
        """

        self._state = "active"


        for middleware in self._before:

            result = middleware(
                context
            )


            if result is not None:

                context = result


            self._executions += 1



        return context



    def after_stage(
        self,
        stage,
        context,
    ):
        """
        Execute after-stage middleware.
        """

        self._state = "active"


        for middleware in self._after:

            result = middleware(
                context
            )


            if result is not None:

                context = result


            self._executions += 1



        return context



    # ======================================================
    # Compatibility API
    # ======================================================

    def apply_before(
        self,
        context,
    ):
        """
        Backward compatible before execution.
        """

        return self.before_stage(
            None,
            context,
        )



    def apply_after(
        self,
        context,
    ):
        """
        Backward compatible after execution.
        """

        return self.after_stage(
            None,
            context,
        )



    # ======================================================
    # Diagnostics
    # ======================================================

    @property
    def before_count(
        self,
    ) -> int:

        return len(
            self._before
        )



    @property
    def after_count(
        self,
    ) -> int:

        return len(
            self._after
        )



    @property
    def executions(
        self,
    ) -> int:

        return self._executions



    def status(
        self,
    ) -> dict[str, Any]:

        return {

            "state":
                self._state,

            "before":
                self.before_count,

            "after":
                self.after_count,

            "executions":
                self.executions,

        }



    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Serializable runtime snapshot.
        """

        return {

            "state":
                self._state,

            "executions":
                self._executions,

            "before_count":
                self.before_count,

            "after_count":
                self.after_count,

        }



    # ======================================================
    # Python Protocols
    # ======================================================

    def __len__(
        self,
    ) -> int:

        return (
            self.before_count
            +
            self.after_count
        )



    def __bool__(
        self,
    ) -> bool:

        return len(self) > 0



    def __repr__(
        self,
    ) -> str:

        return (
            "MiddlewareManager("
            f"before={self.before_count}, "
            f"after={self.after_count}, "
            f"executions={self.executions}"
            ")"
        )