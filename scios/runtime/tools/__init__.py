"""
SciOS Runtime Tools
===================

Public API for SciOS Tool Execution Layer.

Architecture:

    Tool
      |
      +── ToolResult
      |
      +── ToolPolicy
      |
      +── ToolRegistry
      |
      +── ToolSandbox
      |
      +── ToolExecutor


Python 3.11+
"""


from __future__ import annotations



# ==========================================================
# Base Contract
# ==========================================================

from .base import (
    Tool,
)



# ==========================================================
# Result
# ==========================================================

from .result import (
    ToolResult,
)



# ==========================================================
# Security Policy
# ==========================================================

from .policy import (
    ToolPolicy,
)



# ==========================================================
# Registry
# ==========================================================

from .registry import (
    ToolRegistry,
)



# ==========================================================
# Sandbox
# ==========================================================

from .sandbox import (
    ToolSandbox,
)



# ==========================================================
# Executor
# ==========================================================

from .executor import (
    ToolExecutor,
)



# ==========================================================
# Public API
# ==========================================================


__all__ = [

    # Base

    "Tool",


    # Result

    "ToolResult",


    # Security

    "ToolPolicy",


    # Management

    "ToolRegistry",


    # Isolation

    "ToolSandbox",


    # Runtime

    "ToolExecutor",

]