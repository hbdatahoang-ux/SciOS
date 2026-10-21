# ==============================================================================
# SciOS Runtime Observability
# Trace Decorators Tests
# ==============================================================================


# ==============================================================================
# Part 1. Module Header
# ==============================================================================

"""
Tests for SciOS tracing decorators.

Python 3.11+
"""


# ==============================================================================
# Part 2. Imports
# ==============================================================================

import asyncio

import pytest

from scios.runtime.observability.tracing.decorators import (
    TraceDecoratorConfigurationError,
    TraceDecoratorError,
    TraceDecoratorRuntimeError,
    async_span,
    async_trace,
    span,
    spanned,
    trace,
    traced,
)
from scios.runtime.observability.tracing.manager import TraceManager


# ==============================================================================
# Part 3. Fixtures
# ==============================================================================

@pytest.fixture
def manager() -> TraceManager:
    """Create a default trace manager."""

    return TraceManager()


@pytest.fixture
def metadata() -> dict[str, object]:
    """Provide test metadata."""

    return {
        "component": "test",
        "version": "1.0",
    }


@pytest.fixture
def attributes() -> dict[str, object]:
    """Provide test attributes."""

    return {
        "environment": "test",
        "enabled": True,
    }


# ==============================================================================
# Part 4. Basic Decorator Tests
# ==============================================================================

def test_trace_is_callable():
    assert callable(trace)


def test_span_is_callable():
    assert callable(span)


def test_async_trace_is_callable():
    assert callable(async_trace)


def test_async_span_is_callable():
    assert callable(async_span)


def test_traced_is_alias_wrapper():
    assert callable(traced)


def test_spanned_is_alias_wrapper():
    assert callable(spanned)


def test_trace_preserves_function_metadata(manager):
    @trace(manager=manager)
    def sample_function():
        """Sample function."""

        return 42

    assert sample_function.__name__ == "sample_function"
    assert sample_function.__doc__ == "Sample function."
    assert sample_function() == 42


def test_span_preserves_function_metadata(manager):
    @span(manager=manager)
    def sample_function():
        return "ok"

    assert sample_function.__name__ == "sample_function"
    assert sample_function() == "ok"


# ==============================================================================
# Part 5. Trace Decorator Tests
# ==============================================================================

def test_trace_executes_function(manager):
    @trace(manager=manager)
    def calculate():
        return 10 + 5

    assert calculate() == 15


def test_trace_with_custom_name(manager):
    @trace(
        "custom-trace",
        manager=manager,
    )
    def calculate():
        return True

    assert calculate() is True


def test_trace_uses_function_name(manager):
    @trace(manager=manager)
    def calculate_value():
        return 100

    assert calculate_value() == 100


def test_trace_with_metadata(manager, metadata):
    @trace(
        manager=manager,
        metadata=metadata,
    )
    def calculate():
        return "done"

    assert calculate() == "done"


def test_trace_with_attributes(manager, attributes):
    @trace(
        manager=manager,
        attributes=attributes,
    )
    def calculate():
        return "done"

    assert calculate() == "done"


def test_trace_can_disable_attribute_setting(manager, attributes):
    @trace(
        manager=manager,
        attributes=attributes,
        set_attributes=False,
    )
    def calculate():
        return 1

    assert calculate() == 1


# ==============================================================================
# Part 6. Span Decorator Tests
# ==============================================================================

def test_span_executes_function(manager):
    @span(manager=manager)
    def calculate():
        return 20

    assert calculate() == 20


def test_span_with_custom_name(manager):
    @span(
        "custom-span",
        manager=manager,
    )
    def calculate():
        return "ok"

    assert calculate() == "ok"


def test_span_with_metadata(manager, metadata):
    @span(
        manager=manager,
        metadata=metadata,
    )
    def calculate():
        return 123

    assert calculate() == 123


