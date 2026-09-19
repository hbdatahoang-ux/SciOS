# ==========================================================
# Part 1. Imports & Fixtures
# ==========================================================

import copy
import inspect
import pickle
import threading
from pathlib import Path

import pytest
import yaml

from scios.runtime.observability.metrics.core.metrics.exporters.yaml_exporter import (
    DEFAULT_ALLOW_UNICODE,
    DEFAULT_ENCODING,
    DEFAULT_INDENT,
    DEFAULT_SORT_KEYS,
    DEFAULT_VERSION,
    YAMLExporter,
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


@pytest.fixture
def exporter():
    return YAMLExporter()


@pytest.fixture
def metric():
    return DummyMetric()


# ==========================================================
# Part 3. TestConstruction
# ==========================================================

class TestConstruction:

    def test_create_default(self):

        exporter = YAMLExporter()

        assert isinstance(
            exporter,
            YAMLExporter,
        )

    def test_version(self):

        exporter = YAMLExporter()

        assert exporter.version == DEFAULT_VERSION

    def test_encoding(self):

        exporter = YAMLExporter()

        assert exporter.encoding == DEFAULT_ENCODING

    def test_indent(self):

        exporter = YAMLExporter()

        assert exporter.indent == DEFAULT_INDENT

    def test_sort_keys(self):

        exporter = YAMLExporter()

        assert exporter.sort_keys is DEFAULT_SORT_KEYS

    def test_allow_unicode(self):

        exporter = YAMLExporter()

        assert exporter.allow_unicode is DEFAULT_ALLOW_UNICODE

    def test_serializer(self):

        exporter = YAMLExporter()

        assert isinstance(
            exporter.serializer,
            MetricSerializer,
        )

    def test_lock(self):

        exporter = YAMLExporter()

        assert isinstance(
            exporter.lock,
            _RLOCK_TYPE,
        )

# ==========================================================
# Part 4. TestHelpers
# ==========================================================

class TestHelpers:

    def test_metadata(self):

        exporter = YAMLExporter()

        meta = exporter._metadata()

        assert meta["exporter"] == "YAMLExporter"
        assert meta["version"] == DEFAULT_VERSION
        assert meta["encoding"] == DEFAULT_ENCODING

    def test_normalize_metric(self):

        exporter = YAMLExporter()

        data = exporter._normalize(
            DummyMetric(),
        )

        assert data["name"] == "cpu"
        assert data["value"] == 0.5

    def test_normalize_dict(self):

        exporter = YAMLExporter()

        data = exporter._normalize(
            {
                "name": "memory",
                "value": 1,
            }
        )

        assert data["name"] == "memory"

    def test_yaml_kwargs(self):

        exporter = YAMLExporter()

        kwargs = exporter._yaml_kwargs()

        assert kwargs["indent"] == DEFAULT_INDENT
        assert kwargs["sort_keys"] is DEFAULT_SORT_KEYS
        assert kwargs["allow_unicode"] is DEFAULT_ALLOW_UNICODE

    def test_export_payload(self):

        exporter = YAMLExporter()

        payload = exporter._export_payload(
            DummyMetric(),
        )

        assert payload["data"]["name"] == "cpu"

    def test_export_many_payload(self):

        exporter = YAMLExporter()

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

        exporter = YAMLExporter()

        payload = exporter.export(
            DummyMetric(),
        )

        assert payload["data"]["name"] == "cpu"

    def test_export_many(self):

        exporter = YAMLExporter()

        payload = exporter.export_many(
            [
                DummyMetric(),
                DummyMetric(),
            ]
        )

        assert payload["count"] == 2

    def test_export_yaml(self):

        exporter = YAMLExporter()

        text = exporter.export_yaml(
            DummyMetric(),
        )

        assert isinstance(text, str)

        data = yaml.safe_load(text)

        assert data["data"]["name"] == "cpu"

    def test_export_many_yaml(self):

        exporter = YAMLExporter()

        text = exporter.export_many_yaml(
            [
                DummyMetric(),
                DummyMetric(),
            ]
        )

        assert isinstance(text, str)

        data = yaml.safe_load(text)

        assert data["count"] == 2


# ==========================================================
# Part 6. TestFileExport
# ==========================================================

class TestFileExport:

    def test_export_file(
        self,
        tmp_path: Path,
    ):

        exporter = YAMLExporter()

        file_path = tmp_path / "metric.yaml"

        exporter.export_file(
            DummyMetric(),
            file_path,
        )

        assert file_path.exists()

    def test_export_many_file(
        self,
        tmp_path: Path,
    ):

        exporter = YAMLExporter()

        file_path = tmp_path / "metrics.yaml"

        exporter.export_many_file(
            [
                DummyMetric(),
                DummyMetric(),
            ],
            file_path,
        )

        assert file_path.exists()

    def test_load_file(
        self,
        tmp_path: Path,
    ):

        exporter = YAMLExporter()

        file_path = tmp_path / "metric.yaml"

        exporter.export_file(
            DummyMetric(),
            file_path,
        )

        data = exporter.load_file(
            file_path,
        )

        assert data["data"]["name"] == "cpu"

# ==========================================================
# Part 7. TestValidation
# ==========================================================

class TestValidation:

    def test_validate(self):

        exporter = YAMLExporter()

        assert exporter.validate(
            DummyMetric(),
        )

    def test_is_valid(self):

        exporter = YAMLExporter()

        assert exporter.is_valid(
            DummyMetric(),
        )


# ==========================================================
# Part 8. TestPythonProtocols
# ==========================================================

class TestPythonProtocols:

    def test_repr(self):

        exporter = YAMLExporter()

        text = repr(exporter)

        assert "YAMLExporter" in text

    def test_str(self):

        exporter = YAMLExporter()

        text = str(exporter)

        assert "YAMLExporter" in text

    def test_len(self):

        exporter = YAMLExporter()

        assert len(exporter) == 5

    def test_bool(self):

        exporter = YAMLExporter()

        assert bool(exporter)

    def test_copy(self):

        exporter = YAMLExporter()

        copied = copy.copy(exporter)

        assert copied == exporter
        assert copied is not exporter

    def test_deepcopy(self):

        exporter = YAMLExporter()

        copied = copy.deepcopy(exporter)

        assert copied == exporter
        assert copied is not exporter

    def test_eq(self):

        a = YAMLExporter()
        b = YAMLExporter()

        assert a == b

    def test_hash(self):

        exporter = YAMLExporter()

        assert isinstance(
            hash(exporter),
            int,
        )


# ==========================================================
# Part 9. TestAPIFreeze
# ==========================================================

class TestAPIFreeze:

    def test_public_api(self):

        assert "YAMLExporter" in __all__

    def test_annotations(self):

        assert hasattr(
            YAMLExporter.__init__,
            "__annotations__",
        )

    def test_slots(self):

        assert hasattr(
            YAMLExporter,
            "__slots__",
        )

    def test_signature(self):

        sig = inspect.signature(
            YAMLExporter.__init__,
        )

        assert "version" in sig.parameters
        assert "encoding" in sig.parameters
        assert "indent" in sig.parameters
        assert "sort_keys" in sig.parameters
        assert "allow_unicode" in sig.parameters

    def test_pickle(self):

        exporter = YAMLExporter()

        restored = pickle.loads(
            pickle.dumps(exporter)
        )

        assert restored == exporter
        assert restored.version == exporter.version                