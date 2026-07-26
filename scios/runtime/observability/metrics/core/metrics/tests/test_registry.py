"""
SciOS-NG Metrics Core

Tests for MetricRegistry.

"""

import pytest


from scios.runtime.observability.metrics.core.metrics.metric import (
    Metric,
)


from scios.runtime.observability.metrics.core.metrics.metric_registry import (
    MetricRegistry,
)



class TestMetricRegistryFoundation:
    """
    Registry creation.
    """


    def test_create_registry(self):

        registry = MetricRegistry()

        assert registry is not None



    def test_empty_registry(self):

        registry = MetricRegistry()

        metrics = registry.list()

        assert metrics == []



class TestMetricRegistryRegister:
    """
    Register metrics.
    """


    def test_register_metric(self):

        registry = MetricRegistry()


        metric = Metric(
            name="cpu",
            value=50,
        )


        registry.register(
            metric
        )


        assert registry.exists(
            "cpu"
        )



    def test_get_metric(self):

        registry = MetricRegistry()


        metric = Metric(
            name="memory",
            value=100,
        )


        registry.register(
            metric
        )


        result = registry.get(
            "memory"
        )


        assert result is metric



    def test_register_multiple_metrics(self):

        registry = MetricRegistry()


        registry.register(
            Metric(
                name="cpu",
                value=10,
            )
        )


        registry.register(
            Metric(
                name="ram",
                value=20,
            )
        )


        assert len(
            registry.list()
        ) == 2



class TestMetricRegistryRemove:
    """
    Remove operations.
    """


    def test_remove_metric(self):

        registry = MetricRegistry()


        metric = Metric(
            name="disk",
            value=80,
        )


        registry.register(
            metric
        )


        registry.remove(
            "disk"
        )


        assert registry.exists(
            "disk"
        ) is False



    def test_remove_unknown_metric(self):

        registry = MetricRegistry()


        result = registry.remove(
            "unknown"
        )


        assert result is None



class TestMetricRegistryClear:
    """
    Clear registry.
    """


    def test_clear(self):

        registry = MetricRegistry()


        registry.register(
            Metric(
                name="cpu",
                value=10,
            )
        )


        registry.register(
            Metric(
                name="ram",
                value=20,
            )
        )


        registry.clear()


        assert registry.list() == []



class TestMetricRegistrySnapshot:
    """
    Snapshot and debug helpers.
    """


    def test_snapshot(self):

        registry = MetricRegistry()


        registry.register(
            Metric(
                name="cpu",
                value=50,
            )
        )


        snapshot = registry.snapshot()


        assert snapshot is not None



    def test_to_dict(self):

        registry = MetricRegistry()


        registry.register(
            Metric(
                name="cpu",
                value=50,
            )
        )


        data = registry.to_dict()


        assert isinstance(
            data,
            dict,
        )


        assert "cpu" in data