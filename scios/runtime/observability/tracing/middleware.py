# ==============================================================================
# SciOS Runtime Observability
# Trace Middleware
# ==============================================================================


# ==============================================================================
# Part 1. Module Header
# ==============================================================================

"""
SciOS Runtime Observability
===========================

Tracing middleware integration layer.

Provides middleware abstractions for intercepting runtime execution,
creating tracing boundaries, propagating trace context, handling
exceptions, and integrating tracing with the SciOS runtime pipeline.

Python 3.11+
"""


# ==============================================================================
# Part 2. Imports
# ==============================================================================

from __future__ import annotations

import functools
import inspect

from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    Mapping,
    MutableMapping,
    Optional,
    ParamSpec,
    Sequence,
    TypeAlias,
    TypeVar,
)

from .context import TraceContext
from .manager import TraceManager
from .span import Span
from .trace import Trace


# ==============================================================================
# Part 3. Type Aliases
# ==============================================================================

T = TypeVar("T")
P = ParamSpec("P")


MiddlewareCall: TypeAlias = Callable[..., Any]

MiddlewareHandler: TypeAlias = Callable[..., Any]

AsyncMiddlewareHandler: TypeAlias = Callable[
    ...,
    Awaitable[Any],
]

MiddlewareFactory: TypeAlias = Callable[
    ...,
    "TraceMiddleware",
]

MiddlewareMetadata: TypeAlias = MutableMapping[str, Any]

MiddlewareAttributes: TypeAlias = Mapping[str, Any]

MiddlewareNext: TypeAlias = Callable[..., Any]

MiddlewareResult: TypeAlias = Any

MiddlewareCallback: TypeAlias = Callable[..., Any]


# ==============================================================================
# Part 4. Constants
# ==============================================================================

MIDDLEWARE_NAME: str = "tracing"

MIDDLEWARE_VERSION: str = "1.0.0"

MIDDLEWARE_API_VERSION: str = "1.0"

MIDDLEWARE_TYPE: str = "observability.tracing.middleware"


# ------------------------------------------------------------------------------
# Default middleware configuration
# ------------------------------------------------------------------------------

DEFAULT_MIDDLEWARE_ENABLED: bool = True

DEFAULT_SERVICE_NAME: str = "scios"

DEFAULT_MIDDLEWARE_PRIORITY: int = 100

DEFAULT_MIDDLEWARE_ORDER: int = 0


# ------------------------------------------------------------------------------
# Backward-compatible configuration aliases
# ------------------------------------------------------------------------------

DEFAULT_ENABLED: bool = DEFAULT_MIDDLEWARE_ENABLED

DEFAULT_PRIORITY: int = DEFAULT_MIDDLEWARE_PRIORITY

DEFAULT_ORDER: int = DEFAULT_MIDDLEWARE_ORDER

DEFAULT_NAME: str = MIDDLEWARE_NAME


# ------------------------------------------------------------------------------
# Default tracing configuration
# ------------------------------------------------------------------------------

DEFAULT_TRACE_NAME: str = "trace"

DEFAULT_SPAN_NAME: str = "middleware"

DEFAULT_TRACE_KIND: str = "internal"


# Backward-compatible aliases.
DEFAULT_TRACE: str = DEFAULT_TRACE_NAME

DEFAULT_SPAN: str = DEFAULT_SPAN_NAME


# ------------------------------------------------------------------------------
# Default execution configuration
# ------------------------------------------------------------------------------

DEFAULT_CAPTURE_ARGS: bool = False

DEFAULT_CAPTURE_RESULT: bool = False

DEFAULT_CAPTURE_EXCEPTION: bool = True

DEFAULT_CAPTURE_EXCEPTIONS: bool = DEFAULT_CAPTURE_EXCEPTION

DEFAULT_RECORD_ARGUMENTS: bool = DEFAULT_CAPTURE_ARGS

DEFAULT_RECORD_RESULT: bool = DEFAULT_CAPTURE_RESULT

DEFAULT_RECORD_EXCEPTION: bool = DEFAULT_CAPTURE_EXCEPTION

DEFAULT_RECORD_EXCEPTIONS: bool = DEFAULT_CAPTURE_EXCEPTION


