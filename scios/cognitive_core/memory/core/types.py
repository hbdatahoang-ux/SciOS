from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, TypeAlias


MemoryId: TypeAlias = str
MemoryContent: TypeAlias = str
MemoryMetadata: TypeAlias = dict[str, Any]
MemoryTimestamp: TypeAlias = datetime
MemoryQuery: TypeAlias = str


class MemoryKind(str, Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
