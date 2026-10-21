from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ClaimRelationType(str, Enum):
    PRODUCES = "produces"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    EVALUATES = "evaluates"


@dataclass(frozen=True)
class Claim:
    claim_id: str
    statement: str


@dataclass(frozen=True)
class ClaimRelation:
    relation_id: str
    relation_type: ClaimRelationType
    source_id: str
    target_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.relation_type, ClaimRelationType):
            try:
                object.__setattr__(
                    self,
                    "relation_type",
                    ClaimRelationType(self.relation_type),
                )
            except ValueError as exc:
                raise ValueError(
                    f"Unsupported claim relation type: "
                    f"{self.relation_type!r}"
                ) from exc
