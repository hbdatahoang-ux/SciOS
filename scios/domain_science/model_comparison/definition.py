from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExplanatoryEntityDefinition:
    definition_id: str
    entity_id: str
    description: str
    metadata: dict[str, Any]
