# ==========================================================
# Part 1. Imports & Fixtures
# ==========================================================

from __future__ import annotations

import copy
import inspect
import json
import pickle
import threading

from threading import RLock
from typing import Any

import pytest

from scios.runtime.observability.metrics.core.metrics.monitor.health import (
    DEFAULT_HEALTH,
    DEFAULT_MESSAGE,
    DEFAULT_SCORE,
    DEFAULT_VERSION,
    HealthScore,
    HealthValue,
    MetricHealth,
    MetricHealthInfo,
    __all__,
)

_RLOCK_TYPE = type(RLock())


@pytest.fixture
def health() -> MetricHealthInfo:
    return MetricHealthInfo()


# ==========================================================
# Part 2. Dummy Data
# ==========================================================

DUMMY_METADATA = {
    "host": "localhost",
    "service": "metrics",
}

DUMMY_CHECKS = {
    "cpu": True,
    "memory": True,
    "disk": False,
}


# ==========================================================
# Part 3. Construction
# ==========================================================

class TestConstruction:

    def test_create_default(self):

        obj = MetricHealthInfo()

        assert obj.health == MetricHealth.UNKNOWN
        assert obj.score == DEFAULT_SCORE
        assert obj.message == DEFAULT_MESSAGE
        assert obj.version == DEFAULT_VERSION
        assert isinstance(obj.timestamp, obj.timestamp.__class__)
        assert obj.metadata == {}
        assert obj.checks == {}
        assert isinstance(obj.lock, _RLOCK_TYPE)

    def test_create_custom(self):

        obj = MetricHealthInfo(
            health=MetricHealth.HEALTHY,
            score=97.5,
            message="healthy",
            metadata=DUMMY_METADATA,
            checks=DUMMY_CHECKS,
            version="2.0",
        )

        assert obj.health == MetricHealth.HEALTHY
        assert obj.score == 97.5
        assert obj.message == "healthy"
        assert obj.version == "2.0"
        assert obj.metadata == DUMMY_METADATA
        assert obj.checks == DUMMY_CHECKS


# ==========================================================
# Part 4. Properties
# ==========================================================

class TestProperties:

    def test_health(self, health: MetricHealthInfo):

        assert health.health == MetricHealth.UNKNOWN

    def test_score(self, health: MetricHealthInfo):

        assert health.score == DEFAULT_SCORE

    def test_message(self, health: MetricHealthInfo):

        assert health.message == DEFAULT_MESSAGE

    def test_timestamp(self, health: MetricHealthInfo):

        assert health.timestamp is not None

    def test_version(self, health: MetricHealthInfo):

        assert health.version == DEFAULT_VERSION

    def test_metadata(self, health: MetricHealthInfo):

        assert isinstance(health.metadata, dict)
        assert health.metadata == {}

    def test_checks(self, health: MetricHealthInfo):

        assert isinstance(health.checks, dict)
        assert health.checks == {}

    def test_lock(self, health: MetricHealthInfo):

        assert isinstance(health.lock, _RLOCK_TYPE)

# ==========================================================
# Part 5. Health State API
# ==========================================================

class TestHealthStateAPI:

    def test_set_healthy(self, health: MetricHealthInfo):

        health.set_healthy("ok")

        assert health.health == MetricHealth.HEALTHY
        assert health.message == "ok"

    def test_set_degraded(self, health: MetricHealthInfo):

        health.set_degraded("degraded")

        assert health.health == MetricHealth.DEGRADED
        assert health.message == "degraded"

    def test_set_unhealthy(self, health: MetricHealthInfo):

        health.set_unhealthy("bad")

        assert health.health == MetricHealth.UNHEALTHY
        assert health.message == "bad"

    def test_set_critical(self, health: MetricHealthInfo):

        health.set_critical("critical")

        assert health.health == MetricHealth.CRITICAL
        assert health.message == "critical"

    def test_set_unknown(self, health: MetricHealthInfo):

        health.set_unknown("unknown")

        assert health.health == MetricHealth.UNKNOWN
        assert health.message == "unknown"

    def test_reset(self, health: MetricHealthInfo):

        health.set_healthy("ok")
        health.set_metadata("host", "localhost")
        health.add_check("cpu", True)

        health.reset()

        assert health.health == MetricHealth.UNKNOWN
        assert health.score == DEFAULT_SCORE
        assert health.message == DEFAULT_MESSAGE
        assert health.metadata == {}
        assert health.checks == {}


# ==========================================================
# Part 6. Score API
# ==========================================================

class TestScoreAPI:

    def test_set_score(self, health: MetricHealthInfo):

        health.set_score(82.5)

        assert health.score == 82.5

    def test_increase_score(self, health: MetricHealthInfo):

        health.set_score(50)

        health.increase_score(10)

        assert health.score == 60

    def test_decrease_score(self, health: MetricHealthInfo):

        health.set_score(50)

        health.decrease_score(20)

        assert health.score == 30

    def test_normalize_score(self, health: MetricHealthInfo):

        health.set_score(-50)
        health.normalize_score()

        assert health.score == 0

        health.set_score(150)
        health.normalize_score()

        assert health.score == 100

        health.set_score(75)
        health.normalize_score()

        assert health.score == 75

    def test_score_percent(self, health: MetricHealthInfo):

        health.set_score(82.5)

        assert health.score_percent() == pytest.approx(82.5)


