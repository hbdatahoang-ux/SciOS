"""
SciOS Cognitive Result
======================

Defines the result object returned by the CognitivePipeline.
Behaves like a dict for test compatibility.
"""

from __future__ import annotations


class CognitiveResult:
    def __init__(self, stage: str) -> None:
        self.stage = stage
        self.data: dict = {}
        self.messages: list[str] = []
        self.success: bool = True
        self.errors: list[str] = []

    # -----------------------------
    # Core API
    # -----------------------------
    def add_data(self, key: str, value: dict) -> None:
        self.data[key] = value

    def add_message(self, msg: str) -> None:
        self.messages.append(msg)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.success = False

    # -----------------------------
    # Dict-like behavior
    # -----------------------------
    def __getitem__(self, key: str):
        return self.data[key]

    def __contains__(self, key: str) -> bool:
        return key in self.data

    def __iter__(self):
        return iter(self.data)

    def items(self):
        return self.data.items()

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def __repr__(self) -> str:
        return f"CognitiveResult(stage={self.stage}, data={self.data}, success={self.success})"
