# ==============================================================================
# Imports
# ==============================================================================

from __future__ import annotations

import copy
import json

import pytest

from scios.runtime.observability.tracing.manager import (
    TraceManager,
)


# ==============================================================================
# Test Utilities
# ==============================================================================


class MockSpan:
    """
    Minimal span object for TraceManager tests.
    """

    def __init__(
        self,
        name,
        parent=None,
        **kwargs,
    ):
        self.name = name
        self.parent = parent

        self.children = []

        self.tags = {}
        self.metadata = {}

        self.finished = False

        self.context = kwargs.get(
            "context",
            None,
        )

        if parent is not None:
            parent.children.append(self)


    def finish(
        self,
    ):
        """
        Finish span.
        """

        self.finished = True

        return self



    def to_dict(
        self,
    ):
        """
        Serialize span.
        """

        return {
            "name": self.name,
            "finished": self.finished,
            "tags": self.tags.copy(),
            "metadata": self.metadata.copy(),
            "children": [
                child.to_dict()
                for child in self.children
            ],
        }




class MockTrace:
    """
    Minimal trace object.

    Supports:
    - start_span()
    - finish()
    - hierarchy
    """


    def __init__(
        self,
        name,
        context=None,
        **kwargs,
    ):
        self.name = name

        self.context = context

        self.spans = []

        self.current_span = None

        self.finished = False

        self.metadata = {}

        self.tags = {}



    def start_span(
        self,
        name,
        parent=None,
        **kwargs,
    ):
        """
        Create child span.
        """

        if parent is None:
            parent = self.current_span


        span = MockSpan(
            name=name,
            parent=parent,
            **kwargs,
        )


        self.spans.append(
            span
        )


        self.current_span = span


        return span



    def finish(
        self,
    ):
        """
        Finish trace.
        """

        self.finished = True

        return self



    def to_dict(
        self,
    ):
        """
        Serialize trace.
        """

        return {
            "name": self.name,
            "finished": self.finished,
            "metadata": self.metadata.copy(),
            "tags": self.tags.copy(),
            "spans": [
                span.to_dict()
                for span in self.spans
            ],
        }




class MockTracer:
    """
    Minimal tracer implementation.
    """


    def __init__(
        self,
    ):
        self.traces = {}



    def start_trace(
        self,
        name,
        context=None,
        **kwargs,
    ):
        """
        Create trace.
        """

        trace = MockTrace(
            name=name,
            context=context,
            **kwargs,
        )


        self.traces[name] = trace


        return trace



    def finish_trace(
        self,
        trace,
        **kwargs,
    ):
        return trace.finish()
# ==============================================================================
# Part 1 – Fixtures
# ==============================================================================


@pytest.fixture
def create_manager():
    """
    Create basic TraceManager state.

    State:
    - initialized
    - tracer registered
    - one active trace
    - one active span
    """

    manager = TraceManager()

    manager.initialize()

    manager.register_tracer(
        "default",
        MockTracer(),
    )

    manager.start_trace(
        name="runtime",
    )

    manager.start_span(
        name="planner",
    )

    return manager


@pytest.fixture
def create_nested_manager():
    """
    Create nested trace/span hierarchy.

    runtime
      └── planner
            └── solver
                  └── optimizer
    """

    manager = TraceManager()

    manager.initialize()

    manager.register_tracer(
        "default",
        MockTracer(),
    )

    manager.start_trace(
        name="runtime",
    )

    manager.start_span(
        name="planner",
    )

    manager.start_span(
        name="solver",
    )

    manager.start_span(
        name="optimizer",
    )

    return manager


@pytest.fixture
def create_multiple_traces():
    """
    Create manager with multiple traces.
    """

    manager = TraceManager()

    manager.initialize()

    manager.register_tracer(
        "default",
        MockTracer(),
    )

    manager.start_trace(
        name="runtime",
    )

    manager.start_span(
        name="planner",
    )

    manager.finish_span()

    manager.start_trace(
        name="worker",
    )

    manager.start_span(
        name="executor",
    )

    manager.finish_span()

    manager.start_trace(
        name="monitor",
    )

    return manager

# ==============================================================================
# Part 2 – Snapshot Creation
# ==============================================================================


def test_snapshot_returns_dict(
    create_manager,
):
    """
    Snapshot must return dictionary.
    """

    snapshot = create_manager.snapshot()

    assert isinstance(
        snapshot,
        dict,
    )


