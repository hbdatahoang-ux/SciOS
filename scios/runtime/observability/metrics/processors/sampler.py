"""
SciOS Runtime Metrics Sampling Processor
========================================

Metric sampling processor.

SciOS-NG v0.2
"""

from __future__ import annotations

import hashlib
import random
from typing import Any, Callable

from .processor import MetricProcessor


__all__ = [
    "SamplingProcessor",
    "SamplerProcessor",
]


class SamplingProcessor(MetricProcessor):
    """
    Runtime Metric Sampling Processor.

    Responsibilities
    ----------------
    - Reduce metric volume.
    - Apply probabilistic sampling.
    - Support custom sampling callbacks.
    - Support deterministic sampling.
    - Track sampling statistics.
    - Control observability cost.
    """

    def __init__(
        self,
        rate: float = 1.0,
        name: str = "SamplingProcessor",
        description: str = "",
    ) -> None:
        super().__init__(
            name=name,
            description=description,
        )

        self._validate_rate(rate)

        self._rate = float(rate)

        self._sampler: Callable[[Any], bool] | None = None

        self._total = 0
        self._sampled = 0
        self._dropped = 0

    # ==============================================================
    # Validation
    # ==============================================================

    @staticmethod
    def _validate_rate(
        rate: float,
    ) -> None:
        if isinstance(rate, bool) or not isinstance(
            rate,
            (int, float),
        ):
            raise TypeError(
                "Sampling rate must be a number between 0 and 1"
            )

        if rate < 0 or rate > 1:
            raise ValueError(
                "Sampling rate must be between 0 and 1"
            )

    # ==============================================================
    # Processing
    # ==============================================================

    def transform(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any | None:
        """
        Apply sampling decision.

        Returns
        -------
        metric | None
            The original metric when sampled, otherwise ``None``.
        """

        self._total += 1

        if self.should_sample(metric):
            self._sampled += 1
            return metric

        self._dropped += 1
        return None

    # ==============================================================
    # Sampling Logic
    # ==============================================================

    def should_sample(
        self,
        metric: Any = None,
    ) -> bool:
        """
        Determine whether a metric should be sampled.
        """

        if self._sampler is not None:
            return bool(self._sampler(metric))

        return random.random() < self._rate

    # ==============================================================
    # Configuration
    # ==============================================================

    def set_rate(
        self,
        rate: float,
    ) -> SamplingProcessor:
        """
        Set sampling rate.

        Parameters
        ----------
        rate:
            Value in the inclusive range [0, 1].
        """

        self._validate_rate(rate)

        self._rate = float(rate)

        return self

    def rate(
        self,
    ) -> float:
        """
        Return current sampling rate.
        """

        return self._rate

    def set_sampler(
        self,
        sampler: Callable[[Any], bool],
    ) -> SamplingProcessor:
        """
        Install a custom sampling callback.
        """

        if not callable(sampler):
            raise TypeError(
                "sampler must be callable"
            )

        self._sampler = sampler

        return self

    def remove_sampler(
        self,
    ) -> SamplingProcessor:
        """
        Remove the custom sampler.
        """

        self._sampler = None

        return self

    def sampler(
        self,
    ) -> Callable[[Any], bool] | None:
        """
        Return the configured custom sampler.
        """

        return self._sampler

    # ==============================================================
    # Built-in Strategies
    # ==============================================================

    def always(
        self,
    ) -> SamplingProcessor:
        """
        Sample every metric.
        """

        self._rate = 1.0
        self._sampler = None

        return self

    def never(
        self,
    ) -> SamplingProcessor:
        """
        Drop every metric.
        """

        self._rate = 0.0
        self._sampler = None

        return self

    def half(
        self,
    ) -> SamplingProcessor:
        """
        Set sampling rate to 50%.
        """

        self._rate = 0.5
        self._sampler = None

        return self

    def deterministic(
        self,
        key: str = "id",
    ) -> SamplingProcessor:
        """
        Enable stable hash-based deterministic sampling.

        Dictionary metrics use ``key`` as the sampling identity.
        Other objects use their string representation.

        A cryptographic digest is used instead of Python's ``hash()``
        so the result remains stable across interpreter processes.
        """

        if not isinstance(key, str):
            raise TypeError(
                "key must be a string"
            )

        def sampler(metric: Any) -> bool:
            if isinstance(metric, dict):
                value = metric.get(key, "")
            else:
                value = str(metric)

            payload = str(value).encode(
                "utf-8",
                errors="replace",
            )

            digest = hashlib.sha256(payload).digest()

            integer = int.from_bytes(
                digest[:8],
                byteorder="big",
                signed=False,
            )

            score = integer / float(2**64)

            return score < self._rate

        self._sampler = sampler

        return self

    # ==============================================================
    # Statistics
    # ==============================================================

    def statistics(
        self,
    ) -> dict[str, Any]:
        """
        Return sampling statistics.
        """

        data = super().statistics()

        data.update(
            {
                "rate": self._rate,
                "total": self._total,
                "sampled": self._sampled,
                "dropped": self._dropped,
                "efficiency": (
                    self._sampled / self._total
                    if self._total
                    else 0.0
                ),
            }
        )

        return data

    # ==============================================================
    # Reset
    # ==============================================================

    def reset(
        self,
    ) -> SamplingProcessor:
        """
        Reset runtime counters.

        Sampling configuration is preserved.
        """

        self._total = 0
        self._sampled = 0
        self._dropped = 0

        return self

    # ==============================================================
    # Python Protocols
    # ==============================================================

    def __repr__(
        self,
    ) -> str:
        return (
            "SamplingProcessor("
            f"rate={self._rate}, "
            f"sampled={self._sampled}, "
            f"dropped={self._dropped}"
            ")"
        )


SamplerProcessor = SamplingProcessor