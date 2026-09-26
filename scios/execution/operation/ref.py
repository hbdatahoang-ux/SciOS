from dataclasses import dataclass


@dataclass(frozen=True)
class OperationRef:
    name: str
    version: str | None = None
