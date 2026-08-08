from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class MetricAnnotations:
    """
    Metric annotations container.
    """

    values: dict[str, Any] = field(
        default_factory=dict,
    )


    def to_dict(self) -> dict[str, Any]:
        return dict(self.values)


    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricAnnotations":

        return cls(
            values=dict(data),
        )


    def clone(self) -> "MetricAnnotations":

        return MetricAnnotations(
            values=dict(self.values),
        )