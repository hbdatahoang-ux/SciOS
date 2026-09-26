from __future__ import annotations

import copy
import inspect
import json
import pickle
import threading
from threading import RLock
from typing import Any

import pytest

from scios.runtime.observability.metrics.core.metrics.monitor.alert import (
    DEFAULT_ALERT,
    DEFAULT_LEVEL,
    DEFAULT_MESSAGE,
    DEFAULT_VERSION,
    AlertLevel,
    AlertValue,
    MetricAlert,
    MetricAlertInfo,
    __all__,
)

_RLOCK_TYPE = type(RLock())


# ==========================================================
# Part 1. Fixtures
# ==========================================================

@pytest.fixture
def alert() -> MetricAlertInfo:
    return MetricAlertInfo()


# ==========================================================
# Part 2. Dummy Data
# ==========================================================

DUMMY_METADATA = {
    "host": "localhost",
    "service": "metrics",
}


# ==========================================================
# Part 3. Construction
# ==========================================================

class TestConstruction:

    def test_create_default(self):

        a = MetricAlertInfo()

        assert a.alert == MetricAlert.NONE
        assert a.level == DEFAULT_LEVEL
        assert a.message == DEFAULT_MESSAGE
        assert a.source == ""
        assert a.version == DEFAULT_VERSION
        assert a.metadata == {}
        assert a.active is False
        assert a.acknowledged is False
        assert a.resolved is False

    def test_create_custom(self):

        a = MetricAlertInfo(
            alert=MetricAlert.CRITICAL,
            level=5,
            message="failure",
            source="collector",
            version="2.0",
            metadata=DUMMY_METADATA,
            active=True,
            acknowledged=True,
            resolved=False,
        )

        assert a.alert == MetricAlert.CRITICAL
        assert a.level == 5
        assert a.message == "failure"
        assert a.source == "collector"
        assert a.version == "2.0"
        assert a.metadata == DUMMY_METADATA
        assert a.active is True
        assert a.acknowledged is True
        assert a.resolved is False


# ==========================================================
# Part 4. Properties
# ==========================================================

class TestProperties:

    def test_alert(self, alert: MetricAlertInfo):

        assert alert.alert == MetricAlert.NONE

    def test_level(self, alert: MetricAlertInfo):

        assert alert.level == DEFAULT_LEVEL

    def test_message(self, alert: MetricAlertInfo):

        assert alert.message == DEFAULT_MESSAGE

    def test_source(self, alert: MetricAlertInfo):

        assert alert.source == ""

    def test_timestamp(self, alert: MetricAlertInfo):

        assert alert.timestamp is not None

    def test_version(self, alert: MetricAlertInfo):

        assert alert.version == DEFAULT_VERSION

    def test_metadata(self, alert: MetricAlertInfo):

        assert isinstance(alert.lock, (threading._RLock, _RLOCK_TYPE))
        assert alert.metadata == {}

    def test_active(self, alert: MetricAlertInfo):

        assert alert.active is False

    def test_acknowledged(self, alert: MetricAlertInfo):

        assert alert.acknowledged is False

    def test_resolved(self, alert: MetricAlertInfo):

        assert alert.resolved is False

    def test_lock(self, alert: MetricAlertInfo):

        assert hasattr(alert.lock, "acquire")
        assert hasattr(alert.lock, "release")


# ==========================================================
# Part 5. Alert State API
# ==========================================================

