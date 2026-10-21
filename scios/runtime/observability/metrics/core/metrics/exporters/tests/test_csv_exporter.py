# ==========================================================
# Part 1. Imports & Fixtures
# ==========================================================

import copy
import inspect
import pickle
import threading
from pathlib import Path

import pytest

from scios.runtime.observability.metrics.core.metrics.exporters.csv_exporter import (
    CSVExporter,
    DEFAULT_DELIMITER,
    DEFAULT_ENCODING,
    DEFAULT_QUOTECHAR,
    DEFAULT_VERSION,
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


@pytest.fixture
def exporter():

    return CSVExporter()


# ==========================================================
# Part 3. TestConstruction
# ==========================================================

class TestConstruction:

    def test_create_default(self):

        exporter = CSVExporter()

        assert isinstance(
            exporter,
            CSVExporter,
        )

    def test_version(self):

        exporter = CSVExporter()

        assert exporter.version == DEFAULT_VERSION

    def test_encoding(self):

        exporter = CSVExporter()

        assert exporter.encoding == DEFAULT_ENCODING

    def test_delimiter(self):

        exporter = CSVExporter()

        assert exporter.delimiter == DEFAULT_DELIMITER

    def test_quotechar(self):

        exporter = CSVExporter()

        assert exporter.quotechar == DEFAULT_QUOTECHAR

    def test_serializer(self):

        exporter = CSVExporter()

        assert isinstance(
            exporter.serializer,
            MetricSerializer,
        )

    def test_lock(self):

        exporter = CSVExporter()

        assert isinstance(
            exporter.lock,
            _RLOCK_TYPE,
        )

# ==========================================================
# Part 4. TestHelpers
# ==========================================================

class TestHelpers:

    def test_metadata(self):

        exporter = CSVExporter()

        meta = exporter._metadata()

        assert meta["exporter"] == "CSVExporter"
        assert meta["version"] == DEFAULT_VERSION
        assert meta["encoding"] == DEFAULT_ENCODING
        assert meta["delimiter"] == DEFAULT_DELIMITER
        assert meta["quotechar"] == DEFAULT_QUOTECHAR

    def test_normalize_metric(self):

        exporter = CSVExporter()

        metric = DummyMetric()

        data = exporter._normalize(metric)

        assert isinstance(data, dict)
        assert data["name"] == "cpu"
        assert data["value"] == 0.5

    def test_normalize_dict(self):

        exporter = CSVExporter()

        payload = {
            "a": 1,
            "b": 2,
        }

        data = exporter._normalize(payload)

        assert data == payload

    def test_fieldnames(self):

        exporter = CSVExporter()

        fields = exporter._fieldnames(
            [
                {"a": 1, "b": 2},
                {"a": 3, "c": 4},
            ]
        )

        assert fields == [
            "a",
            "b",
            "c",
        ]

    def test_row(self):

        exporter = CSVExporter()

        row = exporter._row(
            {"a": 1},
            ["a", "b"],
        )

        assert row == {
            "a": 1,
            "b": "",
        }

    def test_export_payload(self):

        exporter = CSVExporter()

        payload = exporter._export_payload(
            DummyMetric(),
        )

        assert payload["exporter"] == "CSVExporter"
        assert payload["version"] == DEFAULT_VERSION
        assert payload["data"]["name"] == "cpu"

    def test_export_many_payload(self):

        exporter = CSVExporter()

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

        exporter = CSVExporter()

        data = exporter.export(
            DummyMetric(),
        )

        assert isinstance(data, dict)
        assert data["data"]["name"] == "cpu"

    def test_export_many(self):

        exporter = CSVExporter()

        data = exporter.export_many(
            [
                DummyMetric(),
                DummyMetric(),
            ]
        )

        assert data["count"] == 2
        assert len(data["items"]) == 2

    def test_export_text(self):

        exporter = CSVExporter()

        text = exporter.export_text(
            DummyMetric(),
        )

        assert isinstance(text, str)
        assert "cpu" in text
        assert "value" in text

    def test_export_many_text(self):

        exporter = CSVExporter()

        text = exporter.export_many_text(
            [
                DummyMetric(),
                DummyMetric(),
            ]
        )

        assert isinstance(text, str)
        assert text.count("cpu") == 2


# ==========================================================
# Part 6. TestFileExport
# ==========================================================

class TestFileExport:

    def test_export_file(
        self,
        tmp_path: Path,
    ):

        exporter = CSVExporter()

        path = tmp_path / "metric.csv"

        exporter.export_file(
            DummyMetric(),
            path,
        )

        assert path.exists()

        text = path.read_text(
            encoding="utf-8",
        )

        assert "cpu" in text

    def test_export_many_file(
        self,
        tmp_path: Path,
    ):

        exporter = CSVExporter()

        path = tmp_path / "metrics.csv"

        exporter.export_many_file(
            [
                DummyMetric(),
                DummyMetric(),
            ],
            path,
        )

        assert path.exists()

        text = path.read_text(
            encoding="utf-8",
        )

        assert text.count("cpu") == 2

    def test_load_file(
        self,
        tmp_path: Path,
    ):

        exporter = CSVExporter()

        path = tmp_path / "metric.csv"

        exporter.export_file(
            DummyMetric(),
            path,
        )

        text = exporter.load_file(
            path,
        )

        assert isinstance(text, str)
        assert "cpu" in text

# ==========================================================
# Part 7. TestValidation
# ==========================================================

class TestValidation:

    def test_validate(self):

        exporter = CSVExporter()

        assert exporter.validate(
            DummyMetric(),
        )

    def test_is_valid(self):

        exporter = CSVExporter()

        assert exporter.is_valid(
            DummyMetric(),
        )


# ==========================================================
# Part 8. TestPythonProtocols
# ==========================================================

class TestPythonProtocols:

    def test_repr(self):

        exporter = CSVExporter()

        assert "CSVExporter" in repr(exporter)

    def test_str(self):

        exporter = CSVExporter()

        assert "CSVExporter" in str(exporter)

    def test_len(self):

        exporter = CSVExporter()

        assert len(exporter) == 4

    def test_bool(self):

        exporter = CSVExporter()

        assert bool(exporter) is True

    def test_copy(self):

        exporter = CSVExporter()

        copied = copy.copy(exporter)

        assert copied == exporter
        assert copied is not exporter

    def test_deepcopy(self):

        exporter = CSVExporter()

        copied = copy.deepcopy(exporter)

        assert copied == exporter
        assert copied is not exporter

    def test_eq(self):

        a = CSVExporter()
        b = CSVExporter()

        assert a == b

    def test_hash(self):

        exporter = CSVExporter()

        assert isinstance(
            hash(exporter),
            int,
        )


# ==========================================================
# Part 9. TestAPIFreeze
# ==========================================================

class TestAPIFreeze:

    def test_public_api(self):

        assert "CSVExporter" in __all__

    def test_annotations(self):

        assert hasattr(
            CSVExporter,
            "__annotations__",
        )

    def test_slots(self):

        assert hasattr(
            CSVExporter,
            "__slots__",
        )

    def test_signature(self):

        signature = inspect.signature(
            CSVExporter.__init__,
        )

        assert "version" in signature.parameters
        assert "encoding" in signature.parameters
        assert "delimiter" in signature.parameters
        assert "quotechar" in signature.parameters
        assert "serializer" in signature.parameters

    def test_pickle(self):

        exporter = CSVExporter()

        restored = pickle.loads(
            pickle.dumps(exporter),
        )

        assert restored == exporter        