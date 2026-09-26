"""
SciOS Substrate
===============

Computational substrate of the Scientific Cognitive Operating
System (SciOS).

The substrate provides the low-level computational foundation
for SciOS, including tensor abstraction, memory management,
vector storage, and the Qualitative Temporal Calculus (QTC).

Design Goals
------------
- Lightweight package import.
- Lazy loading of optional/heavy components.
- Stable public API.
- Minimal startup overhead.
- Python 3.11+.

Architecture
------------
Substrate
├── Tensor abstraction
├── Memory management
├── Vector storage
└── Qualitative Temporal Calculus (QTC)
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

__version__ = "0.1.0"

__all__ = [
    "SciOSTensor",
    "MemoryManager",
]

#
# Internal lazy import table
#
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "SciOSTensor": (".tensor", "SciOSTensor"),
    "MemoryManager": (".memory", "MemoryManager"),
}


# ==========================================================
# Lazy Import
# ==========================================================

def __getattr__(name: str) -> Any:
    """
    Lazily import public objects.

    Heavy modules (for example Tensor/PyTorch) are imported only
    when first accessed.

    Examples
    --------
    >>> from scios.substrate import SciOSTensor

    >>> from scios.substrate import MemoryManager
    """

    target = _LAZY_IMPORTS.get(name)

    if target is None:
        raise AttributeError(
            f"module {__name__!r} has no attribute {name!r}"
        )

    module_name, attribute = target

    module = import_module(
        module_name,
        __name__,
    )

    obj = getattr(
        module,
        attribute,
    )

    #
    # Cache the imported object so future lookups
    # are as fast as normal attribute access.
    #
    globals()[name] = obj

    return obj


# ==========================================================
# Module Introspection
# ==========================================================

def __dir__() -> list[str]:
    """
    Support IDE auto-completion.
    """

    return sorted(
        set(globals()) | set(__all__)
    )


# ==========================================================
# Diagnostics
# ==========================================================

def api_summary() -> dict[str, Any]:
    """
    Return the public API description.
    """

    return {
        "package": __name__,
        "version": __version__,
        "exports": list(__all__),
        "lazy_imports": list(_LAZY_IMPORTS),
        "python": "3.11+",
    }


def health() -> dict[str, Any]:
    """
    Lightweight package health information.

    Does not import optional dependencies.
    """

    return {
        "status": "healthy",
        "package": __name__,
        "version": __version__,
        "lazy_loading": True,
        "cached_exports": sorted(
            name
            for name in _LAZY_IMPORTS
            if name in globals()
        ),
    }


# ==========================================================
# Metadata
# ==========================================================

def __repr__() -> str:
    return (
        f"<module '{__name__}' "
        f"version={__version__}>"
    )