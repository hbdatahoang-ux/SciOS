# ==============================================================================
# SciOS Runtime Observability
# Trace Middleware Tests
# ==============================================================================

from __future__ import annotations


# ==============================================================================
# Part 1. Module Header
# ==============================================================================

"""
SciOS Runtime Observability
===========================

Tests for the tracing middleware integration layer.

Python 3.11+
"""


# ==============================================================================
# Part 2. Imports
# ==============================================================================

import asyncio

import pytest

from scios.runtime.observability.tracing.middleware import (
    MIDDLEWARE_NAME,
    MIDDLEWARE_STATUS_CREATED,
    MIDDLEWARE_STATUS_FAILED,
    MIDDLEWARE_STATUS_INITIALIZED,
    MIDDLEWARE_STATUS_RUNNING,
    MIDDLEWARE_STATUS_STOPPED,
    MiddlewareChain,
    MiddlewareConfig,
    MiddlewareEvent,
    MiddlewareResult,
    MiddlewareState,
    TraceMiddleware,
    TraceMiddlewareConfigurationError,
    TraceMiddlewareError,
    TraceMiddlewareExecutionError,
    TraceMiddlewareStateError,
    create_trace_middleware,
)


# ==============================================================================
# Part 3. Fixtures
# ==============================================================================

@pytest.fixture
def middleware() -> TraceMiddleware:
    """Create a default tracing middleware."""

    return TraceMiddleware()


@pytest.fixture
def configured_middleware() -> TraceMiddleware:
    """Create a configured tracing middleware."""

    config = MiddlewareConfig(
        name="test-middleware",
        enabled=True,
        trace_name="test-trace",
        span_name="test-span",
        metadata={
            "environment": "test",
            "source": "pytest",
        },
        attributes={
            "component": "tracing",
        },
    )

    return TraceMiddleware(
        config=config,
    )


@pytest.fixture
def disabled_middleware() -> TraceMiddleware:
    """Create a disabled tracing middleware."""

    return TraceMiddleware(
        enabled=False,
    )


@pytest.fixture
def chain() -> MiddlewareChain:
    """Create an empty middleware chain."""

    return MiddlewareChain()


# ==============================================================================
# Part 4. Basic Middleware Tests
# ==============================================================================

def test_middleware_creation(
    middleware: TraceMiddleware,
) -> None:
    assert middleware.name == MIDDLEWARE_NAME
    assert middleware.enabled is True
    assert middleware.state == MiddlewareState.CREATED
    assert middleware.active is False


def test_middleware_config(
    configured_middleware: TraceMiddleware,
) -> None:
    assert configured_middleware.name == "test-middleware"
    assert configured_middleware._config.trace_name == "test-trace"
    assert configured_middleware._config.span_name == "test-span"


def test_middleware_initialize(
    middleware: TraceMiddleware,
) -> None:
    result = middleware.initialize()

    assert result is middleware
    assert middleware.state == MiddlewareState.INITIALIZED


def test_middleware_start(
    middleware: TraceMiddleware,
) -> None:
    result = middleware.start()

    assert result is middleware
    assert middleware.state == MiddlewareState.RUNNING
    assert middleware.active is True


def test_middleware_stop(
    middleware: TraceMiddleware,
) -> None:
    middleware.start()

    result = middleware.stop()

    assert result is middleware
    assert middleware.state == MiddlewareState.STOPPED
    assert middleware.active is False


def test_middleware_properties(
    middleware: TraceMiddleware,
) -> None:
    assert middleware.manager is None
    assert middleware.trace is None
    assert middleware.span is None
    assert middleware.context is None
    assert middleware.execution_count == 0
    assert middleware.error_count == 0


# ==============================================================================
# Part 5. Trace Lifecycle Tests
# ==============================================================================

def test_trace_lifecycle_without_manager(
    middleware: TraceMiddleware,
) -> None:
    middleware.start()

    result = middleware.execute(
        lambda: "ok",
    )

    assert result == "ok"
    assert middleware.execution_count == 1
    assert middleware.trace is None


def test_custom_trace_name(
    middleware: TraceMiddleware,
) -> None:
    middleware.execute(
        lambda: "ok",
        trace_name="custom-trace",
    )

    assert middleware.execution_count == 1


def test_trace_cleanup_after_execution(
    middleware: TraceMiddleware,
) -> None:
    middleware.execute(
        lambda: 42,
    )

    assert middleware.trace is None
    assert middleware.context is None


# ==============================================================================
# Part 6. Span Lifecycle Tests
# ==============================================================================

