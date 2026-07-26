"""
SciOS-NG
runtime/observability/metrics/integration/__init__.py

Unified Observability Integration Stack.
"""

from .runtime import MetricRuntimeIntegration
from .logging import MetricLoggingIntegration
from .tracing import MetricTracingIntegration
from .profiling import MetricProfilingIntegration
from .qtc import MetricQTCIntegration

__all__ = [
    # Runtime
    "MetricRuntimeIntegration",

    # Logging
    "MetricLoggingIntegration",

    # Tracing
    "MetricTracingIntegration",

    # Profiling
    "MetricProfilingIntegration",

    # QTC
    "MetricQTCIntegration",
]

# -----------------------------------------------------------------------------
# Version
# -----------------------------------------------------------------------------

__version__ = "1.0.0"

# -----------------------------------------------------------------------------
# Integration Registry
# -----------------------------------------------------------------------------

INTEGRATIONS = {
    "runtime": MetricRuntimeIntegration,
    "logging": MetricLoggingIntegration,
    "tracing": MetricTracingIntegration,
    "profiling": MetricProfilingIntegration,
    "qtc": MetricQTCIntegration,
}


def available_integrations() -> list[str]:
    """
    Return the names of all available metric integrations.
    """

    return sorted(INTEGRATIONS.keys())


def get_integration(name: str):
    """
    Return an integration class by name.

    Parameters
    ----------
    name : str
        Integration name.

    Raises
    ------
    KeyError
        If the integration does not exist.
    """

    try:
        return INTEGRATIONS[name]

    except KeyError as exc:
        raise KeyError(
            f"Unknown metric integration: {name!r}"
        ) from exc


def create_integration(name: str, *args, **kwargs):
    """
    Create an integration instance.

    Example
    -------
    >>> runtime = create_integration("runtime")
    >>> profiler = create_integration("profiling")
    """

    cls = get_integration(name)

    return cls(*args, **kwargs)