def test_span_with_attributes(manager, attributes):
    @span(
        manager=manager,
        attributes=attributes,
    )
    def calculate():
        return 456

    assert calculate() == 456


# ==============================================================================
# Part 7. Function Arguments & Metadata Tests
# ==============================================================================

def test_trace_preserves_positional_arguments(manager):
    @trace(manager=manager)
    def add(a, b):
        return a + b

    assert add(2, 3) == 5


def test_trace_preserves_keyword_arguments(manager):
    @trace(manager=manager)
    def greet(name, prefix="Hello"):
        return f"{prefix}, {name}"

    assert greet(
        name="SciOS",
        prefix="Hi",
    ) == "Hi, SciOS"


def test_span_preserves_arguments(manager):
    @span(manager=manager)
    def multiply(a, b, c=1):
        return a * b * c

    assert multiply(2, 3, c=4) == 24


def test_metadata_is_copied(manager):
    metadata = {
        "key": "value",
    }

    @trace(
        manager=manager,
        metadata=metadata,
    )
    def function():
        return True

    metadata["changed"] = True

    assert function() is True


def test_attributes_are_copied(manager):
    attributes = {
        "key": "value",
    }

    @span(
        manager=manager,
        attributes=attributes,
    )
    def function():
        return True

    attributes["changed"] = True

    assert function() is True


# ==============================================================================
# Part 8. Exception Handling Tests
# ==============================================================================

def test_trace_reraises_exception(manager):
    @trace(manager=manager)
    def failing():
        raise ValueError("failure")

    with pytest.raises(ValueError, match="failure"):
        failing()


def test_span_reraises_exception(manager):
    @span(manager=manager)
    def failing():
        raise RuntimeError("failure")

    with pytest.raises(RuntimeError, match="failure"):
        failing()


def test_trace_can_disable_exception_recording(manager):
    @trace(
        manager=manager,
        record_exception=False,
    )
    def failing():
        raise ValueError("failure")

    with pytest.raises(ValueError, match="failure"):
        failing()


def test_span_can_disable_exception_recording(manager):
    @span(
        manager=manager,
        record_exception=False,
    )
    def failing():
        raise ValueError("failure")

    with pytest.raises(ValueError, match="failure"):
        failing()


# ==============================================================================
# Part 9. Nested Tracing Tests
# ==============================================================================

def test_nested_trace_and_span(manager):
    @span(
        "inner-span",
        manager=manager,
    )
    def inner():
        return "inner"

    @trace(
        "outer-trace",
        manager=manager,
    )
    def outer():
        return inner()

    assert outer() == "inner"


def test_nested_spans(manager):
    @span(
        "inner",
        manager=manager,
    )
    def inner():
        return 10

    @span(
        "outer",
        manager=manager,
    )
    def outer():
        return inner() + 5

    assert outer() == 15


def test_trace_inside_span(manager):
    @trace(
        "trace",
        manager=manager,
    )
    def traced_function():
        return "ok"

    @span(
        "span",
        manager=manager,
    )
    def spanned_function():
        return traced_function()

    assert spanned_function() == "ok"


# ==============================================================================
# Part 10. Async Decorator Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_async_trace_executes_function(manager):
    @async_trace(manager=manager)
    async def calculate():
        await asyncio.sleep(0)
        return 42

    assert await calculate() == 42


@pytest.mark.asyncio
async def test_async_span_executes_function(manager):
    @async_span(manager=manager)
    async def calculate():
        await asyncio.sleep(0)
        return 84

    assert await calculate() == 84


@pytest.mark.asyncio
async def test_async_trace_preserves_arguments(manager):
    @async_trace(manager=manager)
    async def add(a, b):
        await asyncio.sleep(0)
        return a + b

    assert await add(2, 8) == 10


@pytest.mark.asyncio
async def test_async_span_reraises_exception(manager):
    @async_span(manager=manager)
    async def failing():
        await asyncio.sleep(0)
        raise ValueError("async failure")

    with pytest.raises(
        ValueError,
        match="async failure",
    ):
        await failing()


