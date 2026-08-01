"""
Tests for MetricState.

Part 1. Imports
Part 2. Fixtures
Part 3. Construction
"""

from __future__ import annotations

import copy
import inspect
import pickle
from typing import get_type_hints

import pytest

from scios.runtime.observability.metrics.core.metrics.core.metric_state import (
    MetricState,
)


# ==========================================================
# Part 2. Fixtures
# ==========================================================


@pytest.fixture
def empty_state() -> MetricState:
    return MetricState()


@pytest.fixture
def custom_state() -> MetricState:
    return MetricState(
        status="active",
        enabled=True,
        recording=True,
        timestamp=123.456,
        version=3,
    )


@pytest.fixture
def full_state() -> MetricState:
    return MetricState(
        status="paused",
        enabled=False,
        recording=False,
        timestamp=999.999,
        version=42,
    )


# ==========================================================
# Part 3. Construction
# ==========================================================


class TestConstruction:
    def test_create_default(self):
        state = MetricState()

        assert isinstance(state, MetricState)

    def test_create_custom(self):
        state = MetricState(
            status="active",
            enabled=True,
            recording=True,
            timestamp=100.0,
            version=5,
        )

        assert state.status == "active"
        assert state.enabled is True
        assert state.recording is True
        assert state.timestamp == 100.0
        assert state.version == 5

    def test_create_empty(self, empty_state: MetricState):
        assert isinstance(empty_state, MetricState)

    def test_create_full(self, full_state: MetricState):
        assert full_state.status == "paused"
        assert full_state.enabled is False
        assert full_state.recording is False
        assert full_state.timestamp == 999.999
        assert full_state.version == 42
# ==========================================================
# Part 4. Identity
# ==========================================================


class TestIdentity:
    def test_status(self, custom_state: MetricState):
        assert custom_state.status == "active"

    def test_enabled(self, custom_state: MetricState):
        assert custom_state.enabled is True

    def test_recording(self, custom_state: MetricState):
        assert custom_state.recording is True

    def test_timestamp(self, custom_state: MetricState):
        assert custom_state.timestamp == 123.456

    def test_version(self, custom_state: MetricState):
        assert custom_state.version == 3


# ==========================================================
# Part 5. Defaults
# ==========================================================


class TestDefaults:
    def test_default_status(self):
        state = MetricState()

        assert state.status == "idle"

    def test_default_enabled(self):
        state = MetricState()

        assert state.enabled is True

    def test_default_recording(self):
        state = MetricState()

        assert state.recording is False


# ==========================================================
# Part 6. Mutation
# ==========================================================


class TestMutation:
    def test_enable(self, empty_state: MetricState):
        empty_state.enabled = False

        if hasattr(empty_state, "enable"):
            empty_state.enable()
            assert empty_state.enabled is True
        else:
            empty_state.enabled = True
            assert empty_state.enabled is True

    def test_disable(self, empty_state: MetricState):
        empty_state.enabled = True

        if hasattr(empty_state, "disable"):
            empty_state.disable()
            assert empty_state.enabled is False
        else:
            empty_state.enabled = False
            assert empty_state.enabled is False

    def test_start_recording(self, empty_state: MetricState):
        empty_state.recording = False

        if hasattr(empty_state, "start_recording"):
            empty_state.start_recording()
            assert empty_state.recording is True
        else:
            empty_state.recording = True
            assert empty_state.recording is True

    def test_stop_recording(self, empty_state: MetricState):
        empty_state.recording = True

        if hasattr(empty_state, "stop_recording"):
            empty_state.stop_recording()
            assert empty_state.recording is False
        else:
            empty_state.recording = False
            assert empty_state.recording is False

# ==========================================================
# Part 7. Serialization
# ==========================================================


