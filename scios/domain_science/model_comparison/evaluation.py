from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EvaluationState(str, Enum):
    SUPPORTED = "supported"
    DISFAVORED = "disfavored"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True)
class Evaluation:
    evaluation_id: str
    entity_id: str
    evidence_id: str
    criterion_id: str
    state: EvaluationState
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.state, EvaluationState):
            try:
                object.__setattr__(
                    self,
                    "state",
                    EvaluationState(self.state),
                )
            except ValueError as exc:
                raise ValueError(
                    f"Unsupported evaluation state: {self.state!r}"
                ) from exc
