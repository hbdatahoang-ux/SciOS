"""
Runtime governance exceptions.

This module defines the exception boundary for Runtime Governance
Integration v0.1.
"""

from __future__ import annotations

__all__ = ["GovernanceError"]


class GovernanceError(Exception):
    """Raised when runtime governance denies or cannot authorize execution."""
