# ==========================================================
# Part 1. Imports & Fixtures
# ==========================================================

from __future__ import annotations

import threading

from datetime import datetime

import pytest

from scios.runtime.observability.metrics.core.metrics.monitor.status import (
    DEFAULT_MESSAGE,
    DEFAULT_STATUS,
    DEFAULT_VERSION,
    MetricStatus,
    MetricStatusInfo,
    StatusValue,
    __all__,
)

_RLOCK_TYPE = type(threading.RLock())


# ==========================================================
# Part 2. Dummy Data
# ==========================================================


class DummyMetadata(dict):
    pass


@pytest.fixture
def status() -> MetricStatusInfo:

    return MetricStatusInfo()


@pytest.fixture
def custom_status() -> MetricStatusInfo:

    return MetricStatusInfo(
        status=MetricStatus.OK,
        message="healthy",
        version="2.0",
        metadata={
            "service": "metrics",
            "node": "local",
        },
    )


# ==========================================================
# Part 3. Construction
# ==========================================================


class TestConstruction:

    def test_create_default(
        self,
        status: MetricStatusInfo,
    ):

        assert status.status is MetricStatus.UNKNOWN
        assert status.message == DEFAULT_MESSAGE
        assert status.version == DEFAULT_VERSION
        assert status.metadata == {}
        assert isinstance(
            status.timestamp,
            datetime,
        )

    def test_create_custom(
        self,
        custom_status: MetricStatusInfo,
    ):

        assert custom_status.status is MetricStatus.OK
        assert custom_status.message == "healthy"
        assert custom_status.version == "2.0"
        assert custom_status.metadata == {
            "service": "metrics",
            "node": "local",
        }


# ==========================================================
# Part 4. Properties
# ==========================================================


class TestProperties:

    def test_status(
        self,
        status: MetricStatusInfo,
    ):

        assert status.status is MetricStatus.UNKNOWN

    def test_message(
        self,
        status: MetricStatusInfo,
    ):

        assert status.message == DEFAULT_MESSAGE

    def test_timestamp(
        self,
        status: MetricStatusInfo,
    ):

        assert isinstance(
            status.timestamp,
            datetime,
        )

    def test_version(
        self,
        status: MetricStatusInfo,
    ):

        assert status.version == DEFAULT_VERSION

    def test_metadata(
        self,
        status: MetricStatusInfo,
    ):

        assert status.metadata == {}
        assert status.metadata is not status.metadata

    def test_lock(
        self,
        status: MetricStatusInfo,
    ):

        assert isinstance(
            status.lock,
            _RLOCK_TYPE,
        )

# ==========================================================
# Part 5. State API
# ==========================================================


class TestStateAPI:

    def test_set_ok(self, status: MetricStatusInfo):

        status.set_ok("ok")

        assert status.status is MetricStatus.OK
        assert status.message == "ok"

    def test_set_warning(self, status: MetricStatusInfo):

        status.set_warning("warn")

        assert status.status is MetricStatus.WARNING
        assert status.message == "warn"

    def test_set_error(self, status: MetricStatusInfo):

        status.set_error("error")

        assert status.status is MetricStatus.ERROR
        assert status.message == "error"

    def test_set_unknown(self, status: MetricStatusInfo):

        status.set_unknown("unknown")

        assert status.status is MetricStatus.UNKNOWN
        assert status.message == "unknown"

    def test_reset(self, custom_status: MetricStatusInfo):

        custom_status.reset()

        assert custom_status.status is MetricStatus.UNKNOWN
        assert custom_status.message == DEFAULT_MESSAGE
        assert custom_status.metadata == {}


# ==========================================================
# Part 6. Query API
# ==========================================================


class TestQueryAPI:

    def test_is_ok(self, status: MetricStatusInfo):

        status.set_ok()

        assert status.is_ok() is True

    def test_is_warning(self, status: MetricStatusInfo):

        status.set_warning()

        assert status.is_warning() is True

    def test_is_error(self, status: MetricStatusInfo):

        status.set_error()

        assert status.is_error() is True

    def test_is_unknown(self, status: MetricStatusInfo):

        assert status.is_unknown() is True


# ==========================================================
# Part 7. Metadata API
# ==========================================================