def test_snapshot_contains_identity(
    create_manager,
):
    """
    Snapshot contains identity information.
    """

    snapshot = create_manager.snapshot()

    assert (
        "identity"
        in snapshot
    )


def test_snapshot_contains_runtime(
    create_manager,
):
    """
    Snapshot contains runtime state.
    """

    snapshot = create_manager.snapshot()

    assert (
        "runtime"
        in snapshot
    )


def test_snapshot_contains_configuration(
    create_manager,
):
    """
    Snapshot contains configuration.
    """

    snapshot = create_manager.snapshot()

    assert (
        "configuration"
        in snapshot
    )


def test_snapshot_contains_traces(
    create_multiple_traces,
):
    """
    Snapshot contains trace data.
    """

    snapshot = create_multiple_traces.snapshot()

    assert (
        "traces"
        in snapshot
    )


def test_snapshot_contains_spans(
    create_manager,
):
    """
    Snapshot contains span data.
    """

    snapshot = create_manager.snapshot()

    assert (
        "spans"
        in snapshot
    )


def test_snapshot_is_independent(
    create_manager,
):
    """
    Snapshot must be independent from future changes.
    """

    snapshot = create_manager.snapshot()

    create_manager.start_span(
        name="future",
    )

    assert (
        snapshot
        !=
        create_manager.snapshot()
    )
# ==============================================================================
# Part 3 – Basic Restore
# ==============================================================================


def test_restore_previous_state(
    create_manager,
):
    """
    Restore manager to previous state.
    """

    snapshot = create_manager.snapshot()

    create_manager.start_span(
        name="temporary",
    )

    assert (
        create_manager.current_span.name
        ==
        "temporary"
    )

    create_manager.restore(
        snapshot,
    )

    assert (
        create_manager.current_span.name
        ==
        "planner"
    )


def test_restore_trace(
    create_manager,
):
    """
    Restore trace state.
    """

    snapshot = create_manager.snapshot()

    create_manager.finish_span()

    create_manager.finish_trace()

    create_manager.restore(
        snapshot,
    )

    assert (
        create_manager.current_trace
        is not None
    )

    assert (
        create_manager.current_trace.name
        ==
        "runtime"
    )


def test_restore_span(
    create_manager,
):
    """
    Restore active span.
    """

    snapshot = create_manager.snapshot()

    create_manager.finish_span()

    assert (
        create_manager.current_span
        is None
    )

    create_manager.restore(
        snapshot,
    )

    assert (
        create_manager.current_span
        is not None
    )

    assert (
        create_manager.current_span.name
        ==
        "planner"
    )


def test_restore_current_trace(
    create_manager,
):
    """
    Restore current trace pointer.
    """

    snapshot = create_manager.snapshot()

    current = (
        create_manager.current_trace
    )

    create_manager.clear_current()

    assert (
        create_manager.current_trace
        is None
    )

    create_manager.restore(
        snapshot,
    )

    assert (
        create_manager.current_trace
        is not None
    )

    assert (
        create_manager.current_trace
        is current
        or
        create_manager.current_trace.name
        ==
        current.name
    )


def test_restore_current_span(
    create_manager,
):
    """
    Restore current span pointer.
    """

    snapshot = create_manager.snapshot()

    current = (
        create_manager.current_span
    )

    create_manager.finish_span()

    assert (
        create_manager.current_span
        is None
    )

    create_manager.restore(
        snapshot,
    )

    assert (
        create_manager.current_span
        is not None
    )

    assert (
        create_manager.current_span.name
        ==
        current.name
    )


def test_restore_runtime_state(
    create_manager,
):
    """
    Restore runtime state.
    """

    snapshot = create_manager.snapshot()

    original_state = (
        create_manager.state
    )

    create_manager.close()

    create_manager.restore(
        snapshot,
    )

    assert (
        create_manager.state
        ==
        original_state
    )
# ==============================================================================
# Part 4 – Nested Snapshot
# ==============================================================================


def test_restore_nested_stack(
    create_nested_manager,
):
    """
    Restore nested span stack.
    """

    snapshot = (
        create_nested_manager
        .snapshot()
    )

    assert (
        create_nested_manager.current_span.name
        ==
        "optimizer"
    )

    create_nested_manager.finish_span()
    create_nested_manager.finish_span()

    create_nested_manager.restore(
        snapshot,
    )

    assert (
        create_nested_manager.current_span
        is not None
    )

    assert (
        create_nested_manager.current_span.name
        ==
        "optimizer"
    )


