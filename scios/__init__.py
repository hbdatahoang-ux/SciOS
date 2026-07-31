"""
SciOS
=====

Scientific Cognitive Operating System (SciOS).

SciOS is a modular scientific computing and cognitive runtime
framework. The top-level package intentionally performs only
lightweight initialization.

Design
------
- Lightweight package import.
- Lazy loading of heavy components.
- Stable public API.
- Python 3.11+.

Example
-------
>>> from scios import SciOS
>>> os = SciOS()
>>> os.boot()
>>> os.run("analyze this system")
"""

from __future__ import annotations

from typing import Any

__version__ = "0.3.0-alpha"
__author__ = "Bui Dinh Hoang"

__all__ = [
    "SciOS",
    "__version__",
    "__author__",
]


def __getattr__(name: str) -> Any:
    """
    Lazily import heavyweight public objects.

    This prevents importing the complete SciOS runtime,
    kernel, API stack, and optional dependencies during a
    simple ``import scios``.
    """

    if name == "SciOS":
        from .api.scios import SciOS

        return SciOS

    raise AttributeError(
        f"module {__name__!r} has no attribute {name!r}"
    )


def __dir__() -> list[str]:
    """
    Return public module attributes.

    Improves IDE auto-completion and interactive inspection.
    """

    return sorted(__all__)


def api_summary() -> dict[str, Any]:
    """
    Return public package metadata.
    """

    return {
        "package": "scios",
        "version": __version__,
        "author": __author__,
        "exports": list(__all__),
        "lazy_imports": [
            "SciOS",
        ],
    }


def health() -> dict[str, Any]:
    """
    Basic package health information.
    """

    return {
        "status": "healthy",
        "package": "scios",
        "version": __version__,
    }