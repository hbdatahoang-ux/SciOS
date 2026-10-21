# ==========================================================
# Part 1. Imports & Fixtures
# ==========================================================

from __future__ import annotations

import copy
import inspect
import json
import pickle

from pathlib import Path
from typing import Any

import threading

from scios.runtime.observability.metrics.core.metrics.exporters.base import (
    DEFAULT_ENCODING,
    DEFAULT_VERSION,
    BaseExporter,
    ExportManyPayload,
    ExportPayload,
    Serializable,
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

    def __init__(self):

        self.name = "cpu"
        self.value = 42

    def to_dict(self):

        return {
            "name": self.name,
            "value": self.value,
        }


# ==========================================================
# Part 3. DummyExporter
# ==========================================================

class DummyExporter(BaseExporter):

    def export(
        self,
        metric,
    ):
        return self._export_payload(metric)

    def export_many(
        self,
        metrics,
    ):
        return self._export_many_payload(metrics)

    def export_bytes(
        self,
        metric,
    ):
        return str(
            self.export(metric),
        ).encode(self.encoding)

    def export_many_bytes(
        self,
        metrics,
    ):
        return str(
            self.export_many(metrics),
        ).encode(self.encoding)


# ==========================================================
# Part 4. TestConstruction
# ==========================================================

class TestConstruction:

    def test_create_default(self):

        exporter = DummyExporter()

        assert isinstance(
            exporter,
            DummyExporter,
        )

    def test_version(self):

        exporter = DummyExporter()

        assert exporter.version == DEFAULT_VERSION

    def test_encoding(self):

        exporter = DummyExporter()

        assert exporter.encoding == DEFAULT_ENCODING

    def test_serializer(self):

        exporter = DummyExporter()

        assert isinstance(
            exporter.serializer,
            MetricSerializer,
        )

    def test_lock(self):

        exporter = DummyExporter()

        assert isinstance(
            exporter.lock,
            _RLOCK_TYPE,
        )

# ==========================================================
# Part 5. TestHelpers
# ==========================================================

class TestHelpers:

    def test_metadata(self):

        exporter = DummyExporter()

        meta = exporter._metadata()

        assert meta["version"] == DEFAULT_VERSION
        assert meta["encoding"] == DEFAULT_ENCODING
        assert meta["exporter"] == "DummyExporter"

    def test_normalize_metric(self):

        exporter = DummyExporter()

        data = exporter._normalize(
            DummyMetric(),
        )

        assert data["name"] == "cpu"
        assert data["value"] == 42

    def test_normalize_dict(self):

        exporter = DummyExporter()

        data = exporter._normalize(
            {
                "a": 1,
            },
        )

        assert data == {
            "a": 1,
        }

    def test_export_payload(self):

        exporter = DummyExporter()

        payload = exporter._export_payload(
            DummyMetric(),
        )

        assert "metadata" in payload
        assert "metric" in payload

    def test_export_many_payload(self):

        exporter = DummyExporter()

        payload = exporter._export_many_payload(
            [
                DummyMetric(),
                DummyMetric(),
            ],
        )

        assert len(payload) == 2


# ==========================================================
# Part 6. TestExportApi
# ==========================================================

class TestExportApi:

    def test_export(self):

        exporter = DummyExporter()

        result = exporter.export(
            DummyMetric(),
        )

        assert "metric" in result

    def test_export_many(self):

        exporter = DummyExporter()

        result = exporter.export_many(
            [
                DummyMetric(),
                DummyMetric(),
            ],
        )

        assert len(result) == 2

    def test_export_bytes(self):

        exporter = DummyExporter()

        result = exporter.export_bytes(
            DummyMetric(),
        )

        assert isinstance(
            result,
            bytes,
        )

    def test_export_many_bytes(self):

        exporter = DummyExporter()

        result = exporter.export_many_bytes(
            [
                DummyMetric(),
                DummyMetric(),
            ],
        )

        assert isinstance(
            result,
            bytes,
        )


# ==========================================================
# Part 7. TestFileApi
# ==========================================================

class TestFileApi:

    def test_export_file(
        self,
        tmp_path: Path,
    ):

        exporter = DummyExporter()

        path = exporter.export_file(
            DummyMetric(),
            tmp_path / "metric.bin",
        )

        assert path.exists()

    def test_export_many_file(
        self,
        tmp_path: Path,
    ):

        exporter = DummyExporter()

        path = exporter.export_many_file(
            [
                DummyMetric(),
                DummyMetric(),
            ],
            tmp_path / "metrics.bin",
        )

        assert path.exists()

    def test_load_file(
        self,
        tmp_path: Path,
    ):

        exporter = DummyExporter()

        path = exporter.export_file(
            DummyMetric(),
            tmp_path / "metric.bin",
        )

        data = exporter.load_file(
            path,
        )

        assert isinstance(
            data,
            bytes,
        )

# ==========================================================
# Part 8. TestValidation
# ==========================================================

class TestValidation:

    def test_validate(self):

        exporter = DummyExporter()

        assert exporter.validate() is True

    def test_is_valid(self):

        exporter = DummyExporter()

        assert exporter.is_valid() is True


# ==========================================================
# Part 9. TestPythonProtocols
# ==========================================================

class TestPythonProtocols:

    def test_repr(self):

        exporter = DummyExporter()

        assert "DummyExporter" in repr(exporter)

    def test_str(self):

        exporter = DummyExporter()

        assert str(exporter) == repr(exporter)

    def test_len(self):

        exporter = DummyExporter()

        assert len(exporter) == 2

    def test_bool(self):

        exporter = DummyExporter()

        assert bool(exporter)

    def test_copy(self):

        exporter = DummyExporter()

        copied = copy.copy(exporter)

        assert copied == exporter
        assert copied is not exporter

    def test_deepcopy(self):

        exporter = DummyExporter()

        copied = copy.deepcopy(exporter)

        assert copied == exporter
        assert copied is not exporter

    def test_eq(self):

        a = DummyExporter()
        b = DummyExporter()

        assert a == b

    def test_hash(self):

        exporter = DummyExporter()

        assert isinstance(
            hash(exporter),
            int,
        )

    def test_pickle(self):

        exporter = DummyExporter()

        restored = pickle.loads(
            pickle.dumps(exporter),
        )

        assert restored == exporter


# ==========================================================
# Part 10. TestAPIFreeze
# ==========================================================

class TestAPIFreeze:

    def test_public_api(self):

        assert "BaseExporter" in __all__
        assert "Serializable" in __all__
        assert "ExportPayload" in __all__
        assert "ExportManyPayload" in __all__

    def test_annotations(self):

        assert isinstance(
            BaseExporter.__annotations__,
            dict,
        )

    def test_slots(self):

        assert hasattr(
            BaseExporter,
            "__slots__",
        )

    def test_signature(self):

        sig = inspect.signature(
            BaseExporter.__init__,
        )

        assert "version" in sig.parameters
        assert "encoding" in sig.parameters
        assert "serializer" in sig.parameters                