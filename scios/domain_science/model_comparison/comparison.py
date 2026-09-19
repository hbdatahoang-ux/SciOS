from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelComparison:
    comparison_id: str
    entity_ids: tuple[str, ...]
    evaluation_ids: tuple[str, ...]
