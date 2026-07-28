"""
SciOS Exporter Registry
=======================

Central registry for observability exporters.

Responsibilities
----------------
- Register exporters.
- Resolve exporters by name.
- List available exporters.
- Manage exporter lifecycle.

Design Goals
------------
- Thread safe
- Extensible
- Runtime independent
- Plugin friendly
"""

from __future__ import annotations


from threading import RLock
from typing import Any


__all__ = [
    "ExporterRegistry",
    "default_registry",
]



class ExporterRegistry:
    """
    Registry managing observability exporters.
    """


    def __init__(self) -> None:

        self._lock = RLock()

        self._exporters: dict[str, Any] = {}



    # ======================================================
    # Registration
    # ======================================================

    def register(
        self,
        name: str,
        exporter: Any,
        *,
        replace: bool = False,
    ) -> None:
        """
        Register exporter.
        """

        if not name:
            raise ValueError(
                "Exporter name cannot be empty."
            )


        with self._lock:

            if (
                name in self._exporters
                and not replace
            ):
                raise ValueError(
                    f"Exporter already exists: {name}"
                )


            self._exporters[name] = exporter



    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove exporter.
        """

        with self._lock:

            self._exporters.pop(
                name,
                None,
            )



    # ======================================================
    # Lookup
    # ======================================================

    def get(
        self,
        name: str,
    ) -> Any:
        """
        Get exporter by name.
        """

        with self._lock:

            if name not in self._exporters:

                raise KeyError(
                    f"Unknown exporter: {name}"
                )


            return self._exporters[name]



    def has(
        self,
        name: str,
    ) -> bool:
        """
        Check exporter existence.
        """

        with self._lock:

            return name in self._exporters



    # ======================================================
    # Discovery
    # ======================================================

    def available(
        self,
    ) -> tuple[str, ...]:
        """
        Return available exporter names.
        """

        with self._lock:

            return tuple(
                sorted(
                    self._exporters.keys()
                )
            )



    def names(
        self,
    ) -> list[str]:
        """
        Return exporter names.
        """

        return list(
            self.available()
        )



    def all(
        self,
    ) -> dict[str, Any]:
        """
        Return exporter snapshot.
        """

        with self._lock:

            return dict(
                self._exporters
            )



    # ======================================================
    # Lifecycle
    # ======================================================

    def clear(
        self,
    ) -> None:
        """
        Remove all exporters.
        """

        with self._lock:

            self._exporters.clear()



    def reset(
        self,
    ) -> None:
        """
        Alias for clear.
        """

        self.clear()



    # ======================================================
    # Statistics
    # ======================================================

    def count(
        self,
    ) -> int:
        """
        Number of exporters.
        """

        with self._lock:

            return len(
                self._exporters
            )



    # ======================================================
    # Protocols
    # ======================================================

    def __contains__(
        self,
        name: str,
    ) -> bool:

        return self.has(name)



    def __len__(
        self,
    ) -> int:

        return self.count()



    def __iter__(
        self,
    ):

        return iter(
            self.available()
        )



    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"exporters={self.available()!r}"
            ")"
        )



# ==========================================================
# Global Registry
# ==========================================================

default_registry = ExporterRegistry()