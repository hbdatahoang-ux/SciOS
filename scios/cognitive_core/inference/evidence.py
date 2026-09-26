from dataclasses import dataclass
from typing import Any


@dataclass
class Evidence:
    id: str
    observation: str
    value: dict[str, Any]
    context: dict[str, Any]
    source: str
    uncertainty: dict[str, Any]
    quality: float