class TestAlertStateAPI:

    def test_trigger(self, alert: MetricAlertInfo):

        alert.trigger("collector", "failure")

        assert alert.active
        assert alert.message == "failure"
        assert alert.source == "collector"

    def test_clear(self, alert: MetricAlertInfo):

        alert.trigger("collector", "failure")
        alert.clear()

        assert not alert.active

    def test_acknowledge(self, alert: MetricAlertInfo):

        alert.trigger("collector", "failure")
        alert.acknowledge()

        assert alert.acknowledged

    def test_resolve(self, alert: MetricAlertInfo):

        alert.trigger("collector", "failure")
        alert.resolve()

        assert alert.resolved
        assert not alert.active

    def test_reopen(self, alert: MetricAlertInfo):

        alert.trigger("collector", "failure")
        alert.resolve()
        alert.reopen()

        assert alert.active
        assert not alert.resolved

    def test_reset(self, alert: MetricAlertInfo):

        alert.trigger("collector", "failure")
        alert.acknowledge()
        alert.resolve()
        alert.reset()

        assert alert.alert == MetricAlert.NONE
        assert alert.level == DEFAULT_LEVEL
        assert alert.message == DEFAULT_MESSAGE
        assert alert.source == ""
        assert not alert.active
        assert not alert.acknowledged
        assert not alert.resolved


# ==========================================================
# Part 6. Alert Level API
# ==========================================================

class TestAlertLevelAPI:

    def test_set_info(self, alert: MetricAlertInfo):

        alert.set_info()

        assert alert.alert == MetricAlert.INFO

    def test_set_warning(self, alert: MetricAlertInfo):

        alert.set_warning()

        assert alert.alert == MetricAlert.WARNING

    def test_set_error(self, alert: MetricAlertInfo):

        alert.set_error()

        assert alert.alert == MetricAlert.ERROR

    def test_set_critical(self, alert: MetricAlertInfo):

        alert.set_critical()

        assert alert.alert == MetricAlert.CRITICAL

    def test_set_none(self, alert: MetricAlertInfo):

        alert.set_warning()
        alert.set_none()

        assert alert.alert == MetricAlert.NONE


# ==========================================================
# Part 7. Query API
# ==========================================================

class TestQueryAPI:

    def test_is_active(self, alert: MetricAlertInfo):

        assert not alert.is_active()

        alert.trigger("collector", "failure")

        assert alert.is_active()

    def test_is_acknowledged(self, alert: MetricAlertInfo):

        assert not alert.is_acknowledged()

        alert.trigger("collector", "failure")
        alert.acknowledge()

        assert alert.is_acknowledged()

    def test_is_resolved(self, alert: MetricAlertInfo):

        assert not alert.is_resolved()

        alert.trigger("collector", "failure")
        alert.resolve()

        assert alert.is_resolved()

    def test_is_info(self, alert: MetricAlertInfo):

        alert.set_info()

        assert alert.is_info()

    def test_is_warning(self, alert: MetricAlertInfo):

        alert.set_warning()

        assert alert.is_warning()

    def test_is_error(self, alert: MetricAlertInfo):

        alert.set_error()

        assert alert.is_error()

    def test_is_critical(self, alert: MetricAlertInfo):

        alert.set_critical()

        assert alert.is_critical()


# ==========================================================
# Part 8. Metadata API
# ==========================================================

class TestMetadataAPI:

    def test_set_metadata(self, alert: MetricAlertInfo):

        alert.set_metadata("host", "localhost")

        assert alert.metadata["host"] == "localhost"

    def test_update_metadata(self, alert: MetricAlertInfo):

        alert.update_metadata(DUMMY_METADATA)

        assert alert.metadata == DUMMY_METADATA

    def test_clear_metadata(self, alert: MetricAlertInfo):

        alert.update_metadata(DUMMY_METADATA)
        alert.clear_metadata()

        assert alert.metadata == {}

# ==========================================================
# Part 9. Serialization
# ==========================================================

class TestSerialization:

    def test_to_dict(self, alert: MetricAlertInfo):

        data = alert.to_dict()

        assert isinstance(data, dict)
        assert data["alert"] == alert.alert.value

    def test_from_dict(self, alert: MetricAlertInfo):

        data = alert.to_dict()

        restored = MetricAlertInfo.from_dict(data)

        assert restored == alert

    def test_to_json(self, alert: MetricAlertInfo):

        text = alert.to_json()

        assert isinstance(text, str)

        obj = json.loads(text)

        assert obj["alert"] == alert.alert.value

    def test_from_json(self, alert: MetricAlertInfo):

        restored = MetricAlertInfo.from_json(alert.to_json())

        assert restored == alert

    def test_roundtrip_dict(self, alert: MetricAlertInfo):

        restored = MetricAlertInfo.from_dict(alert.to_dict())

        assert restored.to_dict() == alert.to_dict()

    def test_roundtrip_json(self, alert: MetricAlertInfo):

        restored = MetricAlertInfo.from_json(alert.to_json())

        assert restored.to_json() == alert.to_json()


