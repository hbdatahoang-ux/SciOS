# ==========================================================
# Part 1. Imports & Fixtures
# ==========================================================

import copy
import inspect
import pickle
import threading
from pathlib import Path

import pytest

from scios.runtime.observability.metrics.core.metrics.exporters.opentelemetry import (
    DEFAULT_ENCODING,
    DEFAULT_SERVICE_NAME,
    DEFAULT_SERVICE_NAMESPACE,
    DEFAULT_VERSION,
    OpenTelemetryExporter,
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
    """
    Dummy metric for exporter testing.
    """

    def __init__(self):

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


# ==========================================================
# Part 3. TestConstruction
# ==========================================================

class TestConstruction:

    def test_create_default(self):

        exporter = OpenTelemetryExporter()

        assert isinstance(
            exporter,
            OpenTelemetryExporter,
        )

    def test_version(self):

        exporter = OpenTelemetryExporter()

        assert exporter.version == DEFAULT_VERSION

    def test_encoding(self):

        exporter = OpenTelemetryExporter()

        assert exporter.encoding == DEFAULT_ENCODING

    def test_service_name(self):

        exporter = OpenTelemetryExporter()

        assert (
            exporter.service_name
            == DEFAULT_SERVICE_NAME
        )

    def test_service_namespace(self):

        exporter = OpenTelemetryExporter()

        assert (
            exporter.service_namespace
            == DEFAULT_SERVICE_NAMESPACE
        )

    def test_serializer(self):

        exporter = OpenTelemetryExporter()

        assert isinstance(
            exporter.serializer,
            MetricSerializer,
        )

    def test_lock(self):

        exporter = OpenTelemetryExporter()

        assert isinstance(
            exporter.lock,
            _RLOCK_TYPE,
        )

# ==========================================================
# Part 4. TestHelpers
# ==========================================================

class TestHelpers:

    def test_metadata(self):

        exporter = OpenTelemetryExporter()

        meta = exporter._metadata()

        assert meta["exporter"] == "OpenTelemetryExporter"
        assert meta["version"] == DEFAULT_VERSION

    def test_normalize_metric(self):

        exporter = OpenTelemetryExporter()

        data = exporter._normalize(
            DummyMetric(),
        )

        assert data["name"] == "cpu"

    def test_normalize_dict(self):

        exporter = OpenTelemetryExporter()

        data = exporter._normalize(
            {
                "a": 1,
            }
        )

        assert data["a"] == 1

    def test_resource_attributes(self):

        exporter = OpenTelemetryExporter()

        attrs = exporter._resource_attributes()

        assert (
            attrs["service.name"]
            == DEFAULT_SERVICE_NAME
        )

        assert (
            attrs["service.namespace"]
            == DEFAULT_SERVICE_NAMESPACE
        )

    def test_export_payload(self):

        exporter = OpenTelemetryExporter()

        payload = exporter._export_payload(
            DummyMetric(),
        )

        assert "resource" in payload
        assert "scopeMetrics" in payload

    def test_export_many_payload(self):

        exporter = OpenTelemetryExporter()

        payload = exporter._export_many_payload(
            [
                DummyMetric(),
                DummyMetric(),
            ]
        )

        assert payload["count"] == 2


# ==========================================================
# Part 5. TestExportApi
# ==========================================================

class TestExportApi:

    def test_export(self):

        exporter = OpenTelemetryExporter()

        data = exporter.export(
            DummyMetric(),
        )

        assert isinstance(
            data,
            dict,
        )

    def test_export_many(self):

        exporter = OpenTelemetryExporter()

        data = exporter.export_many(
            [
                DummyMetric(),
                DummyMetric(),
            ]
        )

        assert data["count"] == 2

    def test_export_otlp(self):

        exporter = OpenTelemetryExporter()

        data = exporter.export_otlp(
            DummyMetric(),
        )

        assert isinstance(
            data,
            bytes,
        )

    def test_export_many_otlp(self):

        exporter = OpenTelemetryExporter()

        data = exporter.export_many_otlp(
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

        exporter = OpenTelemetryExporter()

        path = exporter.export_file(
            DummyMetric(),
            tmp_path / "metric.otlp",
        )

        assert path.exists()

    def test_export_many_file(
        self,
        tmp_path: Path,
    ):

        exporter = OpenTelemetryExporter()

        path = exporter.export_many_file(
            [
                DummyMetric(),
                DummyMetric(),
            ],
            tmp_path / "metrics.otlp",
        )

        assert path.exists()

    def test_load_file(
        self,
        tmp_path: Path,
    ):

        exporter = OpenTelemetryExporter()

        path = exporter.export_file(
            DummyMetric(),
            tmp_path / "metric.otlp",
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

        exporter = OpenTelemetryExporter()

        assert exporter.validate(
            DummyMetric(),
        )

    def test_is_valid(self):

        exporter = OpenTelemetryExporter()

        assert exporter.is_valid(
            DummyMetric(),
        )


# ==========================================================
# Part 8. TestPythonProtocols
# ==========================================================

class TestPythonProtocols:

    def test_repr(self):

        exporter = OpenTelemetryExporter()

        assert "OpenTelemetryExporter" in repr(exporter)

    def test_str(self):

        exporter = OpenTelemetryExporter()

        assert str(exporter).startswith(
            "OpenTelemetryExporter"
        )

    def test_len(self):

        exporter = OpenTelemetryExporter()

        assert len(exporter) == 4

    def test_bool(self):

        exporter = OpenTelemetryExporter()

        assert exporter

    def test_copy(self):

        exporter = OpenTelemetryExporter()

        copied = copy.copy(exporter)

        assert copied == exporter
        assert copied is not exporter

    def test_deepcopy(self):

        exporter = OpenTelemetryExporter()

        copied = copy.deepcopy(exporter)

        assert copied == exporter
        assert copied is not exporter

    def test_eq(self):

        a = OpenTelemetryExporter()
        b = OpenTelemetryExporter()

        assert a == b

    def test_hash(self):

        exporter = OpenTelemetryExporter()

        assert isinstance(
            hash(exporter),
            int,
        )


# ==========================================================
# Part 9. TestAPIFreeze
# ==========================================================

class TestAPIFreeze:

    def test_public_api(self):

        assert __all__ == [
            "DEFAULT_VERSION",
            "DEFAULT_ENCODING",
            "DEFAULT_SERVICE_NAME",
            "DEFAULT_SERVICE_NAMESPACE",
            "Serializable",
            "OpenTelemetryExporter",
        ]

    def test_annotations(self):

        sig = inspect.signature(
            OpenTelemetryExporter.__init__,
        )

        assert "version" in sig.parameters
        assert "encoding" in sig.parameters
        assert "service_name" in sig.parameters
        assert "service_namespace" in sig.parameters

    def test_slots(self):

        assert hasattr(
            OpenTelemetryExporter,
            "__slots__",
        )

    def test_signature(self):

        sig = inspect.signature(
            OpenTelemetryExporter.export,
        )

        assert "obj" in sig.parameters

    def test_pickle(self):

        exporter = OpenTelemetryExporter()

        restored = pickle.loads(
            pickle.dumps(exporter),
        )

        assert restored == exporter
        assert restored is not exporter                