# ==========================================================
# Part 7. Health Query API
# ==========================================================

class TestHealthQueryAPI:

    def test_is_healthy(self, health: MetricHealthInfo):

        health.set_healthy()

        assert health.is_healthy()

    def test_is_degraded(self, health: MetricHealthInfo):

        health.set_degraded()

        assert health.is_degraded()

    def test_is_unhealthy(self, health: MetricHealthInfo):

        health.set_unhealthy()

        assert health.is_unhealthy()

    def test_is_critical(self, health: MetricHealthInfo):

        health.set_critical()

        assert health.is_critical()

    def test_is_unknown(self, health: MetricHealthInfo):

        assert health.is_unknown()

    def test_has_score(self, health: MetricHealthInfo):

        assert health.has_score()

        health.set_score(95)

        assert health.has_score()


# ==========================================================
# Part 8. Check API
# ==========================================================

class TestCheckAPI:

    def test_add_check(self, health: MetricHealthInfo):

        health.add_check("cpu", True)

        assert health.checks["cpu"] is True

    def test_remove_check(self, health: MetricHealthInfo):

        health.add_check("cpu", True)

        health.remove_check("cpu")

        assert "cpu" not in health.checks

    def test_update_check(self, health: MetricHealthInfo):

        health.add_check("cpu", True)

        health.update_check("cpu", False)

        assert health.checks["cpu"] is False

    def test_get_check(self, health: MetricHealthInfo):

        health.add_check("cpu", True)

        assert health.get_check("cpu") is True

    def test_clear_checks(self, health: MetricHealthInfo):

        health.add_check("cpu", True)
        health.add_check("disk", False)

        health.clear_checks()

        assert health.checks == {}

    def test_check_count(self, health: MetricHealthInfo):

        health.add_check("cpu", True)
        health.add_check("disk", False)

        assert health.check_count() == 2

    def test_failed_checks(self, health: MetricHealthInfo):

        health.add_check("cpu", True)
        health.add_check("disk", False)
        health.add_check("network", False)

        assert set(health.failed_checks()) == {
            "disk",
            "network",
        }

    def test_passed_checks(self, health: MetricHealthInfo):

        health.add_check("cpu", True)
        health.add_check("disk", False)
        health.add_check("memory", True)

        assert set(health.passed_checks()) == {
            "cpu",
            "memory",
        }

# ==========================================================
# Part 9. Metadata API
# ==========================================================

class TestMetadataAPI:

    def test_set_metadata(self, health: MetricHealthInfo):

        health.set_metadata("host", "localhost")

        assert health.metadata["host"] == "localhost"

    def test_update_metadata(self, health: MetricHealthInfo):

        health.update_metadata(DUMMY_METADATA)

        assert health.metadata == DUMMY_METADATA

    def test_clear_metadata(self, health: MetricHealthInfo):

        health.update_metadata(DUMMY_METADATA)

        health.clear_metadata()

        assert health.metadata == {}


# ==========================================================
# Part 10. Serialization
# ==========================================================

class TestSerialization:

    def test_to_dict(self, health: MetricHealthInfo):

        health.set_healthy("healthy")
        health.set_score(97.5)
        health.update_metadata(DUMMY_METADATA)
        health.add_check("cpu", True)

        data = health.to_dict()

        assert isinstance(data, dict)
        assert data["health"] == MetricHealth.HEALTHY.value
        assert data["score"] == 97.5
        assert data["message"] == "healthy"
        assert data["metadata"] == DUMMY_METADATA
        assert data["checks"]["cpu"] is True

    def test_from_dict(self):

        data = {
            "health": "healthy",
            "score": 95.0,
            "message": "ok",
            "version": DEFAULT_VERSION,
            "metadata": DUMMY_METADATA,
            "checks": DUMMY_CHECKS,
        }

        obj = MetricHealthInfo.from_dict(data)

        assert obj.health == MetricHealth.HEALTHY
        assert obj.score == 95.0
        assert obj.message == "ok"
        assert obj.metadata == DUMMY_METADATA
        assert obj.checks == DUMMY_CHECKS

    def test_to_json(self, health: MetricHealthInfo):

        text = health.to_json()

        assert isinstance(text, str)

        parsed = json.loads(text)

        assert parsed["health"] == MetricHealth.UNKNOWN.value

    def test_from_json(self, health: MetricHealthInfo):

        text = health.to_json()

        obj = MetricHealthInfo.from_json(text)

        assert obj == health

    def test_roundtrip_dict(self, health: MetricHealthInfo):

        health.set_healthy("ok")
        health.set_score(88.5)
        health.update_metadata(DUMMY_METADATA)
        health.add_check("cpu", True)

        restored = MetricHealthInfo.from_dict(
            health.to_dict(),
        )

        assert restored == health

    def test_roundtrip_json(self, health: MetricHealthInfo):

        health.set_healthy()
        health.set_score(91)

        restored = MetricHealthInfo.from_json(
            health.to_json(),
        )

        assert restored == health