class TestMetadataAPI:

    def test_set_metadata(self, status: MetricStatusInfo):

        status.set_metadata("a", 1)

        assert status.metadata["a"] == 1

    def test_update_metadata(self, status: MetricStatusInfo):

        status.update_metadata(
            {
                "a": 1,
                "b": 2,
            }
        )

        assert status.metadata == {
            "a": 1,
            "b": 2,
        }

    def test_clear_metadata(self, status: MetricStatusInfo):

        status.update_metadata(
            {
                "a": 1,
                "b": 2,
            }
        )

        status.clear_metadata()

        assert status.metadata == {}


# ==========================================================
# Part 8. Serialization
# ==========================================================


class TestSerialization:

    def test_to_dict(self, custom_status: MetricStatusInfo):

        data = custom_status.to_dict()

        assert data["status"] == "ok"
        assert data["message"] == "healthy"

    def test_from_dict(self, custom_status: MetricStatusInfo):

        restored = MetricStatusInfo.from_dict(
            custom_status.to_dict()
        )

        assert restored == custom_status

    def test_to_json(self, custom_status: MetricStatusInfo):

        text = custom_status.to_json()

        assert isinstance(text, str)

    def test_from_json(self, custom_status: MetricStatusInfo):

        restored = MetricStatusInfo.from_json(
            custom_status.to_json()
        )

        assert restored == custom_status

    def test_roundtrip_dict(self, custom_status: MetricStatusInfo):

        assert (
            MetricStatusInfo.from_dict(
                custom_status.to_dict()
            )
            == custom_status
        )

    def test_roundtrip_json(self, custom_status: MetricStatusInfo):

        assert (
            MetricStatusInfo.from_json(
                custom_status.to_json()
            )
            == custom_status
        )


# ==========================================================
# Part 9. Validation
# ==========================================================


class TestValidation:

    def test_validate(self, status: MetricStatusInfo):

        status.validate()

    def test_is_valid(self, status: MetricStatusInfo):

        assert status.is_valid() is True

# ==========================================================
# Part 10. Snapshot
# ==========================================================

import copy
import inspect
import pickle


class TestSnapshot:

    def test_copy(
        self,
        custom_status: MetricStatusInfo,
    ):

        cloned = custom_status.copy()

        assert cloned == custom_status
        assert cloned is not custom_status

    def test_deepcopy(
        self,
        custom_status: MetricStatusInfo,
    ):

        cloned = custom_status.deepcopy()

        assert cloned == custom_status
        assert cloned is not custom_status

    def test_clone(
        self,
        custom_status: MetricStatusInfo,
    ):

        cloned = custom_status.clone()

        assert cloned == custom_status
        assert cloned is not custom_status


# ==========================================================
# Part 11. Python Protocols
# ==========================================================


class TestPythonProtocols:

    def test_repr(
        self,
        status: MetricStatusInfo,
    ):

        assert "MetricStatusInfo" in repr(status)

    def test_str(
        self,
        status: MetricStatusInfo,
    ):

        assert str(status) == DEFAULT_STATUS

    def test_bool(
        self,
        status: MetricStatusInfo,
    ):

        assert bool(status) is False

        status.set_ok()

        assert bool(status) is True

    def test_len(
        self,
        status: MetricStatusInfo,
    ):

        assert len(status) == 0

        status.set_metadata(
            "x",
            1,
        )

        assert len(status) == 1

    def test_eq(
        self,
        custom_status: MetricStatusInfo,
    ):

        cloned = custom_status.clone()

        assert cloned == custom_status

    def test_hash(
        self,
        custom_status: MetricStatusInfo,
    ):

        assert isinstance(
            hash(custom_status),
            int,
        )

    def test_pickle(
        self,
        custom_status: MetricStatusInfo,
    ):

        restored = pickle.loads(
            pickle.dumps(custom_status),
        )

        assert restored == custom_status


# ==========================================================
# Part 12. API Freeze
# ==========================================================


class TestAPIFreeze:

    def test_public_api(self):

        expected = {
            "DEFAULT_STATUS",
            "DEFAULT_MESSAGE",
            "DEFAULT_VERSION",
            "StatusValue",
            "MetricStatus",
            "MetricStatusInfo",
        }

        assert set(__all__) == expected

    def test_annotations(self):

        assert MetricStatusInfo.__init__.__annotations__

    def test_slots(self):

        assert hasattr(
            MetricStatusInfo,
            "__slots__",
        )

    def test_signature(self):

        sig = inspect.signature(
            MetricStatusInfo.__init__,
        )

        assert "status" in sig.parameters
        assert "message" in sig.parameters
        assert "timestamp" in sig.parameters
        assert "version" in sig.parameters
        assert "metadata" in sig.parameters                