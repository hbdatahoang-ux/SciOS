"""
SciOS Logging Framework
=======================

Central logging utilities for the Scientific Cognitive Operating System.

Features
--------
- Singleton logger manager
- Console logging
- File logging
- Configurable log levels
- Child loggers
- Runtime reconfiguration
"""

from __future__ import annotations

import logging
from logging import Logger
from pathlib import Path
from typing import Dict

__all__ = [
    "SciOSLogger",
    "get_logger",
    "configure_logging",
]


# ==========================================================
# Default Formatter
# ==========================================================

DEFAULT_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)s | "
    "%(message)s"
)

DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ==========================================================
# Logger Manager
# ==========================================================

class SciOSLogger:
    """
    Central logger manager.

    Responsibilities
    ----------------
    - Configure logging
    - Provide singleton loggers
    - Manage console/file handlers
    """

    def __init__(self):

        self._configured = False

        self._loggers: Dict[str, Logger] = {}

    # ------------------------------------------------------

    def configure(
        self,
        *,
        level: str = "INFO",
        console: bool = True,
        file: bool = False,
        directory: str | Path = "logs",
        filename: str = "scios.log",
    ) -> None:
        """
        Configure the logging system.
        """

        if self._configured:
            return

        handlers = []

        formatter = logging.Formatter(
            DEFAULT_FORMAT,
            DEFAULT_DATE_FORMAT,
        )

        if console:

            console_handler = logging.StreamHandler()

            console_handler.setFormatter(formatter)

            handlers.append(console_handler)

        if file:

            directory = Path(directory)

            directory.mkdir(
                parents=True,
                exist_ok=True,
            )

            file_handler = logging.FileHandler(
                directory / filename,
                encoding="utf-8",
            )

            file_handler.setFormatter(formatter)

            handlers.append(file_handler)

        logging.basicConfig(
            level=getattr(logging, level.upper()),
            handlers=handlers,
            force=True,
        )

        self._configured = True

    # ------------------------------------------------------

    def get_logger(
        self,
        name: str,
    ) -> Logger:
        """
        Return a named logger.
        """

        if name not in self._loggers:

            self._loggers[name] = logging.getLogger(name)

        return self._loggers[name]

    # ------------------------------------------------------

    @property
    def configured(self) -> bool:
        """
        Return configuration status.
        """

        return self._configured


# ==========================================================
# Global Logger Manager
# ==========================================================

_manager = SciOSLogger()


# ==========================================================
# Public API
# ==========================================================

def configure_logging(
    *,
    level: str = "INFO",
    console: bool = True,
    file: bool = False,
    directory: str | Path = "logs",
    filename: str = "scios.log",
) -> None:
    """
    Configure the global logging system.
    """

    _manager.configure(
        level=level,
        console=console,
        file=file,
        directory=directory,
        filename=filename,
    )


def get_logger(
    name: str = "SciOS",
) -> Logger:
    """
    Return a configured logger.

    Parameters
    ----------
    name:
        Logger name.

    Returns
    -------
    logging.Logger
    """

    if not _manager.configured:

        _manager.configure()

    return _manager.get_logger(name)