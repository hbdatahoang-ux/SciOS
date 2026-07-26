"""
SciOS-NG Runtime Metrics Normalization Processor

Metric data normalization processor.

SciOS-NG v0.2
"""


from __future__ import annotations

from typing import Any


from .processor import MetricProcessor



# ==================================================================
# NormalizerProcessor
# ==================================================================


class NormalizerProcessor(
    MetricProcessor
):
    """
    Runtime Metric Normalization Processor.

    Responsibilities
    ----------------
    - Normalize metric structures
    - Standardize values
    - Normalize field names
    - Prepare metrics for aggregation/export
    """



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        name: str = "NormalizerProcessor",
        description: str = "",
        strategy: str = "auto",
    ) -> None:


        super().__init__(
            name=name,
            description=description,
        )


        # ----------------------------------------------------------
        # Configuration
        # ----------------------------------------------------------

        self._strategy = strategy


        self._field_mapping: dict[str, str] = {}



        # ----------------------------------------------------------
        # Statistics
        # ----------------------------------------------------------

        self._normalized = 0



    # ==============================================================
    # Processing
    # ==============================================================

    def transform(
        self,
        metric: Any,
        **kwargs,
    ):
        """
        Normalize metric data.
        """

        result = metric



        if self._strategy == "auto":

            result = self.auto_normalize(
                metric
            )


        elif self._strategy == "dict":

            result = self.normalize_dict(
                metric
            )


        elif self._strategy == "value":

            result = self.normalize_value(
                metric
            )



        self._normalized += 1


        return result



    # ==============================================================
    # Normalization Strategies
    # ==============================================================

    def auto_normalize(
        self,
        metric: Any,
    ):
        """
        Automatically normalize metric.
        """

        if isinstance(
            metric,
            dict
        ):

            return self.normalize_dict(
                metric
            )



        return self.normalize_value(
            metric
        )



    def normalize_dict(
        self,
        metric: dict,
    ) -> dict:
        """
        Normalize dictionary metrics.
        """

        result = {}



        for key, value in metric.items():

            normalized_key = self.normalize_key(
                key
            )


            result[
                normalized_key
            ] = self.normalize_value(
                value
            )



        return result



    def normalize_key(
        self,
        key: Any,
    ) -> str:
        """
        Normalize field names.
        """

        key = str(
            key
        )


        key = key.strip()


        key = key.lower()


        key = key.replace(
            " ",
            "_",
        )


        key = key.replace(
            "-",
            "_",
        )


        return self._field_mapping.get(
            key,
            key,
        )



    def normalize_value(
        self,
        value: Any,
    ):
        """
        Normalize values.
        """

        if isinstance(
            value,
            str,
        ):

            return value.strip()



        if isinstance(
            value,
            bool,
        ):

            return int(
                value
            )



        if isinstance(
            value,
            (int, float),
        ):

            return float(
                value
            )



        return value



    # ==============================================================
    # Field Mapping
    # ==============================================================

    def map_field(
        self,
        source: str,
        target: str,
    ):

        self._field_mapping[
            source
        ] = target


        return self



    def remove_mapping(
        self,
        source: str,
    ):

        self._field_mapping.pop(
            source,
            None,
        )


        return self



    def mappings(
        self,
    ):

        return dict(
            self._field_mapping
        )



    # ==============================================================
    # Built-in Normalizers
    # ==============================================================

    def normalize_range(
        self,
        value: float,
        minimum: float,
        maximum: float,
    ) -> float:
        """
        Min-max normalization.
        """

        if maximum == minimum:

            return 0.0


        return (
            value - minimum
        ) / (
            maximum - minimum
        )



    def normalize_zscore(
        self,
        value: float,
        mean: float,
        std: float,
    ) -> float:
        """
        Z-score normalization.
        """

        if std == 0:

            return 0.0


        return (
            value - mean
        ) / std



    # ==============================================================
    # Statistics
    # ==============================================================

    def statistics(
        self,
    ):

        data = super().statistics()


        data.update({

            "normalized":
                self._normalized,


            "strategy":
                self._strategy,


            "mappings":
                len(
                    self._field_mapping
                ),

        })


        return data



    # ==============================================================
    # Runtime
    # ==============================================================

    def reset(
        self,
    ):

        self._normalized = 0

        return self



    # ==============================================================
    # Python Protocols
    # ==============================================================

    def __len__(
        self,
    ):

        return len(
            self._field_mapping
        )



    def __repr__(
        self,
    ):

        return (

            f"NormalizerProcessor("
            f"strategy={self._strategy!r}, "
            f"normalized={self._normalized}"
            f")"

        )