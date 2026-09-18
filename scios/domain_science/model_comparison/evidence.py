from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    dataset_id: str
    observable_id: str
    value: Any
    provenance_id: str