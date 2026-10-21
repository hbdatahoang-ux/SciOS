"""
SciOS-NG Runtime Observability Logging Package.

Provides unified logging infrastructure:

- Rotating logs
- JSON logging
- Structured logging
- Context propagation
- Middleware pipeline
- Plugin extensions
"""


# =============================================================================
# Package Metadata
# =============================================================================

__name__ = "scios.runtime.observability.logging"

__version__ = "0.1.0"

__author__ = "SciOS-NG Team"

__description__ = (
    "Runtime observability logging subsystem "
    "for SciOS-NG"
)



# =============================================================================
# Core Logging Components
# =============================================================================

from .rotating import (
    RotationPolicy,
    RotatingHandler,
)


from .json_logger import (
    JSONLogRecord,
    JSONLogger,
)


from .structured import (
    StructuredRecord,
    StructuredLogger,
)


from .context import (
    ContextRecord,
    LoggingContext,
)


from .middleware import (
    MiddlewareRecord,
    LoggingMiddleware,
)


from .plugin import (
    LoggingPlugin,
    PluginManager,
)



# =============================================================================
# Public API
# =============================================================================

__all__ = [

    # -------------------------------------------------------------------------
    # Rotating Logger
    # -------------------------------------------------------------------------

    "RotationPolicy",

    "RotatingHandler",


    # -------------------------------------------------------------------------
    # JSON Logger
    # -------------------------------------------------------------------------

    "JSONLogRecord",

    "JSONLogger",


    # -------------------------------------------------------------------------
    # Structured Logger
    # -------------------------------------------------------------------------

    "StructuredRecord",

    "StructuredLogger",


    # -------------------------------------------------------------------------
    # Context
    # -------------------------------------------------------------------------

    "ContextRecord",

    "LoggingContext",


    # -------------------------------------------------------------------------
    # Middleware
    # -------------------------------------------------------------------------

    "MiddlewareRecord",

    "LoggingMiddleware",


    # -------------------------------------------------------------------------
    # Plugin System
    # -------------------------------------------------------------------------

    "LoggingPlugin",

    "PluginManager",

]



# =============================================================================
# Factory Helpers
# =============================================================================


def create_logger(
    name: str = "scios",
    *,
    level: str = "INFO",
    structured: bool = True,
):
    """
    Create default SciOS logging instance.

    Parameters
    ----------
    name:
        Logger name.

    level:
        Logging level.

    structured:
        Use StructuredLogger when True.
    """

    if structured:

        return StructuredLogger(
            name=name,
            level=level,
        )


    return JSONLogger(
        name=name,
        level=level,
    )



def create_context(
    name: str = "default",
):
    """
    Create runtime logging context.
    """

    return LoggingContext(
        name=name,
    )



def create_plugin_manager(
    name: str = "logging_plugins",
):
    """
    Create logging plugin manager.
    """

    return PluginManager(
        name=name,
    )



# =============================================================================
# Version Information
# =============================================================================

def version():
    """
    Return package version.
    """

    return __version__