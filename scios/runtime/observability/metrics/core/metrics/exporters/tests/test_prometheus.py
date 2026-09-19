import copy
import inspect
import pickle
import threading
from pathlib import Path

import pytest

from scios.runtime.observability.metrics.core.metrics.exporters.prometheus import (
    DEFAULT_VERSION,
    PrometheusExporter,
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
            "labels": dict(self.labels),
        }


# ==========================================================
# Part 3. TestConstruction
# ==========================================================

class TestConstruction:

    def test_create_default(self):

        exporter = PrometheusExporter()

        assert isinstance(
            exporter,
            PrometheusExporter,
        )

    def test_version(self):

        exporter = PrometheusExporter()

        assert exporter.version == DEFAULT_VERSION

    def test_serializer(self):

        exporter = PrometheusExporter()

        assert isinstance(
            exporter.serializer,
            MetricSerializer,
        )

    def test_lock(self):

        exporter = PrometheusExporter()

        assert isinstance(
            exporter.lock,
            _RLOCK_TYPE,
        )

# ==========================================================
# Part 4. TestHelpers
# ==========================================================

class TestHelpers:

    def test_metadata(self):

        exporter = PrometheusExporter()

        data = exporter._metadata()

        assert data["exporter"] == "PrometheusExporter"
        assert data["version"] == DEFAULT_VERSION

    def test_normalize_metric(self):

        exporter = PrometheusExporter()

        metric = DummyMetric()

        data = exporter._normalize(metric)

        assert isinstance(data, dict)
        assert data["name"] == "cpu"
        assert data["value"] == 0.5

    def test_normalize_dict(self):

        exporter = PrometheusExporter()

        payload = {
            "name": "memory",
            "value": 12,
        }

        data = exporter._normalize(payload)

        assert data == payload

    def test_metric_line(self):

        exporter = PrometheusExporter()

        line = exporter._metric_line(
            DummyMetric(),
        )

        assert isinstance(line, str)
        assert "cpu" in line
        assert "0.5" in line

    def test_export_payload(self):

        exporter = PrometheusExporter()

        payload = exporter._export_payload(
            DummyMetric(),
        )

        assert payload["exporter"] == "PrometheusExporter"
        assert payload["version"] == DEFAULT_VERSION
        assert isinstance(payload["text"], str)
        assert "cpu" in payload["text"]

    def test_export_many_payload(self):

        exporter = PrometheusExporter()

        payload = exporter._export_many_payload(
            [
                DummyMetric(),
                DummyMetric(),
            ]
        )

        assert payload["count"] == 2
        assert len(payload["items"]) == 2
        assert payload["count"] == 2
        assert len(payload["items"]) == 2
        assert payload["items"][0]["name"] == "cpu"
        assert payload["items"][1]["name"] == "cpu"


# ==========================================================
# Part 5. TestExportApi
# ==========================================================

class TestExportApi:

    def test_export(self):

        exporter = PrometheusExporter()

        text = exporter.export(
            DummyMetric(),
        )

        assert isinstance(text, str)
        assert "cpu" in text

    def test_export_many(self):

        exporter = PrometheusExporter()

        text = exporter.export_many(
            [
                DummyMetric(),
                DummyMetric(),
            ]
        )

        assert isinstance(text, str)
        assert text.count("cpu") == 2

    def test_export_text(self):

        exporter = PrometheusExporter()

        text = exporter.export_text(
            DummyMetric(),
        )

        assert isinstance(text, str)
        assert "cpu" in text

    def test_export_many_text(self):

        exporter = PrometheusExporter()

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
        tmp_path,
    ):

        exporter = PrometheusExporter()

        metric = DummyMetric()

        path = tmp_path / "metrics.prom"

        exporter.export_file(
            metric,
            path,
        )

        assert path.exists()

        text = path.read_text(
            encoding="utf-8",
        )

        assert "cpu" in text

    def test_export_many_file(
        self,
        tmp_path,
    ):

        exporter = PrometheusExporter()

        metrics = [
            DummyMetric(),
            DummyMetric(),
        ]

        path = tmp_path / "metrics.prom"

        exporter.export_many_file(
            metrics,
            path,
        )

        assert path.exists()

        text = path.read_text(
            encoding="utf-8",
        )

        assert text.count("cpu") == 2

    def test_load_file(
        self,
        tmp_path,
    ):

        exporter = PrometheusExporter()

        path = tmp_path / "metrics.prom"

        exporter.export_file(
            DummyMetric(),
            path,
        )

        text = exporter.load_file(
            path,
        )

        assert isinstance(text, str)
        assert "cpu" in text
        
                