def test_restore_nested_trace(
    create_nested_manager,
):
    """
    Restore nested trace hierarchy.
    """

    snapshot = (
        create_nested_manager
        .snapshot()
    )

    trace_before = (
        create_nested_manager.current_trace
    )

    create_nested_manager.finish_trace()

    create_nested_manager.restore(
        snapshot,
    )

    trace_after = (
        create_nested_manager.current_trace
    )

    assert (
        trace_after
        is not None
    )

    assert (
        trace_after.name
        ==
        trace_before.name
    )


def test_restore_nested_span(
    create_nested_manager,
):
    """
    Restore nested span hierarchy.
    """

    snapshot = (
        create_nested_manager
        .snapshot()
    )

    create_nested_manager.finish_span()

    create_nested_manager.restore(
        snapshot,
    )

    assert (
        create_nested_manager.current_span
        is not None
    )

    assert (
        create_nested_manager.current_span.name
        ==
        "optimizer"
    )


def test_restore_parent_span(
    create_nested_manager,
):
    """
    Restore parent-child span relationship.
    """

    snapshot = (
        create_nested_manager
        .snapshot()
    )

    create_nested_manager.clear()

    create_nested_manager.restore(
        snapshot,
    )

    current = (
        create_nested_manager.current_span
    )

    assert (
        current
        is not None
    )

    assert (
        current.name
        ==
        "optimizer"
    )


def test_restore_deep_hierarchy(
    create_nested_manager,
):
    """
    Restore deep span hierarchy.
    """

    snapshot = (
        create_nested_manager
        .snapshot()
    )

    create_nested_manager.start_span(
        name="deep",
    )

    create_nested_manager.restore(
        snapshot,
    )

    current = (
        create_nested_manager.current_span
    )

    assert (
        current
        is not None
    )

    assert (
        current.name
        ==
        "optimizer"
    )
# ==============================================================================
# Part 5 – Multiple Snapshots
# ==============================================================================


def test_multiple_snapshots(
    create_manager,
):
    """
    Create multiple snapshots.
    """

    snapshot1 = (
        create_manager
        .snapshot()
    )

    create_manager.start_span(
        name="solver",
    )

    snapshot2 = (
        create_manager
        .snapshot()
    )

    assert isinstance(
        snapshot1,
        dict,
    )

    assert isinstance(
        snapshot2,
        dict,
    )

    assert (
        snapshot1
        !=
        snapshot2
    )


def test_restore_old_snapshot(
    create_manager,
):
    """
    Restore an older snapshot.
    """

    snapshot1 = (
        create_manager
        .snapshot()
    )

    create_manager.start_span(
        name="solver",
    )

    snapshot2 = (
        create_manager
        .snapshot()
    )

    assert (
        snapshot1
        !=
        snapshot2
    )

    create_manager.restore(
        snapshot1,
    )

    assert (
        create_manager.current_span.name
        ==
        "planner"
    )


def test_restore_latest_snapshot(
    create_manager,
):
    """
    Restore latest snapshot.
    """

    snapshot1 = (
        create_manager
        .snapshot()
    )

    create_manager.start_span(
        name="solver",
    )

    snapshot2 = (
        create_manager
        .snapshot()
    )

    create_manager.restore(
        snapshot2,
    )

    assert (
        create_manager.current_span.name
        ==
        "solver"
    )


def test_restore_after_multiple_changes(
    create_manager,
):
    """
    Restore after multiple state changes.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    create_manager.start_span(
        name="solver",
    )

    create_manager.start_span(
        name="optimizer",
    )

    create_manager.finish_span()

    create_manager.finish_span()

    create_manager.restore(
        snapshot,
    )

    assert (
        create_manager.current_span.name
        ==
        "planner"
    )


def test_snapshot_chain(
    create_manager,
):
    """
    Test snapshot restore chain.
    """

    snapshot1 = (
        create_manager
        .snapshot()
    )

    create_manager.start_span(
        name="solver",
    )

    snapshot2 = (
        create_manager
        .snapshot()
    )

    create_manager.start_span(
        name="optimizer",
    )

    snapshot3 = (
        create_manager
        .snapshot()
    )

    create_manager.restore(
        snapshot2,
    )

    assert (
        create_manager.current_span.name
        ==
        "solver"
    )

    create_manager.restore(
        snapshot1,
    )

    assert (
        create_manager.current_span.name
        ==
        "planner"
    )

    create_manager.restore(
        snapshot3,
    )

    assert (
        create_manager.current_span.name
        ==
        "optimizer"
    )
# ==============================================================================
# Part 6 – Snapshot Isolation
# ==============================================================================


def test_snapshot_isolated_from_future_changes(
    create_manager,
):
    """
    Snapshot must not change after future mutations.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    original = snapshot.copy()

    create_manager.start_span(
        name="future",
    )

    assert (
        snapshot
        ==
        original
    )


