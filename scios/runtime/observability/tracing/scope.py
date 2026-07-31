"""
SciOS Runtime Observability
===========================

Tracing scope utilities.

Provides context managers and decorators for
TraceManager trace/span lifecycle management.

Python 3.11+
"""

from __future__ import annotations


# ==============================================================================
# Part 1. Foundation
# ==============================================================================

from functools import wraps
from types import TracebackType
from typing import Any, Callable

from .manager import TraceManager
from .manager import ManagerValidationError
import copy


__all__: list[str] = [
    "ScopeError",
    "ScopeValidationError",
    "ScopeStateError",
    "ScopeClosedError",
    "ScopeEnterError",
    "ScopeExitError",
    "TraceScopeError",
    "SpanScopeError",
    "BaseScope",
    "TraceScope",
    "SpanScope",
    "trace_scope",
    "span_scope",
]


# ==============================================================================
# Part 2. Constants
# ==============================================================================

SCOPE_VERSION: str = "1.0.0"

SCOPE_API_VERSION: str = "1"


DEFAULT_TRACE_SCOPE_NAME: str = "TraceScope"

DEFAULT_SPAN_SCOPE_NAME: str = "SpanScope"


DEFAULT_TRACE_NAME: str = "Trace"

DEFAULT_SPAN_NAME: str = "Span"


DEFAULT_AUTO_FINISH: bool = True

DEFAULT_PROPAGATE_EXCEPTION: bool = True



# ==============================================================================
# Part 3. Exceptions
# ==============================================================================


class ScopeError(RuntimeError):
    """
    Base exception for scope subsystem.
    """



class ScopeValidationError(ScopeError):
    """
    Invalid scope configuration.
    """



class ScopeStateError(ScopeError):
    """
    Invalid scope lifecycle state.
    """



class ScopeClosedError(ScopeStateError):
    """
    Scope already closed.
    """



class ScopeEnterError(ScopeStateError):
    """
    Failed entering scope.
    """



class ScopeExitError(ScopeStateError):
    """
    Failed exiting scope.
    """



class TraceScopeError(ScopeError):
    """
    TraceScope specific error.
    """



class SpanScopeError(ScopeError):
    """
    SpanScope specific error.
    """



# ==============================================================================
# Part 4. BaseScope
# ==============================================================================


class BaseScope:
    """
    Shared lifecycle implementation for TraceScope and SpanScope.
    """


    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        manager: TraceManager,
        name: str,
        **attributes: Any,
    ) -> None:


        if not isinstance(
            manager,
            TraceManager,
        ):
            raise ScopeValidationError(
                "manager must be TraceManager"
            )


        if (
            not isinstance(
                name,
                str,
            )
            or not name.strip()
        ):
            raise ScopeValidationError(
                "name cannot be empty"
            )


        self._manager = manager

        self._name = name.strip()


        self._attributes: dict[str, Any] = dict(
            attributes
        )


        self._object: Any | None = None

        self._entered: bool = False

        self._closed: bool = False



    # ------------------------------------------------------------------
    # Internal Utilities
    # ------------------------------------------------------------------

    def _set_runtime_object(
        self,
        obj: Any,
    ) -> Any:


        self._object = obj

        self._entered = True

        self._closed = False


        return obj



    def _clear_runtime_object(
        self,
    ) -> None:


        self._object = None

        self._entered = False

        self._closed = True



    def _ensure_entered(
        self,
    ) -> None:


        if not self._entered:

            raise ScopeStateError(
                "Scope has not been entered"
            )



    def _ensure_open(
        self,
    ) -> None:


        if self._closed:

            raise ScopeClosedError(
                "Scope is closed"
            )



    # ------------------------------------------------------------------
    # Runtime Bootstrap
    # ------------------------------------------------------------------

    def _ensure_manager_ready(
        self,
    ) -> None:
        """
        Ensure TraceManager has a default tracer.

        TraceManager.start_trace()
        requires at least one registered tracer.
        """

        try:

            tracers = getattr(
                self._manager,
                "_tracers",
                None,
            )


            if tracers:

                return



            # ----------------------------------------------------------
            # Try public registration API
            # ----------------------------------------------------------

            register = getattr(
                self._manager,
                "register",
                None,
            )


            if callable(register):

                register(
                    "default",
                )

                if getattr(
                    self._manager,
                    "_tracers",
                    None,
                ):

                    return



            # ----------------------------------------------------------
            # Try register_tracer API
            # ----------------------------------------------------------

            register_tracer = getattr(
                self._manager,
                "register_tracer",
                None,
            )


            if callable(register_tracer):

                try:

                    register_tracer(
                        "default",
                    )

                except TypeError:

                    register_tracer()



                if getattr(
                    self._manager,
                    "_tracers",
                    None,
                ):

                    return



            # ----------------------------------------------------------
            # Last resort: internal minimal tracer
            # ----------------------------------------------------------

            tracers = getattr(
                self._manager,
                "_tracers",
                None,
            )


            if isinstance(
                tracers,
                dict,
            ):

                from .tracer import Tracer


                tracer = Tracer(
                    name="default",
                )


                tracers["default"] = tracer



        except Exception:

            pass



    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def manager(
        self,
    ) -> TraceManager:

        return self._manager



    @property
    def name(
        self,
    ) -> str:

        return self._name



    @property
    def attributes(
        self,
    ) -> dict[str, Any]:

        return dict(
            self._attributes
        )



    @property
    def runtime_object(
        self,
    ) -> Any | None:

        return self._object



    @property
    def active(
        self,
    ) -> bool:

        return (
            self._entered
            and not self._closed
        )



    # ------------------------------------------------------------------
    # Python Protocols
    # ------------------------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(name='{self._name}', "
            f"active={self.active})"
        )



