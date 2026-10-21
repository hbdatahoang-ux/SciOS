"""
SciOS Runtime Metrics Normalizer
================================

Metric normalization processor.

SciOS-NG v0.2
"""

from __future__ import annotations

from typing import Any, Callable

from .processor import MetricProcessor


__all__ = [
    "NormalizerProcessor",
]


class NormalizerProcessor(MetricProcessor):
    """
    Normalize metric values or dictionary fields.

    Supported strategies
    --------------------
    - ``minmax``:
        Normalize to [0, 1].

    - ``zscore``:
        Normalize using mean and standard deviation.

    - ``custom``:
        Apply a user supplied callable.
    """

    def __init__(
        self,
        strategy: str = "minmax",
        name: str = "NormalizerProcessor",
        description: str = "",
    ) -> None:
        super().__init__(
            name=name,
            description=description,
        )

        self._strategy = strategy.lower()
        self._normalizer: Callable[[Any], Any] | None = None

        self._field_mapping: dict[str, str] = {}

        self._minimum: float | None = None
        self._maximum: float | None = None

        self._mean: float | None = None
        self._std: float | None = None

        self._normalized = 0

        self._validate_strategy(self._strategy)

    # ==============================================================
    # Processing
    # ==============================================================

    def transform(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Normalize a metric.

        Dictionary metrics are copied before modification.
        Scalar values are normalized directly.
        """

        if self._strategy == "custom":
            if self._normalizer is None:
                raise RuntimeError(
                    "Custom normalization strategy requires "
                    "a normalizer callable"
                )

            result = self._normalizer(metric)

        elif self._strategy == "minmax":
            result = self._transform_minmax(metric)

        elif self._strategy == "zscore":
            result = self._transform_zscore(metric)

        else:
            raise ValueError(
                f"Unsupported normalization strategy: "
                f"{self._strategy!r}"
            )

        self._normalized += 1

        return result

    # ==============================================================
    # Strategy Validation
    # ==============================================================

    @staticmethod
    def _validate_strategy(
        strategy: str,
    ) -> None:
        if strategy not in {
            "minmax",
            "zscore",
            "custom",
        }:
            raise ValueError(
                f"Unsupported normalization strategy: "
                f"{strategy!r}"
            )

    # ==============================================================
    # Configuration
    # ==============================================================

    def set_strategy(
        self,
        strategy: str,
    ) -> "NormalizerProcessor":
        strategy = strategy.lower()

        self._validate_strategy(strategy)

        self._strategy = strategy

        return self

    def strategy(
        self,
    ) -> str:
        return self._strategy

    # ==============================================================
    # Field Mapping
    # ==============================================================

    def map_field(
        self,
        source: str,
        target: str | None = None,
    ) -> "NormalizerProcessor":
        """
        Register a source field and optional output field.

        If target is omitted, the source field is replaced.
        """

        self._field_mapping[source] = (
            source
            if target is None
            else target
        )

        return self

    def remove_field(
        self,
        source: str,
    ) -> "NormalizerProcessor":
        self._field_mapping.pop(
            source,
            None,
        )

        return self

    def fields(
        self,
    ) -> dict[str, str]:
        return dict(self._field_mapping)

    # ==============================================================
    # Min-Max Configuration
    # ==============================================================

    def set_range(
        self,
        minimum: float,
        maximum: float,
    ) -> "NormalizerProcessor":
        if maximum <= minimum:
            raise ValueError(
                "maximum must be greater than minimum"
            )

        self._minimum = float(minimum)
        self._maximum = float(maximum)

        return self

    # ==============================================================
    # Z-Score Configuration
    # ==============================================================

    def set_distribution(
        self,
        mean: float,
        std: float,
    ) -> "NormalizerProcessor":
        if std < 0:
            raise ValueError(
                "std must be non-negative"
            )

        self._mean = float(mean)
        self._std = float(std)

        return self

    # ==============================================================
    # Custom Normalizer
    # ==============================================================

    def set_normalizer(
        self,
        normalizer: Callable[[Any], Any],
    ) -> "NormalizerProcessor":
        if not callable(normalizer):
            raise TypeError(
                "normalizer must be callable"
            )

        self._normalizer = normalizer
        self._strategy = "custom"

        return self

    def remove_normalizer(
        self,
    ) -> "NormalizerProcessor":
        self._normalizer = None

        return self

    # ==============================================================
    # Normalization Functions
    # ==============================================================

    @staticmethod
    def normalize_minmax(
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

    @staticmethod
    def normalize_zscore(
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
    # Internal Transformation
    # ==============================================================

    def _normalize_value(
        self,
        value: Any,
    ) -> Any:
        if not isinstance(
            value,
            (int, float),
        ):
            return value

        numeric = float(value)

        if self._strategy == "minmax":
            if (
                self._minimum is None
                or self._maximum is None
            ):
                raise RuntimeError(
                    "Min-max normalization requires "
                    "minimum and maximum"
                )

            return self.normalize_minmax(
                numeric,
                self._minimum,
                self._maximum,
            )

        if self._strategy == "zscore":
            if (
                self._mean is None
                or self._std is None
            ):
                raise RuntimeError(
                    "Z-score normalization requires "
                    "mean and std"
                )

            return self.normalize_zscore(
                numeric,
                self._mean,
                self._std,
            )

        return value

    def _transform_minmax(
        self,
        metric: Any,
    ) -> Any:
        return self._transform_fields(
            metric
        )

    def _transform_zscore(
        self,
        metric: Any,
    ) -> Any:
        return self._transform_fields(
            metric
        )

    def _transform_fields(
        self,
        metric: Any,
    ) -> Any:
        if not self._field_mapping:
            return self._normalize_value(
                metric
            )

        if not isinstance(
            metric,
            dict,
        ):
            raise TypeError(
                "Field normalization requires "
                "a dictionary metric"
            )

        result = dict(metric)

        for source, target in self._field_mapping.items():
            if source not in metric:
                continue

            result[target] = self._normalize_value(
                metric[source]
            )

        return result

    # ==============================================================
    # Statistics
    # ==============================================================

    def statistics(
        self,
    ) -> dict[str, Any]:
        data = super().statistics()

        data.update(
            {
                "normalized": self._normalized,
                "strategy": self._strategy,
                "mappings": len(
                    self._field_mapping
                ),
            }
        )

        return data

    # ==============================================================
    # Runtime
    # ==============================================================

    def reset(
        self,
    ) -> "NormalizerProcessor":
        self._normalized = 0

        return self

    # ==============================================================
    # Python Protocols
    # ==============================================================

    def __len__(
        self,
    ) -> int:
        return len(
            self._field_mapping
        )

    def __repr__(
        self,
    ) -> str:
        return (
            "NormalizerProcessor("
            f"strategy={self._strategy!r}, "
            f"normalized={self._normalized}"
            ")"
        )