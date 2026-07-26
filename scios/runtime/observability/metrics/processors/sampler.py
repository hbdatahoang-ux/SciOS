"""
SciOS-NG Runtime Metrics Sampling Processor

Metric sampling processor.

SciOS-NG v0.2
"""


from __future__ import annotations

import random

from typing import Any, Callable


from .processor import MetricProcessor



# ==================================================================
# SamplingProcessor
# ==================================================================


class SamplingProcessor(
    MetricProcessor
):
    """
    Runtime Metric Sampling Processor.

    Responsibilities
    ----------------
    - Reduce metric volume
    - Apply probabilistic sampling
    - Support deterministic sampling
    - Control observability cost
    """



    # ==============================================================
    # Constructor
    # ==============================================================

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


        # ----------------------------------------------------------
        # Sampling Configuration
        # ----------------------------------------------------------

        self._rate = rate



        self._sampler: Callable | None = None



        # ----------------------------------------------------------
        # Statistics
        # ----------------------------------------------------------

        self._sampled = 0

        self._dropped = 0



        self._total = 0



    # ==============================================================
    # Processing
    # ==============================================================

    def transform(
        self,
        metric: Any,
        **kwargs,
    ):
        """
        Apply sampling decision.
        """

        self._total += 1


        if self.should_sample(
            metric
        ):

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
        Determine if metric is sampled.
        """

        if self._sampler:

            return self._sampler(
                metric
            )


        return random.random() <= self._rate



    # ==============================================================
    # Configuration
    # ==============================================================

    def set_rate(
        self,
        rate: float,
    ):

        if rate < 0 or rate > 1:

            raise ValueError(
                "Sampling rate must be between 0 and 1"
            )


        self._rate = rate


        return self



    def rate(
        self,
    ) -> float:

        return self._rate



    def set_sampler(
        self,
        sampler: Callable,
    ):

        self._sampler = sampler


        return self



    def remove_sampler(
        self,
    ):

        self._sampler = None


        return self



    # ==============================================================
    # Built-in Strategies
    # ==============================================================

    def always(
        self,
    ):

        self._rate = 1.0

        return self



    def never(
        self,
    ):

        self._rate = 0.0

        return self



    def half(
        self,
    ):

        self._rate = 0.5

        return self



    def deterministic(
        self,
        key: str = "id",
    ):
        """
        Deterministic hash-based sampling.
        """

        def sampler(metric):

            if isinstance(
                metric,
                dict
            ):

                value = metric.get(
                    key,
                    "",
                )

            else:

                value = str(
                    metric
                )


            score = (
                hash(value)
                %
                100
            ) / 100


            return score <= self._rate



        self._sampler = sampler


        return self



    # ==============================================================
    # Statistics
    # ==============================================================

    def statistics(
        self,
    ):

        data = super().statistics()


        data.update({

            "rate":
                self._rate,


            "total":
                self._total,


            "sampled":
                self._sampled,


            "dropped":
                self._dropped,


            "efficiency":
                (
                    self._sampled
                    /
                    self._total
                )
                if self._total
                else 0,

        })


        return data



    # ==============================================================
    # Reset
    # ==============================================================

    def reset(
        self,
    ):

        self._total = 0

        self._sampled = 0

        self._dropped = 0


        return self



    # ==============================================================
    # Python Protocols
    # ==============================================================

    def __repr__(
        self,
    ):

        return (

            f"SamplingProcessor("
            f"rate={self._rate}, "
            f"sampled={self._sampled}, "
            f"dropped={self._dropped}"
            f")"

        )