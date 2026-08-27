"""
Tests for SciOS Runtime Metrics Async Middleware.
"""

from __future__ import annotations

import pytest

from ..async_middleware import MetricAsyncMiddleware


# ==============================================================
# Fixtures
# ==============================================================


@pytest.fixture
def middleware() -> MetricAsyncMiddleware:
    return MetricAsyncMiddleware()


# ==============================================================
# Construction
# ==============================================================


def test_default_construction(middleware):
    assert middleware.name == "MetricAsyncMiddleware"
    assert middleware.description == ""
    assert middleware.enabled is True
    assert middleware.running is False
    assert middleware.closed is False
    assert middleware.active is True


def test_custom_construction():
    middleware = MetricAsyncMiddleware(
        name="custom",
        description="test",
    )

    assert middleware.name == "custom"
    assert middleware.description == "test"
    assert middleware.id


# ==============================================================
# Execution
# ==============================================================


@pytest.mark.asyncio
async def test_execute_without_handler(middleware):
    metric = {"value": 42}

    result = await middleware.execute(metric)

    assert result == metric


@pytest.mark.asyncio
async def test_execute_sync_handler():
    middleware = MetricAsyncMiddleware(
        handler=lambda metric: {
            "value": metric["value"] + 1
        }
    )

    result = await middleware.execute(
        {"value": 41}
    )

    assert result == {"value": 42}


@pytest.mark.asyncio
async def test_execute_async_handler():
    async def handler(metric):
        return {
            "value": metric["value"] + 1
        }

    middleware = MetricAsyncMiddleware(
        handler=handler
    )

    result = await middleware.execute(
        {"value": 41}
    )

    assert result == {"value": 42}


@pytest.mark.asyncio
async def test_execute_preserves_kwargs():
    async def handler(metric, source=None):
        return {
            "value": metric["value"],
            "source": source,
        }

    middleware = MetricAsyncMiddleware(
        handler=handler
    )

    result = await middleware.execute(
        {"value": 42},
        source="runtime",
    )

    assert result == {
        "value": 42,
        "source": "runtime",
    }


@pytest.mark.asyncio
async def test_run_alias(middleware):
    result = await middleware.run(
        {"value": 42}
    )

    assert result == {"value": 42}


@pytest.mark.asyncio
async def test_process_alias(middleware):
    result = await middleware.process(
        {"value": 42}
    )

    assert result == {"value": 42}


# ==============================================================
# Statistics
# ==============================================================


@pytest.mark.asyncio
async def test_success_statistics(middleware):
    await middleware.execute({"value": 1})
    await middleware.execute({"value": 2})

    stats = middleware.statistics()

    assert stats["executions"] == 2
    assert stats["success"] == 2
    assert stats["failures"] == 0


@pytest.mark.asyncio
async def test_failure_statistics():
    async def handler(metric):
        raise RuntimeError("boom")

    middleware = MetricAsyncMiddleware(
        handler=handler
    )

    with pytest.raises(RuntimeError):
        await middleware.execute({})

    stats = middleware.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 0
    assert stats["failures"] == 1


# ==============================================================
# Diagnostics
# ==============================================================


@pytest.mark.asyncio
async def test_last_result():
    middleware = MetricAsyncMiddleware(
        handler=lambda metric: {
            "value": 42
        }
    )

    result = await middleware.execute({})

    assert middleware.last_result == result
    assert middleware.last_error is None


@pytest.mark.asyncio
async def test_last_error():
    error = RuntimeError("boom")

    async def handler(metric):
        raise error

    middleware = MetricAsyncMiddleware(
        handler=handler
    )

    with pytest.raises(RuntimeError):
        await middleware.execute({})

    assert middleware.last_error is error
    assert middleware.last_result is None


# ==============================================================
# Handler Management
# ==============================================================


def test_set_handler(middleware):
    handler = lambda metric: metric

    assert middleware.set_handler(handler) is middleware
    assert middleware.handler() is handler


def test_set_handler_rejects_invalid(middleware):
    with pytest.raises(TypeError):
        middleware.set_handler("invalid")


def test_clear_handler(middleware):
    middleware.set_handler(lambda metric: metric)

    assert middleware.clear_handler() is middleware
    assert middleware.handler() is None


# ==============================================================
# Lifecycle
# ==============================================================


def test_disable(middleware):
    assert middleware.disable() is middleware
    assert middleware.enabled is False
    assert middleware.active is False


def test_enable(middleware):
    middleware.disable()

    assert middleware.enable() is middleware
    assert middleware.enabled is True
    assert middleware.active is True


def test_close(middleware):
    assert middleware.close() is middleware
    assert middleware.closed is True
    assert middleware.active is False


def test_reopen(middleware):
    middleware.close()

    assert middleware.reopen() is middleware
    assert middleware.closed is False
    assert middleware.active is True


@pytest.mark.asyncio
async def test_disabled_execution_fails(middleware):
    middleware.disable()

    with pytest.raises(RuntimeError, match="disabled"):
        await middleware.execute({})


@pytest.mark.asyncio
async def test_closed_execution_fails(middleware):
    middleware.close()

    with pytest.raises(RuntimeError, match="closed"):
        await middleware.execute({})


# ==============================================================
# Reset
# ==============================================================


@pytest.mark.asyncio
async def test_reset():
    middleware = MetricAsyncMiddleware(
        handler=lambda metric: {
            "value": 42
        }
    )

    await middleware.execute({})

    assert middleware.statistics()["executions"] == 1
    assert middleware.last_result == {
        "value": 42
    }

    assert middleware.reset() is middleware

    stats = middleware.statistics()

    assert stats["executions"] == 0
    assert stats["success"] == 0
    assert stats["failures"] == 0

    assert middleware.last_result is None
    assert middleware.last_error is None
    assert middleware.handler() is not None


# ==============================================================
# Status
# ==============================================================


def test_status(middleware):
    status = middleware.status()

    assert status == {
        "enabled": True,
        "running": False,
        "closed": False,
        "active": True,
    }


# ==============================================================
# Protocols
# ==============================================================


def test_repr(middleware):
    text = repr(middleware)

    assert text.startswith(
        "MetricAsyncMiddleware("
    )
    assert "executions=0" in text
    assert "success=0" in text
    assert "failures=0" in text


def test_str(middleware):
    assert str(middleware) == "MetricAsyncMiddleware"


def test_call_returns_awaitable(middleware):
    result = middleware({"value": 42})

    assert hasattr(result, "__await__")

    # Avoid un-awaited coroutine warning.
    result.close()


def test_len(middleware):
    assert len(middleware) == 0