# ------------------------------------------------------------------------------
# Default tracing behavior
# ------------------------------------------------------------------------------

DEFAULT_CREATE_TRACE: bool = True

DEFAULT_CREATE_SPAN: bool = True

DEFAULT_PROPAGATE_CONTEXT: bool = True

DEFAULT_AUTO_START: bool = True

DEFAULT_AUTO_FINISH: bool = True


# ------------------------------------------------------------------------------
# Middleware lifecycle statuses
# ------------------------------------------------------------------------------

MIDDLEWARE_STATUS_CREATED: str = "created"

MIDDLEWARE_STATUS_INITIALIZED: str = "initialized"

MIDDLEWARE_STATUS_RUNNING: str = "running"

MIDDLEWARE_STATUS_STOPPED: str = "stopped"

MIDDLEWARE_STATUS_FAILED: str = "failed"


SUPPORTED_MIDDLEWARE_STATUSES: tuple[str, ...] = (
    MIDDLEWARE_STATUS_CREATED,
    MIDDLEWARE_STATUS_INITIALIZED,
    MIDDLEWARE_STATUS_RUNNING,
    MIDDLEWARE_STATUS_STOPPED,
    MIDDLEWARE_STATUS_FAILED,
)


# ==============================================================================
# Part 5. Exceptions
# ==============================================================================

class TraceMiddlewareError(Exception):
    """Base exception for tracing middleware errors."""


class TraceMiddlewareConfigurationError(TraceMiddlewareError):
    """Raised when middleware configuration is invalid."""


class TraceMiddlewareStateError(TraceMiddlewareError):
    """Raised when an operation is invalid for the current state."""


class TraceMiddlewareLifecycleError(TraceMiddlewareError):
    """Raised when middleware lifecycle handling fails."""


class TraceMiddlewareExecutionError(TraceMiddlewareError):
    """Raised when middleware execution fails."""


class TraceMiddlewareValidationError(TraceMiddlewareError):
    """Raised when middleware validation fails."""


# ==============================================================================
# Part 6. Enums
# ==============================================================================

class MiddlewareState(Enum):
    """Lifecycle state of the tracing middleware."""

    CREATED = MIDDLEWARE_STATUS_CREATED

    INITIALIZED = MIDDLEWARE_STATUS_INITIALIZED

    RUNNING = MIDDLEWARE_STATUS_RUNNING

    STOPPED = MIDDLEWARE_STATUS_STOPPED

    FAILED = MIDDLEWARE_STATUS_FAILED


class MiddlewareEvent(Enum):
    """Tracing middleware lifecycle events."""

    CREATED = "created"

    INITIALIZED = "initialized"

    STARTED = "started"

    STOPPED = "stopped"

    FAILED = "failed"

    TRACE_STARTED = "trace_started"

    TRACE_FINISHED = "trace_finished"

    SPAN_STARTED = "span_started"

    SPAN_FINISHED = "span_finished"

    EXECUTION_STARTED = "execution_started"

    EXECUTION_FINISHED = "execution_finished"

    EXECUTION_FAILED = "execution_failed"


# ==============================================================================
# Part 7. Dataclasses
# ==============================================================================

@dataclass
class MiddlewareConfig:
    """
    Runtime configuration for TraceMiddleware.
    """

    name: str = DEFAULT_NAME

    version: str = MIDDLEWARE_VERSION

    api_version: str = MIDDLEWARE_API_VERSION

    service_name: str = DEFAULT_SERVICE_NAME

    enabled: bool = DEFAULT_ENABLED

    priority: int = DEFAULT_PRIORITY

    order: int = DEFAULT_ORDER

    trace_name: str = DEFAULT_TRACE_NAME

    span_name: str = DEFAULT_SPAN_NAME

    trace_kind: str = DEFAULT_TRACE_KIND

    capture_arguments: bool = DEFAULT_CAPTURE_ARGS

    capture_result: bool = DEFAULT_CAPTURE_RESULT

    capture_exception: bool = DEFAULT_CAPTURE_EXCEPTION

    capture_exceptions: bool = DEFAULT_CAPTURE_EXCEPTIONS

    record_arguments: bool = DEFAULT_RECORD_ARGUMENTS

    record_result: bool = DEFAULT_RECORD_RESULT

    record_exception: bool = DEFAULT_RECORD_EXCEPTION

    record_exceptions: bool = DEFAULT_RECORD_EXCEPTIONS

    create_trace: bool = DEFAULT_CREATE_TRACE

    create_span: bool = DEFAULT_CREATE_SPAN

    propagate_context: bool = DEFAULT_PROPAGATE_CONTEXT

    auto_start: bool = DEFAULT_AUTO_START

    auto_finish: bool = DEFAULT_AUTO_FINISH

    metadata: Dict[str, Any] = field(
        default_factory=dict,
    )

    attributes: Dict[str, Any] = field(
        default_factory=dict,
    )