def test_custom_span_name(
    middleware: TraceMiddleware,
) -> None:
    middleware.execute(
        lambda: "ok",
        span_name="custom-span",
    )

    assert middleware.execution_count == 1


def test_span_cleanup_after_execution(
    middleware: TraceMiddleware,
) -> None:
    middleware.execute(
        lambda: "ok",
    )

    assert middleware.span is None


def test_span_and_trace_are_cleared_on_completion(
    middleware: TraceMiddleware,
) -> None:
    middleware.execute(
        lambda: "completed",
    )

    assert middleware.trace is None
    assert middleware.span is None
    assert middleware.context is None


# ==============================================================================
# Part 7. Context Propagation Tests
# ==============================================================================

def test_initial_context(
    middleware: TraceMiddleware,
) -> None:
    assert middleware.context is None


def test_context_cleanup(
    middleware: TraceMiddleware,
) -> None:
    middleware.execute(
        lambda: "result",
    )

    assert middleware.context is None


def test_manager_can_be_assigned(
    middleware: TraceMiddleware,
) -> None:
    result = middleware.set_manager(None)

    assert result is middleware
    assert middleware.manager is None


# ==============================================================================
# Part 8. Request / Execution Tests
# ==============================================================================

def test_execute_returns_result(
    middleware: TraceMiddleware,
) -> None:
    result = middleware.execute(
        lambda: 123,
    )

    assert result == 123


def test_execute_preserves_positional_arguments(
    middleware: TraceMiddleware,
) -> None:
    def operation(
        first: int,
        second: int,
    ) -> int:
        return first + second

    result = middleware.execute(
        operation,
        10,
        20,
    )

    assert result == 30


def test_execute_preserves_keyword_arguments(
    middleware: TraceMiddleware,
) -> None:
    def operation(
        value: int,
        *,
        multiplier: int,
    ) -> int:
        return value * multiplier

    result = middleware.execute(
        operation,
        5,
        multiplier=4,
    )

    assert result == 20


def test_execute_increments_counter(
    middleware: TraceMiddleware,
) -> None:
    middleware.execute(lambda: 1)
    middleware.execute(lambda: 2)
    middleware.execute(lambda: 3)

    assert middleware.execution_count == 3


def test_callable_decorator(
    middleware: TraceMiddleware,
) -> None:
    @middleware
    def operation(value: int) -> int:
        return value * 2

    assert operation(5) == 10
    assert middleware.execution_count == 1


def test_decorator_preserves_function_name(
    middleware: TraceMiddleware,
) -> None:
    @middleware
    def operation() -> str:
        return "ok"

    assert operation.__name__ == "operation"


# ==============================================================================
# Part 9. Metadata & Attributes Tests
# ==============================================================================

def test_initial_metadata(
    configured_middleware: TraceMiddleware,
) -> None:
    metadata = configured_middleware.metadata

    assert metadata["environment"] == "test"
    assert metadata["source"] == "pytest"


def test_initial_attributes(
    configured_middleware: TraceMiddleware,
) -> None:
    attributes = configured_middleware.attributes

    assert attributes["component"] == "tracing"


def test_set_metadata(
    middleware: TraceMiddleware,
) -> None:
    result = middleware.set_metadata(
        {
            "key": "value",
        },
    )

    assert result is middleware
    assert middleware.metadata["key"] == "value"


def test_set_attributes(
    middleware: TraceMiddleware,
) -> None:
    result = middleware.set_attributes(
        {
            "key": "value",
        },
    )

    assert result is middleware
    assert middleware.attributes["key"] == "value"


def test_execution_metadata(
    middleware: TraceMiddleware,
) -> None:
    middleware.execute(
        lambda: "ok",
        metadata={
            "request.id": "123",
        },
    )

    assert middleware.execution_count == 1


def test_execution_attributes(
    middleware: TraceMiddleware,
) -> None:
    middleware.execute(
        lambda: "ok",
        attributes={
            "request.type": "test",
        },
    )

    assert middleware.execution_count == 1


# ==============================================================================
# Part 10. Exception Handling Tests
# ==============================================================================

def test_exception_is_reraised(
    middleware: TraceMiddleware,
) -> None:
    def operation() -> None:
        raise ValueError("boom")

    with pytest.raises(
        ValueError,
        match="boom",
    ):
        middleware.execute(operation)

    assert middleware.error_count == 1


