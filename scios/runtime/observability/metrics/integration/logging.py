"""
SciOS-NG Runtime Metrics Logging Integration

Logging integration for the Metrics subsystem.

SciOS-NG v0.2
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any


# ==============================================================
# MetricLoggingIntegration
# ==============================================================


class MetricLoggingIntegration:
    """
    Logging integration for the Metrics subsystem.

    Responsibilities
    ----------------
    - Provide a unified metrics logging API
    - Integrate with Python logging
    - Support standard log levels
    - Track logging statistics
    - Provide runtime diagnostics
    - Manage logging lifecycle
    """

    LEVELS = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    def __init__(
        self,
        logger: logging.Logger | None = None,
        name: str = "MetricLoggingIntegration",
        level: int = logging.INFO,
        enabled: bool = True,
        description: str = "",
    ) -> None:

        self._name = name
        self._description = description

        self._logger = (
            logger
            if logger is not None
            else logging.getLogger(name)
        )

        self._level = level

        self._enabled = enabled
        self._closed = False

        self._messages = 0
        self._debug = 0
        self._info = 0
        self._warning = 0
        self._error = 0
        self._critical = 0

        self._last_message: str | None = None
        self._last_level: int | None = None
        self._last_error: Exception | None = None

        self._created_at = datetime.utcnow()
        self._updated_at = self._created_at

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def level(self) -> int:
        return self._level

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def active(self) -> bool:
        return self._enabled and not self._closed

    @property
    def messages(self) -> int:
        return self._messages

    @property
    def last_message(self) -> str | None:
        return self._last_message

    @property
    def last_level(self) -> int | None:
        return self._last_level

    @property
    def last_error(self) -> Exception | None:
        return self._last_error

    # ==========================================================
    # Logger Management
    # ==========================================================

    def set_logger(
        self,
        logger: logging.Logger,
    ) -> "MetricLoggingIntegration":
        """
        Replace the underlying logger.
        """

        if not isinstance(
            logger,
            logging.Logger,
        ):
            raise TypeError(
                "logger must be an instance of logging.Logger"
            )

        self._logger = logger
        self._updated_at = datetime.utcnow()

        return self

    def set_level(
        self,
        level: int,
    ) -> "MetricLoggingIntegration":
        """
        Set the logging level.
        """

        if not isinstance(level, int):
            raise TypeError(
                "level must be an integer"
            )

        self._level = level
        self._logger.setLevel(level)
        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Core Logging
    # ==========================================================

    def log(
        self,
        level: int,
        message: Any,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        """
        Log a message at the specified level.

        Returns
        -------
        bool
            True when the message was accepted by the
            integration, False when logging is disabled.
        """

        self._ensure_active()

        if not isinstance(level, int):
            raise TypeError(
                "level must be an integer"
            )

        text = str(message)

        try:

            self._logger.log(
                level,
                message,
                *args,
                **kwargs,
            )

            self._messages += 1
            self._last_message = text
            self._last_level = level
            self._last_error = None

            self._increment_level_counter(level)

            self._updated_at = datetime.utcnow()

            return True

        except Exception as exc:

            self._last_error = exc
            self._updated_at = datetime.utcnow()

            raise

    # ==========================================================
    # Convenience Levels
    # ==========================================================

    def debug(
        self,
        message: Any,
        *args: Any,
        **kwargs: Any,
    ) -> bool:

        return self.log(
            logging.DEBUG,
            message,
            *args,
            **kwargs,
        )

    def info(
        self,
        message: Any,
        *args: Any,
        **kwargs: Any,
    ) -> bool:

        return self.log(
            logging.INFO,
            message,
            *args,
            **kwargs,
        )

    def warning(
        self,
        message: Any,
        *args: Any,
        **kwargs: Any,
    ) -> bool:

        return self.log(
            logging.WARNING,
            message,
            *args,
            **kwargs,
        )

    def error(
        self,
        message: Any,
        *args: Any,
        **kwargs: Any,
    ) -> bool:

        return self.log(
            logging.ERROR,
            message,
            *args,
            **kwargs,
        )

    def critical(
        self,
        message: Any,
        *args: Any,
        **kwargs: Any,
    ) -> bool:

        return self.log(
            logging.CRITICAL,
            message,
            *args,
            **kwargs,
        )

    # ==========================================================
    # Metric Logging
    # ==========================================================

    def log_metric(
        self,
        metric: Any,
        level: int = logging.INFO,
        prefix: str = "metric",
        **kwargs: Any,
    ) -> bool:
        """
        Log a metric object.

        Dictionaries are represented using their normal
        string representation; keyword metadata is appended
        when provided.
        """

        message = f"{prefix}: {metric}"

        if kwargs:
            metadata = ", ".join(
                f"{key}={value!r}"
                for key, value in kwargs.items()
            )

            message = (
                f"{message} [{metadata}]"
            )

        return self.log(
            level,
            message,
        )

    def info_metric(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> bool:

        return self.log_metric(
            metric,
            level=logging.INFO,
            **kwargs,
        )

    def debug_metric(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> bool:

        return self.log_metric(
            metric,
            level=logging.DEBUG,
            **kwargs,
        )

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def enable(
        self,
    ) -> "MetricLoggingIntegration":

        self._enabled = True
        self._updated_at = datetime.utcnow()

        return self

    def disable(
        self,
    ) -> "MetricLoggingIntegration":

        self._enabled = False
        self._updated_at = datetime.utcnow()

        return self

    def close(
        self,
    ) -> "MetricLoggingIntegration":

        self._closed = True
        self._updated_at = datetime.utcnow()

        return self

    def reopen(
        self,
    ) -> "MetricLoggingIntegration":

        self._closed = False
        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Statistics
    # ==========================================================

    def statistics(self) -> dict[str, Any]:
        """
        Return logging statistics.
        """

        return {
            "name": self._name,
            "messages": self._messages,
            "debug": self._debug,
            "info": self._info,
            "warning": self._warning,
            "error": self._error,
            "critical": self._critical,
            "enabled": self._enabled,
            "closed": self._closed,
        }

    # ==========================================================
    # Diagnostics
    # ==========================================================

    def status(self) -> dict[str, Any]:
        """
        Return runtime logging status.
        """

        return {
            "enabled": self._enabled,
            "closed": self._closed,
            "active": self.active,
            "messages": self._messages,
            "level": self._level,
        }

    def reset(
        self,
    ) -> "MetricLoggingIntegration":
        """
        Reset runtime statistics.
        """

        self._messages = 0
        self._debug = 0
        self._info = 0
        self._warning = 0
        self._error = 0
        self._critical = 0

        self._last_message = None
        self._last_level = None
        self._last_error = None

        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Internal
    # ==========================================================

    def _increment_level_counter(
        self,
        level: int,
    ) -> None:

        if level >= logging.CRITICAL:
            self._critical += 1

        elif level >= logging.ERROR:
            self._error += 1

        elif level >= logging.WARNING:
            self._warning += 1

        elif level >= logging.INFO:
            self._info += 1

        else:
            self._debug += 1

    def _ensure_active(self) -> None:

        if not self._enabled:
            raise RuntimeError(
                f"Logging integration {self._name} disabled"
            )

        if self._closed:
            raise RuntimeError(
                f"Logging integration {self._name} closed"
            )

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __call__(
        self,
        message: Any,
        level: int = logging.INFO,
        **kwargs: Any,
    ) -> bool:

        return self.log(
            level,
            message,
            **kwargs,
        )

    def __len__(self) -> int:
        return self._messages

    def __repr__(self) -> str:

        return (
            f"MetricLoggingIntegration("
            f"name={self._name!r}, "
            f"messages={self._messages}, "
            f"enabled={self._enabled}, "
            f"closed={self._closed}"
            f")"
        )

    def __str__(self) -> str:
        return self._name