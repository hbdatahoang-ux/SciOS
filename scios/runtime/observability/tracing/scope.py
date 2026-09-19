"""
SciOS Runtime Observability
===========================

Tracing scope utilities.

Provides context managers and decorators for
TraceManager trace/span lifecycle management.

Python 3.11+
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from .manager import TraceManager


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


# ==============================================================================
# Part 2. Constants
# ==============================================================================

SCOPE_VERSION = "1.0.0"

SCOPE_API_VERSION = "1"

DEFAULT_TRACE_SCOPE_NAME = "TraceScope"

DEFAULT_SPAN_SCOPE_NAME = "SpanScope"

DEFAULT_TRACE_NAME = "Trace"

DEFAULT_SPAN_NAME = "Span"

DEFAULT_AUTO_FINISH = True

DEFAULT_PROPAGATE_EXCEPTION = True


# ==============================================================================
# Part 3. Exceptions
# ==============================================================================


class ScopeError(RuntimeError):
    """Base exception for scope subsystem."""


class ScopeValidationError(ScopeError):
    """Invalid scope configuration."""


class ScopeStateError(ScopeError):
    """Invalid scope lifecycle state."""


class ScopeClosedError(ScopeStateError):
    """Scope already closed."""


class ScopeEnterError(ScopeStateError):
    """Failed entering scope."""


class ScopeExitError(ScopeStateError):
    """Failed exiting scope."""


class TraceScopeError(ScopeError):
    """TraceScope specific error."""


class SpanScopeError(ScopeError):
    """SpanScope specific error."""


# ==============================================================================
# Part 4. BaseScope
# ==============================================================================


class BaseScope:
    """
    Shared lifecycle implementation for TraceScope and SpanScope.
    """

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

        self._attributes = dict(
            attributes
        )

        self._object: Any | None = None

        self._entered = False

        self._closed = False

    # --------------------------------------------------------------------------
    # Internal Utilities
    # --------------------------------------------------------------------------

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

    def _ensure_manager_ready(
        self,
    ) -> None:
        """
        Ensure TraceManager has a usable tracer.

        TraceManager.start_trace() may require
        a registered tracer.
        """

        try:

            tracers = getattr(
                self._manager,
                "_tracers",
                None,
            )

            if tracers:
                return

            register = getattr(
                self._manager,
                "register",
                None,
            )

            if callable(register):

                try:
                    register("default")
                except Exception:
                    pass

                tracers = getattr(
                    self._manager,
                    "_tracers",
                    None,
                )

                if tracers:
                    return

            register_tracer = getattr(
                self._manager,
                "register_tracer",
                None,
            )

            if callable(register_tracer):

                try:
                    register_tracer(
                        "default"
                    )

                except TypeError:

                    try:
                        register_tracer()
                    except Exception:
                        pass

                except Exception:
                    pass

                tracers = getattr(
                    self._manager,
                    "_tracers",
                    None,
                )

                if tracers:
                    return

            tracers = getattr(
                self._manager,
                "_tracers",
                None,
            )

            if isinstance(
                tracers,
                dict,
            ):

                try:

                    from .tracer import Tracer

                    tracers["default"] = Tracer(
                        name="default"
                    )

                except Exception:
                    pass

        except Exception:
            pass

    def _current_trace(
        self,
    ) -> Any | None:
        """Return the manager's current trace."""
        return self._manager.current_trace

    def _trace_is_active(
        self,
        trace: Any | None,
    ) -> bool:
        """
        Determine whether a trace can host this span.

        A trace remains usable while its lifecycle state is non-terminal.
        ``Trace.active`` is intentionally not used because the current
        Trace lifecycle model may report ``active=False`` for a created trace.
        """

        if trace is None:
            return False

        state = getattr(
            trace,
            "state",
            None,
        )

        if state is None:
            return True

        state_name = getattr(
            state,
            "name",
            str(state),
        )

        return str(state_name).lower() not in {
            "finished",
            "completed",
            "closed",
            "cancelled",
            "canceled",
        }
    # --------------------------------------------------------------------------
    # Properties
    # --------------------------------------------------------------------------

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

    # --------------------------------------------------------------------------
    # Diagnostics
    # --------------------------------------------------------------------------

    def summary(
        self,
    ) -> dict[str, Any]:

        return {
            "scope": self.__class__.__name__,
            "name": self._name,
            "active": self.active,
            "closed": self._closed,
            "runtime_object": self._object is not None,
            "attribute_count": len(
                self._attributes
            ),
        }

    def health(
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

            if (
                self._entered
                and self._object is None
            ):
                return False

            return True

        except Exception:
            return False

    # --------------------------------------------------------------------------
    # Python Protocols
    # --------------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(name={self._name!r}, "
            f"active={self.active!r}, "
            f"attributes={self._attributes!r})"
        )

    def __str__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}"
            f"({self._name})"
        )

    def __bool__(
        self,
    ) -> bool:

        return self.health()


# ==============================================================================
# Part 5. TraceScope
# ==============================================================================


