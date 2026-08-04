# ==========================================================
# Part 1. Imports & Constants
# ==========================================================

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from threading import RLock
from typing import Any, Final, TypeAlias, Union

DEFAULT_HEALTH: Final[str] = "unknown"
DEFAULT_SCORE: Final[float] = 0.0
DEFAULT_MESSAGE: Final[str] = ""
DEFAULT_VERSION: Final[str] = "1.0"

HealthValue: TypeAlias = Union[str, "MetricHealth"]
HealthScore: TypeAlias = float

__all__ = [
    "DEFAULT_HEALTH",
    "DEFAULT_SCORE",
    "DEFAULT_MESSAGE",
    "DEFAULT_VERSION",
    "HealthValue",
    "HealthScore",
    "MetricHealth",
    "MetricHealthInfo",
]


# ==========================================================
# Part 2. Enums
# ==========================================================

class MetricHealth(str, Enum):
    """
    Overall health state for metrics subsystem.
    """

    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

# ==========================================================
# Part 3. Constructor
# ==========================================================


class MetricHealthInfo:
    """
    Runtime health information.

    Represents the overall health of the metrics subsystem.
    """

    __slots__ = (
        "_health",
        "_score",
        "_message",
        "_timestamp",
        "_version",
        "_metadata",
        "_checks",
        "_lock",
    )

    def __init__(
        self,
        *,
        health: HealthValue = MetricHealth.UNKNOWN,
        score: HealthScore = DEFAULT_SCORE,
        message: str = DEFAULT_MESSAGE,
        timestamp: datetime | None = None,
        version: str = DEFAULT_VERSION,
        metadata: dict[str, Any] | None = None,
        checks: dict[str, Any] | None = None,
    ) -> None:

        if isinstance(health, MetricHealth):
            self._health = health
        else:
            self._health = MetricHealth(str(health))

        self._score = float(score)
        self._message = str(message)

        self._timestamp = (
            timestamp.astimezone(UTC)
            if timestamp is not None
            else datetime.now(UTC)
        )

        self._version = str(version)

        self._metadata: dict[str, Any] = (
            dict(metadata)
            if metadata is not None
            else {}
        )

        self._checks: dict[str, Any] = (
            dict(checks)
            if checks is not None
            else {}
        )

        self._lock = RLock()

    # ==========================================================
    # Part 4. Properties
    # ==========================================================

    @property
    def health(self) -> MetricHealth:
        return self._health

    @property
    def score(self) -> float:
        return self._score

    @property
    def message(self) -> str:
        return self._message

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def version(self) -> str:
        return self._version

    @property
    def metadata(self) -> dict[str, Any]:
        return self._metadata

    @property
    def checks(self) -> dict[str, Any]:
        return self._checks

    @property
    def lock(self) -> RLock:
        return self._lock

    # ==========================================================
    # Part 5. Health State API
    # ==========================================================

    def set_healthy(
        self,
        message: str | None = None,
    ) -> None:

        with self._lock:
            self._health = MetricHealth.HEALTHY
            if message is not None:
                self._message = str(message)
            self._timestamp = datetime.now(UTC)

    def set_degraded(
        self,
        message: str | None = None,
    ) -> None:

        with self._lock:
            self._health = MetricHealth.DEGRADED
            if message is not None:
                self._message = str(message)
            self._timestamp = datetime.now(UTC)

    def set_unhealthy(
        self,
        message: str | None = None,
    ) -> None:

        with self._lock:
            self._health = MetricHealth.UNHEALTHY
            if message is not None:
                self._message = str(message)
            self._timestamp = datetime.now(UTC)

    def set_critical(
        self,
        message: str | None = None,
    ) -> None:

        with self._lock:
            self._health = MetricHealth.CRITICAL
            if message is not None:
                self._message = str(message)
            self._timestamp = datetime.now(UTC)

    def set_unknown(
        self,
        message: str | None = None,
    ) -> None:

        with self._lock:
            self._health = MetricHealth.UNKNOWN
            if message is not None:
                self._message = str(message)
            self._timestamp = datetime.now(UTC)

    def reset(self) -> None:

        with self._lock:
            self._health = MetricHealth.UNKNOWN
            self._score = DEFAULT_SCORE
            self._message = DEFAULT_MESSAGE
            self._timestamp = datetime.now(UTC)
            self._metadata.clear()
            self._checks.clear()

    # ==========================================================
    # Part 6. Score API
    # ==========================================================

    def set_score(
        self,
        score: HealthScore,
    ) -> None:

        with self._lock:
            self._score = float(score)
            self._timestamp = datetime.now(UTC)


    def increase_score(
        self,
        delta: float,
    ) -> None:

        with self._lock:
            self._score += float(delta)
            self._timestamp = datetime.now(UTC)


    def decrease_score(
        self,
        delta: float,
    ) -> None:

        with self._lock:
            self._score -= float(delta)
            self._timestamp = datetime.now(UTC)


    def normalize_score(self) -> float:
        """
        Clamp score into the valid range [0, 100].
        """

        with self._lock:
            self._score = max(
                0.0,
                min(
                    100.0,
                    float(self._score),
                ),
            )
            self._timestamp = datetime.now(UTC)
            return self._score


    def score_percent(self) -> float:
        """
        Return score as a percentage.
        """

        return float(self._score)

    # ==========================================================
    # Part 7. Health Query API
    # ==========================================================

    def is_healthy(self) -> bool:

        return self._health is MetricHealth.HEALTHY


    def is_degraded(self) -> bool:

        return self._health is MetricHealth.DEGRADED


    def is_unhealthy(self) -> bool:

        return self._health is MetricHealth.UNHEALTHY


    def is_critical(self) -> bool:

        return self._health is MetricHealth.CRITICAL


    def is_unknown(self) -> bool:

        return self._health is MetricHealth.UNKNOWN


    def has_score(self) -> bool:
        """
        Return True when the object contains a valid numeric score,
        including the default score of 0.0.
        """

        return isinstance(self._score, (int, float))

    # ==========================================================
    # Part 8. Check API
    # ==========================================================

    def add_check(
        self,
        name: str,
        value: Any,
    ) -> None:

        with self._lock:
            self._checks[str(name)] = value
            self._timestamp = datetime.now(UTC)

    def remove_check(
        self,
        name: str,
    ) -> None:

        with self._lock:
            self._checks.pop(
                str(name),
                None,
            )
            self._timestamp = datetime.now(UTC)

    def update_check(
        self,
        name: str,
        value: Any,
    ) -> None:

        with self._lock:
            self._checks[str(name)] = value
            self._timestamp = datetime.now(UTC)

    def get_check(
        self,
        name: str,
        default: Any = None,
    ) -> Any:

        return self._checks.get(
            str(name),
            default,
        )

    def clear_checks(self) -> None:

        with self._lock:
            self._checks.clear()
            self._timestamp = datetime.now(UTC)

    def check_count(self) -> int:

        return len(self._checks)

    def failed_checks(self) -> dict[str, Any]:

        return {
            k: v
            for k, v in self._checks.items()
            if not bool(v)
        }

    def passed_checks(self) -> dict[str, Any]:

        return {
            k: v
            for k, v in self._checks.items()
            if bool(v)
        }

    # ==========================================================
    # Part 9. Metadata API
    # ==========================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:

        with self._lock:
            self._metadata[str(key)] = value
            self._timestamp = datetime.now(UTC)

    def update_metadata(
        self,
        metadata: dict[str, Any],
    ) -> None:

        with self._lock:
            self._metadata.update(dict(metadata))
            self._timestamp = datetime.now(UTC)

    def clear_metadata(self) -> None:

        with self._lock:
            self._metadata.clear()
            self._timestamp = datetime.now(UTC)

    # ==========================================================
    # Part 10. Serialization
    # ==========================================================

    def to_dict(self) -> dict[str, Any]:

        return {
            "health": self._health.value,
            "score": self._score,
            "message": self._message,
            "timestamp": self._timestamp.isoformat(),
            "version": self._version,
            "metadata": dict(self._metadata),
            "checks": dict(self._checks),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricHealthInfo":

        return cls(
            health=data.get("health", DEFAULT_HEALTH),
            score=data.get("score", DEFAULT_SCORE),
            message=data.get("message", DEFAULT_MESSAGE),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if data.get("timestamp")
            else None,
            version=data.get("version", DEFAULT_VERSION),
            metadata=data.get("metadata"),
            checks=data.get("checks"),
        )

    def to_json(self) -> str:

        import json

        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
        )

    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "MetricHealthInfo":

        import json

        return cls.from_dict(
            json.loads(payload),
        )

    # ==========================================================
    # Part 11. Validation
    # ==========================================================

    def validate(self) -> bool:
        """
        Validate current health object.

        Returns
        -------
        bool
            True if valid, otherwise False.
        """

        if not isinstance(self._score, (int, float)):
            return False

        if not (0.0 <= self._score <= 100.0):
            return False

        if not isinstance(self._health, MetricHealth):
            return False

        if not isinstance(self._metadata, dict):
            return False

        if not isinstance(self._checks, dict):
            return False

        return True


    def is_valid(self) -> bool:
        return self.validate()

    # ==========================================================
    # Part 12. Snapshot API
    # ==========================================================

    def copy(self) -> "MetricHealthInfo":

        import copy

        return copy.copy(self)

    def deepcopy(self) -> "MetricHealthInfo":

        import copy

        return copy.deepcopy(self)

    def clone(self) -> "MetricHealthInfo":

        return self.deepcopy()

    # ==========================================================
    # Part 13. Python Protocols
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"health={self._health.value!r}, "
            f"score={self._score!r})"
        )

    def __str__(self) -> str:

        return (
            f"{self._health.value}"
            f" ({self._score:.1f}%)"
        )

    def __bool__(self) -> bool:

        return self._health is not MetricHealth.CRITICAL

    def __len__(self) -> int:

        return len(self._checks)

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(
            other,
            MetricHealthInfo,
        ):
            return NotImplemented

        return self.to_dict() == other.to_dict()

    def __hash__(self) -> int:

        return hash(
            (
                self._health,
                self._score,
                self._version,
            )
        )

    def __getstate__(self) -> dict[str, Any]:

        return {
            "health": self._health,
            "score": self._score,
            "message": self._message,
            "timestamp": self._timestamp,
            "version": self._version,
            "metadata": self._metadata,
            "checks": self._checks,
        }

    def __setstate__(
        self,
        state: dict[str, Any],
    ) -> None:

        self._health = state["health"]
        self._score = state["score"]
        self._message = state["message"]
        self._timestamp = state["timestamp"]
        self._version = state["version"]
        self._metadata = dict(state["metadata"])
        self._checks = dict(state["checks"])
        self._lock = RLock()

    # ==========================================================
    # Part 14. Diagnostics API
    # ==========================================================

    def summary(self) -> dict[str, Any]:

        return {
            "health": self._health.value,
            "score": self._score,
            "checks": len(self._checks),
        }

    def diagnostics(self) -> dict[str, Any]:

        return {
            "health": self._health.value,
            "score": self._score,
            "message": self._message,
            "metadata": dict(self._metadata),
            "checks": dict(self._checks),
        }

    def health_report(self) -> dict[str, Any]:

        passed = len(self.passed_checks())
        failed = len(self.failed_checks())

        return {
            "health": self._health.value,
            "score": self._score,
            "checks": len(self._checks),
            "passed": passed,
            "failed": failed,
        }

    def health_score(self) -> float:

        return self._score

    def overall_status(self) -> MetricHealth:

        return self._health


# ==========================================================
# Part 15. Public API
# ==========================================================

__all__ = [
    "DEFAULT_HEALTH",
    "DEFAULT_SCORE",
    "DEFAULT_MESSAGE",
    "DEFAULT_VERSION",
    "HealthValue",
    "HealthScore",
    "MetricHealth",
    "MetricHealthInfo",
]                