"""
SciOS-NG Runtime Metrics Batching Processor

Batch processing processor.

SciOS-NG v0.2
"""


from __future__ import annotations

import time

from typing import Any, Callable


from .processor import MetricProcessor



# ==================================================================
# BatchingProcessor
# ==================================================================


class BatchingProcessor(
    MetricProcessor
):
    """
    Runtime Metric Batch Processing Processor.

    Responsibilities
    ----------------
    - Group metrics into batches
    - Control batch size
    - Support timed flushing
    - Optimize exporter throughput
    """



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        batch_size: int = 100,
        flush_interval: float = 5.0,
        name: str = "BatchingProcessor",
        description: str = "",
    ) -> None:


        super().__init__(
            name=name,
            description=description,
        )


        # ----------------------------------------------------------
        # Configuration
        # ----------------------------------------------------------

        self._batch_size = batch_size

        self._flush_interval = flush_interval



        # ----------------------------------------------------------
        # Runtime Buffer
        # ----------------------------------------------------------

        self._buffer: list[Any] = []

        self._last_flush = time.time()



        # ----------------------------------------------------------
        # Callback
        # ----------------------------------------------------------

        self._flush_handler: Callable | None = None



        # ----------------------------------------------------------
        # Statistics
        # ----------------------------------------------------------

        self._batches = 0

        self._flushed = 0

        self._dropped = 0



    # ==============================================================
    # Processing
    # ==============================================================

    def transform(
        self,
        metric: Any,
        **kwargs,
    ):
        """
        Add metric into batch buffer.
        """

        self._buffer.append(
            metric
        )


        if self.should_flush():

            return self.flush()



        return None



    # ==============================================================
    # Batch API
    # ==============================================================

    def add(
        self,
        metric: Any,
    ):

        self._buffer.append(
            metric
        )


        return self



    def extend(
        self,
        metrics: list[Any],
    ):

        self._buffer.extend(
            metrics
        )


        return self



    def batch(
        self,
    ) -> list[Any]:

        return list(
            self._buffer
        )



    def size(
        self,
    ) -> int:

        return len(
            self._buffer
        )



    # ==============================================================
    # Flush Management
    # ==============================================================

    def should_flush(
        self,
    ) -> bool:

        if len(
            self._buffer
        ) >= self._batch_size:

            return True



        if (
            time.time()
            -
            self._last_flush
        ) >= self._flush_interval:

            return True



        return False



    def flush(
        self,
    ):
        """
        Flush current batch.
        """

        if not self._buffer:

            return []



        batch = list(
            self._buffer
        )


        self._buffer.clear()


        self._last_flush = time.time()


        self._batches += 1


        self._flushed += len(
            batch
        )


        if self._flush_handler:

            self._flush_handler(
                batch
            )



        return batch



    def set_flush_handler(
        self,
        handler: Callable,
    ):

        self._flush_handler = handler


        return self



    # ==============================================================
    # Configuration
    # ==============================================================

    def set_batch_size(
        self,
        size: int,
    ):

        self._batch_size = size


        return self



    def set_interval(
        self,
        interval: float,
    ):

        self._flush_interval = interval


        return self



    def batch_size(
        self,
    ):

        return self._batch_size



    def interval(
        self,
    ):

        return self._flush_interval



    # ==============================================================
    # Runtime Operations
    # ==============================================================

    def clear(
        self,
    ):

        self._dropped += len(
            self._buffer
        )


        self._buffer.clear()


        return self



    def reset(
        self,
    ):

        self.clear()


        self._batches = 0

        self._flushed = 0

        self._dropped = 0


        return self



    # ==============================================================
    # Statistics
    # ==============================================================

    def statistics(
        self,
    ):

        data = super().statistics()


        data.update({

            "buffer_size":
                len(
                    self._buffer
                ),


            "batch_size":
                self._batch_size,


            "flush_interval":
                self._flush_interval,


            "batches":
                self._batches,


            "flushed":
                self._flushed,


            "dropped":
                self._dropped,

        })


        return data



    # ==============================================================
    # Python Protocols
    # ==============================================================

    def __len__(
        self,
    ):

        return len(
            self._buffer
        )



    def __iter__(
        self,
    ):

        return iter(
            self._buffer
        )



    def __contains__(
        self,
        item,
    ):

        return item in self._buffer



    def __repr__(
        self,
    ):

        return (

            f"BatchingProcessor("
            f"size={len(self._buffer)}, "
            f"batch_size={self._batch_size}, "
            f"batches={self._batches}"
            f")"

        )