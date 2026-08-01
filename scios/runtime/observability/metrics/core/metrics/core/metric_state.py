# ==========================================================
# Part 1. Imports
# ==========================================================

from __future__ import annotations

import copy as _copy
import json
from dataclasses import dataclass, field, replace as dc_replace
from typing import Any, Final, TypeAlias


# ==========================================================
# Part 2. Constants & Type Aliases
# ==========================================================

MetricStatus: TypeAlias = str

DEFAULT_STATUS: Final[MetricStatus] = "idle"
DEFAULT_ENABLED: Final[bool] = True
DEFAULT_RECORDING: Final[bool] = False
DEFAULT_TIMESTAMP: Final[float] = 0.0
DEFAULT_VERSION: Final[int] = 1

VALID_STATUSES: Final[frozenset[str]] = frozenset(
    {
        "idle",
        "active",
        "paused",
        "stopped",
        "error",
    }
)


# ==========================================================
# Part 3. Dataclass / Core Container
# ==========================================================

@dataclass(
    slots=True,
    eq=False,
)

class MetricState:
    """
    Runtime state of a metric.
    """

    status: MetricStatus = DEFAULT_STATUS

    enabled: bool = DEFAULT_ENABLED

    recording: bool = DEFAULT_RECORDING

    timestamp: float = DEFAULT_TIMESTAMP

    version: int = DEFAULT_VERSION
# ==========================================================
# Part 4. Validation
# ==========================================================

    def __post_init__(self) -> None:
        """
        Normalize state.
        """
        self.status = str(self.status).strip()

        if isinstance(self.timestamp, int):
            self.timestamp = float(self.timestamp)

    def validate(self) -> None:
        """
        Validate state.
        """

        if self.status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status: {self.status}"
            )

        if not isinstance(self.enabled, bool):
            raise TypeError(
                "enabled must be bool."
            )

        if not isinstance(self.recording, bool):
            raise TypeError(
                "recording must be bool."
            )

        if not isinstance(self.timestamp, (int, float)):
            raise TypeError(
                "timestamp must be numeric."
            )

        if not isinstance(self.version, int):
            raise TypeError(
                "version must be int."
            )

    def is_valid(self) -> bool:
        """
        Return True if state is valid.
        """

        try:
            self.validate()
            return True
        except Exception:
            return False


# ==========================================================
# Part 5. Serialization
# ==========================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Export to dictionary.
        """

        return {
            "status": self.status,
            "enabled": self.enabled,
            "recording": self.recording,
            "timestamp": self.timestamp,
            "version": self.version,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricState":
        """
        Construct from dictionary.
        """

        return cls(
            status=data.get("status", DEFAULT_STATUS),
            enabled=data.get("enabled", DEFAULT_ENABLED),
            recording=data.get(
                "recording",
                DEFAULT_RECORDING,
            ),
            timestamp=data.get(
                "timestamp",
                DEFAULT_TIMESTAMP,
            ),
            version=data.get(
                "version",
                DEFAULT_VERSION,
            ),
        )

    def to_json(self) -> str:
        """
        Export to JSON.
        """

        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
        )

    @classmethod
    def from_json(
        cls,
        text: str,
    ) -> "MetricState":
        """
        Construct from JSON.
        """

        return cls.from_dict(
            json.loads(text),
        )


# ==========================================================
# Part 6. Copy API
# ==========================================================

    def copy(self) -> "MetricState":
        """
        Shallow copy.
        """

        return _copy.copy(self)

    def clone(self) -> "MetricState":
        """
        Alias of deepcopy().
        """

        return _copy.deepcopy(self)

    def deepcopy(self) -> "MetricState":
        """
        Deep copy.
        """

        return _copy.deepcopy(self)

    def replace(
        self,
        **changes: Any,
    ) -> "MetricState":
        """
        Return replaced copy.
        """

        return dc_replace(
            self,
            **changes,
        )
# ==========================================================
# Part 7. Comparison
# ==========================================================

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Equality comparison.
        """

        if not isinstance(other, MetricState):
            return NotImplemented

        return (
            self.status == other.status
            and self.enabled == other.enabled
            and self.recording == other.recording
            and self.timestamp == other.timestamp
            and self.version == other.version
        )

    def __hash__(self) -> int:
        """
        Stable hash.
        """

        return hash(
            (
                self.status,
                self.enabled,
                self.recording,
                self.timestamp,
                self.version,
            )
        )


# ==========================================================
# Part 8. Python Protocols
# ==========================================================

    def __repr__(self) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"status={self.status!r}, "
            f"enabled={self.enabled!r}, "
            f"recording={self.recording!r}, "
            f"timestamp={self.timestamp!r}, "
            f"version={self.version!r})"
        )

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return (
            f"{self.status}"
            f"(enabled={self.enabled}, "
            f"recording={self.recording})"
        )

    def __bool__(self) -> bool:
        """
        Truthiness.
        """

        return self.enabled


# ==========================================================
# Part 9. Public API
# ==========================================================

__all__ = [
    "MetricStatus",
    "DEFAULT_STATUS",
    "DEFAULT_ENABLED",
    "DEFAULT_RECORDING",
    "DEFAULT_TIMESTAMP",
    "DEFAULT_VERSION",
    "VALID_STATUSES",
    "MetricState",
]            