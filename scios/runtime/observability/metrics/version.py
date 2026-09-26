"""
SciOS Runtime Metrics Version
=============================

Version information for SciOS Metrics subsystem.

Python 3.11+
"""

from __future__ import annotations


__all__ = [
    "METRICS_VERSION",
    "METRICS_NAME",
    "METRICS_API_VERSION",
]



# ==========================================================
# Package Identity
# ==========================================================


METRICS_NAME = "SciOS Runtime Metrics"



# ==========================================================
# Version
# ==========================================================


METRICS_VERSION = "0.1.0"



# ==========================================================
# Public API Version
# ==========================================================


METRICS_API_VERSION = "v1"



# ==========================================================
# Helpers
# ==========================================================


def version_info() -> dict[str, str]:
    """
    Return metrics version metadata.

    Used by:
    - diagnostics
    - dashboard
    - exporters
    - runtime health checks
    """

    return {

        "name":
            METRICS_NAME,

        "version":
            METRICS_VERSION,

        "api":
            METRICS_API_VERSION,
    }