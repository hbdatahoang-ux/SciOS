# ==========================================================
# Part 1. Imports
# ==========================================================

from __future__ import annotations

from threading import RLock

import json
import inspect
import pickle

from scios.runtime.observability.metrics.core.metrics.serialization import (
    MetricSerializer,
)


# ==========================================================
# TestConstruction
# ==========================================================


class TestConstruction:

    def test_create_default(self):

        serializer = MetricSerializer()

        assert isinstance(serializer, MetricSerializer)

    def test_version(self):

        serializer = MetricSerializer()

        assert serializer.version == MetricSerializer.VERSION

    def test_lock(self):

        serializer = MetricSerializer()

        assert serializer.lock is not None


# ==========================================================
# TestHelpers
# ==========================================================


class TestHelpers:

    def test_base(self):

        serializer = MetricSerializer()

        data = serializer._base()

        assert isinstance(data, dict)

        assert data["serializer"] == "MetricSerializer"

        assert data["version"] == MetricSerializer.VERSION

# ==========================================================
# TestDictSerialization
# ==========================================================


class DummyMetric:

    def to_dict(self):
        return {
            "name": "cpu",
            "value": 1,
        }

    def snapshot(self):
        return {
            "snapshot": True,
        }


class TestDictSerialization:

    def test_serialize_metric(self):

        serializer = MetricSerializer()

        metric = DummyMetric()

        data = serializer.serialize_metric(metric)

        assert data["serializer"] == "MetricSerializer"
        assert data["version"] == MetricSerializer.VERSION
        assert data["data"]["name"] == "cpu"

    def test_serialize_dict(self):

        serializer = MetricSerializer()

        payload = {
            "a": 1,
            "b": 2,
        }

        data = serializer.serialize(payload)

        assert data["data"] == payload

    def test_serialize_snapshot(self):

        serializer = MetricSerializer()

        metric = DummyMetric()

        data = serializer.serialize(metric)

        assert data["data"]["name"] == "cpu"

    def test_to_dict(self):

        serializer = MetricSerializer()

        metric = DummyMetric()

        data = serializer.to_dict(metric)

        assert isinstance(data, dict)
        assert "serializer" in data
        assert "version" in data
        assert "data" in data

    def test_serialize_many(self):

        serializer = MetricSerializer()

        metrics = [
            DummyMetric(),
            DummyMetric(),
        ]

        data = serializer.serialize_many(metrics)

        assert data["count"] == 2
        assert len(data["items"]) == 2
        assert data["serializer"] == "MetricSerializer"


# ==========================================================
# TestJsonSerialization
# ==========================================================


class TestJsonSerialization:

    def test_to_json(self):

        serializer = MetricSerializer()

        metric = DummyMetric()

        text = serializer.to_json(metric)

        assert isinstance(text, str)

        data = json.loads(text)

        assert data["serializer"] == "MetricSerializer"
        assert data["version"] == MetricSerializer.VERSION

    def test_from_json(self):

        serializer = MetricSerializer()

        metric = DummyMetric()

        text = serializer.to_json(metric)

        restored = serializer.from_json(text)

        assert isinstance(restored, dict)
        assert restored["name"] == "cpu"

# ==========================================================
# TestFileSerialization
# ==========================================================


class TestFileSerialization:

    def test_save_json(self, tmp_path):

        serializer = MetricSerializer()

        metric = DummyMetric()

        path = tmp_path / "metric.json"

        serializer.save_json(
            metric,
            path,
        )

        assert path.exists()

    def test_load_json(self, tmp_path):

        serializer = MetricSerializer()

        metric = DummyMetric()

        path = tmp_path / "metric.json"

        serializer.save_json(
            metric,
            path,
        )

        data = serializer.load_json(path)

        assert isinstance(data, dict)
        assert data["name"] == "cpu"


# ==========================================================
# TestSnapshot
# ==========================================================


class DummyRestorable:

    def __init__(self):

        self.state = {}

    def snapshot(self):

        return {
            "value": 123,
        }

    def restore(
        self,
        state,
    ):

        self.state = state


class TestSnapshot:

    def test_create_snapshot(self):

        serializer = MetricSerializer()

        obj = DummyRestorable()

        snapshot = serializer.create_snapshot(obj)

        assert snapshot["serializer"] == "MetricSerializer"
        assert snapshot["type"] == "DummyRestorable"
        assert snapshot["snapshot"]["value"] == 123

    def test_snapshot_data(self):

        serializer = MetricSerializer()

        snapshot = serializer.create_snapshot(
            DummyRestorable()
        )

        data = serializer.snapshot_data(snapshot)

        assert data["value"] == 123

    def test_clone_snapshot(self):

        serializer = MetricSerializer()

        snapshot = serializer.create_snapshot(
            DummyRestorable()
        )

        clone = serializer.clone_snapshot(snapshot)

        assert clone == snapshot
        assert clone is not snapshot

    def test_restore_snapshot(self):

        serializer = MetricSerializer()

        obj = DummyRestorable()

        snapshot = serializer.create_snapshot(obj)

        restored = DummyRestorable()

        serializer.restore_snapshot(
            snapshot,
            restored,
        )

        assert restored.state["value"] == 123

# ==========================================================
# TestValidation
# ==========================================================


class TestValidation:

    def test_validate(self):

        serializer = MetricSerializer()

        assert serializer.validate() is True

    def test_is_valid(self):

        serializer = MetricSerializer()

        assert serializer.is_valid() is True


# ==========================================================
# TestPythonProtocols
# ==========================================================


class TestPythonProtocols:

    def test_repr(self):

        serializer = MetricSerializer()

        text = repr(serializer)

        assert "MetricSerializer" in text

    def test_str(self):

        serializer = MetricSerializer()

        text = str(serializer)

        assert "MetricSerializer" in text


# ==========================================================
# TestAPIFreeze
# ==========================================================


class TestAPIFreeze:

    def test_public_api(self):

        assert MetricSerializer.__name__ == "MetricSerializer"

    def test_annotations(self):

        assert isinstance(
            MetricSerializer.__annotations__,
            dict,
        )

    def test_signature(self):

        sig = inspect.signature(
            MetricSerializer.__init__,
        )

        assert "self" in sig.parameters

    def test_pickle(self):

        serializer = MetricSerializer()

        restored = pickle.loads(
            pickle.dumps(serializer)
        )

        assert isinstance(
            restored,
            MetricSerializer,
        )

        assert (
            restored.version
            == serializer.version
        )                        