class TraceScope(BaseScope):
    """
    Context manager and decorator for trace lifecycle.

    TraceScope owns the trace that it creates.

    Responsibilities
    ----------------
    - Start exactly one trace on entry.
    - Apply scope attributes to the trace.
    - Record exceptions raised inside the scope when supported.
    - Finish the trace on exit.
    - Never swallow exceptions from the wrapped block.
    - Support decorator usage.
    """

    # ==========================================================================
    # Context Manager
    # ==========================================================================

    def __enter__(
        self,
    ) -> Any:

        if self._entered:
            raise ScopeStateError(
                "TraceScope already entered."
            )

        try:

            # ------------------------------------------------------------------
            # Ensure the manager can create a trace.
            # ------------------------------------------------------------------

            self._ensure_manager_ready()

            # ------------------------------------------------------------------
            # TraceScope owns trace creation.
            # ------------------------------------------------------------------

            trace = self._manager.start_trace(
                self._name,
            )

            if trace is None:
                raise ScopeEnterError(
                    "Unable to create trace.",
                )

            # ------------------------------------------------------------------
            # Apply scope attributes.
            # ------------------------------------------------------------------

            setter = getattr(
                trace,
                "set_attribute",
                None,
            )

            if callable(setter):

                for key, value in self._attributes.items():

                    setter(
                        key,
                        value,
                    )

            else:

                # --------------------------------------------------------------
                # Compatibility fallback.
                # --------------------------------------------------------------

                for key, value in self._attributes.items():

                    try:
                        setattr(
                            trace,
                            key,
                            value,
                        )
                    except Exception:
                        pass

            # ------------------------------------------------------------------
            # Register runtime object.
            # ------------------------------------------------------------------

            return self._set_runtime_object(
                trace,
            )

        except ScopeError:
            raise

        except Exception as exc:

            raise ScopeEnterError(
                str(exc),
            ) from exc

    # ==========================================================================
    # Exit
    # ==========================================================================

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

                # ------------------------------------------------------------------
                # Record exception on the trace when supported.
                # ------------------------------------------------------------------

                if exc_value is not None:

                    record_exception = getattr(
                        trace,
                        "record_exception",
                        None,
                    )

                    if callable(record_exception):

                        try:
                            record_exception(
                                exc_value,
                            )
                        except Exception:
                            pass

                # ------------------------------------------------------------------
                # TraceScope owns the trace.
                #
                # Therefore TraceScope is responsible for finishing it.
                # ------------------------------------------------------------------

                self._manager.finish_trace(
    trace,
)

        except ScopeError:
            raise

        except Exception as exc:

            raise ScopeExitError(
                str(exc),
            ) from exc

        finally:

            self._clear_runtime_object()

        # ----------------------------------------------------------------------
        # Never swallow exceptions raised by the wrapped block.
        # ----------------------------------------------------------------------

        return False

    # ==========================================================================
    # Decorator
    # ==========================================================================

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

    SpanScope delegates span creation entirely to TraceManager.

    Behavior
    --------
    - If an active trace exists, the span is created inside it.
    - If no active trace exists, an implicit trace is created first.
    - TraceManager remains the single authority for span creation.
    - Scope attributes are applied after span construction.
    - SpanScope owns the implicit trace only when it created it.
    - Nested SpanScope instances remain inside the existing trace.
    - The previous current trace is restored on exit.
    """

    def __init__(
        self,
        manager: TraceManager,
        name: str,
        **attributes: Any,
    ) -> None:
        super().__init__(
            manager,
            name,
            **attributes,
        )

        self._previous_trace: Any | None = None

    # ==========================================================================
    # Trace Resolution
    # ==========================================================================

    def _current_trace(self) -> Any | None:
        """
        Return the TraceManager's current trace.

        TraceManager._trace is the single source of truth.
        Scope objects must never maintain a second current-trace state.
        """

        return self._manager.current_trace

    def _trace_is_active(
        self,
        trace: Any | None,
    ) -> bool:
        """
        Determine whether a trace can host this span.

        Trace.active is intentionally ignored because a Trace in
        the "created" state may report active=False while still
        being the current usable trace.
        """

        if trace is None:
            return False

        state = getattr(
            trace,
            "state",
            None,
        )

        if state is not None:

            state_name = getattr(
                state,
                "name",
                str(state),
            )

            if str(state_name).lower() in {
                "finished",
                "completed",
                "closed",
                "cancelled",
                "canceled",
            }:
                return False

        return True

    # ==========================================================================
    # Context Manager
    # ==========================================================================

    def __enter__(
        self,
    ) -> Any:
        """
        Enter the SpanScope and create a span.

        Lifecycle semantics
        -------------------
        SpanScope supports both explicit and standalone usage.

        1. If an active trace already exists, the span is created inside it.
        2. If no active trace exists, SpanScope creates one implicit trace.
        3. TraceManager remains the single authority for span creation.
        4. ``component`` and ``task_id`` are semantic Span fields and are
        therefore passed to ``TraceManager.start_span()``.
        5. Remaining attributes are applied through ``Span.set_attribute()``.
        6. An implicit trace is finished when the scope exits.
        7. An externally owned trace is never finished by SpanScope.
        """

        # ==================================================================
        # Part 1. Scope State Validation
        # ==================================================================

        if self._entered:
            raise ScopeStateError(
                "SpanScope already entered."
            )

        # ==================================================================
        # Part 2. Reset Runtime Bookkeeping
        # ==================================================================

        self._implicit_trace = None

        # ------------------------------------------------------------------
        # Preserve the trace that existed before entering this scope.
        #
        # This is required for:
        # - nested scopes
        # - explicit trace ownership
        # - implicit trace ownership
        # - rollback
        # ------------------------------------------------------------------

        self._previous_trace = self._current_trace()

        try:

            # ==============================================================
            # Part 3. Ensure Manager Is Ready
            # ==============================================================

            self._ensure_manager_ready()

            # ==============================================================
            # Part 4. Resolve Trace
            #
            # Existing trace:
            #     reuse it
            #
            # No existing trace:
            #     create an implicit trace owned by this scope
            # ==============================================================

            trace = self._current_trace()

            if not self._trace_is_active(
                trace,
            ):
                trace = self._manager.start_trace(
                    DEFAULT_TRACE_NAME,
                )

                if trace is None:
                    raise ScopeEnterError(
                        "Unable to create implicit trace."
                    )

                self._implicit_trace = trace

            # ==============================================================
            # Part 5. Resolve Semantic Span Fields
            #
            # component and task_id are first-class Span fields.
            #
            # They MUST be supplied during Span construction rather than
            # being treated as ordinary attributes.
            # ==============================================================

            component = self._attributes.get(
                "component",
            )

            task_id = self._attributes.get(
                "task_id",
            )

            # ==============================================================
            # Part 6. Create Span
            #
            # TraceManager remains the single authority for span creation.
            # ==============================================================

            span = self._manager.start_span(
                self._name,
                component=component,
                task_id=task_id,
            )

            if span is None:
                raise ScopeEnterError(
                    "Unable to create span."
                )

            # ==============================================================
            # Part 7. Apply Ordinary Span Attributes
            #
            # component and task_id are excluded because they have already
            # been initialized as semantic Span fields.
            # ==============================================================

            setter = getattr(
                span,
                "set_attribute",
                None,
            )

            if not callable(setter):
                raise ScopeEnterError(
                    "Span does not support set_attribute()."
                )

            for key, value in self._attributes.items():

                if key in {
                    "component",
                    "task_id",
                }:
                    continue

                setter(
                    key,
                    value,
                )

            # ==============================================================
            # Part 8. Commit Scope Runtime State
            #
            # Do this only after every operation above succeeds.
            # ==============================================================

            return self._set_runtime_object(
                span,
            )

        except ScopeError:

            # ==============================================================
            # Part 9. Roll Back Implicit Trace
            # ==============================================================

            if self._implicit_trace is not None:

                try:
                    self._manager.finish_trace(
                        self._implicit_trace,
                    )
                except Exception:
                    # Rollback must never mask the original ScopeError.
                    pass

            self._implicit_trace = None
            self._previous_trace = None

            raise

        except Exception as exc:

            # ==============================================================
            # Part 10. Roll Back Implicit Trace
            # ==============================================================

            if self._implicit_trace is not None:

                try:
                    self._manager.finish_trace(
                        self._implicit_trace,
                    )
                except Exception:
                    # Preserve the original exception.
                    pass

            self._implicit_trace = None
            self._previous_trace = None

            raise ScopeEnterError(
                str(exc),
            ) from exc

    # ==========================================================================
    # Exit
    # ==========================================================================

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> bool:

        self._ensure_entered()

        try:

            # ------------------------------------------------------------------
            # Record exception on the span when supported.
            # ------------------------------------------------------------------

            if (
                self._object is not None
                and exc_value is not None
            ):

                record_exception = getattr(
                    self._object,
                    "record_exception",
                    None,
                )

                if callable(record_exception):

                    try:
                        record_exception(
                            exc_value,
                        )
                    except Exception:
                        pass

            # ------------------------------------------------------------------
            # Finish the current span.
            #
            # TraceManager owns active-span state.
            # ------------------------------------------------------------------

            if self._object is not None:

                self._manager.finish_span()

            # ------------------------------------------------------------------
            # Finish the implicit trace only when this scope created it.
            #
            # Explicitly pass the owned trace object so that trace
            # finalization cannot accidentally target another trace.
            # ------------------------------------------------------------------

            if self._implicit_trace is not None:

                self._manager.finish_trace(
                    self._implicit_trace,
                )

        except ScopeError:
            raise

        except Exception as exc:

            raise ScopeExitError(
                str(exc),
            ) from exc

        finally:

            # ------------------------------------------------------------------
            # Clear scope-local runtime state.
            #
            # TraceManager.current_trace is the single source of truth.
            # SpanScope must not restore or mutate manager trace state here.
            # ------------------------------------------------------------------

            self._clear_runtime_object()

            self._implicit_trace = None
            self._previous_trace = None

        # ----------------------------------------------------------------------
        # Never swallow exceptions raised by the wrapped block.
        # ----------------------------------------------------------------------

        return False

    # ==========================================================================
    # Decorator
    # ==========================================================================

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
# Part 8. Public API
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
