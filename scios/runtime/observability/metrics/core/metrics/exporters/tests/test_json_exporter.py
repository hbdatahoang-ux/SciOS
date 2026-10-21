import threading

import json
import inspect
import pickle
import copy

from scios.runtime.observability.metrics.core.metrics.exporters.json_exporter import (
    DEFAULT_ENCODING,
    DEFAULT_ENSURE_ASCII,
    DEFAULT_INDENT,
    DEFAULT_VERSION,
    JSONExporter,
    __all__,
)

from scios.runtime.observability.metrics.core.metrics.serialization.metric_serializer import (
    MetricSerializer,
)


# ==========================================================
# Dummy
# ==========================================================

class DummyMetric:

    def to_dict(self):

        return {
            "name": "cpu",
            "value": 42,
        }


# ==========================================================
# TestConstruction
# ==========================================================

class TestConstruction:

    def test_create_default(self):

        exporter = JSONExporter()

        assert isinstance(
            exporter,
            JSONExporter,
        )

    def test_version(self):

        exporter = JSONExporter()

        assert exporter.version == DEFAULT_VERSION

    def test_encoding(self):

        exporter = JSONExporter()

        assert exporter.encoding == DEFAULT_ENCODING

    def test_indent(self):

        exporter = JSONExporter()

        assert exporter.indent == DEFAULT_INDENT

    def test_ensure_ascii(self):

        exporter = JSONExporter()

        assert (
            exporter.ensure_ascii
            is DEFAULT_ENSURE_ASCII
        )

    def test_serializer(self):

        exporter = JSONExporter()

        assert isinstance(
            exporter.serializer,
            MetricSerializer,
        )

    def test_lock(self):

        exporter = JSONExporter()

        assert isinstance(
            exporter.lock,
            type(threading.RLock()),
        )

# ==========================================================
# TestHelpers
# ==========================================================

class TestHelpers:

    def test_metadata(self):

        exporter = JSONExporter()

        data = exporter._metadata()

        assert data["exporter"] == "JSONExporter"
        assert data["version"] == DEFAULT_VERSION

    def test_normalize_metric(self):

        exporter = JSONExporter()

        metric = DummyMetric()

        data = exporter._normalize(metric)

        assert isinstance(data, dict)
        assert data["name"] == "cpu"
        assert data["value"] == 42

    def test_normalize_dict(self):

        exporter = JSONExporter()

        payload = {
            "a": 1,
            "b": 2,
        }

        data = exporter._normalize(payload)

        assert data == payload

    def test_export_payload(self):

        exporter = JSONExporter()

        payload = exporter._export_payload(
            DummyMetric()
        )

        assert payload["exporter"] == "JSONExporter"
        assert payload["version"] == DEFAULT_VERSION
        assert payload["data"]["name"] == "cpu"

    def test_export_many_payload(self):

        exporter = JSONExporter()

        payload = exporter._export_many_payload(
            [
                DummyMetric(),
                DummyMetric(),
            ]
        )

        assert payload["count"] == 2
        assert len(payload["items"]) == 2
        assert payload["items"][0]["name"] == "cpu"
        assert payload["items"][1]["value"] == 42

class TestExportApi:

    def test_export(self):

        exporter = JSONExporter()

        metric = DummyMetric()

        data = exporter.export(metric)

        assert isinstance(data, dict)
        assert data["name"] == "cpu"

    def test_export_many(self):

        exporter = JSONExporter()

        metrics = [
            DummyMetric(),
            DummyMetric(),
        ]

        data = exporter.export_many(metrics)

        assert data["count"] == 2
        assert len(data["items"]) == 2

    def test_export_json(self):

        exporter = JSONExporter()

        metric = DummyMetric()

        text = exporter.export_json(metric)

        assert isinstance(text, str)

        payload = json.loads(text)

        assert payload["name"] == "cpu"

    def test_export_many_json(self):

        exporter = JSONExporter()

        metrics = [
            DummyMetric(),
            DummyMetric(),
        ]

        text = exporter.export_many_json(metrics)

        payload = json.loads(text)

        assert payload["count"] == 2
        assert len(payload["items"]) == 2

# ==========================================================
# TestFileExport
# ==========================================================

class TestFileExport:

    def test_export_file(
        self,
        tmp_path,
    ):

        exporter = JSONExporter()

        metric = DummyMetric()

        path = tmp_path / "metric.json"

        exporter.export_file(
            metric,
            path,
        )

        assert path.exists()

        data = json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )

        assert data["data"]["name"] == "cpu"

    def test_export_many_file(
        self,
        tmp_path,
    ):

        exporter = JSONExporter()

        metrics = [
            DummyMetric(),
            DummyMetric(),
        ]

        path = tmp_path / "metrics.json"

        exporter.export_many_file(
            metrics,
            path,
        )

        assert path.exists()

        data = json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )

        assert data["count"] == 2

    def test_load_file(
        self,
        tmp_path,
    ):

        exporter = JSONExporter()

        metric = DummyMetric()

        path = tmp_path / "metric.json"

        exporter.export_file(
            metric,
            path,
        )

        data = exporter.load_file(
            path,
        )

        assert isinstance(
            data,
            dict,
        )

        assert data["data"]["name"] == "cpu"

# ==========================================================
# TestValidation
# ==========================================================

class TestValidation:

    def test_validate(self):

        exporter = JSONExporter()

        assert exporter.validate(
            DummyMetric(),
        ) is True

        assert exporter.validate(
            {"name": "cpu"},
        ) is True

    def test_is_valid(self):

        exporter = JSONExporter()

        assert exporter.is_valid(
            DummyMetric(),
        ) is True

        assert exporter.is_valid(
            {"value": 1},
        ) is True

# ==========================================================
# TestPythonProtocols
# ==========================================================


class TestPythonProtocols:

    def test_repr(self):

        exporter = JSONExporter()

        text = repr(exporter)

        assert "JSONExporter" in text

    def test_str(self):

        exporter = JSONExporter()

        text = str(exporter)

        assert "JSONExporter" in text

    def test_len(self):

        exporter = JSONExporter()

        assert len(exporter) == 1

    def test_bool(self):

        exporter = JSONExporter()

        assert bool(exporter) is True

    def test_copy(self):

        exporter = JSONExporter()

        cloned = copy.copy(exporter)

        assert isinstance(
            cloned,
            JSONExporter,
        )

        assert cloned == exporter

    def test_deepcopy(self):

        exporter = JSONExporter()

        cloned = copy.deepcopy(exporter)

        assert isinstance(
            cloned,
            JSONExporter,
        )

        assert cloned == exporter

    def test_eq(self):

        a = JSONExporter()

        b = JSONExporter()

        assert a == b

    def test_hash(self):

        exporter = JSONExporter()

        assert isinstance(
            hash(exporter),
            int,
        )

# ==========================================================
# TestAPIFreeze
# ==========================================================

class TestAPIFreeze:

    def test_public_api(self):

        assert "JSONExporter" in __all__

    def test_annotations(self):

        assert hasattr(
            JSONExporter,
            "__annotations__",
        )

    def test_slots(self):

        assert hasattr(
            JSONExporter,
            "__slots__",
        )

    def test_signature(self):

        sig = inspect.signature(
            JSONExporter.__init__,
        )

        assert "serializer" in sig.parameters
        assert "encoding" in sig.parameters
        assert "indent" in sig.parameters
        assert "ensure_ascii" in sig.parameters

    def test_pickle(self):

        exporter = JSONExporter()

        restored = pickle.loads(
            pickle.dumps(exporter)
        )

        assert isinstance(
            restored,
            JSONExporter,
        )

        assert restored == exporter                                                