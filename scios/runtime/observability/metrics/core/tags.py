from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class MetricTags:
    """
    Metric tags container.
    """

    values: set[str] = field(
        default_factory=set,
    )


    def to_dict(self) -> list[str]:
        return sorted(self.values)


    @classmethod
    def from_dict(
        cls,
        data: list[str],
    ) -> "MetricTags":

        return cls(
            values=set(data),
        )


    def clone(self) -> "MetricTags":

        return MetricTags(
            values=set(self.values),
        )