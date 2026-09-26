# ==============================================================================
# SciOS Runtime Observability
# Trace Decorators
# ==============================================================================

from __future__ import annotations


# ==============================================================================
# Part 1. Module Header
# ==============================================================================

"""
SciOS Runtime Observability
===========================

Tracing decorators for function and method instrumentation.

Python 3.11+
"""


# ==============================================================================
# Part 2. Imports
# ==============================================================================

import asyncio
import functools

from typing import (
    Any,
    Callable,
    Dict,
    Mapping,
    Optional,
    ParamSpec,
    TypeVar,
)

from .manager import TraceManager
from .span import Span
from .trace import Trace


# ==============================================================================
# Part 3. Type Aliases
# ==============================================================================

P = ParamSpec("P")
R = TypeVar("R")

DecoratedCallable = Callable[P, R]
Metadata = Mapping[str, Any]
Attributes = Mapping[str, Any]


# ==============================================================================
# Part 4. Constants
# ==============================================================================

DEFAULT_TRACE_NAME: str = "function"
DEFAULT_SPAN_NAME: str = "function"

TRACE_DECORATOR_NAME: str = "trace"
SPAN_DECORATOR_NAME: str = "span"

DEFAULT_RECORD_EXCEPTION: bool = True
DEFAULT_SET_ATTRIBUTES: bool = True

EMPTY_METADATA: Dict[str, Any] = {}
EMPTY_ATTRIBUTES: Dict[str, Any] = {}


# ==============================================================================
# Part 5. Exceptions
# ==============================================================================

class TraceDecoratorError(Exception):
    """Base exception for tracing decorator errors."""


class TraceDecoratorConfigurationError(TraceDecoratorError):
    """Raised when decorator configuration is invalid."""


class TraceDecoratorRuntimeError(TraceDecoratorError):
    """Raised when decorator runtime handling fails."""


# ==============================================================================
# Part 6. Internal Helpers
# ==============================================================================

def _resolve_manager(
    manager: Optional[TraceManager] = None,
) -> TraceManager:
    """
    Resolve a tracing manager.

    A supplied manager is preferred. Otherwise a default manager is created.
    """

    if manager is not None:
        return manager

    return TraceManager()


def _resolve_name(
    name: Optional[str],
    default: str,
    function: Callable[..., Any],
) -> str:
    """Resolve a trace/span name."""

    if name is not None:
        value = str(name).strip()

        if value:
            return value

    return getattr(
        function,
        "__qualname__",
        getattr(
            function,
            "__name__",
            default,
        ),
    )


