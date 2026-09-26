"""
SciOS Runtime Observability
===========================

Exporter Registry
-----------------

Central registry for managing exporter instances.

Responsibilities
----------------
- Register exporters
- Unregister exporters
- Lookup exporters by name
- Replace existing exporters explicitly
- Enable / disable exporters
- Start / stop / reset / close exporters
- Export through one or multiple registered exporters
- Provide registry statistics and diagnostics

The registry does not implement any concrete export backend.

Python 3.11+
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .base import ExportPayload, ExportResult, Exporter


# ==============================================================================
# Part 1. Exceptions
# ==============================================================================


class ExporterRegistryError(RuntimeError):
    """
    Base exception for exporter registry failures.
    """


class ExporterAlreadyRegisteredError(ExporterRegistryError):
    """
    Raised when an exporter name is already registered.
    """


class ExporterNotFoundError(ExporterRegistryError):
    """
    Raised when a requested exporter does not exist.
    """


# ==============================================================================
# Part 2. ExporterRegistry
# ==============================================================================


class ExporterRegistry:
    """
    Registry and lifecycle manager for exporters.

    Exporters are uniquely identified by their ``name``.
    """

    def __init__(
        self,
        exporters: Iterable[Exporter] | None = None,
    ) -> None:
        self._exporters: dict[str, Exporter] = {}

        if exporters is not None:
            for exporter in exporters:
                self.register(exporter)

    # ==========================================================================
    # Part 3. Basic properties
    # ==========================================================================

    @property
    def exporters(self) -> dict[str, Exporter]:
        """
        Return a shallow copy of registered exporters.
        """

        return dict(self._exporters)

    @property
    def names(self) -> tuple[str, ...]:
        """
        Return registered exporter names in insertion order.
        """

        return tuple(self._exporters)

    @property
    def count(self) -> int:
        """
        Return the number of registered exporters.
        """

        return len(self._exporters)

    @property
    def empty(self) -> bool:
        """
        Return whether the registry contains no exporters.
        """

        return not self._exporters

    # ==========================================================================
    # Part 4. Registration
    # ==========================================================================

    def register(
        self,
        exporter: Exporter,
        *,
        replace: bool = False,
    ) -> Exporter:
        """
        Register an exporter.

        Parameters
        ----------
        exporter:
            Exporter instance to register.

        replace:
            Replace an existing exporter with the same name when ``True``.

        Returns
        -------
        Exporter
            The registered exporter.
        """

        if not isinstance(exporter, Exporter):
            raise TypeError(
                "exporter must be an Exporter instance"
            )

        name = exporter.name

        if name in self._exporters and not replace:
            raise ExporterAlreadyRegisteredError(
                f"exporter already registered: {name!r}"
            )

        self._exporters[name] = exporter
        return exporter

    def unregister(
        self,
        name: str,
        *,
        close: bool = False,
    ) -> Exporter:
        """
        Remove an exporter from the registry.

        Parameters
        ----------
        name:
            Registered exporter name.

        close:
            Close the exporter before removing it.
        """

        exporter = self.get(name)

        if close:
            exporter.close()

        del self._exporters[name]

        return exporter

    def clear(
        self,
        *,
        close: bool = False,
    ) -> None:
        """
        Remove all exporters from the registry.

        Parameters
        ----------
        close:
            Close all exporters before removing them.
        """

        exporters = tuple(self._exporters.values())

        if close:
            for exporter in exporters:
                exporter.close()

        self._exporters.clear()

    # ==========================================================================
    # Part 5. Lookup
    # ==========================================================================

    def get(
        self,
        name: str,
    ) -> Exporter:
        """
        Return an exporter by name.

        Raises
        ------
        ExporterNotFoundError
            If the exporter does not exist.
        """

        try:
            return self._exporters[name]
        except KeyError as exc:
            raise ExporterNotFoundError(
                f"exporter not found: {name!r}"
            ) from exc

    def find(
        self,
        name: str,
    ) -> Exporter | None:
        """
        Return an exporter by name or ``None``.
        """

        return self._exporters.get(name)

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return whether an exporter is registered.
        """

        return name in self._exporters

    # ==========================================================================
    # Part 6. Enable / disable
    # ==========================================================================

    def enable(
        self,
        name: str,
    ) -> Exporter:
        """
        Enable an exporter.
        """

        exporter = self.get(name)
        exporter.enabled = True
        return exporter

    def disable(
        self,
        name: str,
    ) -> Exporter:
        """
        Disable an exporter.
        """

        exporter = self.get(name)
        exporter.enabled = False
        return exporter

    # ==========================================================================
    # Part 7. Lifecycle
    # ==========================================================================

    def start(self) -> "ExporterRegistry":
        """
        Start all registered exporters.
        """

        for exporter in self._exporters.values():
            exporter.start()

        return self

    def stop(self) -> "ExporterRegistry":
        """
        Stop all registered exporters.
        """

        for exporter in self._exporters.values():
            exporter.stop()

        return self

    def reset(self) -> "ExporterRegistry":
        """
        Reset all registered exporters.
        """

        for exporter in self._exporters.values():
            exporter.reset()

        return self

    def close(self) -> "ExporterRegistry":
        """
        Close all registered exporters.

        The registry itself remains reusable for registration of new
        exporters after close.
        """

        for exporter in self._exporters.values():
            exporter.close()

        return self

    def flush(self) -> "ExporterRegistry":
        """
        Flush all registered exporters.
        """

        for exporter in self._exporters.values():
            exporter.flush()

        return self

    # ==========================================================================
    # Part 8. Export
    # ==========================================================================

    def export(
        self,
        payload: ExportPayload | Mapping[str, Any],
        *,
        exporters: Iterable[str] | None = None,
        **options: Any,
    ) -> dict[str, ExportResult]:
        """
        Export one payload through selected exporters.

        Parameters
        ----------
        payload:
            Payload to export.

        exporters:
            Optional iterable of exporter names.

            If omitted, all registered exporters are used.

        **options:
            Per-export options forwarded to each exporter.
        """

        selected = self._select(exporters)

        return {
            exporter.name: exporter.export(
                payload,
                **options,
            )
            for exporter in selected
        }

    def export_many(
        self,
        payloads: Iterable[
            ExportPayload | Mapping[str, Any]
        ],
        *,
        exporters: Iterable[str] | None = None,
        **options: Any,
    ) -> dict[str, list[ExportResult]]:
        """
        Export multiple payloads through selected exporters.
        """

        selected = self._select(exporters)

        return {
            exporter.name: exporter.export_many(
                payloads,
                **options,
            )
            for exporter in selected
        }

    # ==========================================================================
    # Part 9. Internal selection
    # ==========================================================================

    def _select(
        self,
        names: Iterable[str] | None,
    ) -> tuple[Exporter, ...]:
        """
        Resolve exporter names into exporter instances.
        """

        if names is None:
            return tuple(self._exporters.values())

        return tuple(
            self.get(name)
            for name in names
        )

    # ==========================================================================
    # Part 10. Statistics
    # ==========================================================================

    @property
    def export_count(self) -> int:
        """
        Return total export attempts across all exporters.
        """

        return sum(
            exporter.export_count
            for exporter in self._exporters.values()
        )

    @property
    def success_count(self) -> int:
        """
        Return total successful exports.
        """

        return sum(
            exporter.success_count
            for exporter in self._exporters.values()
        )

    @property
    def error_count(self) -> int:
        """
        Return total failed exports.
        """

        return sum(
            exporter.error_count
            for exporter in self._exporters.values()
        )

    @property
    def bytes_exported(self) -> int:
        """
        Return total exported bytes.
        """

        return sum(
            exporter.bytes_exported
            for exporter in self._exporters.values()
        )

    # ==========================================================================
    # Part 11. Diagnostics
    # ==========================================================================

    def health(self) -> dict[str, Any]:
        """
        Return lightweight registry health information.
        """

        exporter_health = {
            name: exporter.health()
            for name, exporter in self._exporters.items()
        }

        healthy = all(
            data["healthy"]
            for data in exporter_health.values()
        )

        return {
            "healthy": healthy,
            "count": self.count,
            "exporters": exporter_health,
        }

    def diagnostics(self) -> dict[str, Any]:
        """
        Return detailed registry diagnostics.
        """

        return {
            "count": self.count,
            "names": self.names,
            "exporters": {
                name: exporter.diagnostics()
                for name, exporter in self._exporters.items()
            },
            "statistics": {
                "export_count": self.export_count,
                "success_count": self.success_count,
                "error_count": self.error_count,
                "bytes_exported": self.bytes_exported,
            },
        }

    def summary(self) -> dict[str, Any]:
        """
        Return compact registry summary.
        """

        return {
            "count": self.count,
            "names": self.names,
            "export_count": self.export_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "bytes_exported": self.bytes_exported,
        }

    # ==========================================================================
    # Part 12. Representation
    # ==========================================================================

    def __contains__(self, name: str) -> bool:
        return self.contains(name)

    def __len__(self) -> int:
        return self.count

    def __iter__(self):
        return iter(self._exporters.values())

    def __repr__(self) -> str:
        return (
            f"ExporterRegistry("
            f"count={self.count}, "
            f"names={self.names!r})"
        )

    def __str__(self) -> str:
        return (
            f"ExporterRegistry("
            f"count={self.count}, "
            f"exporters={', '.join(self.names)})"
        )


__all__ = [
    "ExporterAlreadyRegisteredError",
    "ExporterNotFoundError",
    "ExporterRegistry",
    "ExporterRegistryError",
]