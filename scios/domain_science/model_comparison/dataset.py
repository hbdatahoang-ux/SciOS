from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Dataset:
    dataset_id: str
    source: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class Processing:
    processing_id: str
    input_dataset_id: str
    description: str
    parameters: dict[str, Any]