def test_exception_does_not_break_cleanup(
    middleware: TraceMiddleware,
) -> None:
    def operation() -> None:
        raise RuntimeError("failure")

    with pytest.raises(RuntimeError):
        middleware.execute(operation)

    assert middleware.trace is None
    assert middleware.span is None
    assert middleware.context is None


def test_multiple_errors_are_counted(
    middleware: TraceMiddleware,
) -> None:
    for _ in range(3):
        with pytest.raises(ValueError):
            middleware.execute(
                lambda: (_ for _ in ()).throw(
                    ValueError("error"),
                ),
            )

    assert middleware.error_count == 3


# ==============================================================================
# Part 11. Nested Middleware Tests
# ==============================================================================

def test_nested_middleware_execution() -> None:
    outer = TraceMiddleware(
        trace_name="outer",
    )

    inner = TraceMiddleware(
        trace_name="inner",
    )

    @outer
    @inner
    def operation() -> str:
        return "nested"

    result = operation()

    assert result == "nested"
    assert outer.execution_count == 1
    assert inner.execution_count == 1


def test_nested_middleware_exception() -> None:
    outer = TraceMiddleware()
    inner = TraceMiddleware()

    @outer
    @inner
    def operation() -> None:
        raise ValueError("nested failure")

    with pytest.raises(
        ValueError,
        match="nested failure",
    ):
        operation()

    assert outer.error_count == 1
    assert inner.error_count == 1


# ==============================================================================
# Part 12. Middleware Composition Tests
# ==============================================================================

def test_empty_chain(
    chain: MiddlewareChain,
) -> None:
    assert chain.middleware == ()


def test_chain_add(
    chain: MiddlewareChain,
    middleware: TraceMiddleware,
) -> None:
    result = chain.add(middleware)

    assert result is chain
    assert chain.middleware == (middleware,)


def test_chain_remove(
    chain: MiddlewareChain,
) -> None:
    middleware = TraceMiddleware()

    chain.add(middleware)
    result = chain.remove(middleware)

    assert result is chain
    assert chain.middleware == ()


def test_chain_start(
    chain: MiddlewareChain,
) -> None:
    first = TraceMiddleware()
    second = TraceMiddleware()

    chain.add(first)
    chain.add(second)

    result = chain.start()

    assert result is chain
    assert first.active is True
    assert second.active is True


def test_chain_stop(
    chain: MiddlewareChain,
) -> None:
    first = TraceMiddleware()
    second = TraceMiddleware()

    chain.add(first)
    chain.add(second)
    chain.start()

    result = chain.stop()

    assert result is chain
    assert first.state == MiddlewareState.STOPPED
    assert second.state == MiddlewareState.STOPPED


def test_chain_execute(
    chain: MiddlewareChain,
) -> None:
    chain.add(TraceMiddleware())
    chain.add(TraceMiddleware())

    result = chain.execute(
        lambda value: value + 1,
        10,
    )

    assert result == 11


def test_chain_rejects_invalid_middleware(
    chain: MiddlewareChain,
) -> None:
    with pytest.raises(TypeError):
        chain.add(object())  # type: ignore[arg-type]


# ==============================================================================
# Part 13. Disabled / Error-State Tests
# ==============================================================================

def test_disabled_middleware(
    disabled_middleware: TraceMiddleware,
) -> None:
    result = disabled_middleware.execute(
        lambda: "disabled",
    )

    assert result == "disabled"
    assert disabled_middleware.execution_count == 0
    assert disabled_middleware.trace is None
    assert disabled_middleware.span is None


def test_disabled_middleware_does_not_execute_tracing(
    disabled_middleware: TraceMiddleware,
) -> None:
    called = []

    def operation() -> str:
        called.append(True)
        return "ok"

    assert disabled_middleware.execute(operation) == "ok"
    assert called == [True]


def test_invalid_callable(
    middleware: TraceMiddleware,
) -> None:
    with pytest.raises(TypeError):
        middleware.execute(123)  # type: ignore[arg-type]


def test_lifecycle_after_stop(
    middleware: TraceMiddleware,
) -> None:
    middleware.start()
    middleware.stop()

    with pytest.raises(TraceMiddlewareStateError):
        middleware.start()


# ==============================================================================
# Part 14. Async Middleware Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_async_execution(
    middleware: TraceMiddleware,
) -> None:
    async def operation(value: int) -> int:
        await asyncio.sleep(0)
        return value * 2

    result = await middleware.execute_async(
        operation,
        5,
    )

    assert result == 10
    assert middleware.execution_count == 1


