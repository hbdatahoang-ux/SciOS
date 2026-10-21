from dataclasses import dataclass
from typing import Any


@dataclass
class Hypothesis:
    id: str
    variables: list[str]
    mechanism: str
    causal_structure: dict[str, Any]
    parameters: dict[str, Any]