@dataclass
class MiddlewareStatistics:
    """Runtime statistics maintained by TraceMiddleware."""

    execution_count: int = 0

    trace_count: int = 0

    span_count: int = 0

    success_count: int = 0

    error_count: int = 0

    exception_count: int = 0

    reset_count: int = 0

    def reset(self) -> None:
        """Reset all middleware counters."""

        self.execution_count = 0
        self.trace_count = 0
        self.span_count = 0
        self.success_count = 0
        self.error_count = 0
        self.exception_count = 0
        self.reset_count += 1


@dataclass
class MiddlewareSnapshot:
    """Serializable runtime snapshot of TraceMiddleware."""

    name: str

    version: str

    state: MiddlewareState

    enabled: bool

    active: bool

    metadata: Dict[str, Any] = field(
        default_factory=dict,
    )

    attributes: Dict[str, Any] = field(
        default_factory=dict,
    )

    statistics: MiddlewareStatistics = field(
        default_factory=MiddlewareStatistics,
    )

    trace: Optional[Trace] = None

    current_span: Optional[Span] = None

    context: Optional[TraceContext] = None


# ==============================================================================
# Part 8. Internal Helpers
# ==============================================================================

    def _is_awaitable(value: Any) -> bool:
        """Return True when value is awaitable."""

        return inspect.isawaitable(value)


    def _copy_mapping(
        value: Optional[Mapping[str, Any]],
    ) -> Dict[str, Any]:
        """Return a mutable copy of a mapping."""

        if value is None:
            return {}

        return dict(value)


    def _merge_mapping(
        base: Mapping[str, Any],
        override: Optional[Mapping[str, Any]],
    ) -> Dict[str, Any]:
        """Merge two mappings into a new dictionary."""

        result = dict(base)

        if override:
            result.update(override)

        return result


    def _safe_bool(value: Any) -> bool:
        """Normalize a value to bool."""

        return bool(value)


    def _safe_int(value: Any, default: int = 0) -> int:
        """Normalize a value to int."""

        try:
            return int(value)
        except (TypeError, ValueError):
            return default


# ==============================================================================
# Part 9. TraceMiddleware
# ==============================================================================