# ==========================================================
# Part 10. Validation
# ==========================================================

class TestValidation:

    def test_validate(self, alert: MetricAlertInfo):

        assert alert.validate()

        alert._alert = "bad"
        assert not alert.validate()

        alert._alert = MetricAlert.NONE
        alert._level = "bad"
        assert not alert.validate()

        alert._level = DEFAULT_LEVEL
        alert._source = 123
        assert not alert.validate()

        alert._source = ""
        alert._metadata = []
        assert not alert.validate()

    def test_is_valid(self, alert: MetricAlertInfo):

        assert alert.is_valid()

        alert._alert = "invalid"

        assert not alert.is_valid()


# ==========================================================
# Part 11. Snapshot API
# ==========================================================

class TestSnapshot:

    def test_copy(self, alert: MetricAlertInfo):

        clone = alert.copy()

        assert clone == alert
        assert clone is not alert

    def test_deepcopy(self, alert: MetricAlertInfo):

        clone = copy.deepcopy(alert)

        assert clone == alert
        assert clone.metadata is not alert.metadata

    def test_clone(self, alert: MetricAlertInfo):

        clone = alert.clone()

        assert clone == alert
        assert clone is not alert


# ==========================================================
# Part 12. Python Protocols
# ==========================================================

class TestPythonProtocols:

    def test_repr(self, alert: MetricAlertInfo):

        assert "MetricAlertInfo" in repr(alert)

    def test_str(self, alert: MetricAlertInfo):

        assert isinstance(str(alert), str)

    def test_bool(self, alert: MetricAlertInfo):

        assert not bool(alert)

        alert.trigger("collector", "failure")

        assert bool(alert)

    def test_len(self, alert: MetricAlertInfo):

        assert len(alert) == 0

        alert.update_metadata(DUMMY_METADATA)

        assert len(alert) == len(DUMMY_METADATA)

    def test_eq(self):

        a = MetricAlertInfo()
        b = MetricAlertInfo()

        assert a == b

    def test_hash(self):

        assert isinstance(hash(MetricAlertInfo()), int)

    def test_pickle(self, alert: MetricAlertInfo):

        restored = pickle.loads(pickle.dumps(alert))

        assert restored == alert


# ==========================================================
# Part 13. Diagnostics API
# ==========================================================

class TestDiagnosticsAPI:

    def test_summary(self, alert: MetricAlertInfo):

        data = alert.summary()

        assert isinstance(data, dict)

    def test_diagnostics(self, alert: MetricAlertInfo):

        data = alert.diagnostics()

        assert isinstance(data, dict)

    def test_alert_report(self, alert: MetricAlertInfo):

        report = alert.alert_report()

        assert isinstance(report, dict)

        assert "alert" in report
        assert "active" in report

    def test_overall_status(self, alert: MetricAlertInfo):

        status = alert.overall_status()

        assert isinstance(status, str)


# ==========================================================
# Part 14. API Freeze
# ==========================================================

class TestAPIFreeze:

    def test_public_api(self):

        expected = {
            "DEFAULT_ALERT",
            "DEFAULT_LEVEL",
            "DEFAULT_MESSAGE",
            "DEFAULT_VERSION",
            "AlertValue",
            "AlertLevel",
            "MetricAlert",
            "MetricAlertInfo",
        }

        assert set(__all__) == expected

    def test_annotations(self):

        assert MetricAlertInfo.__annotations__

    def test_slots(self):

        assert hasattr(MetricAlertInfo, "__slots__")

    def test_signature(self):

        sig = inspect.signature(MetricAlertInfo)

        assert "alert" in sig.parameters                