def _normalize_mapping(
    value: Optional[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Return a mutable copy of a mapping."""

    if value is None:
        return {}

    return dict(value)


def _set_attributes(
    target: Any,
    attributes: Mapping[str, Any],
) -> None:
    """Attach attributes to a trace/span when supported."""

    if target is None or not attributes:
        return

    setter = getattr(
        target,
        "set_attribute",
        None,
    )

    if callable(setter):
        for key, value in attributes.items():
            setter(
                str(key),
                value,
            )

        return

    setter = getattr(
        target,
        "set_attributes",
        None,
    )

    if callable(setter):
        setter(
            dict(attributes),
        )


def _set_metadata(
    target: Any,
    metadata: Mapping[str, Any],
) -> None:
    """Attach metadata to a trace/span when supported."""

    if target is None or not metadata:
        return

    setter = getattr(
        target,
        "set_metadata",
        None,
    )

    if callable(setter):
        # Support both:
        #
        #     set_metadata(key, value)
        #
        # and manager-style:
        #
        #     set_metadata(mapping)
        #
        try:
            setter(
                dict(metadata),
            )
        except TypeError:
            for key, value in metadata.items():
                setter(
                    str(key),
                    value,
                )


def _record_exception(
    target: Any,
    exception: BaseException,
) -> None:
    """Record an exception on a trace/span when supported."""

    if target is None:
        return

    recorder = getattr(
        target,
        "record_exception",
        None,
    )

    if callable(recorder):
        recorder(exception)
        return

    recorder = getattr(
        target,
        "attach_exception",
        None,
    )

    if callable(recorder):
        recorder(exception)


def _finish(
    target: Any,
) -> Any:
    """
    Finish a trace/span when supported.

    The decorator layer is idempotent: an already-finished target is
    returned unchanged instead of invoking its lifecycle method again.
    """

    if target is None:
        return None

    # ------------------------------------------------------------------
    # Already finished
    # ------------------------------------------------------------------

    finished = getattr(
        target,
        "finished",
        False,
    )

    if callable(finished):
        finished = finished()

    if finished:
        return target

    is_finished = getattr(
        target,
        "is_finished",
        None,
    )

    if callable(is_finished) and is_finished():
        return target

    # ------------------------------------------------------------------
    # Finish lifecycle
    # ------------------------------------------------------------------

    for method_name in (
        "finish",
        "end",
        "close",
    ):
        method = getattr(
            target,
            method_name,
            None,
        )

        if callable(method):
            return method()

    return None


def _cancel(
    target: Any,
) -> Any:
    """Cancel a trace/span when supported."""

    if target is None:
        return None

    for method_name in (
        "cancel",
        "abort",
    ):
        method = getattr(
            target,
            method_name,
            None,
        )

        if callable(method):
            return method()

    return None


def _start_trace(
    manager: TraceManager,
    name: str,
) -> Optional[Trace]:
    """Start a trace using the manager."""

    method = getattr(
        manager,
        "start_trace",
        None,
    )

    if not callable(method):
        raise TraceDecoratorRuntimeError(
            "TraceManager does not provide start_trace().",
        )

    return method(name)


def _start_span(
    manager: TraceManager,
    name: str,
) -> Optional[Span]:
    """Start a span using the manager."""

    method = getattr(
        manager,
        "start_span",
        None,
    )

    if not callable(method):
        raise TraceDecoratorRuntimeError(
            "TraceManager does not provide start_span().",
        )

    return method(name)


def _start_span_with_trace(
    manager: TraceManager,
    name: str,
) -> tuple[Optional[Span], Optional[Trace]]:
    """
    Start a span and create an implicit trace when necessary.

    Returns:
        (span, implicit_trace)

    ``implicit_trace`` is ``None`` when a trace was already active.
    """

    current_trace = getattr(
        manager,
        "current_trace",
        None,
    )

    implicit_trace: Optional[Trace] = None

    if current_trace is None:
        implicit_trace = _start_trace(
            manager,
            f"{name}.trace",
        )

    span = _start_span(
        manager,
        name,
    )

    return span, implicit_trace


# ==============================================================================
# Part 7. Trace Decorator
# ==============================================================================

def trace(
    name: Optional[str] = None,
    *,
    manager: Optional[TraceManager] = None,
    metadata: Optional[Metadata] = None,
    attributes: Optional[Attributes] = None,
    record_exception: bool = DEFAULT_RECORD_EXCEPTION,
    set_attributes: bool = DEFAULT_SET_ATTRIBUTES,
) -> Callable[
    [DecoratedCallable[P, R]],
    DecoratedCallable[P, R],
]:
    """
    Decorate a function with a tracing lifecycle.

    The trace is started before function execution and finished after
    successful execution. Exceptions are optionally recorded and the trace
    is cancelled before the exception is re-raised.
    """

    normalized_metadata = _normalize_mapping(metadata)
    normalized_attributes = _normalize_mapping(attributes)

    def decorator(
        function: DecoratedCallable[P, R],
    ) -> DecoratedCallable[P, R]:

        resolved_name = _resolve_name(
            name,
            DEFAULT_TRACE_NAME,
            function,
        )

        @functools.wraps(function)
        def wrapper(
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> R:

            runtime_manager = _resolve_manager(manager)
            current_trace = _start_trace(
                runtime_manager,
                resolved_name,
            )

            _set_metadata(
                current_trace,
                normalized_metadata,
            )

            if set_attributes:
                _set_attributes(
                    current_trace,
                    normalized_attributes,
                )

            try:
                result = function(
                    *args,
                    **kwargs,
                )
            except Exception as exc:
                if record_exception:
                    _record_exception(
                        current_trace,
                        exc,
                    )

                _cancel(current_trace)
                raise
            else:
                _finish(current_trace)
                return result

        return wrapper

    return decorator


# ==============================================================================
# Part 8. Span Decorator
# ==============================================================================

def span(
    name: Optional[str] = None,
    *,
    manager: Optional[TraceManager] = None,
    metadata: Optional[Metadata] = None,
    attributes: Optional[Attributes] = None,
    record_exception: bool = DEFAULT_RECORD_EXCEPTION,
    set_attributes: bool = DEFAULT_SET_ATTRIBUTES,
) -> Callable[
    [DecoratedCallable[P, R]],
    DecoratedCallable[P, R],
]:
    """
    Decorate a function with a span lifecycle.

    If an active trace exists, the span is attached to it.

    If no active trace exists, an implicit trace is created for the
    duration of the decorated function.
    """

    normalized_metadata = _normalize_mapping(
        metadata,
    )

    normalized_attributes = _normalize_mapping(
        attributes,
    )

    def decorator(
        function: DecoratedCallable[P, R],
    ) -> DecoratedCallable[P, R]:

        resolved_name = _resolve_name(
            name,
            DEFAULT_SPAN_NAME,
            function,
        )

        @functools.wraps(function)
        def wrapper(
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> R:

            runtime_manager = _resolve_manager(
                manager,
            )

            (
                current_span,
                implicit_trace,
            ) = _start_span_with_trace(
                runtime_manager,
                resolved_name,
            )

            _set_metadata(
                current_span,
                normalized_metadata,
            )

            if set_attributes:
                _set_attributes(
                    current_span,
                    normalized_attributes,
                )

            try:
                result = function(
                    *args,
                    **kwargs,
                )

            except Exception as exc:
                if record_exception:
                    _record_exception(
                        current_span,
                        exc,
                    )

                _cancel(
                    current_span,
                )

                if implicit_trace is not None:
                    _cancel(
                        implicit_trace,
                    )

                raise

            else:
                _finish(
                    current_span,
                )

                if implicit_trace is not None:
                    _finish(
                        implicit_trace,
                    )

                return result

        return wrapper

    return decorator

# ==============================================================================
# Part 9. Async Decorators
# ==============================================================================

def async_trace(
    name: Optional[str] = None,
    *,
    manager: Optional[TraceManager] = None,
    metadata: Optional[Metadata] = None,
    attributes: Optional[Attributes] = None,
    record_exception: bool = DEFAULT_RECORD_EXCEPTION,
    set_attributes: bool = DEFAULT_SET_ATTRIBUTES,
) -> Callable[..., Any]:
    """
    Decorate an async function with a trace lifecycle.

    The trace is created before execution and finished after successful
    execution. Exceptions are optionally recorded, then the trace is
    cancelled before the exception is re-raised.
    """

    normalized_metadata = _normalize_mapping(
        metadata,
    )

    normalized_attributes = _normalize_mapping(
        attributes,
    )

    def decorator(
        function: Callable[P, Any],
    ) -> Callable[P, Any]:

        if not asyncio.iscoroutinefunction(function):
            raise TraceDecoratorConfigurationError(
                "async_trace() requires an async function.",
            )

        resolved_name = _resolve_name(
            name,
            DEFAULT_TRACE_NAME,
            function,
        )

        @functools.wraps(function)
        async def wrapper(
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> Any:

            runtime_manager = _resolve_manager(
                manager,
            )

            current_trace = _start_trace(
                runtime_manager,
                resolved_name,
            )

            _set_metadata(
                current_trace,
                normalized_metadata,
            )

            if set_attributes:
                _set_attributes(
                    current_trace,
                    normalized_attributes,
                )

            try:
                result = await function(
                    *args,
                    **kwargs,
                )

            except Exception as exc:
                if record_exception:
                    _record_exception(
                        current_trace,
                        exc,
                    )

                _cancel(
                    current_trace,
                )

                raise

            else:
                _finish(
                    current_trace,
                )

                return result

        return wrapper

    return decorator


def async_span(
    name: Optional[str] = None,
    *,
    manager: Optional[TraceManager] = None,
    metadata: Optional[Metadata] = None,
    attributes: Optional[Attributes] = None,
    record_exception: bool = DEFAULT_RECORD_EXCEPTION,
    set_attributes: bool = DEFAULT_SET_ATTRIBUTES,
) -> Callable[..., Any]:
    """
    Decorate an async function with a span lifecycle.

    If an active trace exists, the span is attached to it.

    If no active trace exists, an implicit trace is created for the
    duration of the decorated function.
    """

    normalized_metadata = _normalize_mapping(
        metadata,
    )

    normalized_attributes = _normalize_mapping(
        attributes,
    )

    def decorator(
        function: Callable[P, Any],
    ) -> Callable[P, Any]:

        if not asyncio.iscoroutinefunction(function):
            raise TraceDecoratorConfigurationError(
                "async_span() requires an async function.",
            )

        resolved_name = _resolve_name(
            name,
            DEFAULT_SPAN_NAME,
            function,
        )

        @functools.wraps(function)
        async def wrapper(
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> Any:

            runtime_manager = _resolve_manager(
                manager,
            )

            (
                current_span,
                implicit_trace,
            ) = _start_span_with_trace(
                runtime_manager,
                resolved_name,
            )

            _set_metadata(
                current_span,
                normalized_metadata,
            )

            if set_attributes:
                _set_attributes(
                    current_span,
                    normalized_attributes,
                )

            try:
                result = await function(
                    *args,
                    **kwargs,
                )

            except Exception as exc:
                if record_exception:
                    _record_exception(
                        current_span,
                        exc,
                    )

                _cancel(
                    current_span,
                )

                if implicit_trace is not None:
                    _cancel(
                        implicit_trace,
                    )

                raise

            else:
                _finish(
                    current_span,
                )

                if implicit_trace is not None:
                    _finish(
                        implicit_trace,
                    )

                return result

        return wrapper

    return decorator


# ==============================================================================
# Part 10. Context / Metadata Helpers
# ==============================================================================

def traced(
    name: Optional[str] = None,
    **kwargs: Any,
) -> Callable[
    [DecoratedCallable[P, R]],
    DecoratedCallable[P, R],
]:
    """Alias for the trace decorator."""

    return trace(
        name=name,
        **kwargs,
    )


def spanned(
    name: Optional[str] = None,
    **kwargs: Any,
) -> Callable[
    [DecoratedCallable[P, R]],
    DecoratedCallable[P, R],
]:
    """Alias for the span decorator."""

    return span(
        name=name,
        **kwargs,
    )


# ==============================================================================
# Part 11. Public API
# ==============================================================================

__all__ = [
    "TraceDecoratorError",
    "TraceDecoratorConfigurationError",
    "TraceDecoratorRuntimeError",
    "trace",
    "span",
    "async_trace",
    "async_span",
    "traced",
    "spanned",
]


# ==============================================================================
# Part 12. Module Exports
# ==============================================================================
