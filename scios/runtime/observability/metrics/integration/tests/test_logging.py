"""
Tests for MetricLoggingIntegration.

SciOS-NG v0.2
"""

from __future__ import annotations

import logging

import pytest

from ..logging import MetricLoggingIntegration


# ==============================================================
# Fixtures
# ==============================================================


@pytest.fixture
def logger():

    return logging.getLogger(
        "test_metric_logging_integration"
    )


@pytest.fixture
def integration(
    logger,
):

    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)

    return MetricLoggingIntegration(
        logger=logger
    )


# ==============================================================
# Constructor
# ==============================================================


def test_default_constructor():

    integration = MetricLoggingIntegration()

    assert integration.name == "MetricLoggingIntegration"
    assert integration.description == ""
    assert integration.enabled is True
    assert integration.closed is False
    assert integration.active is True

    assert integration.messages == 0
    assert integration.last_message is None
    assert integration.last_level is None
    assert integration.last_error is None


def test_custom_constructor(logger):

    integration = MetricLoggingIntegration(
        logger=logger,
        name="Custom",
        level=logging.DEBUG,
        enabled=False,
        description="test",
    )

    assert integration.name == "Custom"
    assert integration.description == "test"
    assert integration.logger is logger
    assert integration.level == logging.DEBUG
    assert integration.enabled is False


# ==============================================================
# Logger Management
# ==============================================================


def test_set_logger(
    integration,
):

    logger = logging.getLogger(
        "replacement_logger"
    )

    assert integration.set_logger(
        logger
    ) is integration

    assert integration.logger is logger


def test_set_logger_invalid(
    integration,
):

    with pytest.raises(
        TypeError,
        match="logging.Logger",
    ):
        integration.set_logger(
            object()
        )


def test_set_level(
    integration,
):

    assert integration.set_level(
        logging.DEBUG
    ) is integration

    assert integration.level == logging.DEBUG
    assert integration.logger.level == logging.DEBUG


def test_set_level_invalid(
    integration,
):

    with pytest.raises(
        TypeError,
        match="integer",
    ):
        integration.set_level(
            "INFO"
        )


# ==============================================================
# Core Logging
# ==============================================================


def test_log(
    integration,
    caplog,
):

    with caplog.at_level(
        logging.INFO,
        logger=integration.logger.name,
    ):

        assert integration.log(
            logging.INFO,
            "hello",
        ) is True

    assert "hello" in caplog.text

    assert integration.messages == 1
    assert integration.last_message == "hello"
    assert integration.last_level == logging.INFO


def test_log_with_args(
    integration,
    caplog,
):

    with caplog.at_level(
        logging.INFO,
        logger=integration.logger.name,
    ):

        integration.log(
            logging.INFO,
            "value=%s",
            42,
        )

    assert "value=42" in caplog.text


def test_log_level_counters(
    integration,
):

    integration.debug("debug")
    integration.info("info")
    integration.warning("warning")
    integration.error("error")
    integration.critical("critical")

    stats = integration.statistics()

    assert stats["messages"] == 5
    assert stats["debug"] == 1
    assert stats["info"] == 1
    assert stats["warning"] == 1
    assert stats["error"] == 1
    assert stats["critical"] == 1


# ==============================================================
# Convenience APIs
# ==============================================================


def test_debug(
    integration,
):

    assert integration.debug(
        "debug"
    ) is True


def test_info(
    integration,
):

    assert integration.info(
        "info"
    ) is True


def test_warning(
    integration,
):

    assert integration.warning(
        "warning"
    ) is True


def test_error(
    integration,
):

    assert integration.error(
        "error"
    ) is True


def test_critical(
    integration,
):

    assert integration.critical(
        "critical"
    ) is True


# ==============================================================
# Metric Logging
# ==============================================================


def test_log_metric(
    integration,
    caplog,
):

    with caplog.at_level(
        logging.INFO,
        logger=integration.logger.name,
    ):

        assert integration.log_metric(
            {"value": 42},
            source="test",
        ) is True

    assert "metric: {'value': 42}" in caplog.text
    assert "source='test'" in caplog.text


def test_info_metric(
    integration,
):

    assert integration.info_metric(
        {"value": 1}
    ) is True


def test_debug_metric(
    integration,
):

    assert integration.debug_metric(
        {"value": 1}
    ) is True


# ==============================================================
# Callable
# ==============================================================


def test_call(
    integration,
):

    assert integration(
        "hello"
    ) is True

    assert integration.last_message == "hello"


# ==============================================================
# Lifecycle
# ==============================================================


def test_disable(
    integration,
):

    assert integration.disable() is integration
    assert integration.enabled is False
    assert integration.active is False

    with pytest.raises(
        RuntimeError,
        match="disabled",
    ):
        integration.info("test")


def test_enable(
    integration,
):

    integration.disable()

    assert integration.enable() is integration
    assert integration.enabled is True
    assert integration.active is True


def test_close(
    integration,
):

    assert integration.close() is integration
    assert integration.closed is True
    assert integration.active is False

    with pytest.raises(
        RuntimeError,
        match="closed",
    ):
        integration.info("test")


def test_reopen(
    integration,
):

    integration.close()

    assert integration.reopen() is integration
    assert integration.closed is False
    assert integration.active is True


# ==============================================================
# Statistics
# ==============================================================


def test_statistics_initial(
    integration,
):

    stats = integration.statistics()

    assert stats["name"] == "MetricLoggingIntegration"
    assert stats["messages"] == 0
    assert stats["debug"] == 0
    assert stats["info"] == 0
    assert stats["warning"] == 0
    assert stats["error"] == 0
    assert stats["critical"] == 0


def test_status(
    integration,
):

    status = integration.status()

    assert status["enabled"] is True
    assert status["closed"] is False
    assert status["active"] is True
    assert status["messages"] == 0


def test_reset(
    integration,
):

    integration.info("one")
    integration.error("two")

    assert integration.messages == 2

    assert integration.reset() is integration

    assert integration.messages == 0
    assert integration.last_message is None
    assert integration.last_level is None
    assert integration.last_error is None

    stats = integration.statistics()

    assert stats["debug"] == 0
    assert stats["info"] == 0
    assert stats["warning"] == 0
    assert stats["error"] == 0
    assert stats["critical"] == 0


# ==============================================================
# Protocols
# ==============================================================


def test_len(
    integration,
):

    integration.info("one")
    integration.info("two")

    assert len(integration) == 2


def test_repr(
    integration,
):

    value = repr(integration)

    assert "MetricLoggingIntegration" in value
    assert "messages=0" in value


def test_str(
    integration,
):

    assert str(integration) == "MetricLoggingIntegration"