def test_snapshot_isolation_traces(
    create_multiple_traces,
):
    """
    Snapshot trace data must be isolated.
    """

    snapshot = (
        create_multiple_traces
        .snapshot()
    )

    original_traces = (
        snapshot
        .get(
            "traces",
            {},
        )
        .copy()
    )

    create_multiple_traces.start_trace(
        name="new_trace",
    )

    assert (
        snapshot
        .get(
            "traces",
            {},
        )
        ==
        original_traces
    )


def test_snapshot_isolation_spans(
    create_manager,
):
    """
    Snapshot span data must be isolated.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    original_spans = (
        snapshot
        .get(
            "spans",
            {},
        )
        .copy()
    )

    create_manager.start_span(
        name="new_span",
    )

    assert (
        snapshot
        .get(
            "spans",
            {},
        )
        ==
        original_spans
    )


def test_snapshot_isolation_metadata(
    create_manager,
):
    """
    Snapshot metadata must be isolated.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    original_metadata = (
        snapshot
        .get(
            "metadata",
            {},
        )
        .copy()
    )

    create_manager.update(
        metadata={
            "changed": True,
        },
    )

    assert (
        snapshot
        .get(
            "metadata",
            {},
        )
        ==
        original_metadata
    )


def test_snapshot_isolation_tags(
    create_manager,
):
    """
    Snapshot tags must be isolated.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    original_tags = (
        snapshot
        .get(
            "tags",
            [],
        )
        .copy()
    )

    create_manager.tags.append(
        "future-tag",
    )

    assert (
        snapshot
        .get(
            "tags",
            [],
        )
        ==
        original_tags
    )
# ==============================================================================
# Part 7 – Runtime State Recovery
# ==============================================================================


def test_restore_after_finish_trace(
    create_manager,
):
    """
    Restore state after finishing trace.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    create_manager.finish_span()

    create_manager.finish_trace()

    assert (
        create_manager.current_trace
        is None
    )

    create_manager.restore(
        snapshot,
    )

    assert (
        create_manager.current_trace
        is not None
    )

    assert (
        create_manager.current_trace.name
        ==
        "runtime"
    )


def test_restore_after_finish_span(
    create_manager,
):
    """
    Restore state after finishing span.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    create_manager.finish_span()

    assert (
        create_manager.current_span
        is None
    )

    create_manager.restore(
        snapshot,
    )

    assert (
        create_manager.current_span
        is not None
    )

    assert (
        create_manager.current_span.name
        ==
        "planner"
    )


def test_restore_after_clear(
    create_manager,
):
    """
    Restore after clear operation.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    create_manager.clear()

    create_manager.restore(
        snapshot,
    )

    assert (
        create_manager.current_trace
        is not None
    )

    assert (
        create_manager.current_span
        is not None
    )


def test_restore_after_reset(
    create_manager,
):
    """
    Restore after reset operation.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    create_manager.reset()

    create_manager.restore(
        snapshot,
    )

    assert (
        create_manager.current_trace
        is not None
    )

    assert (
        create_manager.current_span
        is not None
    )


def test_restore_after_flush(
    create_manager,
):
    """
    Restore after flush operation.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    create_manager.flush()

    create_manager.restore(
        snapshot,
    )

    assert (
        create_manager.current_trace
        is not None
    )


