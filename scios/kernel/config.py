"""
SciOS Kernel Configuration
==========================

Defines configuration options for the SciOS Kernel.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(slots=True)
class KernelConfig:
    """
    Configuration for the SciOS Kernel.
    """

    enable_events: bool = True
    enable_plugins: bool = True
    enable_artifacts: bool = True

    auto_boot: bool = False
    debug: bool = False
