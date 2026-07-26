"""
SciOS-NG Metrics Core

Tests for MetricState implementation.

"""

import time

import pytest


from scios.runtime.observability.metrics.core.metrics.metric_state import (
    MetricState,
)



class TestMetricStateFoundation:
    """
    MetricState creation.
    """


    def test_create_state(self):

        state = MetricState(
            value=10,
        )

        assert state.value == 10



    def test_default_state(self):

        state = MetricState()

        assert state.value == 0
        assert state.update_count == 0



class TestMetricStateValueAPI:
    """
    Value update behavior.
    """


    def test_update_value(self):

        state = MetricState(
            value=10,
        )

        state.update(
            20
        )

        assert state.value == 20



    def test_previous_value(self):

        state = MetricState(
            value=10,
        )

        state.update(
            25
        )

        assert state.previous_value == 10



    def test_update_count(self):

        state = MetricState(
            value=0,
        )


        state.update(1)
        state.update(2)
        state.update(3)


        assert state.update_count == 3



    def test_timestamp_update(self):

        state = MetricState()


        before = time.time()

        state.update(10)

        after = time.time()


        assert before <= state.timestamp <= after



class TestMetricStateLifecycle:
    """
    Enable / freeze / close lifecycle.
    """


    def test_initial_enabled(self):

        state = MetricState()

        assert state.enabled is True



    def test_disable(self):

        state = MetricState()

        state.disable()

        assert state.enabled is False



    def test_enable(self):

        state = MetricState()

        state.disable()
        state.enable()

        assert state.enabled is True



    def test_freeze(self):

        state = MetricState()

        state.freeze()

        assert state.frozen is True



    def test_unfreeze(self):

        state = MetricState()

        state.freeze()
        state.unfreeze()

        assert state.frozen is False



    def test_close(self):

        state = MetricState()

        state.close()

        assert state.closed is True



    def test_reopen(self):

        state = MetricState()

        state.close()
        state.reopen()

        assert state.closed is False



class TestMetricStateSnapshot:
    """
    Snapshot behavior.
    """


    def test_snapshot(self):

        state = MetricState(
            value=100,
        )


        snapshot = state.snapshot()


        assert snapshot is not None



    def test_restore(self):

        state = MetricState(
            value=100,
        )


        snapshot = state.snapshot()


        state.update(200)

        state.restore(snapshot)


        assert state.value == 100



class TestMetricStateSerialization:
    """
    Debug serialization.
    """


    def test_to_dict(self):

        state = MetricState(
            value=50,
        )


        data = state.to_dict()


        assert isinstance(
            data,
            dict,
        )


        assert data["value"] == 50