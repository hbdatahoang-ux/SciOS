"""
SciOS Runtime Observability
===========================

In-memory exporter.

The MemoryExporter stores successfully exported payloads in memory.
It is intended for:

- tests
- development
- local inspection
- integration pipelines
- deterministic exporter chaining

Python 3.11+
"""

from __future__ import annotations

import time
from collections.abc import Iterable
from typing import Any, Mapping

from .base import ExportPayload, ExportResult, Exporter

# ==============================================================================
# Part 1. MemoryExporter
# ==============================================================================


class MemoryExporter(Exporter):
    """
    Exporter that stores exported payloads in memory.

    Stored payloads preserve their original object identity.
    This is useful for deterministic testing and local inspection.

    Parameters
    ----------
    name:
        Exporter name.

    max_items:
        Optional maximum number of stored payloads.

        ``None`` means unlimited storage.

    format:
        Export format inherited from :class:`Exporter`.

    enabled:
        Whether the exporter is enabled.

    encoding:
        Text encoding inherited from :class:`Exporter`.

    options:
        Exporter-level configuration options.
    """

    def __init__(
        self,
        name: str = "memory",
        *,
        max_items: int | None = None,
        format: Any = None,
        enabled: bool = True,
        encoding: str = "utf-8",
        options: Mapping[str, Any] | None = None,
    ) -> None:
        self._validate_max_items(max_items)

        if format is None:
            super().__init__(
                name=name,
                enabled=enabled,
                encoding=encoding,
                options=options,
            )
        else:
            super().__init__(
                name=name,
                format=format,
                enabled=enabled,
                encoding=encoding,
                options=options,
            )

        self._max_items = max_items
        self._items: list[
            ExportPayload | Mapping[str, Any]
        ] = []

    # ==========================================================================
    # Part 2. Configuration
    # ==========================================================================

    @staticmethod
    def _validate_max_items(
        value: int | None,
    ) -> None:
        if value is not None:
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(
                    "max_items must be an integer or None"
                )

            if value < 0:
                raise ValueError(
                    "max_items must be >= 0"
                )

    @property
    def max_items(self) -> int | None:
        """
        Maximum number of stored items.

        ``None`` means unlimited.
        """
        return self._max_items

    @max_items.setter
    def max_items(
        self,
        value: int | None,
    ) -> None:
        self._validate_max_items(value)

        self._max_items = value
        self._trim()

    # ==========================================================================
    # Part 3. Storage access
    # ==========================================================================

    @property
    def items(
        self,
    ) -> tuple[
        ExportPayload | Mapping[str, Any],
        ...,
    ]:
        """
        Return an immutable snapshot of stored payloads.
        """
        return tuple(self._items)

    @property
    def count(self) -> int:
        """
        Number of currently stored payloads.
        """
        return len(self._items)

    @property
    def latest(
        self,
    ) -> ExportPayload | Mapping[str, Any] | None:
        """
        Return the most recently stored payload.
        """
        if not self._items:
            return None

        return self._items[-1]

    def snapshot(
        self,
    ) -> tuple[
        ExportPayload | Mapping[str, Any],
        ...,
    ]:
        """
        Return an immutable storage snapshot.
        """
        return self.items

    # ==========================================================================
    # Part 4. Option validation
    # ==========================================================================

    def validate_options(
        self,
        options: Mapping[str, Any],
    ) -> None:
        """
        Validate exporter-level options.

        Custom exporter-level options are allowed and are delegated
        to the base exporter. ``max_items`` receives additional
        MemoryExporter-specific validation.
        """

        super().validate_options(options)

        if "max_items" in options:
            self._validate_max_items(
                options["max_items"]
            )

    # ==========================================================================
    # Part 5. Export
    # ==========================================================================

    def export(
        self,
        payload: ExportPayload | Mapping[str, Any],
        **options: Any,
    ) -> ExportResult:
        """
        Export one payload.

        The original payload object is retained in memory.
        Exporter statistics and lifecycle accounting remain owned
        by the base exporter.
        """

        started_at = time.perf_counter()

        # --------------------------------------------------------------
        # Validate input before entering exporter lifecycle accounting.
        # --------------------------------------------------------------
        self.validate_payload(payload)

        # --------------------------------------------------------------
        # Per-call options are intentionally restricted.
        # Constructor-level options are handled by Part 4.
        # --------------------------------------------------------------
        self._validate_export_options(options)

        # --------------------------------------------------------------
        # Attempt accounting.
        # --------------------------------------------------------------
        self._export_count += 1
        self._last_export = time.time()

        try:
            if self._closed:
                raise RuntimeError(
                    f"exporter '{self.name}' is closed"
                )

            if not self.enabled:
                return ExportResult(
                    success=False,
                    exporter=self.name,
                    count=0,
                    bytes_exported=0,
                    duration=time.perf_counter() - started_at,
                    error="exporter is disabled",
                )

            # ----------------------------------------------------------
            # Preserve original object identity.
            # ----------------------------------------------------------
            self._store(payload)

            self._success_count += 1
            self._last_error = None

            return ExportResult(
                success=True,
                exporter=self.name,
                count=1,
                bytes_exported=0,
                duration=time.perf_counter() - started_at,
                data=payload,
            )

        except Exception as exc:
            return self._handle_error(
                exc,
                duration=time.perf_counter() - started_at,
            )


    def _validate_export_options(
        self,
        options: Mapping[str, Any],
    ) -> None:
        """
        Validate options supplied to a single export call.

        Only MemoryExporter-specific per-call options are accepted.
        Constructor-level custom options are handled separately.
        """

        if not isinstance(options, Mapping):
            raise TypeError(
                "options must be a mapping"
            )

        allowed = {
            "max_items",
        }

        unknown = set(options) - allowed

        if unknown:
            names = ", ".join(
                sorted(str(name) for name in unknown)
            )

            raise ValueError(
                f"unsupported memory exporter option(s): {names}"
            )

        if "max_items" in options:
            self._validate_max_items(
                options["max_items"]
            )        

    # ==========================================================================
    # Part 6. Storage management
    # ==========================================================================

    def clear(self) -> None:
        """
        Remove all stored payloads without resetting statistics.
        """
        self._items.clear()

    def pop(
        self,
    ) -> ExportPayload | Mapping[str, Any]:
        """
        Remove and return the oldest payload.
        """
        return self._items.pop(0)

    def pop_latest(
        self,
    ) -> ExportPayload | Mapping[str, Any]:
        """
        Remove and return the newest payload.
        """
        return self._items.pop()

    # ==========================================================================
    # Part 7. Internal storage
    # ==========================================================================

    def _store(
        self,
        payload: ExportPayload | Mapping[str, Any],
    ) -> None:
        """
        Store payload and enforce FIFO capacity.
        """
        self._items.append(payload)
        self._trim()

    def _trim(self) -> None:
        """
        Enforce ``max_items`` using FIFO eviction.
        """
        if self._max_items is None:
            return

        if self._max_items == 0:
            self._items.clear()
            return

        excess = len(self._items) - self._max_items

        if excess > 0:
            del self._items[:excess]

    # ==========================================================================
    # Part 8. Lifecycle
    # ==========================================================================

    def reset(self) -> "MemoryExporter":
        """
        Reset exporter statistics and storage.
        """
        self.clear()
        super().reset()
        return self

    def start(self) -> "MemoryExporter":
        """
        Start exporter without modifying stored items.
        """
        super().start()
        return self

    def stop(self) -> "MemoryExporter":
        """
        Stop exporter without modifying stored items.
        """
        super().stop()
        return self

    # ==========================================================================
    # Part 9. Representation
    # ==========================================================================

    def __repr__(self) -> str:
        return (
            f"MemoryExporter("
            f"name={self.name!r}, "
            f"count={self.count}, "
            f"max_items={self.max_items!r}, "
            f"enabled={self.enabled!r})"
        )

    def __str__(self) -> str:
        return (
            f"MemoryExporter("
            f"name={self.name}, "
            f"count={self.count})"
        )


__all__ = [
    "MemoryExporter",
]