# ==========================================================
# Part 11. Validation
# ==========================================================

class TestValidation:

    def test_validate(self, health: MetricHealthInfo):

        assert health.validate()

        health.set_score(-10)

        assert not health.validate()

        health.set_score(120)

        assert not health.validate()

        health.set_score(50)

        health._health = "invalid"

        assert not health.validate()

        health._health = MetricHealth.HEALTHY

        health._metadata = "invalid"

        assert not health.validate()

        health._metadata = {}

        health._checks = "invalid"

        assert not health.validate()

    def test_is_valid(self, health: MetricHealthInfo):

        assert health.is_valid()

        health.set_score(150)

        assert not health.is_valid()


# ==========================================================
# Part 12. Snapshot API
# ==========================================================

class TestSnapshot:

    def test_copy(self, health: MetricHealthInfo):

        health.set_healthy()
        health.update_metadata(DUMMY_METADATA)

        cloned = health.copy()

        assert cloned == health
        assert cloned is not health

    def test_deepcopy(self, health: MetricHealthInfo):

        health.update_metadata(DUMMY_METADATA)
        health.add_check("cpu", True)

        cloned = copy.deepcopy(health)

        assert cloned == health
        assert cloned is not health

        cloned.metadata["host"] = "remote"

        assert health.metadata["host"] == "localhost"

    def test_clone(self, health: MetricHealthInfo):

        health.set_critical()
        health.add_check("disk", False)

        cloned = health.clone()

        assert cloned == health
        assert cloned is not health

# ==========================================================
# Part 13. Python Protocols
# ==========================================================

class TestPythonProtocols:

    def test_repr(self, health: MetricHealthInfo):

        text = repr(health)

        assert "MetricHealthInfo" in text

    def test_str(self, health: MetricHealthInfo):

        text = str(health)

        assert isinstance(text, str)

    def test_bool(self, health: MetricHealthInfo):

        health.set_healthy()

        assert bool(health) is True

        health.set_critical()

        assert bool(health) is False

    def test_len(self, health: MetricHealthInfo):

        assert len(health) == 0

        health.add_check("cpu", True)
        health.add_check("disk", False)

        assert len(health) == 2

    def test_eq(self):

        a = MetricHealthInfo()
        b = MetricHealthInfo()

        assert a == b

        b.set_healthy()

        assert a != b

    def test_hash(self):

        obj = MetricHealthInfo()

        assert isinstance(hash(obj), int)

    def test_pickle(self):

        obj = MetricHealthInfo()

        obj.set_healthy()
        obj.add_check("cpu", True)

        restored = pickle.loads(
            pickle.dumps(obj),
        )

        assert restored == obj


# ==========================================================
# Part 14. Diagnostics API
# ==========================================================

class TestDiagnosticsAPI:

    def test_summary(self, health: MetricHealthInfo):

        health.set_healthy()
        health.set_score(97.5)

        summary = health.summary()

        assert isinstance(summary, dict)

        assert "health" in summary
        assert "score" in summary

    def test_diagnostics(self, health: MetricHealthInfo):

        diagnostics = health.diagnostics()

        assert isinstance(diagnostics, dict)

    def test_health_report(self, health: MetricHealthInfo):

        health.set_healthy()
        health.set_score(95)

        health.add_check("cpu", True)
        health.add_check("disk", False)

        report = health.health_report()

        assert report["health"] == MetricHealth.HEALTHY.value
        assert report["score"] == 95

        assert "checks" in report
        assert "passed" in report
        assert "failed" in report

    def test_health_score(self, health: MetricHealthInfo):

        health.set_score(88.5)

        assert health.health_score() == pytest.approx(88.5)

    def test_overall_status(self, health: MetricHealthInfo):

        health.set_healthy()

        assert health.overall_status() == MetricHealth.HEALTHY


# ==========================================================
# Part 15. API Freeze
# ==========================================================

class TestAPIFreeze:

    def test_public_api(self):

        expected = {
            "DEFAULT_HEALTH",
            "DEFAULT_SCORE",
            "DEFAULT_MESSAGE",
            "DEFAULT_VERSION",
            "HealthValue",
            "HealthScore",
            "MetricHealth",
            "MetricHealthInfo",
        }

        assert set(__all__) == expected

    def test_annotations(self):

        assert hasattr(
            MetricHealthInfo,
            "__annotations__",
        )

    def test_slots(self):

        assert hasattr(
            MetricHealthInfo,
            "__slots__",
        )

    def test_signature(self):

        signature = inspect.signature(
            MetricHealthInfo,
        )

        assert "health" in signature.parameters
        assert "score" in signature.parameters
        assert "message" in signature.parameters                        