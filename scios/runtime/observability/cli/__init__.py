"""
SciOS-NG Runtime Observability

Command Line Interface (CLI)

This package provides command-line style interfaces for
inspecting and interacting with the SciOS runtime
observability subsystem.

Modules
-------
trace
    Runtime trace inspection CLI.

metrics
    Runtime metrics inspection CLI.

logs
    Runtime log inspection CLI.

inspect
    Unified observability inspector.

Example
-------
>>> from scios.runtime.observability.cli import (
...     TraceCLI,
...     MetricsCLI,
...     LogsCLI,
...     InspectCLI,
... )

>>> trace = TraceCLI()
>>> metrics = MetricsCLI()
>>> logs = LogsCLI()

>>> inspector = InspectCLI(
...     trace=trace,
...     metrics=metrics,
...     logs=logs,
... )
"""

from __future__ import annotations

from .trace import TraceCLI
from .metrics import MetricsCLI
from .logs import LogsCLI
from .inspect import InspectCLI

__all__ = [
    "TraceCLI",
    "MetricsCLI",
    "LogsCLI",
    "InspectCLI",
]

__version__ = "0.1.0"

__author__ = "SciOS-NG"

__description__ = (
    "SciOS Runtime Observability CLI"
)