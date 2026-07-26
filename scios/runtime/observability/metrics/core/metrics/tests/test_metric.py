"""
SciOS-NG Metrics Core

Tests for Metric implementation.

"""

import pytest

from scios.runtime.observability.metrics.core.metrics.metric import (
    Metric,
)



class TestMetricFoundation:
    """
    Metric creation and metadata.
    """


    def test_create_metric(self):

        metric = Metric(
            name="cpu_usage",
            value=10,
        )

        assert metric.name == "cpu_usage"
        assert metric.value == 10



    def test_default_value(self):

        metric = Metric(
            name="memory"
        )

        assert metric.value == 0



class TestMetricValueAPI:
    """
    Value API.
    """


    def test_get(self):

        metric = Metric(
            name="temperature",
            value=25,
        )

        assert metric.get() == 25



    def test_set(self):

        metric = Metric(
            name="temperature"
        )

        metric.set(30)

        assert metric.get() == 30



    def test_update(self):

        metric = Metric(
            name="temperature",
            value=10,
        )

        metric.update(20)

        assert metric.value == 20



    def test_delta(self):

        metric = Metric(
            name="temperature",
            value=10,
        )

        metric.update(15)

        assert metric.delta() == 5



    def test_changed(self):

        metric = Metric(
            name="temperature",
            value=10,
        )

        assert metric.changed() is False

        metric.update(20)

        assert metric.changed() is True



class TestMetricSnapshotAPI:
    """
    Snapshot and cloning.
    """


    def test_snapshot(self):

        metric = Metric(
            name="cpu",
            value=50,
        )

        snapshot = metric.snapshot()

        assert snapshot is not None



    def test_restore(self):

        metric = Metric(
            name="cpu",
            value=50,
        )

        snapshot = metric.snapshot()

        metric.set(100)

        metric.restore(snapshot)

        assert metric.value == 50



    def test_clone(self):

        metric = Metric(
            name="cpu",
            value=50,
        )

        clone = metric.clone()

        assert clone is not metric
        assert clone.name == metric.name
        assert clone.value == metric.value



class TestMetricLifecycleAPI:
    """
    Lifecycle management.
    """


    def test_freeze(self):

        metric = Metric(
            name="counter",
            value=1,
        )

        metric.freeze()

        assert metric.frozen is True



    def test_unfreeze(self):

        metric = Metric(
            name="counter",
            value=1,
        )

        metric.freeze()
        metric.unfreeze()

        assert metric.frozen is False



    def test_enable_disable(self):

        metric = Metric(
            name="counter"
        )

        metric.disable()

        assert metric.enabled is False


        metric.enable()

        assert metric.enabled is True



    def test_close_reopen(self):

        metric = Metric(
            name="counter"
        )

        metric.close()

        assert metric.closed is True


        metric.reopen()

        assert metric.closed is False



class TestMetricSerialization:
    """
    Serialization helpers.
    """


    def test_to_dict(self):

        metric = Metric(
            name="cpu",
            value=70,
        )

        data = metric.to_dict()

        assert isinstance(
            data,
            dict,
        )

        assert data["name"] == "cpu"