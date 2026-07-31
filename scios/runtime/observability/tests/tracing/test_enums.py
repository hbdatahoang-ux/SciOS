"""
SciOS Runtime Observability
Tracing Test - Enums

Tests:

- ExecutionPhase
- SpanKind
- TraceState
- SamplingDecision
- Severity
- Enum serialization
- Enum comparison
- Public API

"""

from __future__ import annotations


import pytest


from scios.runtime.observability.tracing.enums import (
    ExecutionPhase,
    SpanKind,
    TraceState,
    SamplingDecision,
    Severity,
)



# ============================================================
# ExecutionPhase
# ============================================================


def test_execution_phase_exists():

    assert ExecutionPhase is not None



@pytest.mark.parametrize(
    "phase, value",
    [
        (
            ExecutionPhase.CREATED,
            "created",
        ),
        (
            ExecutionPhase.SUBMITTED,
            "submitted",
        ),
        (
            ExecutionPhase.STARTED,
            "started",
        ),
        (
            ExecutionPhase.RUNNING,
            "running",
        ),
        (
            ExecutionPhase.COMPLETED,
            "completed",
        ),
        (
            ExecutionPhase.FAILED,
            "failed",
        ),
        (
            ExecutionPhase.CANCELLED,
            "cancelled",
        ),
    ],
)
def test_execution_phase_values(
    phase,
    value,
):

    assert phase.value == value



def test_execution_phase_string_behavior():

    assert (
        ExecutionPhase.STARTED
        ==
        "started"
    )



def test_execution_phase_conversion():

    phase = ExecutionPhase(
        "running"
    )


    assert (
        phase
        ==
        ExecutionPhase.RUNNING
    )



# ============================================================
# SpanKind
# ============================================================


@pytest.mark.parametrize(
    "kind, value",
    [
        (
            SpanKind.INTERNAL,
            "internal",
        ),
        (
            SpanKind.SERVER,
            "server",
        ),
        (
            SpanKind.CLIENT,
            "client",
        ),
        (
            SpanKind.PRODUCER,
            "producer",
        ),
        (
            SpanKind.CONSUMER,
            "consumer",
        ),
    ],
)
def test_span_kind_values(
    kind,
    value,
):

    assert kind.value == value



def test_span_kind_conversion():

    assert (
        SpanKind(
            "client"
        )
        ==
        SpanKind.CLIENT
    )



# ============================================================
# TraceState
# ============================================================


@pytest.mark.parametrize(
    "state, value",
    [
        (
            TraceState.ACTIVE,
            "active",
        ),
        (
            TraceState.COMPLETED,
            "completed",
        ),
        (
            TraceState.ERROR,
            "error",
        ),
        (
            TraceState.CANCELLED,
            "cancelled",
        ),
    ],
)
def test_trace_state_values(
    state,
    value,
):

    assert state.value == value



# ============================================================
# SamplingDecision
# ============================================================


@pytest.mark.parametrize(
    "decision, value",
    [
        (
            SamplingDecision.DROP,
            "drop",
        ),
        (
            SamplingDecision.RECORD,
            "record",
        ),
        (
            SamplingDecision.RECORD_AND_SAMPLE,
            "record_and_sample",
        ),
    ],
)
def test_sampling_decision_values(
    decision,
    value,
):

    assert decision.value == value



# ============================================================
# Severity
# ============================================================


@pytest.mark.parametrize(
    "severity, value",
    [
        (
            Severity.DEBUG,
            "debug",
        ),
        (
            Severity.INFO,
            "info",
        ),
        (
            Severity.WARNING,
            "warning",
        ),
        (
            Severity.ERROR,
            "error",
        ),
        (
            Severity.CRITICAL,
            "critical",
        ),
    ],
)
def test_severity_values(
    severity,
    value,
):

    assert severity.value == value



# ============================================================
# Common Enum Behavior
# ============================================================


def test_enum_is_string_based():

    assert isinstance(
        ExecutionPhase.CREATED,
        str,
    )


    assert isinstance(
        Severity.ERROR,
        str,
    )



def test_invalid_execution_phase():

    with pytest.raises(
        ValueError
    ):

        ExecutionPhase(
            "invalid"
        )



def test_invalid_span_kind():

    with pytest.raises(
        ValueError
    ):

        SpanKind(
            "invalid"
        )



def test_enum_iteration():

    values = [
        item.value
        for item in ExecutionPhase
    ]


    assert (
        "created"
        in values
    )



# ============================================================
# Public API
# ============================================================


def test_public_exports():

    from scios.runtime.observability.tracing import enums


    assert (
        "ExecutionPhase"
        in enums.__all__
    )