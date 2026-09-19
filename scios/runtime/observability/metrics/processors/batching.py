"""
SciOS Runtime Metrics Batching Processor
========================================

Metric batching processor.

Responsibilities
-----------------
- Accumulate metrics into batches.
- Emit a batch when the configured size is reached.
- Support explicit flushing of partial batches.
- Track batching statistics.
- Preserve input isolation.
- Support runtime reset without losing configuration.

Python 3.11+
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .processor import MetricProcessor


__all__ = [
    "BatchingProcessor",
]


# ======================================================================
# Batching Processor
# ======================================================================


class BatchingProcessor(MetricProcessor):
    """
    Runtime metric batching processor.

    Metrics are accumulated until ``batch_size`` is reached.

    ``transform()`` returns:

    - ``None`` while the current batch is incomplete.
    - ``list`` containing the completed batch when the batch is full.

    ``flush()`` emits any remaining partial batch.
    """

    # ==================================================================
    # Constructor
    # ==================================================================

    def __init__(
        self,
        batch_size: int = 10,
        name: str = "BatchingProcessor",
        description: str = "",
    ) -> None:
        super().__init__(
            name=name,
            description=description,
        )

        if not isinstance(batch_size, int):
            raise TypeError(
                "batch_size must be an integer"
            )

        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than zero"
            )

        self._batch_size = batch_size

        self._buffer: list[Any] = []

        self._processed = 0
        self._batches = 0
        self._flushed = 0

        self._full = False
    # ==================================================================
    # Configuration
    # ==================================================================

    @property
    def batch_size(self) -> int:
        """
        Return configured batch size.
        """

        return self._batch_size

    def set_batch_size(
        self,
        batch_size: int,
    ) -> "BatchingProcessor":
        """
        Change batch size.

        Existing buffered metrics are preserved.
        """

        if not isinstance(batch_size, int):
            raise TypeError(
                "batch_size must be an integer"
            )

        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than zero"
            )

        self._batch_size = batch_size

        return self

    # ==================================================================
    # Processing
    # ==================================================================

    def transform(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> list[Any] | None:
        """
        Add a metric to the current batch.

        Returns a completed batch when the configured size is reached.
        Otherwise returns None.
        """

        # A new metric starts a new batch state.
        self._full = False

        self._buffer.append(
            deepcopy(metric)
        )

        self._processed += 1

        if len(self._buffer) < self._batch_size:
            return None

        batch = self._emit_batch()

        self._full = True

        return batch

    # ==================================================================
    # Batch Emission
    # ==================================================================

    def _emit_batch(
        self,
    ) -> list[Any]:
        """
        Emit the current full batch.

        Caller must ensure the buffer is non-empty.
        """

        batch = self._buffer

        self._buffer = []

        self._batches += 1

        return batch

    # ==================================================================
    # Flush
    # ==================================================================

    def flush(
        self,
    ) -> list[Any] | None:
        """
        Emit the current partial batch.

        Returns None if no metrics are pending.
        """

        if not self._buffer:
            self._full = False
            return None

        batch = self._emit_batch()

        self._flushed += 1
        self._full = False

        return batch

    # ==================================================================
    # Buffer Inspection
    # ==================================================================

    def pending(
        self,
    ) -> int:
        """
        Return number of metrics currently buffered.
        """

        return len(
            self._buffer
        )

    def buffered(
        self,
    ) -> list[Any]:
        """
        Return a copy of the current buffer.
        """

        return deepcopy(
            self._buffer
        )

    def is_empty(
        self,
    ) -> bool:
        """
        Return whether the current buffer is empty.
        """

        return not self._buffer

    def is_full(
        self,
    ) -> bool:
        """
        Return whether the most recent transform completed a full batch.
        """

        return self._full

    # ==================================================================
    # Statistics
    # ==================================================================

    def statistics(
        self,
    ) -> dict[str, Any]:
        """
        Return processor statistics.
        """

        data = super().statistics()

        data.update(
            {
                "batch_size": self._batch_size,
                "pending": len(self._buffer),
                "processed": self._processed,
                "batches": self._batches,
                "flushed": self._flushed,
            }
        )

        return data

    # ==================================================================
    # Runtime
    # ==================================================================

    def reset(
        self,
    ) -> "BatchingProcessor":
        """
        Reset runtime state.

        Configuration survives reset.
        """

        self._buffer.clear()

        self._processed = 0
        self._batches = 0
        self._flushed = 0
        self._full = False

        return self

    # ==================================================================
    # Python Protocols
    # ==================================================================

    def __len__(
        self,
    ) -> int:
        """
        Return number of currently buffered metrics.
        """

        return len(
            self._buffer
        )

    def __bool__(
        self,
    ) -> bool:
        """
        Return whether metrics are currently buffered.
        """

        return bool(
            self._buffer
        )

    def __repr__(
        self,
    ) -> str:
        return (
            "BatchingProcessor("
            f"batch_size={self._batch_size}, "
            f"pending={len(self._buffer)}, "
            f"processed={self._processed}, "
            f"batches={self._batches}"
            ")"
        )