import copy
import inspect
import pickle
import threading
from pathlib import Path

import pytest

from scios.runtime.observability.metrics.core.metrics.exporters.msgpack_exporter import (
    DEFAULT_ENCODING,
    DEFAULT_STRICT_TYPES,
    DEFAULT_USE_BIN_TYPE,
    DEFAULT_VERSION,
    MsgPackExporter,
    __all__,
)

from scios.runtime.observability.metrics.core.metrics.serialization.metric_serializer import (
    MetricSerializer,
)

_RLOCK_TYPE = type(threading.RLock())


@pytest.fixture()
def exporter() -> MsgPackExporter:
    return MsgPackExporter()

class DummyMetric:
    def __init__(self) -> None:
        self.name = "cpu"
        self.value = 0.5
        self.labels = {
            "host": "localhost",
        }

    def to_dict(self):
        return {
            "name": self.name,
            "value": self.value,
            "labels": self.labels,
        }

class TestConstruction:

    def test_create_default(self):
        exporter = MsgPackExporter()
        assert exporter is not None

    def test_version(self):
        exporter = MsgPackExporter()
        assert exporter.version == DEFAULT_VERSION

    def test_encoding(self):
        exporter = MsgPackExporter()
        assert exporter.encoding == DEFAULT_ENCODING

    def test_use_bin_type(self):
        exporter = MsgPackExporter()
        assert exporter.use_bin_type == DEFAULT_USE_BIN_TYPE

    def test_strict_types(self):
        exporter = MsgPackExporter()
        assert exporter.strict_types == DEFAULT_STRICT_TYPES

    def test_serializer(self):
        exporter = MsgPackExporter()
        assert isinstance(
            exporter.serializer,
            MetricSerializer,
        )

    def test_lock(self):
        exporter = MsgPackExporter()
        assert isinstance(
            exporter.lock,
            _RLOCK_TYPE,
        )

# ==========================================================
# Part 4. TestHelpers
# ==========================================================

class TestHelpers:

    def test_metadata(self):

        exporter = MsgPackExporter()

        meta = exporter._metadata()

        assert meta["exporter"] == "MsgPackExporter"
        assert meta["version"] == DEFAULT_VERSION

    def test_normalize_metric(self):

        exporter = MsgPackExporter()

        data = exporter._normalize(
            DummyMetric(),
        )

        assert data["name"] == "cpu"

    def test_normalize_dict(self):

        exporter = MsgPackExporter()

        data = exporter._normalize(
            {"a": 1},
        )

        assert data["a"] == 1

    def test_packer_kwargs(self):

        exporter = MsgPackExporter()

        kwargs = exporter._packer_kwargs()

        assert kwargs["use_bin_type"] == DEFAULT_USE_BIN_TYPE
        assert kwargs["strict_types"] == DEFAULT_STRICT_TYPES

    def test_export_payload(self):

        exporter = MsgPackExporter()

        payload = exporter._export_payload(
            DummyMetric(),
        )

        assert payload["data"]["name"] == "cpu"

    def test_export_many_payload(self):

        exporter = MsgPackExporter()

        payload = exporter._export_many_payload(
            [
                DummyMetric(),
                DummyMetric(),
            ]
        )

        assert payload["count"] == 2
        assert len(payload["items"]) == 2
        assert payload["items"][0]["name"] == "cpu"


# ==========================================================
# Part 5. TestExportApi
# ==========================================================

class TestExportApi:

    def test_export(self):

        exporter = MsgPackExporter()

        payload = exporter.export(
            DummyMetric(),
        )

        assert payload["data"]["name"] == "cpu"

    def test_export_many(self):

        exporter = MsgPackExporter()

        payload = exporter.export_many(
            [
                DummyMetric(),
                DummyMetric(),
            ]
        )

        assert payload["count"] == 2

    def test_export_msgpack(self):

        exporter = MsgPackExporter()

        blob = exporter.export_msgpack(
            DummyMetric(),
        )

        assert isinstance(
            blob,
            bytes,
        )

    def test_export_many_msgpack(self):

        exporter = MsgPackExporter()

        blob = exporter.export_many_msgpack(
            [
                DummyMetric(),
                DummyMetric(),
            ]
        )

        assert isinstance(
            blob,
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

        exporter = MsgPackExporter()

        path = exporter.export_file(
            DummyMetric(),
            tmp_path / "metric.msgpack",
        )

        assert path.exists()

    def test_export_many_file(
        self,
        tmp_path: Path,
    ):

        exporter = MsgPackExporter()

        path = exporter.export_many_file(
            [
                DummyMetric(),
                DummyMetric(),
            ],
            tmp_path / "metrics.msgpack",
        )

        assert path.exists()

    def test_load_file(
        self,
        tmp_path: Path,
    ):

        exporter = MsgPackExporter()

        path = exporter.export_file(
            DummyMetric(),
            tmp_path / "metric.msgpack",
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

        exporter = MsgPackExporter()

        assert exporter.validate(
            DummyMetric(),
        )

    def test_is_valid(self):

        exporter = MsgPackExporter()

        assert exporter.is_valid(
            DummyMetric(),
        )


# ==========================================================
# Part 8. TestPythonProtocols
# ==========================================================

class TestPythonProtocols:

    def test_repr(self):

        exporter = MsgPackExporter()

        assert "MsgPackExporter" in repr(exporter)

    def test_str(self):

        exporter = MsgPackExporter()

        assert "MsgPackExporter" in str(exporter)

    def test_len(self):

        exporter = MsgPackExporter()

        assert len(exporter) == 4

    def test_bool(self):

        exporter = MsgPackExporter()

        assert bool(exporter)

    def test_copy(self):

        exporter = MsgPackExporter()

        cloned = copy.copy(exporter)

        assert cloned == exporter
        assert cloned is not exporter

    def test_deepcopy(self):

        exporter = MsgPackExporter()

        cloned = copy.deepcopy(exporter)

        assert cloned == exporter
        assert cloned is not exporter

    def test_eq(self):

        a = MsgPackExporter()
        b = MsgPackExporter()

        assert a == b

    def test_hash(self):

        exporter = MsgPackExporter()

        assert isinstance(
            hash(exporter),
            int,
        )


# ==========================================================
# Part 9. TestAPIFreeze
# ==========================================================

class TestAPIFreeze:

    def test_public_api(self):

        assert "MsgPackExporter" in __all__

    def test_annotations(self):

        assert hasattr(
            MsgPackExporter,
            "__annotations__",
        )

    def test_slots(self):

        assert hasattr(
            MsgPackExporter,
            "__slots__",
        )

    def test_signature(self):

        signature = inspect.signature(
            MsgPackExporter,
        )

        assert "version" in str(signature)

    def test_pickle(self):

        exporter = MsgPackExporter()

        restored = pickle.loads(
            pickle.dumps(exporter)
        )

        assert restored == exporter                            