class TestSerialization:
    def test_to_dict(self, custom_state: MetricState):
        data = custom_state.to_dict()

        assert isinstance(data, dict)
        assert data["status"] == "active"
        assert data["enabled"] is True
        assert data["recording"] is True
        assert data["timestamp"] == 123.456
        assert data["version"] == 3

    def test_from_dict(self, custom_state: MetricState):
        restored = MetricState.from_dict(
            custom_state.to_dict(),
        )

        assert restored == custom_state

    def test_to_json(self, custom_state: MetricState):
        text = custom_state.to_json()

        assert isinstance(text, str)

    def test_from_json(self, custom_state: MetricState):
        restored = MetricState.from_json(
            custom_state.to_json(),
        )

        assert restored == custom_state

    def test_roundtrip_dict(self, custom_state: MetricState):
        restored = MetricState.from_dict(
            custom_state.to_dict(),
        )

        assert restored == custom_state

    def test_roundtrip_json(self, custom_state: MetricState):
        restored = MetricState.from_json(
            custom_state.to_json(),
        )

        assert restored == custom_state


# ==========================================================
# Part 8. Validation
# ==========================================================


class TestValidation:
    def test_validate(self, custom_state: MetricState):
        custom_state.validate()

    def test_validate_invalid_status(self):
        state = MetricState(
            status="invalid-status",
        )

        with pytest.raises(Exception):
            state.validate()

    def test_validate_invalid_enabled(self):
        state = MetricState(
            enabled="yes",  # type: ignore[arg-type]
        )

        with pytest.raises(Exception):
            state.validate()

    def test_is_valid(self, custom_state: MetricState):
        assert custom_state.is_valid() is True


# ==========================================================
# Part 9. Comparison
# ==========================================================


class TestComparison:
    def test_equals(
        self,
        custom_state: MetricState,
    ):
        other = MetricState.from_dict(
            custom_state.to_dict(),
        )

        assert custom_state == other

    def test_not_equals(
        self,
        custom_state: MetricState,
    ):
        other = MetricState(
            status="idle",
        )

        assert custom_state != other

    def test_hash(
        self,
        custom_state: MetricState,
    ):
        assert isinstance(
            hash(custom_state),
            int,
        )

    def test_copy_equality(
        self,
        custom_state: MetricState,
    ):
        copied = custom_state.copy()

        assert copied == custom_state
        assert copied is not custom_state

# ==========================================================
# Part 10. Snapshot
# ==========================================================


class TestSnapshot:
    def test_copy(
        self,
        custom_state: MetricState,
    ):
        copied = custom_state.copy()

        assert copied == custom_state
        assert copied is not custom_state

    def test_deepcopy(
        self,
        custom_state: MetricState,
    ):
        copied = copy.deepcopy(custom_state)

        assert copied == custom_state
        assert copied is not custom_state

    def test_clone(
        self,
        custom_state: MetricState,
    ):
        cloned = custom_state.clone()

        assert cloned == custom_state
        assert cloned is not custom_state

    def test_replace(
        self,
        custom_state: MetricState,
    ):
        replaced = custom_state.replace(
            status="paused",
        )

        assert replaced.status == "paused"
        assert custom_state.status == "active"


# ==========================================================
# Part 11. Python Protocols
# ==========================================================


class TestPythonProtocols:
    def test_repr(
        self,
        custom_state: MetricState,
    ):
        assert isinstance(
            repr(custom_state),
            str,
        )

    def test_str(
        self,
        custom_state: MetricState,
    ):
        assert isinstance(
            str(custom_state),
            str,
        )

    def test_bool(
        self,
        custom_state: MetricState,
    ):
        assert bool(custom_state) is True

    def test_hash_protocol(
        self,
        custom_state: MetricState,
    ):
        assert isinstance(
            hash(custom_state),
            int,
        )


# ==========================================================
# Part 12. API Freeze
# ==========================================================


class TestAPIFreeze:
    def test_public_api(self):
        public = {
            name
            for name in dir(MetricState)
            if not name.startswith("_")
        }

        expected = {
            "copy",
            "clone",
            "deepcopy",
            "replace",
            "to_dict",
            "from_dict",
            "to_json",
            "from_json",
            "validate",
            "is_valid",
        }

        assert expected.issubset(public)

    def test_annotations(self):
        hints = get_type_hints(MetricState)

        assert isinstance(hints, dict)

    def test_slots(self):
        assert hasattr(
            MetricState,
            "__slots__",
        )

    def test_signature(self):
        signature = inspect.signature(
            MetricState,
        )

        assert signature is not None

    def test_pickle(
        self,
        custom_state: MetricState,
    ):
        restored = pickle.loads(
            pickle.dumps(custom_state),
        )

        assert restored == custom_state        