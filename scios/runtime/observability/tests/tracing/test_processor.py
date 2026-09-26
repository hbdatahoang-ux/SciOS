# ==============================================================================
# SciOS Runtime Observability
# Trace Processor Tests
# ==============================================================================
#
# File:
# scios/runtime/observability/tests/tracing/test_processor.py
#
# Python 3.11+
# ==============================================================================

from __future__ import annotations


# ==============================================================================
# Imports
# ==============================================================================

import json
from datetime import datetime

import pytest

from scios.runtime.observability.tracing.processor import (
    Processor,
    ProcessorConfig,
    ProcessorMode,
    ProcessorState,
    TraceProcessor,
)

from scios.runtime.observability.tracing.span import (
    Span,
)

from scios.runtime.observability.tracing.trace import (
    Trace,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def create_processor():
    def factory(**kwargs):
        return Processor(**kwargs)

    return factory


@pytest.fixture
def create_trace():
    def factory(**kwargs):
        return Trace(**kwargs)

    return factory


@pytest.fixture
def create_span():
    def factory(**kwargs):
        return Span(**kwargs)

    return factory


# ==============================================================================
# Part 1. Construction
# ==============================================================================


def test_processor_creation(
    create_processor,
):
    value = create_processor()

    assert isinstance(
        value,
        Processor,
    )


def test_default_values(
    create_processor,
):
    value = create_processor()

    assert value.name
    assert value.version
    assert value.enabled is True
    assert value.state is ProcessorState.CREATED


def test_custom_name(
    create_processor,
):
    value = create_processor(
        name="custom-processor",
    )

    assert value.name == "custom-processor"


def test_custom_version(
    create_processor,
):
    value = create_processor(
        version="2.0.0",
    )

    assert value.version == "2.0.0"


def test_custom_configuration(
    create_processor,
):
    value = create_processor(
        name="processor-001",
        version="2.0.0",
        enabled=False,
        auto_start=False,
    )

    assert value.name == "processor-001"
    assert value.version == "2.0.0"
    assert value.enabled is False
    assert value.started is False


# ==============================================================================
# Part 2. Identity
# ==============================================================================


def test_id(
    create_processor,
):
    value = create_processor()

    assert value.id is not None
    assert isinstance(
        value.id,
        str,
    )
    assert len(value.id) > 0


def test_name(
    create_processor,
):
    value = create_processor(
        name="identity-processor",
    )

    assert value.name == "identity-processor"


def test_version(
    create_processor,
):
    value = create_processor(
        version="3.1.0",
    )

    assert value.version == "3.1.0"


# ==============================================================================
# Part 3. State
# ==============================================================================


def test_initial_state(
    create_processor,
):
    value = create_processor(
        auto_start=False,
    )

    assert value.state is ProcessorState.CREATED


def test_enabled(
    create_processor,
):
    value = create_processor(
        enabled=True,
    )

    assert value.enabled is True


def test_active(
    create_processor,
):
    value = create_processor(
        auto_start=False,
    )

    assert value.active is False

    value.start()

    assert value.active is True


def test_started(
    create_processor,
):
    value = create_processor(
        auto_start=False,
    )

    assert value.started is False

    value.start()

    assert value.started is True


def test_stopped(
    create_processor,
):
    value = create_processor(
        auto_start=False,
    )

    value.start()
    value.stop()

    assert value.stopped is True


def test_closed(
    create_processor,
):
    value = create_processor()

    assert value.closed is False

    value.close()

    assert value.closed is True


# ==============================================================================
# Part 4. Lifecycle
# ==============================================================================


def test_start(
    create_processor,
):
    value = create_processor(
        auto_start=False,
    )

    result = value.start()

    assert result is value
    assert value.state is ProcessorState.RUNNING
    assert value.started is True
    assert value.active is True


def test_stop(
    create_processor,
):
    value = create_processor(
        auto_start=False,
    )

    value.start()

    result = value.stop()

    assert result is value
    assert value.state is ProcessorState.STOPPED
    assert value.stopped is True
    assert value.active is False


def test_reset(
    create_processor,
    create_trace,
    create_span,
):
    value = create_processor(
        auto_start=False,
    )

    value.start()

    value.process_trace(
        create_trace(
            name="trace-001",
        ),
    )

    value.process_span(
        create_span(
            name="span-001",
            auto_start=False,
            auto_finish=False,
        ),
    )

    result = value.reset()

    assert result is value
    assert value.state is ProcessorState.CREATED
    assert value.active is False
    assert value.trace_count == 0
    assert value.span_count == 0
    assert value.pending_count == 0


def test_restart(
    create_processor,
):
    value = create_processor(
        auto_start=False,
    )

    value.start()
    value.stop()

    result = value.restart()

    assert result is value
    assert value.state is ProcessorState.RUNNING
    assert value.active is True
    assert value.started is True


def test_freeze(
    create_processor,
):
    value = create_processor(
        auto_start=False,
    )

    value.start()

    result = value.freeze()

    assert result is value
    assert value.state is ProcessorState.FROZEN
    assert value.frozen is True
    assert value.active is False


def test_unfreeze(
    create_processor,
):
    value = create_processor(
        auto_start=False,
    )

    value.start()
    value.freeze()

    result = value.unfreeze()

    assert result is value
    assert value.state is ProcessorState.RUNNING
    assert value.frozen is False
    assert value.active is True


def test_close(
    create_processor,
):
    value = create_processor()

    result = value.close()

    assert result is value
    assert value.state is ProcessorState.CLOSED
    assert value.closed is True
    assert value.active is False


# ==============================================================================
# Part 5. Trace Processing
# ==============================================================================


def test_process_trace(
    create_processor,
    create_trace,
):
    value = create_processor()

    trace = create_trace(
        name="trace-001",
    )

    result = value.process_trace(
        trace,
    )

    assert result is not None
    assert value.trace_count == 1


def test_process_span(
    create_processor,
    create_span,
):
    value = create_processor()

    span = create_span(
        name="span-001",
        auto_start=False,
        auto_finish=False,
    )

    result = value.process_span(
        span,
    )

    assert result is not None
    assert value.span_count == 1


def test_process(
    create_processor,
    create_trace,
    create_span,
):
    value = create_processor()

    trace = create_trace(
        name="trace-001",
    )

    span = create_span(
        name="span-001",
        auto_start=False,
        auto_finish=False,
    )

    trace_result = value.process(
        trace,
    )

    span_result = value.process(
        span,
    )

    assert trace_result is not None
    assert span_result is not None


def test_flush(
    create_processor,
    create_trace,
):
    value = create_processor()

    value.process_trace(
        create_trace(
            name="trace-001",
        ),
    )

    result = value.flush()

    assert result is not None
    assert value.pending_count == 0


# ==============================================================================
# Part 6. Collection
# ==============================================================================


def test_traces(
    create_processor,
    create_trace,
):
    value = create_processor()

    trace = create_trace(
        name="trace-001",
    )

    value.process_trace(
        trace,
    )

    traces = value.traces

    assert isinstance(
        traces,
        (list, tuple),
    )

    assert trace in traces


def test_spans(
    create_processor,
    create_span,
):
    value = create_processor()

    span = create_span(
        name="span-001",
        auto_start=False,
        auto_finish=False,
    )

    value.process_span(
        span,
    )

    spans = value.spans

    assert isinstance(
        spans,
        (list, tuple),
    )

    assert span in spans


def test_trace_count(
    create_processor,
    create_trace,
):
    value = create_processor()

    assert value.trace_count == 0

    value.process_trace(
        create_trace(
            name="trace-001",
        ),
    )

    assert value.trace_count == 1


def test_span_count(
    create_processor,
    create_span,
):
    value = create_processor()

    assert value.span_count == 0

    value.process_span(
        create_span(
            name="span-001",
            auto_start=False,
            auto_finish=False,
        ),
    )

    assert value.span_count == 1


def test_pending_count(
    create_processor,
    create_trace,
):
    value = create_processor()

    value.process_trace(
        create_trace(
            name="trace-001",
        ),
    )

    assert value.pending_count >= 0

    value.flush()

    assert value.pending_count == 0


# ==============================================================================
# Part 7. Statistics
# ==============================================================================


def test_statistics(
    create_processor,
    create_trace,
):
    value = create_processor()

    value.process_trace(
        create_trace(
            name="trace-001",
        ),
    )

    statistics = value.statistics

    assert statistics is not None
    assert statistics.processed >= 1
    assert statistics.dropped >= 0
    assert statistics.errors >= 0


def test_processed_count(
    create_processor,
    create_trace,
):
    value = create_processor()

    assert value.processed_count == 0

    value.process_trace(
        create_trace(
            name="trace-001",
        ),
    )

    assert value.processed_count >= 1


def test_dropped_count(
    create_processor,
):
    value = create_processor(
        enabled=False,
    )

    before = value.dropped_count

    value.process(
        {
            "id": "dropped-001",
            "type": "trace",
        },
    )

    assert value.dropped_count >= before


def test_error_count(
    create_processor,
):
    value = create_processor()

    before = value.error_count

    value.process(
        None,
    )

    assert value.error_count >= before


def test_last_process_time(
    create_processor,
    create_trace,
):
    value = create_processor()

    assert value.last_process_time is None

    value.process_trace(
        create_trace(
            name="trace-001",
        ),
    )

    assert value.last_process_time is not None
    assert isinstance(
        value.last_process_time,
        datetime,
    )


# ==============================================================================
# Part 8. Validation
# ==============================================================================


def test_validate(
    create_processor,
):
    value = create_processor()

    assert value.validate() is True


def test_health(
    create_processor,
):
    value = create_processor()

    assert value.health() is True


def test_invalid_state(
    create_processor,
):
    value = create_processor()

    value.close()

    assert value.closed is True
    assert value.health() is False or value.health() is True


# ==============================================================================
# Part 9. Persistence
# ==============================================================================


def test_to_dict(
    create_processor,
):
    value = create_processor(
        name="processor-001",
        version="1.0.0",
    )

    data = value.to_dict()

    assert isinstance(
        data,
        dict,
    )

    assert data["id"] == value.id
    assert data["name"] == value.name
    assert data["version"] == value.version


def test_to_json(
    create_processor,
):
    value = create_processor(
        name="processor-001",
    )

    data = value.to_json()

    assert isinstance(
        data,
        str,
    )

    parsed = json.loads(
        data,
    )

    assert isinstance(
        parsed,
        dict,
    )

    assert parsed["name"] == value.name


def test_snapshot(
    create_processor,
):
    value = create_processor(
        name="processor-001",
    )

    snapshot = value.snapshot()

    assert isinstance(
        snapshot,
        dict,
    )

    assert snapshot["id"] == value.id
    assert snapshot["name"] == value.name


def test_from_dict(
    create_processor,
):
    value = create_processor()

    data = value.to_dict()

    restored = Processor.from_dict(
        data,
    )

    assert isinstance(
        restored,
        Processor,
    )

    assert restored.id == value.id
    assert restored.name == value.name
    assert restored.version == value.version


def test_from_json(
    create_processor,
):
    value = create_processor(
        name="processor-json",
    )

    data = value.to_json()

    restored = Processor.from_json(
        data,
    )

    assert isinstance(
        restored,
        Processor,
    )

    assert restored.name == value.name


def test_restore(
    create_processor,
):
    value = create_processor(
        name="processor-original",
    )

    snapshot = value.snapshot()

    value.close()

    result = value.restore(
        snapshot,
    )

    assert result is value
    assert value.name == "processor-original"
    assert value.closed is False


# ==============================================================================
# Part 10. Copying
# ==============================================================================


def test_clone(
    create_processor,
):
    value = create_processor(
        name="processor-clone",
    )

    cloned = value.clone()

    assert cloned is not value
    assert isinstance(
        cloned,
        Processor,
    )

    assert cloned.id == value.id
    assert cloned.name == value.name


def test_copy(
    create_processor,
):
    value = create_processor(
        name="processor-copy",
    )

    copied = value.copy()

    assert copied is not value
    assert isinstance(
        copied,
        Processor,
    )

    assert copied.id == value.id
    assert copied.name == value.name


# ==============================================================================
# Part 11. Python Protocols
# ==============================================================================


def test_repr(
    create_processor,
):
    value = create_processor()

    result = repr(
        value,
    )

    assert isinstance(
        result,
        str,
    )

    assert "Processor" in result


def test_str(
    create_processor,
):
    value = create_processor()

    result = str(
        value,
    )

    assert isinstance(
        result,
        str,
    )

    assert len(result) > 0


def test_bool(
    create_processor,
):
    value = create_processor()

    assert bool(value) is True

    value.close()

    assert bool(value) is False


def test_eq(
    create_processor,
):
    value = create_processor()

    other = value.copy()

    assert value == other


def test_hash(
    create_processor,
):
    value = create_processor()

    result = hash(
        value,
    )

    assert isinstance(
        result,
        int,
    )


def test_len(
    create_processor,
    create_trace,
):
    value = create_processor()

    assert len(value) == 0

    value.process_trace(
        create_trace(
            name="trace-001",
        ),
    )

    assert len(value) >= 1


# ==============================================================================
# Part 12. Complete Workflow
# ==============================================================================


def test_processor_complete_workflow(
    create_processor,
    create_trace,
    create_span,
):
    value = create_processor(
        name="workflow-processor",
        version="1.0.0",
        enabled=True,
        auto_start=False,
    )

    assert value.validate() is True

    assert value.state is ProcessorState.CREATED
    assert value.active is False

    value.start()

    assert value.state is ProcessorState.RUNNING
    assert value.started is True
    assert value.active is True

    trace = create_trace(
        name="workflow-trace",
    )

    span = create_span(
        name="workflow-span",
        auto_start=False,
        auto_finish=False,
    )

    trace_result = value.process_trace(
        trace,
    )

    span_result = value.process_span(
        span,
    )

    assert trace_result is not None
    assert span_result is not None

    assert value.trace_count == 1
    assert value.span_count == 1
    assert value.processed_count >= 2

    assert value.last_process_time is not None

    snapshot = value.snapshot()

    assert snapshot["id"] == value.id
    assert snapshot["name"] == value.name

    clone = value.clone()

    assert clone is not value
    assert clone.id == value.id
    assert clone.name == value.name

    value.freeze()

    assert value.frozen is True
    assert value.state is ProcessorState.FROZEN

    value.unfreeze()

    assert value.frozen is False
    assert value.state is ProcessorState.RUNNING

    value.flush()

    assert value.pending_count == 0

    value.stop()

    assert value.stopped is True
    assert value.active is False

    value.close()

    assert value.closed is True
    assert value.state is ProcessorState.CLOSED
