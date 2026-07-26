"""
SciOS-NG Metrics Core

Tests for MetricCollector.

"""

import pytest


from scios.runtime.observability.metrics.core.metrics.metric import (
    Metric,
)


from scios.runtime.observability.metrics.core.metrics.metric_collector import (
    MetricCollector,
)



class TestMetricCollectorFoundation:
    """
    Collector creation.
    """


    def test_create_collector(self):

        collector = MetricCollector()

        assert collector is not None



    def test_empty_collector(self):

        collector = MetricCollector()

        result = collector.collect()

        assert result is not None



class TestMetricCollectorRegistration:
    """
    Metric source registration.
    """


    def test_register_metric(self):

        collector = MetricCollector()


        metric = Metric(
            name="cpu",
            value=50,
        )


        collector.register(
            metric
        )


        assert collector.exists(
            "cpu"
        )



    def test_register_multiple_metrics(self):

        collector = MetricCollector()


        collector.register(
            Metric(
                name="cpu",
                value=20,
            )
        )


        collector.register(
            Metric(
                name="memory",
                value=40,
            )
        )


        assert len(
            collector.list()
        ) == 2



class TestMetricCollectorCollection:
    """
    Collection API.
    """


    def test_collect_single_metric(self):

        collector = MetricCollector()


        collector.register(
            Metric(
                name="cpu",
                value=75,
            )
        )


        result = collector.collect()


        assert "cpu" in result



    def test_collect_all(self):

        collector = MetricCollector()


        collector.register(
            Metric(
                name="cpu",
                value=10,
            )
        )


        collector.register(
            Metric(
                name="ram",
                value=30,
            )
        )


        result = collector.collect_all()


        assert len(result) == 2



    def test_snapshot(self):

        collector = MetricCollector()


        collector.register(
            Metric(
                name="disk",
                value=90,
            )
        )


        snapshot = collector.snapshot()


        assert snapshot is not None



class TestMetricCollectorLifecycle:
    """
    Collector lifecycle.
    """


    def test_remove_metric(self):

        collector = MetricCollector()


        collector.register(
            Metric(
                name="cpu",
                value=10,
            )
        )


        collector.remove(
            "cpu"
        )


        assert collector.exists(
            "cpu"
        ) is False



    def test_clear(self):

        collector = MetricCollector()


        collector.register(
            Metric(
                name="cpu",
                value=10,
            )
        )


        collector.clear()


        assert collector.list() == []



class TestMetricCollectorSerialization:
    """
    Debug helpers.
    """


    def test_to_dict(self):

        collector = MetricCollector()


        collector.register(
            Metric(
                name="cpu",
                value=50,
            )
        )


        data = collector.to_dict()


        assert isinstance(
            data,
            dict,
        )


        assert "cpu" in data