@pytest.mark.asyncio
async def test_async_decorator(
    middleware: TraceMiddleware,
) -> None:
    @middleware
    async def operation(value: int) -> int:
        await asyncio.sleep(0)
        return value + 1

    result = await operation(10)

    assert result == 11
    assert middleware.execution_count == 1


@pytest.mark.asyncio
async def test_async_arguments(
    middleware: TraceMiddleware,
) -> None:
    async def operation(
        first: int,
        *,
        second: int,
    ) -> int:
        await asyncio.sleep(0)
        return first + second

    result = await middleware.execute_async(
        operation,
        10,
        second=20,
    )

    assert result == 30


@pytest.mark.asyncio
async def test_async_exception(
    middleware: TraceMiddleware,
) -> None:
    async def operation() -> None:
        await asyncio.sleep(0)
        raise RuntimeError("async failure")

    with pytest.raises(
        RuntimeError,
        match="async failure",
    ):
        await middleware.execute_async(operation)

    assert middleware.error_count == 1
    assert middleware.trace is None
    assert middleware.span is None


@pytest.mark.asyncio
async def test_async_chain() -> None:
    chain = MiddlewareChain(
        [
            TraceMiddleware(),
            TraceMiddleware(),
        ],
    )

    async def operation(value: int) -> int:
        await asyncio.sleep(0)
        return value * 3

    result = await chain.execute_async(
        operation,
        7,
    )

    assert result == 21


# ==============================================================================
# Part 15. Edge Cases
# ==============================================================================

def test_metadata_is_defensive(
    middleware: TraceMiddleware,
) -> None:
    source = {
        "key": "value",
    }

    middleware.set_metadata(source)
    source["key"] = "changed"

    assert middleware.metadata["key"] == "value"


def test_attributes_are_defensive(
    middleware: TraceMiddleware,
) -> None:
    source = {
        "key": "value",
    }

    middleware.set_attributes(source)
    source["key"] = "changed"

    assert middleware.attributes["key"] == "value"


def test_config_is_defensive() -> None:
    config = MiddlewareConfig(
        metadata={
            "key": "value",
        },
        attributes={
            "attribute": "value",
        },
    )

    middleware = TraceMiddleware(
        config=config,
    )

    config.metadata["key"] = "changed"
    config.attributes["attribute"] = "changed"

    assert middleware.metadata["key"] == "value"
    assert middleware.attributes["attribute"] == "value"


def test_create_trace_middleware() -> None:
    middleware = create_trace_middleware()

    assert isinstance(
        middleware,
        TraceMiddleware,
    )

    assert middleware.state == MiddlewareState.INITIALIZED


def test_middleware_result_dataclass() -> None:
    result = MiddlewareResult(
        value="ok",
    )

    assert result.value == "ok"
    assert result.trace is None
    assert result.span is None
    assert result.context is None
    assert result.error is None


# ==============================================================================
# Part 16. Public API Tests
# ==============================================================================

def test_public_middleware_states() -> None:
    assert MiddlewareState.CREATED.value == MIDDLEWARE_STATUS_CREATED
    assert MiddlewareState.INITIALIZED.value == MIDDLEWARE_STATUS_INITIALIZED
    assert MiddlewareState.RUNNING.value == MIDDLEWARE_STATUS_RUNNING
    assert MiddlewareState.STOPPED.value == MIDDLEWARE_STATUS_STOPPED
    assert MiddlewareState.FAILED.value == MIDDLEWARE_STATUS_FAILED


def test_public_middleware_events() -> None:
    assert MiddlewareEvent.CREATED.value == "created"
    assert MiddlewareEvent.INITIALIZED.value == "initialized"
    assert MiddlewareEvent.STARTED.value == "started"
    assert MiddlewareEvent.FINISHED.value == "finished"
    assert MiddlewareEvent.STOPPED.value == "stopped"
    assert MiddlewareEvent.FAILED.value == "failed"


def test_public_exceptions() -> None:
    assert issubclass(
        TraceMiddlewareConfigurationError,
        TraceMiddlewareError,
    )

    assert issubclass(
        TraceMiddlewareExecutionError,
        TraceMiddlewareError,
    )

    assert issubclass(
        TraceMiddlewareStateError,
        TraceMiddlewareError,
    )


def test_factory_returns_initialized_middleware() -> None:
    middleware = create_trace_middleware(
        enabled=True,
        name="factory-test",
        trace_name="factory-trace",
        span_name="factory-span",
    )

    assert middleware.name == "factory-test"
    assert middleware._config.trace_name == "factory-trace"
    assert middleware._config.span_name == "factory-span"
    assert middleware.state == MiddlewareState.INITIALIZED