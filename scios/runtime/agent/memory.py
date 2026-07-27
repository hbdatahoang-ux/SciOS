"""
SciOS Runtime Agent Memory
==========================

Simple agent memory store.

Python 3.11+
"""

from __future__ import annotations


__all__ = [
    "Memory",
]



class Memory:
    """
    Agent short-term memory.
    """


    def __init__(self):

        self._items: list[str] = []



    def add(
        self,
        value: str,
    ) -> None:

        self._items.append(
            value
        )



    def last(
        self,
    ) -> str | None:

        if not self._items:
            return None

        return self._items[-1]



    def search(
        self,
        query: str,
    ) -> list[str]:

        return [
            item
            for item in self._items
            if query.lower()
            in item.lower()
        ]



    def clear(self):

        self._items.clear()



    def __len__(self):

        return len(
            self._items
        )