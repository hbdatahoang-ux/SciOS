"""
SciOS Runtime Metrics Compression Processor
===========================================

Metric compression processor.

Responsibilities
-----------------
- Compress metric payloads.
- Support configurable compression levels.
- Preserve input values.
- Provide deterministic compression/decompression.
- Track compression statistics.
- Support runtime reset without losing configuration.

Python 3.11+
"""

from __future__ import annotations

import gzip
import json
import zlib
from typing import Any

from .processor import MetricProcessor


__all__ = [
    "CompressionProcessor",
]


# ======================================================================
# Compression Processor
# ======================================================================


class CompressionProcessor(MetricProcessor):
    """
    Runtime metric compression processor.

    Metrics are encoded as JSON and compressed using the configured
    compression algorithm.

    Supported algorithms
    --------------------
    - ``gzip``
    - ``zlib``

    ``transform()`` returns compressed ``bytes``.
    """

    # ==================================================================
    # Constructor
    # ==================================================================

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

        self._validate_algorithm(
            algorithm
        )

        self._validate_level(
            level
        )

        self._algorithm = algorithm
        self._level = level

        self._compressed = 0
        self._decompressed = 0
        self._bytes_in = 0
        self._bytes_out = 0

    # ==================================================================
    # Validation
    # ==================================================================

    @staticmethod
    def _validate_algorithm(
        algorithm: str,
    ) -> None:
        if algorithm not in {
            "gzip",
            "zlib",
        }:
            raise ValueError(
                "Unsupported compression algorithm: "
                f"{algorithm}"
            )

    @staticmethod
    def _validate_level(
        level: int,
    ) -> None:
        if not isinstance(level, int):
            raise TypeError(
                "compression level must be an integer"
            )

        if level < 0 or level > 9:
            raise ValueError(
                "compression level must be between 0 and 9"
            )

    # ==================================================================
    # Configuration
    # ==================================================================

    @property
    def algorithm(self) -> str:
        return self._algorithm

    def set_algorithm(
        self,
        algorithm: str,
    ) -> "CompressionProcessor":
        """
        Change compression algorithm.
        """

        self._validate_algorithm(
            algorithm
        )

        self._algorithm = algorithm

        return self

    @property
    def level(self) -> int:
        return self._level

    def set_level(
        self,
        level: int,
    ) -> "CompressionProcessor":
        """
        Change compression level.
        """

        self._validate_level(
            level
        )

        self._level = level

        return self

    # ==================================================================
    # Encoding
    # ==================================================================

    @staticmethod
    def _encode(
        metric: Any,
    ) -> bytes:
        """
        Encode a metric as deterministic JSON bytes.
        """

        return json.dumps(
            metric,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode(
            "utf-8"
        )

    # ==================================================================
    # Compression
    # ==================================================================

    def _compress(
        self,
        payload: bytes,
    ) -> bytes:
        """
        Compress raw bytes.
        """

        if self._algorithm == "gzip":
            return gzip.compress(
                payload,
                compresslevel=self._level,
            )

        return zlib.compress(
            payload,
            level=self._level,
        )

    def _decompress(
        self,
        payload: bytes,
    ) -> bytes:
        """
        Decompress raw bytes.
        """

        if self._algorithm == "gzip":
            return gzip.decompress(
                payload
            )

        return zlib.decompress(
            payload
        )

    # ==================================================================
    # Processing
    # ==================================================================

    def transform(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> bytes:
        """
        Encode and compress a metric.

        Returns
        -------
        bytes
            Compressed metric payload.
        """

        payload = self._encode(
            metric
        )

        result = self._compress(
            payload
        )

        self._compressed += 1

        self._bytes_in += len(
            payload
        )

        self._bytes_out += len(
            result
        )

        return result

    # ==================================================================
    # Decompression API
    # ==================================================================

    def decompress(
        self,
        payload: bytes,
    ) -> Any:
        """
        Decompress and decode a metric payload.
        """

        if not isinstance(payload, bytes):
            raise TypeError(
                "payload must be bytes"
            )

        raw = self._decompress(
            payload
        )

        result = json.loads(
            raw.decode("utf-8")
        )

        self._decompressed += 1

        return result

    # ==================================================================
    # Compression Metrics
    # ==================================================================

    def ratio(
        self,
    ) -> float:
        """
        Return compressed-size / original-size ratio.

        Returns ``0.0`` when no data has been processed.
        """

        if self._bytes_in == 0:
            return 0.0

        return (
            self._bytes_out
            / self._bytes_in
        )

    def saved_bytes(
        self,
    ) -> int:
        """
        Return number of bytes saved by compression.
        """

        return (
            self._bytes_in
            - self._bytes_out
        )

    # ==================================================================
    # Statistics
    # ==================================================================

    def statistics(
        self,
    ) -> dict[str, Any]:
        """
        Return compression statistics.
        """

        data = super().statistics()

        data.update(
            {
                "algorithm": self._algorithm,
                "level": self._level,
                "compressed": self._compressed,
                "decompressed": self._decompressed,
                "bytes_in": self._bytes_in,
                "bytes_out": self._bytes_out,
                "ratio": self.ratio(),
                "saved_bytes": self.saved_bytes(),
            }
        )

        return data

    # ==================================================================
    # Runtime
    # ==================================================================

    def reset(
        self,
    ) -> "CompressionProcessor":
        """
        Reset runtime statistics.

        Configuration survives reset.
        """

        self._compressed = 0
        self._decompressed = 0
        self._bytes_in = 0
        self._bytes_out = 0

        return self

    # ==================================================================
    # Python Protocols
    # ==================================================================

    def __len__(
        self,
    ) -> int:
        """
        Return number of metrics compressed.
        """

        return self._compressed

    def __repr__(
        self,
    ) -> str:
        return (
            "CompressionProcessor("
            f"algorithm={self._algorithm!r}, "
            f"level={self._level}, "
            f"compressed={self._compressed}, "
            f"decompressed={self._decompressed}"
            ")"
        )
