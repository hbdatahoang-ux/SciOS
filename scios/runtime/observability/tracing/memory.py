# ==============================================================================
# Part 1. Imports
# ==============================================================================

from __future__ import annotations

from collections import OrderedDict
from typing import Any, Mapping

from .exporter import (
    ExportError,
    ExportFormat,
    ExportPayload,
    ExportResult,
    Exporter,
)


# ==============================================================================
# Part 2. Public API
# ==============================================================================


__all__ = [
    "MemoryExporter",
]


# ==============================================================================
# Part 3. MemoryExporter
# ==============================================================================


class MemoryExporter(Exporter):
    """
    In-memory exporter for SciOS runtime observability data.
    """

    def __init__(
        self,
        name: str = "memory",
        *,
        format: ExportFormat = ExportFormat.JSON,
        encoding: str = "utf-8",
        enabled: bool = True,
        max_items: int | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> None:

        super().__init__(
            name=name,
            format=format,
            encoding=encoding,
            enabled=enabled,
            options=options,
        )

        if max_items is not None:
            if not isinstance(max_items, int):
                raise TypeError(
                    "max_items must be an int or None",
                )

            if max_items <= 0:
                raise ValueError(
                    "max_items must be greater than zero",
                )

        self._max_items = max_items

        # Ordered storage:
        # key -> original payload
        self._storage: OrderedDict[
            int,
            ExportPayload,
        ] = OrderedDict()

    # ==============================================================================
    # Part 4. Core Properties
    # ==============================================================================


    @property
    def items(
        self,
    ) -> list[ExportPayload]:
        """
        Return stored payloads in insertion order.
        """

        return list(
            self._storage.values(),
        )


    @property
    def size(
        self,
    ) -> int:
        """
        Return number of stored payloads.
        """

        return len(
            self._storage,
        )


    @property
    def max_items(
        self,
    ) -> int | None:
        """
        Return maximum number of stored payloads.
        """

        return self._max_items

    # ==============================================================================
    # Part 5. Export
    # ==============================================================================


    def export(
        self,
        payload: ExportPayload,
        **options: Any,
    ) -> ExportResult:
        """
        Export and retain one payload in memory.
        """

        result = super().export(
            payload,
            **options,
        )

        # Use export_count - 1 as stable zero-based storage key.
        key = self.export_count - 1

        self._storage[key] = payload

        # Keep only the newest max_items entries.
        if self._max_items is not None:
            while len(self._storage) > self._max_items:
                self._storage.popitem(
                    last=False,
                )

        return result

    # ==============================================================================
    # Part 6. Storage API
    # ==============================================================================


    def clear(
        self,
    ) -> None:
        """
        Remove all stored payloads.
        """

        self._storage.clear()


    def get(
        self,
        key: int,
        default: Any = None,
    ) -> Any:
        """
        Return a stored payload by storage key.
        """

        return self._storage.get(
            key,
            default,
        )


    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Return a snapshot of the current memory state.
        """

        return {
            "size": self.size,
            "max_items": self.max_items,
            "items": list(
                self._storage.values(),
            ),
        }


    # ==============================================================================
    # Part 7. Lifecycle
    # ==============================================================================


    def reset(
        self,
    ) -> "MemoryExporter":
        """
        Clear memory and reset exporter runtime state.
        """

        if self._state == "closed":
            raise ExportError(
                "cannot reset a closed memory exporter",
                exporter=self._name,
            )

        self._storage.clear()

        super().reset()

        return self


    def close(
        self,
    ) -> "MemoryExporter":
        """
        Close the memory exporter.
        """

        if self._state == "closed":
            return self

        self._state = "closed"

        return self


    # ==============================================================================
    # Part 8. Diagnostics / Representation
    # ==============================================================================


    def diagnostics(
        self,
    ) -> dict[str, Any]:
        """
        Return detailed memory exporter diagnostics.
        """

        data = super().diagnostics()

        data.update(
            {
                "items": self.size,
                "max_items": self.max_items,
            }
        )

        return data

    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Return compact memory exporter summary.
        """

        data = super().summary()

        data.update(
            {
                "items": self.size,
                "max_items": self.max_items,
            }
        )

        return data


    def __repr__(
        self,
    ) -> str:
        return (
            f"{type(self).__name__}("
            f"name={self._name!r}, "
            f"items={self.size}, "
            f"max_items={self._max_items!r}, "
            f"state={self._state!r}, "
            f"enabled={self._enabled!r}"
            f")"
        )


    def __str__(
        self,
    ) -> str:
        return (
            f"{self._name}("
            f"items={self.size}, "
            f"max_items={self._max_items!r}, "
            f"state={self._state}, "
            f"enabled={self._enabled}"
            f")"
        )


# ==============================================================================
# Part 9. End
# ==============================================================================


__all__ = [
    "MemoryExporter",
]
