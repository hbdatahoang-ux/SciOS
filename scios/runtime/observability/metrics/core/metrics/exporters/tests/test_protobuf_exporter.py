# ==========================================================
# Part 1. Imports & Fixtures
# ==========================================================

import copy
import inspect
import pickle
import threading
from pathlib import Path

import pytest

from scios.runtime.observability.metrics.core.metrics.exporters.protobuf_exporter import (
    DEFAULT_DETERMINISTIC,
    DEFAULT_ENCODING,
    DEFAULT_PRESERVE_PROTO_FIELD_NAME,
    DEFAULT_VERSION,
    ProtobufExporter,
    __all__,
)

from scios.runtime.observability.metrics.core.metrics.serialization.metric_serializer import (
    MetricSerializer,
)

_RLOCK_TYPE = type(threading.RLock())

# ==========================================================
# Part 2. DummyMetric
# ==========================================================


class DummyMetric:

    def to_dict(self):

        return {
            "name": "cpu",
            "value": 0.5,
            "labels": {
                "host": "localhost",
            },
        }

# ==========================================================
# Part 3. TestConstruction
# ==========================================================


class TestConstruction:

    def test_create_default(self):

        exporter = ProtobufExporter()

        assert isinstance(
            exporter,
            ProtobufExporter,
        )

    def test_version(self):

        exporter = ProtobufExporter()

        assert exporter.version == DEFAULT_VERSION

    def test_encoding(self):

        exporter = ProtobufExporter()

        assert exporter.encoding == DEFAULT_ENCODING

    def test_deterministic(self):

        exporter = ProtobufExporter()

        assert (
            exporter.deterministic
            == DEFAULT_DETERMINISTIC
        )

    def test_preserve_proto_field_name(self):

        exporter = ProtobufExporter()

        assert (
            exporter.preserve_proto_field_name
            == DEFAULT_PRESERVE_PROTO_FIELD_NAME
        )

    def test_serializer(self):

        exporter = ProtobufExporter()

        assert isinstance(
            exporter.serializer,
            MetricSerializer,
        )

    def test_lock(self):

        exporter = ProtobufExporter()

        assert isinstance(
            exporter.lock,
            _RLOCK_TYPE,
        )

# ==========================================================
# Part 4. TestHelpers
# ==========================================================


class TestHelpers:

    def test_metadata(self):

        exporter = ProtobufExporter()

        meta = exporter._metadata()

        assert meta["version"] == DEFAULT_VERSION

    def test_normalize_metric(self):

        exporter = ProtobufExporter()

        metric = exporter._normalize(
            DummyMetric(),
        )

        assert metric["name"] == "cpu"

    def test_normalize_dict(self):

        exporter = ProtobufExporter()

        metric = exporter._normalize(
            {"x": 1},
        )

        assert metric["x"] == 1

    def test_dumps_kwargs(self):

        exporter = ProtobufExporter()

        kwargs = exporter._dumps_kwargs()

        assert kwargs["deterministic"] is True

    def test_export_payload(self):

        exporter = ProtobufExporter()

        payload = exporter._export_payload(
            DummyMetric(),
        )

        assert payload["data"]["name"] == "cpu"

    def test_export_many_payload(self):

        exporter = ProtobufExporter()

        payload = exporter._export_many_payload(
            [
                DummyMetric(),
                DummyMetric(),
            ]
        )

        assert payload["count"] == 2
        assert len(payload["items"]) == 2


# ==========================================================
# Part 5. TestExportApi
# ==========================================================


class TestExportApi:

    def test_export(self):

        exporter = ProtobufExporter()

        payload = exporter.export(
            DummyMetric(),
        )

        assert payload["data"]["name"] == "cpu"

    def test_export_many(self):

        exporter = ProtobufExporter()

        payload = exporter.export_many(
            [
                DummyMetric(),
                DummyMetric(),
            ]
        )

        assert payload["count"] == 2

    def test_export_protobuf(self):

        exporter = ProtobufExporter()

        data = exporter.export_protobuf(
            DummyMetric(),
        )

        assert isinstance(
            data,
            bytes,
        )

    def test_export_many_protobuf(self):

        exporter = ProtobufExporter()

        data = exporter.export_many_protobuf(
            [
                DummyMetric(),
                DummyMetric(),
            ]
        )

        assert isinstance(
            data,
            bytes,
        )


# ==========================================================
# Part 6. TestFileExport
# ==========================================================


class TestFileExport:

    def test_export_file(
        self,
        tmp_path: Path,
    ):

        exporter = ProtobufExporter()

        path = exporter.export_file(
            DummyMetric(),
            tmp_path / "metric.pb",
        )

        assert path.exists()

    def test_export_many_file(
        self,
        tmp_path: Path,
    ):

        exporter = ProtobufExporter()

        path = exporter.export_many_file(
            [
                DummyMetric(),
                DummyMetric(),
            ],
            tmp_path / "metrics.pb",
        )

        assert path.exists()

    def test_load_file(
        self,
        tmp_path: Path,
    ):

        exporter = ProtobufExporter()

        path = exporter.export_file(
            DummyMetric(),
            tmp_path / "metric.pb",
        )

        data = exporter.load_file(path)

        assert isinstance(
            data,
            bytes,
        )


# ==========================================================
# Part 7. TestValidation
# ==========================================================


class TestValidation:

    def test_validate(self):

        exporter = ProtobufExporter()

        assert exporter.validate(
            DummyMetric(),
        )

    def test_is_valid(self):

        exporter = ProtobufExporter()

        assert exporter.is_valid(
            DummyMetric(),
        )


# ==========================================================
# Part 8. TestPythonProtocols
# ==========================================================


class TestPythonProtocols:

    def test_repr(self):

        exporter = ProtobufExporter()

        assert "ProtobufExporter" in repr(exporter)

    def test_str(self):

        exporter = ProtobufExporter()

        assert "ProtobufExporter" in str(exporter)

    def test_len(self):

        exporter = ProtobufExporter()

        assert len(exporter) == 4

    def test_bool(self):

        exporter = ProtobufExporter()

        assert exporter

    def test_copy(self):

        exporter = ProtobufExporter()

        copied = copy.copy(exporter)

        assert copied == exporter

    def test_deepcopy(self):

        exporter = ProtobufExporter()

        copied = copy.deepcopy(exporter)

        assert copied == exporter

    def test_eq(self):

        assert (
            ProtobufExporter()
            == ProtobufExporter()
        )

    def test_hash(self):

        hash(
            ProtobufExporter(),
        )


# ==========================================================
# Part 9. TestAPIFreeze
# ==========================================================


class TestAPIFreeze:

    def test_public_api(self):

        assert "ProtobufExporter" in __all__

    def test_annotations(self):

        assert inspect.isclass(
            ProtobufExporter,
        )

    def test_slots(self):

        assert hasattr(
            ProtobufExporter,
            "__slots__",
        )

    def test_signature(self):

        inspect.signature(
            ProtobufExporter,
        )

    def test_pickle(self):

        exporter = ProtobufExporter()

        restored = pickle.loads(
            pickle.dumps(exporter),
        )

        assert restored == exporter                