def test_restore_after_update(
    create_manager,
):
    """
    Restore after update operation.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    create_manager.update(
        metadata={
            "changed": True,
        },
    )

    create_manager.restore(
        snapshot,
    )

    restored = (
        create_manager.snapshot()
    )

    assert (
        restored
        ==
        snapshot
    )
# ==============================================================================
# Part 8 – Error Handling
# ==============================================================================


def test_restore_none(
    create_manager,
):
    """
    Restore with None should fail.
    """

    with pytest.raises(
        Exception,
    ):
        create_manager.restore(
            None,
        )


def test_restore_invalid_type(
    create_manager,
):
    """
    Restore with invalid type.
    """

    with pytest.raises(
        Exception,
    ):
        create_manager.restore(
            "invalid_snapshot",
        )


def test_restore_empty_snapshot(
    create_manager,
):
    """
    Restore from empty snapshot.
    """

    result = (
        create_manager.restore(
            {},
        )
    )

    assert (
        result
        is create_manager
    )


def test_restore_missing_fields(
    create_manager,
):
    """
    Restore from incomplete snapshot.
    """

    snapshot = {
        "identity": {},
    }

    result = (
        create_manager.restore(
            snapshot,
        )
    )

    assert (
        result
        is create_manager
    )


def test_restore_corrupted_snapshot(
    create_manager,
):
    """
    Restore from corrupted snapshot.
    """

    snapshot = {
        "identity": {
            "uuid": "invalid-uuid",
        },
    }

    with pytest.raises(
        Exception,
    ):
        create_manager.restore(
            snapshot,
        )


def test_restore_partial_snapshot(
    create_manager,
):
    """
    Restore from partial valid snapshot.
    """

    snapshot = {
        "runtime": {},
        "configuration": {},
    }

    result = (
        create_manager.restore(
            snapshot,
        )
    )

    assert (
        result
        is create_manager
    )
# ==============================================================================
# Part 9 – Edge Cases
# ==============================================================================


def test_snapshot_empty_manager():
    """
    Snapshot empty manager.
    """

    manager = TraceManager()

    snapshot = (
        manager.snapshot()
    )

    assert isinstance(
        snapshot,
        dict,
    )


def test_snapshot_without_trace():
    """
    Snapshot manager without active trace.
    """

    manager = TraceManager()

    snapshot = (
        manager.snapshot()
    )

    assert (
        snapshot
        is not None
    )

    assert isinstance(
        snapshot,
        dict,
    )


def test_snapshot_without_span():
    """
    Snapshot manager without active span.
    """

    manager = TraceManager()

    manager.start_trace(
        name="runtime",
    )

    snapshot = (
        manager.snapshot()
    )

    assert (
        snapshot
        is not None
    )

    assert isinstance(
        snapshot,
        dict,
    )


def test_restore_multiple_times(
    create_manager,
):
    """
    Restore same snapshot multiple times.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    create_manager.start_span(
        name="temporary",
    )

    create_manager.restore(
        snapshot,
    )

    create_manager.start_span(
        name="another",
    )

    create_manager.restore(
        snapshot,
    )

    assert (
        create_manager.current_span.name
        ==
        "planner"
    )


def test_restore_same_snapshot_twice(
    create_manager,
):
    """
    Restore identical snapshot twice.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    create_manager.restore(
        snapshot,
    )

    create_manager.restore(
        snapshot,
    )

    assert (
        create_manager.current_span.name
        ==
        "planner"
    )


def test_snapshot_large_hierarchy():
    """
    Snapshot large span hierarchy.
    """

    manager = TraceManager()

    manager.start_trace(
        name="runtime",
    )

    for index in range(20):
        manager.start_span(
            name=f"span-{index}",
        )

    snapshot = (
        manager.snapshot()
    )

    assert isinstance(
        snapshot,
        dict,
    )


def test_snapshot_after_close():
    """
    Snapshot after close.
    """

    manager = TraceManager()

    manager.close()

    snapshot = (
        manager.snapshot()
    )

    assert isinstance(
        snapshot,
        dict,
    )


def test_snapshot_after_freeze():
    """
    Snapshot after freeze.
    """

    manager = TraceManager()

    manager.freeze()

    snapshot = (
        manager.snapshot()
    )

    assert isinstance(
        snapshot,
        dict,
    )


def test_restore_closed_manager(
    create_manager,
):
    """
    Restore into closed manager.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    create_manager.close()

    result = (
        create_manager.restore(
            snapshot,
        )
    )

    assert (
        result
        is create_manager
    )


