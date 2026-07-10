"""
SciOS Tool Use Package
======================

Public API for the SciOS Tool Use subsystem.

This package provides:

- Tool lifecycle management
- Tool execution state
- Request / Response models
- Metrics & Monitoring
- Recovery
- Sandbox execution

The symbols exported here form the stable public API.
"""

from __future__ import annotations

__version__ = "0.1.0"

# ---------------------------------------------------------------------
# Core Models
# ---------------------------------------------------------------------

from .request import ToolRequest
from .response import ToolResponse

# ---------------------------------------------------------------------
# Runtime Components
# ---------------------------------------------------------------------

from .history import ToolHistory
from .metrics import Metrics
from .monitor import Monitor
from .recovery import Recovery

# ---------------------------------------------------------------------
# Adapters
# ---------------------------------------------------------------------

from .adapters import (
    RequestAdapter,
    ResponseAdapter,
)

# ---------------------------------------------------------------------
# Tool Stage
# ---------------------------------------------------------------------

from .stage import (
    ToolUseStage,
    ToolStage,          # Backward compatibility alias
)

# ---------------------------------------------------------------------
# Sandbox
# ---------------------------------------------------------------------

from .sandbox import ToolSandbox

# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

__all__ = (
    "ToolRequest",
    "ToolResponse",
    "ToolHistory",
    "Metrics",
    "Monitor",
    "Recovery",
    "RequestAdapter",
    "ResponseAdapter",
    "ToolUseStage",
    "ToolStage",
    "ToolSandbox",
)