# ==============================================================================
# Part 5. TraceScope
# ==============================================================================


class TraceScope(BaseScope):
    """
    Context manager and decorator for trace lifecycle.
    """

    # ------------------------------------------------------------------
    # Context Manager
    # ------------------------------------------------------------------

    def __enter__(
        self,
    ) -> Any:

        if self._entered:
            raise ScopeStateError(
                "TraceScope already entered."
            )

        try:

            self._ensure_manager_ready()

            trace = self._manager.start_trace(
                self._name,
            )

            for key, value in self._attributes.items():

                if hasattr(
                    trace,
                    "set_attribute",
                ):
                    trace.set_attribute(
                        key,
                        value,
                    )

            return self._set_runtime_object(
                trace
            )

        except ManagerValidationError as exc:

            raise ValueError(
                str(exc)
            ) from exc

        except Exception as exc:

            raise ScopeEnterError(
                str(exc)
            ) from exc

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> bool:

        self._ensure_entered()

        try:

            trace = self._object

            if trace is not None:

                self._manager.finish_trace(
                    trace
                )

        except Exception as exc:

            raise ScopeExitError(
                str(exc)
            ) from exc

        finally:

            self._clear_runtime_object()

        return False

    # ------------------------------------------------------------------
    # Decorator
    # ------------------------------------------------------------------

    def __call__(
        self,
        func: Callable[..., Any],
    ) -> Callable[..., Any]:

        @wraps(func)
        def wrapper(
            *args: Any,
            **kwargs: Any,
        ) -> Any:

            with TraceScope(
                self._manager,
                self._name,
                **self._attributes,
            ):
                return func(
                    *args,
                    **kwargs,
                )

        return wrapper

# ==============================================================================
# Part 6. SpanScope
# ==============================================================================


class SpanScope(BaseScope):
    """
    Context manager and decorator for span lifecycle.
    """

    def __enter__(
        self,
    ) -> Any:

        if self._entered:

            raise ScopeStateError(
                "SpanScope already entered."
            )

        try:

            span = self._manager.start_span(
                self._name,
            )

            for key, value in self._attributes.items():

                span.set_attribute(
                    key,
                    value,
                )

            return self._set_runtime_object(
                span
            )


        except Exception as exc:

            raise ScopeEnterError(
                str(exc)
            ) from exc



    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> bool:

        self._ensure_entered()

        try:

            if self._object is not None:

                self._object.finish()

        except Exception as exc:

            raise ScopeExitError(
                str(exc)
            ) from exc


        finally:

            self._clear_runtime_object()


        return False



    def __call__(
        self,
        func: Callable[..., Any],
    ) -> Callable[..., Any]:

        @wraps(func)
        def wrapper(
            *args: Any,
            **kwargs: Any,
        ) -> Any:

            with SpanScope(
                self._manager,
                self._name,
                **self._attributes,
            ):

                return func(
                    *args,
                    **kwargs,
                )

        return wrapper



# ==============================================================================
# Part 7. Functional API
# ==============================================================================


def trace_scope(
    manager: TraceManager,
    name: str = DEFAULT_TRACE_NAME,
    **attributes: Any,
) -> TraceScope:

    return TraceScope(
        manager,
        name,
        **attributes,
    )



def span_scope(
    manager: TraceManager,
    name: str = DEFAULT_SPAN_NAME,
    **attributes: Any,
) -> SpanScope:

    return SpanScope(
        manager,
        name,
        **attributes,
    )



# ==============================================================================
# Part 8. Diagnostics
# ==============================================================================


def _scope_summary(
    self,
) -> dict[str, Any]:

    return {

        "scope":
            self.__class__.__name__,

        "name":
            self._name,

        "active":
            self.active,

        "closed":
            self._closed,

        "runtime_object":
            self._object is not None,

        "attribute_count":
            len(self._attributes),
    }



def _scope_health(
    self,
) -> bool:

    try:

        if not isinstance(
            self._manager,
            TraceManager,
        ):
            return False


        if not self._name.strip():

            return False


        if self._entered and self._object is None:

            return False


        return True


    except Exception:

        return False



BaseScope.summary = _scope_summary

BaseScope.health = _scope_health



# ==============================================================================
# Part 9. Python Protocols
# ==============================================================================


def _scope_repr(
    self,
) -> str:

    return (

        f"{self.__class__.__name__}"

        f"(name={self._name!r}, "

        f"active={self.active!r})"

    )



def _scope_str(
    self,
) -> str:

    return (

        f"{self.__class__.__name__}"

        f"({self._name})"

    )



def _scope_bool(
    self,
) -> bool:

    return self.health()



BaseScope.__repr__ = _scope_repr

BaseScope.__str__ = _scope_str

BaseScope.__bool__ = _scope_bool



# ==============================================================================
# Part 10. Public API
# ==============================================================================


__all__ = [

    "DEFAULT_TRACE_SCOPE_NAME",
    "DEFAULT_SPAN_SCOPE_NAME",

    "DEFAULT_TRACE_NAME",
    "DEFAULT_SPAN_NAME",

    "ScopeError",
    "ScopeValidationError",
    "ScopeStateError",
    "ScopeClosedError",
    "ScopeEnterError",
    "ScopeExitError",

    "TraceScopeError",
    "SpanScopeError",

    "BaseScope",
    "TraceScope",
    "SpanScope",

    "trace_scope",
    "span_scope",

]