def test_restore_frozen_manager(
    create_manager,
):
    """
    Restore into frozen manager.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    create_manager.freeze()

    result = (
        create_manager.restore(
            snapshot,
        )
    )

    assert (
        result
        is create_manager
    )
# ==============================================================================
# Part 10 – Consistency
# ==============================================================================


def test_snapshot_restore_roundtrip(
    create_manager,
):
    """
    Snapshot -> Restore -> Snapshot must be consistent.
    """

    snapshot1 = (
        create_manager
        .snapshot()
    )

    create_manager.restore(
        snapshot1,
    )

    snapshot2 = (
        create_manager
        .snapshot()
    )

    assert (
        snapshot2
        ==
        snapshot1
    )


def test_restore_preserves_identity(
    create_manager,
):
    """
    Restore preserves manager identity.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    identity_before = (
        snapshot
        .get(
            "identity",
            {},
        )
    )

    create_manager.restore(
        snapshot,
    )

    snapshot_after = (
        create_manager
        .snapshot()
    )

    assert (
        snapshot_after["identity"]
        ==
        identity_before
    )


def test_restore_preserves_statistics(
    create_manager,
):
    """
    Restore preserves statistics.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    statistics_before = (
        snapshot
        .get(
            "statistics",
            {},
        )
    )

    create_manager.restore(
        snapshot,
    )

    statistics_after = (
        create_manager
        .snapshot()
        .get(
            "statistics",
            {},
        )
    )

    assert (
        statistics_after
        ==
        statistics_before
    )


def test_restore_preserves_configuration(
    create_manager,
):
    """
    Restore preserves configuration.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    configuration_before = (
        snapshot
        .get(
            "configuration",
            {},
        )
    )

    create_manager.restore(
        snapshot,
    )

    configuration_after = (
        create_manager
        .snapshot()
        .get(
            "configuration",
            {},
        )
    )

    assert (
        configuration_after
        ==
        configuration_before
    )


def test_restore_preserves_metadata(
    create_manager,
):
    """
    Restore preserves metadata.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    metadata_before = (
        snapshot
        .get(
            "metadata",
            {},
        )
    )

    create_manager.restore(
        snapshot,
    )

    metadata_after = (
        create_manager
        .snapshot()
        .get(
            "metadata",
            {},
        )
    )

    assert (
        metadata_after
        ==
        metadata_before
    )


def test_restore_preserves_tags(
    create_manager,
):
    """
    Restore preserves tags.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    tags_before = (
        snapshot
        .get(
            "tags",
            [],
        )
    )

    create_manager.restore(
        snapshot,
    )

    tags_after = (
        create_manager
        .snapshot()
        .get(
            "tags",
            [],
        )
    )

    assert (
        tags_after
        ==
        tags_before
    )


def test_restore_preserves_context(
    create_manager,
):
    """
    Restore preserves context.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    context_before = (
        snapshot
        .get(
            "context",
            {},
        )
    )

    create_manager.restore(
        snapshot,
    )

    context_after = (
        create_manager
        .snapshot()
        .get(
            "context",
            {},
        )
    )

    assert (
        context_after
        ==
        context_before
    )


def test_restore_preserves_callbacks(
    create_manager,
):
    """
    Restore preserves callbacks.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    callbacks_before = (
        snapshot
        .get(
            "callbacks",
            [],
        )
    )

    create_manager.restore(
        snapshot,
    )

    callbacks_after = (
        create_manager
        .snapshot()
        .get(
            "callbacks",
            [],
        )
    )

    assert (
        callbacks_after
        ==
        callbacks_before
    )


def test_restore_preserves_history(
    create_manager,
):
    """
    Restore preserves history.
    """

    snapshot = (
        create_manager
        .snapshot()
    )

    history_before = (
        snapshot
        .get(
            "history",
            {},
        )
    )

    create_manager.restore(
        snapshot,
    )

    history_after = (
        create_manager
        .snapshot()
        .get(
            "history",
            {},
        )
    )

    assert (
        history_after
        ==
        history_before
    )


def test_restore_consistency(
    create_manager,
):
    """
    Complete snapshot restore consistency.
    """

    snapshot_before = (
        create_manager
        .snapshot()
    )

    create_manager.start_span(
        name="temporary",
    )

    create_manager.restore(
        snapshot_before,
    )

    snapshot_after = (
        create_manager
        .snapshot()
    )

    assert (
        snapshot_after
        ==
        snapshot_before
    )                                    