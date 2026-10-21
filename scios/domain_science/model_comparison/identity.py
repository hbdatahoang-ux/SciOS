from __future__ import annotations

from dataclasses import dataclass


_ALLOWED_ENTITY_TYPES = frozenset(
    {
        "constitutive_model",
        "competing_hypothesis",
    }
)


@dataclass(frozen=True)
class ExplanatoryEntityIdentity:
    entity_id: str
    name: str
    version: str
    entity_type: str

    def __post_init__(self) -> None:
        if self.entity_type not in _ALLOWED_ENTITY_TYPES:
            raise ValueError(
                f"Unsupported entity_type: {self.entity_type!r}"
            )