class TraceMiddleware:
    """
    Runtime tracing middleware.

    The middleware owns execution boundaries but does not own a
    TraceManager unless one is explicitly assigned.

    Lifecycle:

        CREATED
            â†“
        INITIALIZED
            â†“
        RUNNING
            â†“
        INITIALIZED / STOPPED
    """

    def __init__(
        self,
        manager: Optional[TraceManager] = None,
        *,
        config: Optional[MiddlewareConfig] = None,
        name: Optional[str] = None,
        trace_name: Optional[str] = None,
        span_name: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> None:
        self._manager = manager

        # Defensive copy of configuration.
        if config is None:
            self._config = MiddlewareConfig()
        else:
            self._config = MiddlewareConfig(
                name=config.name,
                enabled=config.enabled,
                priority=config.priority,
                order=config.order,
                service_name=config.service_name,
                trace_name=config.trace_name,
                span_name=config.span_name,
                trace_kind=config.trace_kind,
                capture_arguments=config.capture_arguments,
                capture_result=config.capture_result,
                capture_exceptions=config.capture_exceptions,
                record_arguments=config.record_arguments,
                record_result=config.record_result,
                record_exceptions=config.record_exceptions,
                create_trace=config.create_trace,
                create_span=config.create_span,
                metadata=dict(config.metadata),
                attributes=dict(config.attributes),
            )

        if name is not None:
            self._config.name = name

        if trace_name is not None:
            self._config.trace_name = trace_name

        if span_name is not None:
            self._config.span_name = span_name

        if enabled is not None:
            self._config.enabled = enabled

        self._enabled = bool(self._config.enabled)

        # IMPORTANT:
        # Constructor contract is CREATED.
        # Do NOT transition to INITIALIZED here.
        self._state = MiddlewareState.CREATED

        self._active = False

        self._trace: Optional[Trace] = None
        self._span: Optional[Span] = None
        self._context: Optional[TraceContext] = None

        self._metadata: Dict[str, Any] = dict(
            self._config.metadata,
        )

        self._attributes: Dict[str, Any] = dict(
            self._config.attributes,
        )

        self._execution_count = 0
        self._error_count = 0

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def manager(self) -> Optional[TraceManager]:
        return self._manager

    @property
    def config(self) -> MiddlewareConfig:
        return self._config

    @property
    def state(self) -> MiddlewareState:
        return self._state

    @property
    def active(self) -> bool:
        return self._active

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def trace(self) -> Optional[Trace]:
        return self._trace

    @property
    def span(self) -> Optional[Span]:
        return self._span

    @property
    def context(self) -> Optional[TraceContext]:
        return self._context

    @property
    def metadata(self) -> Dict[str, Any]:
        return dict(self._metadata)

    @property
    def attributes(self) -> Dict[str, Any]:
        return dict(self._attributes)

    @property
    def execution_count(self) -> int:
        return self._execution_count

    @property
    def error_count(self) -> int:
        return self._error_count

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self) -> "TraceMiddleware":
        """
        Initialize the middleware.

        CREATED -> INITIALIZED
        """
        if self._state == MiddlewareState.STOPPED:
            raise TraceMiddlewareStateError(
                "Middleware has already been stopped",
            )

        if self._state == MiddlewareState.FAILED:
            raise TraceMiddlewareStateError(
                "Middleware is in failed state",
            )

        if self._state == MiddlewareState.RUNNING:
            return self

        self._state = MiddlewareState.INITIALIZED
        self._active = False

        return self

    def start(self) -> "TraceMiddleware":
        """
        Start middleware execution.

        CREATED -> INITIALIZED -> RUNNING
        INITIALIZED -> RUNNING
        """
        if self._state == MiddlewareState.STOPPED:
            raise TraceMiddlewareStateError(
                "Middleware has already been stopped",
            )

        if self._state == MiddlewareState.FAILED:
            raise TraceMiddlewareStateError(
                "Middleware is in failed state",
            )

        if self._state == MiddlewareState.CREATED:
            self.initialize()

        self._state = MiddlewareState.RUNNING
        self._active = True

        return self

    def stop(self) -> "TraceMiddleware":
        """
        Stop the middleware permanently.
        """
        if self._state == MiddlewareState.STOPPED:
            return self

        self._span = None
        self._trace = None
        self._context = None

        self._active = False
        self._state = MiddlewareState.STOPPED

        return self

    # ------------------------------------------------------------------
    # Manager
    # ------------------------------------------------------------------

    def set_manager(
        self,
        manager: Optional[TraceManager],
    ) -> "TraceMiddleware":
        self._manager = manager
        return self

    # ------------------------------------------------------------------
    # Context
    # ------------------------------------------------------------------

    def set_context(
        self,
        context: Optional[TraceContext],
    ) -> "TraceMiddleware":
        self._context = context
        return self

    # ------------------------------------------------------------------
    # Metadata / attributes
    # ------------------------------------------------------------------

    def set_metadata(
        self,
        metadata: Mapping[str, Any],
        value: Any = None,
    ) -> "TraceMiddleware":
        if not isinstance(metadata, Mapping):
            raise TypeError("metadata must be a mapping")

        values = dict(metadata)

        if value is not None and values:
            first_key = next(iter(values))
            values[first_key] = value

        self._metadata.update(values)

        return self

    def set_attributes(
        self,
        attributes: Mapping[str, Any],
        value: Any = None,
    ) -> "TraceMiddleware":
        if not isinstance(attributes, Mapping):
            raise TypeError("attributes must be a mapping")

        values = dict(attributes)

        if value is not None and values:
            first_key = next(iter(values))
            values[first_key] = value

        self._attributes.update(values)

        return self

    # ------------------------------------------------------------------
    # Trace lifecycle
    # ------------------------------------------------------------------

    def start_trace(
        self,
        name: Optional[str] = None,
    ) -> Optional[Trace]:
        if self._manager is None:
            return None

        trace_name_value = (
            name
            or self._config.trace_name
            or DEFAULT_TRACE_NAME
        )

        result = self._manager.start_trace(
            trace_name_value,
        )

        self._trace = result

        return result

    def finish_trace(self) -> Any:
        if self._manager is None:
            self._trace = None
            return None

        try:
            return self._manager.finish_trace()
        finally:
            self._trace = None

    def start_span(
        self,
        name: Optional[str] = None,
    ) -> Optional[Span]:
        if self._manager is None:
            return None

        span_name_value = (
            name
            or self._config.span_name
            or DEFAULT_SPAN_NAME
        )

        result = self._manager.start_span(
            span_name_value,
        )

        self._span = result

        return result

    def finish_span(self) -> Any:
        if self._manager is None:
            self._span = None
            return None

        try:
            return self._manager.finish_span()
        finally:
            self._span = None

    # ------------------------------------------------------------------
    # Callable / decorator support
    # ------------------------------------------------------------------

    def __call__(
        self,
        handler: Callable[..., T],
    ) -> Callable[..., Any]:
        if not callable(handler):
            raise TypeError("handler must be callable")

        if inspect.iscoroutinefunction(handler):

            @functools.wraps(handler)
            async def async_wrapper(
                *args: Any,
                **kwargs: Any,
            ) -> T:
                return await self.execute_async(
                    handler,
                    *args,
                    **kwargs,
                )

            return async_wrapper

        @functools.wraps(handler)
        def wrapper(
            *args: Any,
            **kwargs: Any,
        ) -> T:
            return self.execute(
                handler,
                *args,
                **kwargs,
            )

        return wrapper

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        handler: Callable[..., T],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        if not callable(handler):
            raise TypeError("handler must be callable")

        if not self._enabled:
            return handler(*args, **kwargs)

        if self._state == MiddlewareState.STOPPED:
            raise TraceMiddlewareStateError(
                "Cannot execute stopped middleware",
            )

        if self._state == MiddlewareState.FAILED:
            raise TraceMiddlewareStateError(
                "Cannot execute failed middleware",
            )

        trace_name = kwargs.pop("trace_name", None)
        span_name = kwargs.pop("span_name", None)

        execution_metadata = kwargs.pop(
            "metadata",
            None,
        )

        execution_attributes = kwargs.pop(
            "attributes",
            None,
        )

        if execution_metadata is not None:
            self.set_metadata(execution_metadata)

        if execution_attributes is not None:
            self.set_attributes(execution_attributes)

        self.start()

        self._execution_count += 1

        trace_created = False
        span_created = False

        try:
            if (
                self._config.create_trace
                and self._trace is None
            ):
                self.start_trace(trace_name)
                trace_created = self._trace is not None

            if self._config.create_span:
                self.start_span(span_name)
                span_created = self._span is not None

            return handler(
                *args,
                **kwargs,
            )

        except Exception:
            self._error_count += 1
            raise

        finally:
            if span_created and self._span is not None:
                try:
                    self.finish_span()
                except Exception:
                    self._span = None

            if trace_created and self._trace is not None:
                try:
                    self.finish_trace()
                except Exception:
                    self._trace = None

            self._span = None
            self._trace = None
            self._context = None

            if self._state == MiddlewareState.RUNNING:
                self._state = MiddlewareState.INITIALIZED

            self._active = False

    # ------------------------------------------------------------------
    # Async execution
    # ------------------------------------------------------------------

    async def execute_async(
        self,
        handler: Callable[..., Awaitable[T]],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        if not callable(handler):
            raise TypeError("handler must be callable")

        if not self._enabled:
            return await handler(*args, **kwargs)

        if self._state == MiddlewareState.STOPPED:
            raise TraceMiddlewareStateError(
                "Cannot execute stopped middleware",
            )

        if self._state == MiddlewareState.FAILED:
            raise TraceMiddlewareStateError(
                "Cannot execute failed middleware",
            )

        trace_name = kwargs.pop("trace_name", None)
        span_name = kwargs.pop("span_name", None)

        execution_metadata = kwargs.pop(
            "metadata",
            None,
        )

        execution_attributes = kwargs.pop(
            "attributes",
            None,
        )

        if execution_metadata is not None:
            self.set_metadata(execution_metadata)

        if execution_attributes is not None:
            self.set_attributes(execution_attributes)

        self.start()

        self._execution_count += 1

        trace_created = False
        span_created = False

        try:
            if (
                self._config.create_trace
                and self._trace is None
            ):
                self.start_trace(trace_name)
                trace_created = self._trace is not None

            if self._config.create_span:
                self.start_span(span_name)
                span_created = self._span is not None

            return await handler(
                *args,
                **kwargs,
            )

        except Exception:
            self._error_count += 1
            raise

        finally:
            if span_created and self._span is not None:
                try:
                    self.finish_span()
                except Exception:
                    self._span = None

            if trace_created and self._trace is not None:
                try:
                    self.finish_trace()
                except Exception:
                    self._trace = None

            self._span = None
            self._trace = None
            self._context = None

            if self._state == MiddlewareState.RUNNING:
                self._state = MiddlewareState.INITIALIZED

            self._active = False


# ==============================================================================
# Part 10. Context Middleware
# ==============================================================================


class TraceContextMiddleware(TraceMiddleware):
    """Middleware that propagates an existing TraceContext."""

    def __init__(
        self,
        manager: Optional[TraceManager] = None,
        *,
        context: Optional[TraceContext] = None,
        config: Optional[MiddlewareConfig] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            manager=manager,
            config=config,
            **kwargs,
        )

        self._context = context

    @property
    def context(self) -> Optional[TraceContext]:
        return self._context

    def set_context(
        self,
        context: Optional[TraceContext],
    ) -> "TraceContextMiddleware":
        self._context = context
        return self


# ==============================================================================
# Part 11. Trace Lifecycle Middleware
# ==============================================================================


class TraceLifecycleMiddleware(TraceMiddleware):
    """Explicit lifecycle-oriented tracing middleware."""

    def begin(
        self,
        trace_name: Optional[str] = None,
        span_name: Optional[str] = None,
    ) -> "TraceLifecycleMiddleware":
        self.start()

        if self._config.create_trace:
            self.start_trace(trace_name)

        if self._config.create_span:
            self.start_span(span_name)

        return self

    def end(self) -> "TraceLifecycleMiddleware":
        if self._span is not None:
            self.finish_span()

        if self._trace is not None:
            self.finish_trace()

        self._active = False

        if self._state == MiddlewareState.RUNNING:
            self._state = MiddlewareState.INITIALIZED

        return self


# ==============================================================================
# Part 12. Exception Middleware
# ==============================================================================


class TraceExceptionMiddleware(TraceMiddleware):
    """Tracing middleware specialized for exception capture."""

    def execute(
        self,
        handler: Callable[..., T],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        return super().execute(
            handler,
            *args,
            **kwargs,
        )

    async def execute_async(
        self,
        handler: Callable[..., Awaitable[T]],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        return await super().execute_async(
            handler,
            *args,
            **kwargs,
        )


# ==============================================================================
# Part 13. Middleware Composition
# ==============================================================================


class MiddlewareChain:
    """Composable ordered collection of tracing middleware."""

    def __init__(
        self,
        middleware: Optional[Sequence[TraceMiddleware]] = None,
    ) -> None:
        self._middleware = tuple(
            middleware or (),
        )

    @property
    def middleware(
        self,
    ) -> tuple[TraceMiddleware, ...]:
        return self._middleware

    def add(
        self,
        middleware: TraceMiddleware,
    ) -> "MiddlewareChain":
        if not isinstance(
            middleware,
            TraceMiddleware,
        ):
            raise TypeError(
                "middleware must be TraceMiddleware",
            )

        self._middleware = (
            *self._middleware,
            middleware,
        )

        return self

    def remove(
        self,
        middleware: TraceMiddleware,
    ) -> "MiddlewareChain":
        self._middleware = tuple(
            item
            for item in self._middleware
            if item is not middleware
        )

        return self

    def start(self) -> "MiddlewareChain":
        for middleware in self._middleware:
            middleware.start()

        return self

    def stop(self) -> "MiddlewareChain":
        for middleware in reversed(
            self._middleware,
        ):
            middleware.stop()

        return self

    def execute(
        self,
        handler: Callable[..., T],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        current: Callable[..., Any] = handler

        for middleware in reversed(
            self._middleware,
        ):
            previous = current

            def wrapped(
                *call_args: Any,
                _middleware: TraceMiddleware = middleware,
                _previous: Callable[..., Any] = previous,
                **call_kwargs: Any,
            ) -> Any:
                return _middleware.execute(
                    _previous,
                    *call_args,
                    **call_kwargs,
                )

            current = wrapped

        return current(
            *args,
            **kwargs,
        )

    async def execute_async(
        self,
        handler: Callable[..., Awaitable[T]],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        current: Callable[..., Awaitable[Any]] = handler

        for middleware in reversed(
            self._middleware,
        ):
            previous = current

            async def wrapped(
                *call_args: Any,
                _middleware: TraceMiddleware = middleware,
                _previous: Callable[..., Awaitable[Any]] = previous,
                **call_kwargs: Any,
            ) -> Any:
                return await _middleware.execute_async(
                    _previous,
                    *call_args,
                    **call_kwargs,
                )

            current = wrapped

        return await current(
            *args,
            **kwargs,
        )


# ==============================================================================
# Part 14. Public API
# ==============================================================================


@dataclass
class MiddlewareResult:
    """Result returned by middleware integrations."""

    value: Any = None
    trace: Optional[Trace] = None
    span: Optional[Span] = None
    context: Optional[TraceContext] = None
    error: Optional[BaseException] = None


class MiddlewareEvent(str, Enum):
    CREATED = "created"
    INITIALIZED = "initialized"
    STARTED = "started"
    FINISHED = "finished"
    STOPPED = "stopped"
    FAILED = "failed"


# ==============================================================================
# Factory
# ==============================================================================


def create_trace_middleware(
    manager: Optional[TraceManager] = None,
    *,
    config: Optional[MiddlewareConfig] = None,
    **kwargs: Any,
) -> TraceMiddleware:
    """
    Create an initialized TraceMiddleware.

    Direct construction preserves the CREATED lifecycle state.
    Factory construction performs initialization immediately.
    """

    middleware = TraceMiddleware(
        manager=manager,
        config=config,
        **kwargs,
    )

    middleware.initialize()

    return middleware


def create_context_middleware(
    manager: Optional[TraceManager] = None,
    *,
    context: Optional[TraceContext] = None,
    config: Optional[MiddlewareConfig] = None,
    **kwargs: Any,
) -> TraceContextMiddleware:
    """
    Create a TraceContextMiddleware instance.
    """

    middleware = TraceContextMiddleware(
        manager=manager,
        context=context,
        config=config,
        **kwargs,
    )

    middleware.initialize()

    return middleware


def compose_middleware(
    *middleware: TraceMiddleware,
) -> MiddlewareChain:
    """
    Compose tracing middleware into an ordered middleware chain.
    """

    return MiddlewareChain(
        middleware,
    )


# ==============================================================================
# Public exports
# ==============================================================================


__all__ = [
    "TraceMiddleware",
    "TraceContextMiddleware",
    "TraceLifecycleMiddleware",
    "TraceExceptionMiddleware",
    "MiddlewareChain",
    "MiddlewareResult",
    "MiddlewareEvent",
    "create_trace_middleware",
    "create_context_middleware",
    "compose_middleware",
]
