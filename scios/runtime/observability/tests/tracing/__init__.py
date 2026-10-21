"""
SciOS-NG Observability
Tracing Test Package

This package contains test suites for:

    - Tracing Core
    - Trace Context
    - Span Lifecycle
    - Events
    - Exporters
    - Serialization
    - Plugins
    - Processors

Location:

    scios/runtime/observability/tests/tracing/

"""

from __future__ import annotations


# ============================================================
# Package Metadata
# ============================================================

__all__ = [
    "TEST_PACKAGE",
    "TEST_SCOPE",
]


# ============================================================
# Constants
# ============================================================

TEST_PACKAGE = "observability.tracing.tests"


TEST_SCOPE = (
    "SciOS-NG Observability "
    "Tracing Validation Suite"
)