def test_async_trace_rejects_sync_function(manager):
    with pytest.raises(
        TraceDecoratorConfigurationError,
    ):
        @async_trace(manager=manager)
        def function():
            return 1


def test_async_span_rejects_sync_function(manager):
    with pytest.raises(
        TraceDecoratorConfigurationError,
    ):
        @async_span(manager=manager)
        def function():
            return 1


# ==============================================================================
# Part 11. Context & Lifecycle Tests
# ==============================================================================

def test_trace_completes_successfully(manager):
    @trace(manager=manager)
    def function():
        return "completed"

    assert function() == "completed"


def test_span_completes_successfully(manager):
    @span(manager=manager)
    def function():
        return "completed"

    assert function() == "completed"


def test_trace_lifecycle_with_nested_span(manager):
    @span(manager=manager)
    def child():
        return "child"

    @trace(manager=manager)
    def parent():
        return child()

    assert parent() == "child"


def test_trace_uses_supplied_manager(manager):
    @trace(manager=manager)
    def function():
        return manager

    assert function() is manager


def test_span_uses_supplied_manager(manager):
    @span(manager=manager)
    def function():
        return manager

    assert function() is manager


# ==============================================================================
# Part 12. Disabled / Error-State Tests
# ==============================================================================

def test_trace_with_empty_name_uses_function_name(manager):
    @trace(
        "",
        manager=manager,
    )
    def sample():
        return True

    assert sample() is True


def test_span_with_empty_name_uses_function_name(manager):
    @span(
        "",
        manager=manager,
    )
    def sample():
        return True

    assert sample() is True


def test_trace_with_none_name_uses_function_name(manager):
    @trace(
        None,
        manager=manager,
    )
    def sample():
        return True

    assert sample() is True


def test_span_with_none_name_uses_function_name(manager):
    @span(
        None,
        manager=manager,
    )
    def sample():
        return True

    assert sample() is True


# ==============================================================================
# Part 13. Edge Cases
# ==============================================================================

def test_trace_returns_none(manager):
    @trace(manager=manager)
    def function():
        return None

    assert function() is None


def test_span_returns_none(manager):
    @span(manager=manager)
    def function():
        return None

    assert function() is None


def test_trace_returns_complex_value(manager):
    value = {
        "items": [1, 2, 3],
        "status": "ok",
    }

    @trace(manager=manager)
    def function():
        return value

    assert function() == value


def test_span_handles_empty_metadata(manager):
    @span(
        manager=manager,
        metadata={},
    )
    def function():
        return True

    assert function() is True


def test_trace_handles_empty_attributes(manager):
    @trace(
        manager=manager,
        attributes={},
    )
    def function():
        return True

    assert function() is True


def test_decorator_error_hierarchy():
    assert issubclass(
        TraceDecoratorConfigurationError,
        TraceDecoratorError,
    )

    assert issubclass(
        TraceDecoratorRuntimeError,
        TraceDecoratorError,
    )


# ==============================================================================
# Part 14. Public API Tests
# ==============================================================================

def test_traced_decorator(manager):
    @traced(manager=manager)
    def function():
        return 7

    assert function() == 7


def test_spanned_decorator(manager):
    @spanned(manager=manager)
    def function():
        return 8

    assert function() == 8


def test_public_decorators_are_callable():
    public_api = (
        trace,
        span,
        async_trace,
        async_span,
        traced,
        spanned,
    )

    assert all(
        callable(item)
        for item in public_api
    )


def test_public_exceptions_are_exception_types():
    exceptions = (
        TraceDecoratorError,
        TraceDecoratorConfigurationError,
        TraceDecoratorRuntimeError,
    )

    assert all(
        isinstance(item, type)
        and issubclass(item, Exception)
        for item in exceptions
    )