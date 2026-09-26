"""
Tests for SciOS shared logging framework.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

import scios.shared.logger as logger_module
from scios.shared.logger import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_FORMAT,
    SciOSLogger,
    configure_logging,
    get_logger,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def reset_logging_state():
    """
    Reset SciOS logger manager and root logging state around every test.
    """

    old_manager = logger_module._manager

    root = logging.getLogger()

    old_handlers = root.handlers[:]
    old_level = root.level

    logger_module._manager = SciOSLogger()

    for handler in root.handlers[:]:
        root.removeHandler(handler)
        try:
            handler.close()
        except Exception:
            pass

    yield

    for handler in root.handlers[:]:
        root.removeHandler(handler)
        try:
            handler.close()
        except Exception:
            pass

    for handler in old_handlers:
        root.addHandler(handler)

    root.setLevel(old_level)

    logger_module._manager = old_manager


# ============================================================================
# Constants
# ============================================================================


def test_default_format_exists():
    assert isinstance(DEFAULT_FORMAT, str)
    assert "%(asctime)s" in DEFAULT_FORMAT
    assert "%(levelname)" in DEFAULT_FORMAT
    assert "%(name)s" in DEFAULT_FORMAT
    assert "%(message)s" in DEFAULT_FORMAT


def test_default_date_format_exists():
    assert DEFAULT_DATE_FORMAT == "%Y-%m-%d %H:%M:%S"


# ============================================================================
# SciOSLogger construction
# ============================================================================


def test_manager_initializes_unconfigured():
    manager = SciOSLogger()

    assert manager.configured is False


def test_manager_starts_with_empty_logger_cache():
    manager = SciOSLogger()

    assert manager._loggers == {}


# ============================================================================
# Configuration
# ============================================================================


def test_configure_marks_manager_configured():
    manager = SciOSLogger()

    manager.configure()

    assert manager.configured is True


def test_configure_console_by_default():
    manager = SciOSLogger()

    manager.configure()

    root = logging.getLogger()

    assert root.level == logging.INFO
    assert len(root.handlers) == 1
    assert isinstance(root.handlers[0], logging.StreamHandler)


def test_configure_without_console_creates_no_handlers():
    manager = SciOSLogger()

    manager.configure(console=False)

    root = logging.getLogger()

    assert manager.configured is True
    assert root.handlers == []


def test_configure_debug_level():
    manager = SciOSLogger()

    manager.configure(
        level="DEBUG",
        console=False,
    )

    assert logging.getLogger().level == logging.DEBUG


def test_configure_warning_level():
    manager = SciOSLogger()

    manager.configure(
        level="WARNING",
        console=False,
    )

    assert logging.getLogger().level == logging.WARNING


def test_configure_error_level():
    manager = SciOSLogger()

    manager.configure(
        level="ERROR",
        console=False,
    )

    assert logging.getLogger().level == logging.ERROR


def test_configure_case_insensitive_level():
    manager = SciOSLogger()

    manager.configure(
        level="debug",
        console=False,
    )

    assert logging.getLogger().level == logging.DEBUG


def test_configure_invalid_level_raises():
    manager = SciOSLogger()

    with pytest.raises(AttributeError):
        manager.configure(
            level="NOT_A_REAL_LEVEL",
            console=False,
        )


# ============================================================================
# Formatter
# ============================================================================


def test_console_handler_has_default_formatter():
    manager = SciOSLogger()

    manager.configure()

    handler = logging.getLogger().handlers[0]

    assert handler.formatter is not None
    assert handler.formatter._fmt == DEFAULT_FORMAT
    assert handler.formatter.datefmt == DEFAULT_DATE_FORMAT


# ============================================================================
# File logging
# ============================================================================


def test_file_logging_creates_directory(tmp_path: Path):
    manager = SciOSLogger()

    log_dir = tmp_path / "nested" / "logs"

    manager.configure(
        console=False,
        file=True,
        directory=log_dir,
    )

    assert log_dir.exists()
    assert log_dir.is_dir()


def test_file_logging_creates_log_file(tmp_path: Path):
    manager = SciOSLogger()

    manager.configure(
        console=False,
        file=True,
        directory=tmp_path,
        filename="runtime.log",
    )

    logger = manager.get_logger("test.file")
    logger.warning("hello")

    for handler in logging.getLogger().handlers:
        handler.flush()

    log_file = tmp_path / "runtime.log"

    assert log_file.exists()
    assert "hello" in log_file.read_text(encoding="utf-8")


def test_file_logging_uses_requested_filename(tmp_path: Path):
    manager = SciOSLogger()

    manager.configure(
        console=False,
        file=True,
        directory=tmp_path,
        filename="custom.log",
    )

    assert (tmp_path / "custom.log").exists()


def test_file_handler_has_default_formatter(tmp_path: Path):
    manager = SciOSLogger()

    manager.configure(
        console=False,
        file=True,
        directory=tmp_path,
    )

    handlers = logging.getLogger().handlers

    assert len(handlers) == 1

    handler = handlers[0]

    assert isinstance(handler, logging.FileHandler)
    assert handler.formatter is not None
    assert handler.formatter._fmt == DEFAULT_FORMAT
    assert handler.formatter.datefmt == DEFAULT_DATE_FORMAT


def test_console_and_file_can_be_enabled_together(tmp_path: Path):
    manager = SciOSLogger()

    manager.configure(
        console=True,
        file=True,
        directory=tmp_path,
    )

    handlers = logging.getLogger().handlers

    assert len(handlers) == 2

    assert any(
        isinstance(handler, logging.FileHandler)
        for handler in handlers
    )

    assert any(
        isinstance(handler, logging.StreamHandler)
        and not isinstance(handler, logging.FileHandler)
        for handler in handlers
    )


# ============================================================================
# Idempotency
# ============================================================================


def test_configure_is_idempotent():
    manager = SciOSLogger()

    manager.configure(
        level="INFO",
        console=True,
    )

    root = logging.getLogger()

    first_handlers = root.handlers[:]
    first_level = root.level

    manager.configure(
        level="DEBUG",
        console=False,
    )

    assert manager.configured is True
    assert root.handlers == first_handlers
    assert root.level == first_level


def test_second_configure_does_not_replace_handlers():
    manager = SciOSLogger()

    manager.configure()

    first_handlers = tuple(logging.getLogger().handlers)

    manager.configure()

    second_handlers = tuple(logging.getLogger().handlers)

    assert second_handlers == first_handlers


# ============================================================================
# Logger retrieval
# ============================================================================


def test_get_logger_returns_logging_logger():
    manager = SciOSLogger()

    logger = manager.get_logger("test")

    assert isinstance(logger, logging.Logger)


def test_get_logger_preserves_name():
    manager = SciOSLogger()

    logger = manager.get_logger("scios.runtime")

    assert logger.name == "scios.runtime"


def test_get_logger_caches_named_logger():
    manager = SciOSLogger()

    first = manager.get_logger("test")
    second = manager.get_logger("test")

    assert first is second


def test_get_logger_supports_multiple_names():
    manager = SciOSLogger()

    first = manager.get_logger("first")
    second = manager.get_logger("second")

    assert first is not second
    assert first.name == "first"
    assert second.name == "second"


def test_get_logger_cache_is_populated():
    manager = SciOSLogger()

    manager.get_logger("one")
    manager.get_logger("two")

    assert set(manager._loggers) == {"one", "two"}


# ============================================================================
# Global public API
# ============================================================================


def test_global_get_logger_auto_configures():
    assert logger_module._manager.configured is False

    logger = get_logger("SciOS.test")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "SciOS.test"
    assert logger_module._manager.configured is True


def test_global_get_logger_uses_default_name():
    logger = get_logger()

    assert isinstance(logger, logging.Logger)
    assert logger.name == "SciOS"


def test_global_get_logger_returns_same_logger():
    first = get_logger("SciOS.runtime")
    second = get_logger("SciOS.runtime")

    assert first is second


def test_global_configure_logging_configures_manager():
    assert logger_module._manager.configured is False

    configure_logging(
        level="WARNING",
        console=False,
    )

    assert logger_module._manager.configured is True
    assert logging.getLogger().level == logging.WARNING


def test_global_configure_logging_accepts_file(tmp_path: Path):
    configure_logging(
        console=False,
        file=True,
        directory=tmp_path,
        filename="scios-test.log",
    )

    assert (tmp_path / "scios-test.log").exists()


# ============================================================================
# Logging behavior
# ============================================================================


def test_logger_can_emit_message():
    manager = SciOSLogger()

    manager.configure(
        level="INFO",
        console=False,
    )

    logger = manager.get_logger("test.emit")

    records = []

    class CaptureHandler(logging.Handler):
        def emit(self, record):
            records.append(record)

    handler = CaptureHandler()
    logger.addHandler(handler)

    try:
        logger.info("test message")
    finally:
        logger.removeHandler(handler)

    assert any(
        record.getMessage() == "test message"
        for record in records
    )


def test_logger_respects_configured_level():
    manager = SciOSLogger()

    manager.configure(
        level="WARNING",
        console=False,
    )

    logger = manager.get_logger("test.level")

    records = []

    class CaptureHandler(logging.Handler):
        def emit(self, record):
            records.append(record)

    handler = CaptureHandler()
    logger.addHandler(handler)

    try:
        logger.info("hidden message")
        logger.warning("visible message")
    finally:
        logger.removeHandler(handler)

    messages = [
        record.getMessage()
        for record in records
    ]

    assert "visible message" in messages
    assert "hidden message" not in messages


# ============================================================================
# Public contract
# ============================================================================


def test_scios_logger_public_methods_exist():
    expected = (
        "configure",
        "get_logger",
    )

    for name in expected:
        assert hasattr(SciOSLogger, name)
        assert callable(getattr(SciOSLogger, name))


def test_scios_logger_configured_property_exists():
    manager = SciOSLogger()

    assert hasattr(manager, "configured")
    assert isinstance(manager.configured, bool)


def test_logger_module_public_api():
    assert logger_module.__all__ == [
        "SciOSLogger",
        "get_logger",
        "configure_logging",
    ]
