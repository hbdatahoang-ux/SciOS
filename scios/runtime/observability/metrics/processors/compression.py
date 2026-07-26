"""
SciOS-NG Runtime Metrics Compression Processor

Metric compression processor.

SciOS-NG v0.2
"""


from __future__ import annotations

import gzip
import json
import zlib

from typing import Any


from .processor import MetricProcessor



# ==================================================================
# CompressionProcessor
# ==================================================================


class CompressionProcessor(
    MetricProcessor
):
    """
    Runtime Metric Compression Processor.

    Responsibilities
    ----------------
    - Compress metric payloads
    - Reduce storage/network overhead
    - Support multiple compression algorithms
    - Prepare metrics for transport/export
    """



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        algorithm: str = "gzip",
        level: int = 6,
        name: str = "CompressionProcessor",
        description: str = "",
    ) -> None:


        super().__init__(
            name=name,
            description=description,
        )


        # ----------------------------------------------------------
        # Configuration
        # ----------------------------------------------------------

        self._algorithm = algorithm

        self._level = level



        # ----------------------------------------------------------
        # Statistics
        # ----------------------------------------------------------

        self._compressed = 0

        self._decompressed = 0

        self._original_size = 0

        self._compressed_size = 0



    # ==============================================================
    # Processing
    # ==============================================================

    def transform(
        self,
        metric: Any,
        **kwargs,
    ):
        """
        Compress metric payload.
        """

        return self.compress(
            metric
        )



    # ==============================================================
    # Compression API
    # ==============================================================

    def compress(
        self,
        data: Any,
    ) -> bytes:
        """
        Compress metric data.
        """

        payload = self.encode(
            data
        )


        self._original_size += len(
            payload
        )


        if self._algorithm == "gzip":

            result = gzip.compress(
                payload,
                compresslevel=self._level,
            )


        elif self._algorithm == "zlib":

            result = zlib.compress(
                payload,
                level=self._level,
            )


        elif self._algorithm == "none":

            result = payload


        else:

            raise ValueError(
                f"Unsupported compression: {self._algorithm}"
            )



        self._compressed += 1


        self._compressed_size += len(
            result
        )


        return result



    def decompress(
        self,
        data: bytes,
    ):
        """
        Decompress payload.
        """

        if self._algorithm == "gzip":

            result = gzip.decompress(
                data
            )


        elif self._algorithm == "zlib":

            result = zlib.decompress(
                data
            )


        else:

            result = data



        self._decompressed += 1


        return self.decode(
            result
        )



    # ==============================================================
    # Encode / Decode
    # ==============================================================

    def encode(
        self,
        data: Any,
    ) -> bytes:

        if isinstance(
            data,
            bytes,
        ):

            return data



        return json.dumps(
            data,
            default=str,
        ).encode(
            "utf-8"
        )



    def decode(
        self,
        data: bytes,
    ):

        try:

            return json.loads(
                data.decode(
                    "utf-8"
                )
            )

        except Exception:

            return data



    # ==============================================================
    # Configuration
    # ==============================================================

    def set_algorithm(
        self,
        algorithm: str,
    ):

        self._algorithm = algorithm


        return self



    def algorithm(
        self,
    ):

        return self._algorithm



    def set_level(
        self,
        level: int,
    ):

        self._level = level


        return self



    def level(
        self,
    ):

        return self._level



    # ==============================================================
    # Compression Strategies
    # ==============================================================

    def gzip(
        self,
        level: int = 6,
    ):

        self._algorithm = "gzip"

        self._level = level


        return self



    def zlib(
        self,
        level: int = 6,
    ):

        self._algorithm = "zlib"

        self._level = level


        return self



    def disable(
        self,
    ):

        self._algorithm = "none"


        return self



    # ==============================================================
    # Statistics
    # ==============================================================

    def statistics(
        self,
    ):

        data = super().statistics()


        ratio = (

            self._compressed_size

            /

            self._original_size

        ) if self._original_size else 0



        data.update({

            "algorithm":
                self._algorithm,


            "compressed":
                self._compressed,


            "decompressed":
                self._decompressed,


            "original_size":
                self._original_size,


            "compressed_size":
                self._compressed_size,


            "compression_ratio":
                ratio,

        })


        return data



    # ==============================================================
    # Reset
    # ==============================================================

    def reset(
        self,
    ):

        self._compressed = 0

        self._decompressed = 0

        self._original_size = 0

        self._compressed_size = 0


        return self



    # ==============================================================
    # Python Protocols
    # ==============================================================

    def __repr__(
        self,
    ):

        return (

            f"CompressionProcessor("
            f"algorithm={self._algorithm!r}, "
            f"compressed={self._compressed}"
            f")"

        )