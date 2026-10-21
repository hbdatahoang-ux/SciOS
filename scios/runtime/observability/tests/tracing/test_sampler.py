# ==============================================================================
# SciOS Runtime Observability
# Trace Sampler Tests
# ==============================================================================
#
# File:
#     scios/runtime/observability/tests/tracing/test_sampler.py
#
# Python 3.11+
# ==============================================================================

from __future__ import annotations

# ==============================================================================
# Imports
# ==============================================================================

import json
import time
import uuid

import pytest

from datetime import datetime

from scios.runtime.observability.tracing.sampler import (
    DEFAULT_ENCODING,
    DEFAULT_HISTORY_LIMIT,
    DEFAULT_SAMPLE_RATE,
    DEFAULT_SAMPLER_NAME,
    DEFAULT_SEED,
    SAMPLER_VERSION,
    InvalidSampleRateError,
    Sampler,
    SamplerCapability,
    SamplerClosedError,
    SamplerConfigurationError,
    SamplerError,
    SamplerFrozenError,
    SamplerState,
    SamplerType,
    SamplingDecision,
    SamplingError,
    SamplingRecord,
    SamplingResult,
    SamplingStatistics,
    TraceSampler,
)

# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def create_sampler():
    def factory(**kwargs):
        return TraceSampler(**kwargs)

    return factory


@pytest.fixture
def sampler(create_sampler):
    return create_sampler()


@pytest.fixture
def always_on(create_sampler):
    return create_sampler(
        sampler_type=SamplerType.ALWAYS_ON,
        sample_rate=1.0,
    )


@pytest.fixture
def always_off(create_sampler):
    return create_sampler(
        sampler_type=SamplerType.ALWAYS_OFF,
        sample_rate=0.0,
    )


# ==============================================================================
# Part 1. Foundation
# ==============================================================================


def test_imports():
    assert TraceSampler is not None
    assert Sampler is TraceSampler
    assert SamplingDecision is not None
    assert SamplerType is not None
    assert SamplerState is not None
    assert SamplerCapability is not None


def test_public_api():
    import scios.runtime.observability.tracing.sampler as module

    public = set(module.__all__)

    expected = {
        "TraceSampler",
        "Sampler",
        "SamplingDecision",
        "SamplerType",
        "SamplerState",
        "SamplerCapability",
        "SamplingRecord",
        "SamplingStatistics",
        "SamplingResult",
        "SamplerError",
        "SamplingError",
        "InvalidSampleRateError",
        "SamplerClosedError",
        "SamplerFrozenError",
        "SamplerConfigurationError",
        "DEFAULT_SAMPLER_NAME",
        "DEFAULT_SAMPLE_RATE",
        "DEFAULT_SEED",
        "DEFAULT_HISTORY_LIMIT",
        "DEFAULT_ENCODING",
        "SAMPLER_VERSION",
    }

    assert expected.issubset(public)


def test_constants():
    assert isinstance(DEFAULT_SAMPLER_NAME, str)
    assert isinstance(DEFAULT_SAMPLE_RATE, float)
    assert DEFAULT_SAMPLE_RATE == 1.0
    assert DEFAULT_SEED is None or isinstance(DEFAULT_SEED, int)
    assert DEFAULT_HISTORY_LIMIT > 0
    assert isinstance(DEFAULT_ENCODING, str)
    assert isinstance(SAMPLER_VERSION, str)


def test_type_aliases():
    import scios.runtime.observability.tracing.sampler as module

    for name in (
        "TraceId",
        "SpanId",
        "SampleRate",
        "SampleMetadata",
        "SampleAttributes",
        "SampleOptions",
        "SampleContext",
        "SamplePayload",
        "SampleHook",
        "SampleCallback",
        "SampleFilter",
        "SampleHistory",
    ):
        assert hasattr(module, name)


# ==============================================================================
# Part 2. Exceptions & Enums
# ==============================================================================


def test_sampler_error_hierarchy():
    assert issubclass(SamplingError, SamplerError)
    assert issubclass(InvalidSampleRateError, SamplerError)
    assert issubclass(SamplerClosedError, SamplerError)
    assert issubclass(SamplerFrozenError, SamplerError)
    assert issubclass(SamplerConfigurationError, SamplerError)


def test_sampling_decision_values():
    assert SamplingDecision.DROP.value == "drop"
    assert SamplingDecision.RECORD.value == "record"
    assert SamplingDecision.RECORD_AND_SAMPLE.value == "record_and_sample"


def test_sampler_type_values():
    assert SamplerType.ALWAYS_ON.value == "always_on"
    assert SamplerType.ALWAYS_OFF.value == "always_off"
    assert SamplerType.TRACE_ID_RATIO.value == "trace_id_ratio"
    assert SamplerType.PARENT_BASED.value == "parent_based"
    assert SamplerType.PROBABILISTIC.value == "probabilistic"
    assert SamplerType.ADAPTIVE.value == "adaptive"
    assert SamplerType.CUSTOM.value == "custom"


def test_sampler_state_values():
    assert SamplerState.CREATED.value == "created"
    assert SamplerState.INITIALIZED.value == "initialized"
    assert SamplerState.READY.value == "ready"
    assert SamplerState.RUNNING.value == "running"
    assert SamplerState.STOPPED.value == "stopped"
    assert SamplerState.FROZEN.value == "frozen"
    assert SamplerState.CLOSED.value == "closed"
    assert SamplerState.FAILED.value == "failed"


def test_sampler_capability_values():
    assert SamplerCapability.NONE.value == 0

    capabilities = [
        SamplerCapability.DETERMINISTIC,
        SamplerCapability.PROBABILISTIC,
        SamplerCapability.PARENT_BASED,
        SamplerCapability.ADAPTIVE,
        SamplerCapability.DYNAMIC_RATE,
        SamplerCapability.FILTERING,
        SamplerCapability.SERIALIZATION,
        SamplerCapability.CALLBACKS,
        SamplerCapability.HOOKS,
        SamplerCapability.METRICS,
    ]

    assert all(cap.value != 0 for cap in capabilities)


# ==============================================================================
# Part 3. Dataclasses
# ==============================================================================


def test_sampling_record_defaults():
    value = SamplingRecord()

    assert value.id
    assert isinstance(value.id, str)
    assert isinstance(value.timestamp, float)
    assert value.trace_id is None
    assert value.span_id is None
    assert value.decision is SamplingDecision.RECORD_AND_SAMPLE
    assert value.sampled is True
    assert value.probability == 1.0
    assert value.duration == 0.0
    assert value.metadata == {}
    assert value.attributes == {}


def test_sampling_record_custom_values():
    value = SamplingRecord(
        trace_id="trace-001",
        span_id="span-001",
        decision=SamplingDecision.RECORD,
        sampled=False,
        probability=0.5,
        duration=0.25,
        metadata={"source": "test"},
        attributes={"key": "value"},
    )

    assert value.trace_id == "trace-001"
    assert value.span_id == "span-001"
    assert value.decision is SamplingDecision.RECORD
    assert value.sampled is False
    assert value.probability == 0.5
    assert value.duration == 0.25
    assert value.metadata["source"] == "test"


def test_sampling_statistics_defaults():
    value = SamplingStatistics()

    assert value.samples == 0
    assert value.accepted == 0
    assert value.rejected == 0
    assert value.errors == 0
    assert value.acceptance_rate == 0.0
    assert value.rejection_rate == 0.0
    assert value.last_sample is None
    assert value.average_latency == 0.0
    assert value.minimum_latency == 0.0
    assert value.maximum_latency == 0.0
    assert value.bytes_processed == 0


def test_sampling_statistics_custom_values():
    value = SamplingStatistics(
        samples=10,
        accepted=7,
        rejected=3,
        errors=1,
        acceptance_rate=0.7,
        rejection_rate=0.3,
        last_sample=123.0,
        average_latency=0.01,
        minimum_latency=0.001,
        maximum_latency=0.05,
        bytes_processed=1000,
    )

    assert value.samples == 10
    assert value.accepted == 7
    assert value.rejected == 3
    assert value.errors == 1
    assert value.acceptance_rate == 0.7
    assert value.rejection_rate == 0.3
    assert value.bytes_processed == 1000


def test_sampling_result_defaults():
    value = SamplingResult()

    assert value.decision is SamplingDecision.RECORD_AND_SAMPLE
    assert value.sampled is True
    assert value.probability == 1.0
    assert value.trace_id is None
    assert value.span_id is None
    assert isinstance(value.timestamp, float)
    assert value.duration == 0.0
    assert value.metadata == {}
    assert value.attributes == {}
    assert value.record is None
    assert value.message == ""


def test_sampling_result_custom_values():
    value = SamplingResult(
        decision=SamplingDecision.RECORD,
        sampled=False,
        probability=0.25,
        trace_id="trace-001",
        span_id="span-001",
        duration=0.2,
        metadata={"x": 1},
        attributes={"y": 2},
        message="rejected",
    )

    assert value.decision is SamplingDecision.RECORD
    assert value.sampled is False
    assert value.probability == 0.25
    assert value.trace_id == "trace-001"
    assert value.span_id == "span-001"
    assert value.message == "rejected"


def test_sampling_record_compatibility_alias():
    assert SamplingRecord is SamplingResult


# ==============================================================================
# Part 4. Constructor
# ==============================================================================


def test_create_sampler(create_sampler):
    value = create_sampler()

    assert isinstance(value, TraceSampler)


def test_default_configuration(sampler):
    assert sampler.name == DEFAULT_SAMPLER_NAME
    assert sampler.sample_rate == DEFAULT_SAMPLE_RATE
    assert sampler.seed == DEFAULT_SEED
    assert sampler.encoding == DEFAULT_ENCODING
    assert sampler.history_limit == DEFAULT_HISTORY_LIMIT


def test_custom_configuration(create_sampler):
    value = create_sampler(
        name="custom",
        sample_rate=0.25,
        seed=42,
        parent_based=True,
        deterministic=True,
        metadata={"env": "test"},
        options={"mode": "strict"},
    )

    assert value.name == "custom"
    assert value.sample_rate == 0.25
    assert value.seed == 42
    assert value.parent_based is True
    assert value.deterministic is True
    assert value.options["mode"] == "strict"


@pytest.mark.parametrize(
    "rate",
    [-1.0, -0.01, 1.01, 2.0, float("nan"), float("inf")],
)
def test_invalid_sample_rate(create_sampler, rate):
    with pytest.raises(
        (InvalidSampleRateError, SamplerConfigurationError, ValueError),
    ):
        create_sampler(sample_rate=rate)


def test_invalid_sampler_type(create_sampler):
    with pytest.raises(
        (SamplerConfigurationError, ValueError),
    ):
        create_sampler(
            sampler_type="invalid",
        )


def test_seed_configuration(create_sampler):
    value = create_sampler(seed=42)

    assert value.seed == 42


def test_parent_based_configuration(create_sampler):
    value = create_sampler(parent_based=True)

    assert value.parent_based is True


def test_deterministic_configuration(create_sampler):
    value = create_sampler(deterministic=True)

    assert value.deterministic is True


def test_custom_sampler_function(create_sampler):
    def sampler_fn(*args, **kwargs):
        return True

    value = create_sampler(
        sampler_type=SamplerType.CUSTOM,
        sampler_fn=sampler_fn,
    )

    assert value.sampler_fn is sampler_fn


def test_metadata_configuration(create_sampler):
    value = create_sampler(
        metadata={"environment": "test"},
    )

    assert value.metadata["environment"] == "test"


def test_options_configuration(create_sampler):
    value = create_sampler(
        options={"strict": True},
    )

    assert value.options["strict"] is True


# ==============================================================================
# Part 5. Identity & Properties
# ==============================================================================


def test_id(sampler):
    assert isinstance(sampler.id, str)
    assert sampler.id


def test_uuid(sampler):
    assert sampler.uuid is not None


def test_name(sampler):
    assert sampler.name == DEFAULT_SAMPLER_NAME


def test_description(sampler):
    assert isinstance(sampler.description, str)


def test_version(sampler):
    assert sampler.version == SAMPLER_VERSION


def test_sampler_type(sampler):
    assert isinstance(sampler.sampler_type, SamplerType)


def test_sample_rate(sampler):
    assert 0.0 <= sampler.sample_rate <= 1.0


def test_seed(sampler):
    assert sampler.seed == DEFAULT_SEED


def test_parent_based(sampler):
    assert sampler.parent_based is False


def test_deterministic(sampler):
    assert sampler.deterministic is False


def test_encoding(sampler):
    assert sampler.encoding == DEFAULT_ENCODING


def test_history_limit(sampler):
    assert sampler.history_limit == DEFAULT_HISTORY_LIMIT


def test_options(sampler):
    assert isinstance(sampler.options, dict)


def test_capabilities(sampler):
    assert isinstance(
        sampler.capabilities,
        SamplerCapability,
    )


def test_enabled(sampler):
    assert isinstance(sampler.enabled, bool)


def test_initialized(sampler):
    assert isinstance(sampler.initialized, bool)


def test_running(sampler):
    assert isinstance(sampler.running, bool)


def test_active(sampler):
    assert isinstance(sampler.active, bool)


def test_frozen(sampler):
    assert isinstance(sampler.frozen, bool)


def test_closed(sampler):
    assert sampler.closed is False


def test_state(sampler):
    assert isinstance(sampler.state, SamplerState)


def test_created_at(sampler):
    assert sampler.created_at is not None


def test_updated_at(sampler):
    assert sampler.updated_at is not None


def test_last_sample(sampler):
    assert sampler.last_sample is None


def test_uptime(sampler):
    assert sampler.uptime >= 0.0


def test_last_decision(sampler):
    assert sampler.last_decision is None


def test_last_trace_id(sampler):
    assert sampler.last_trace_id is None


def test_last_span_id(sampler):
    assert sampler.last_span_id is None


def test_current_context(sampler):
    assert isinstance(sampler.current_context, dict)


# ==============================================================================
# Part 6. Lifecycle
# ==============================================================================


def test_initialize(sampler):
    result = sampler.initialize()

    assert result is sampler
    assert sampler.initialized is True


def test_start(sampler):
    sampler.initialize()

    result = sampler.start()

    assert result is sampler
    assert sampler.running is True


def test_stop(sampler):
    sampler.initialize()
    sampler.start()

    result = sampler.stop()

    assert result is sampler
    assert sampler.running is False


def test_freeze(sampler):
    sampler.initialize()
    sampler.start()

    result = sampler.freeze()

    assert result is sampler
    assert sampler.frozen is True


def test_unfreeze(sampler):
    sampler.initialize()
    sampler.start()
    sampler.freeze()

    result = sampler.unfreeze()

    assert result is sampler
    assert sampler.frozen is False


def test_close(sampler):
    result = sampler.close()

    assert result is sampler
    assert sampler.closed is True
    assert sampler.state is SamplerState.CLOSED


def test_reset(sampler):
    sampler.initialize()
    sampler.start()

    sampler.sample(
        trace_id="trace-001",
    )

    sampler.reset()

    assert sampler.sample_count == 0
    assert sampler.accepted_count == 0
    assert sampler.rejected_count == 0


def test_restart(sampler):
    sampler.initialize()
    sampler.start()
    sampler.stop()

    result = sampler.restart()

    assert result is sampler
    assert sampler.running is True


def test_cleanup(sampler):
    sampler.initialize()
    sampler.start()

    result = sampler.cleanup()

    assert result is sampler


def test_context_manager_enter(sampler):
    value = sampler.__enter__()

    assert value is sampler
    assert sampler.running is True


def test_context_manager_exit(sampler):
    sampler.__enter__()

    result = sampler.__exit__(
        None,
        None,
        None,
    )

    assert result is None
    assert sampler.closed is True


def test_closed_sampler_rejects_operation(sampler):
    sampler.close()

    with pytest.raises(
        (SamplerClosedError, SamplerError),
    ):
        sampler.sample(
            trace_id="trace-closed",
        )


def test_frozen_sampler_rejects_operation(sampler):
    sampler.initialize()
    sampler.start()
    sampler.freeze()

    with pytest.raises(
        (SamplerFrozenError, SamplerError),
    ):
        sampler.sample(
            trace_id="trace-frozen",
        )


# ==============================================================================
# Part 7. Validation
# ==============================================================================


def test_validate(sampler):
    assert sampler.validate() is True


def test_validate_rate(sampler):
    assert sampler.validate_rate(0.0) is True
    assert sampler.validate_rate(0.5) is True
    assert sampler.validate_rate(1.0) is True


def test_validate_seed(sampler):
    assert sampler.validate_seed() is True


def test_validate_configuration(sampler):
    assert sampler.validate_configuration() is True


def test_check_integrity(sampler):
    assert sampler.check_integrity() is True


def test_invalid_rate_detection(sampler):
    with pytest.raises(
        (InvalidSampleRateError, SamplerConfigurationError, ValueError),
    ):
        sampler.set_rate(2.0)


def test_invalid_seed_detection(sampler):
    with pytest.raises(
        (SamplerConfigurationError, ValueError, TypeError),
    ):
        sampler.reseed("invalid")


def test_invalid_state_detection(sampler):
    sampler._state = "invalid"

    assert sampler.validate() is False or sampler.check_integrity() is False


def test_invalid_history_limit_detection(sampler):
    sampler._history_limit = -1

    assert sampler.validate() is False or sampler.check_integrity() is False


def test_negative_counter_detection(sampler):
    sampler._statistics.samples = -1

    assert sampler.validate() is False or sampler.check_integrity() is False


def test_counter_integrity_detection(sampler):
    sampler._statistics.samples = 10
    sampler._statistics.accepted = 20

    assert sampler.validate() is False or sampler.check_integrity() is False


# ==============================================================================
# Part 8. Events & Hooks
# ==============================================================================


def test_before_sample(sampler):
    result = sampler.before_sample(
        trace_id="trace-001",
    )

    assert result is not False


def test_after_sample(sampler):
    result = sampler.after_sample(
        SamplingResult(),
    )

    assert result is not False


def test_add_hook(sampler):
    calls = []

    def hook(*args, **kwargs):
        calls.append((args, kwargs))

    result = sampler.add_hook(
        hook,
    )

    assert result is sampler
    assert hook in sampler.hooks


def test_remove_hook(sampler):
    def hook(*args, **kwargs):
        return None

    sampler.add_hook(hook)
    result = sampler.remove_hook(hook)

    assert result is sampler
    assert hook not in sampler.hooks


def test_clear_hooks(sampler):
    sampler.add_hook(lambda *a, **k: None)
    sampler.clear_hooks()

    assert len(sampler.hooks) == 0


def test_add_callback(sampler):
    callback = lambda *args, **kwargs: None

    result = sampler.add_callback(callback)

    assert result is sampler
    assert callback in sampler.callbacks


def test_remove_callback(sampler):
    callback = lambda *args, **kwargs: None

    sampler.add_callback(callback)
    result = sampler.remove_callback(callback)

    assert result is sampler
    assert callback not in sampler.callbacks


def test_clear_callbacks(sampler):
    sampler.add_callback(
        lambda *args, **kwargs: None,
    )

    sampler.clear_callbacks()

    assert len(sampler.callbacks) == 0


def test_emit_event(sampler):
    result = sampler.emit_event(
        "test",
        {"value": 1},
    )

    assert result is not False


def test_emit_event_safe(sampler):
    result = sampler._emit_event_safe(
        "test",
        {"value": 1},
    )

    assert result is not False


def test_hook_called_before_sampling(sampler):
    calls = []

    def hook(*args, **kwargs):
        calls.append("before")

    sampler.add_hook(hook)
    sampler.sample(trace_id="trace-001")

    assert "before" in calls


def test_hook_called_after_sampling(sampler):
    calls = []

    def hook(*args, **kwargs):
        calls.append("after")

    sampler.add_hook(hook)
    sampler.sample(trace_id="trace-001")

    assert calls


def test_callback_called_after_sampling(sampler):
    calls = []

    def callback(*args, **kwargs):
        calls.append("callback")

    sampler.add_callback(callback)
    sampler.sample(trace_id="trace-001")

    assert "callback" in calls


# ==============================================================================
# Part 9. Filtering & Context
# ==============================================================================


def test_add_filter(sampler):
    def filter_fn(value):
        return True

    result = sampler.add_filter(filter_fn)

    assert result is sampler
    assert filter_fn in sampler.filters


def test_remove_filter(sampler):
    def filter_fn(value):
        return True

    sampler.add_filter(filter_fn)
    result = sampler.remove_filter(filter_fn)

    assert result is sampler
    assert filter_fn not in sampler.filters


def test_clear_filters(sampler):
    sampler.add_filter(lambda value: True)
    sampler.clear_filters()

    assert len(sampler.filters) == 0


def test_apply_filters(sampler):
    sampler.add_filter(lambda value: True)

    assert sampler.apply_filters(
        {"id": "trace-001"},
    ) is True


def test_set_context(sampler):
    result = sampler.set_context(
        trace_id="trace-001",
        span_id="span-001",
    )

    assert result is sampler
    assert sampler.current_context["trace_id"] == "trace-001"


def test_update_context(sampler):
    sampler.set_context(
        trace_id="trace-001",
    )

    result = sampler.update_context(
        span_id="span-001",
    )

    assert result is sampler
    assert sampler.current_context["span_id"] == "span-001"


def test_clear_context(sampler):
    sampler.set_context(
        trace_id="trace-001",
    )

    result = sampler.clear_context()

    assert result is sampler
    assert sampler.current_context == {}


def test_filter_accept(sampler):
    sampler.add_filter(
        lambda value: value.get("accept") is True,
    )

    assert sampler.apply_filters(
        {"accept": True},
    ) is True


def test_filter_reject(sampler):
    sampler.add_filter(
        lambda value: value.get("accept") is True,
    )

    assert sampler.apply_filters(
        {"accept": False},
    ) is False


# ==============================================================================
# Part 10. Sampling Engine
# ==============================================================================


def test_sample(sampler):
    result = sampler.sample(
        trace_id="trace-001",
    )

    assert isinstance(
        result,
        SamplingResult,
    )


def test_sample_result_type(sampler):
    result = sampler.sample(
        trace_id="trace-001",
    )

    assert isinstance(result, SamplingResult)
    assert isinstance(result.decision, SamplingDecision)


def test_sample_many(sampler):
    results = sampler.sample_many(
        [
            {"trace_id": "trace-001"},
            {"trace_id": "trace-002"},
            {"trace_id": "trace-003"},
        ],
    )

    assert len(results) == 3
    assert all(
        isinstance(
            value,
            SamplingResult,
        )
        for value in results
    )


def test_sample_batch(sampler):
    results = sampler.sample_batch(
        [
            {"trace_id": "trace-001"},
            {"trace_id": "trace-002"},
        ],
    )

    assert len(results) == 2


def test_decision(sampler):
    result = sampler.decision(
        trace_id="trace-001",
    )

    assert isinstance(
        result,
        SamplingDecision,
    )


def test_probability(sampler):
    result = sampler.probability(
        trace_id="trace-001",
    )

    assert 0.0 <= result <= 1.0


def test_random(sampler):
    value = sampler.random()

    assert 0.0 <= value < 1.0


def test_next_probability(sampler):
    value = sampler.next_probability()

    assert 0.0 <= value <= 1.0


def test_always_on(always_on):
    result = always_on.sample(
        trace_id="trace-001",
    )

    assert result.sampled is True
    assert result.decision is SamplingDecision.RECORD_AND_SAMPLE


def test_always_off(always_off):
    result = always_off.sample(
        trace_id="trace-001",
    )

    assert result.sampled is False
    assert result.decision in {
        SamplingDecision.DROP,
        SamplingDecision.RECORD,
    }


def test_trace_id_ratio(create_sampler):
    value = create_sampler(
        sampler_type=SamplerType.TRACE_ID_RATIO,
        sample_rate=1.0,
        deterministic=True,
    )

    result = value.sample(
        trace_id="trace-001",
    )

    assert result.sampled is True


def test_parent_based(create_sampler):
    value = create_sampler(
        sampler_type=SamplerType.PARENT_BASED,
        parent_based=True,
    )

    result = value.sample(
        trace_id="trace-001",
        parent_sampled=True,
    )

    assert isinstance(result, SamplingResult)


def test_probabilistic(create_sampler):
    value = create_sampler(
        sampler_type=SamplerType.PROBABILISTIC,
        sample_rate=1.0,
    )

    result = value.sample(
        trace_id="trace-001",
    )

    assert result.sampled is True


def test_adaptive(create_sampler):
    value = create_sampler(
        sampler_type=SamplerType.ADAPTIVE,
        sample_rate=0.5,
    )

    result = value.sample(
        trace_id="trace-001",
    )

    assert isinstance(result, SamplingResult)


def test_custom_sampler(create_sampler):
    def sampler_fn(*args, **kwargs):
        return True

    value = create_sampler(
        sampler_type=SamplerType.CUSTOM,
        sampler_fn=sampler_fn,
    )

    result = value.sample(
        trace_id="trace-custom",
    )

    assert result.sampled is True


# ==============================================================================
# Part 11. Sampling Statistics
# ==============================================================================


def test_sample_count(sampler):
    before = sampler.sample_count

    sampler.sample(
        trace_id="trace-001",
    )

    assert sampler.sample_count == before + 1


def test_accepted_count(always_on):
    always_on.sample(
        trace_id="trace-001",
    )

    assert always_on.accepted_count >= 1


def test_rejected_count(always_off):
    always_off.sample(
        trace_id="trace-001",
    )

    assert always_off.rejected_count >= 1


def test_error_count(sampler):
    assert sampler.error_count >= 0


def test_success_rate(always_on):
    always_on.sample(
        trace_id="trace-001",
    )

    assert 0.0 <= always_on.success_rate <= 1.0


def test_failure_rate(always_off):
    always_off.sample(
        trace_id="trace-001",
    )

    assert 0.0 <= always_off.failure_rate <= 1.0


def test_decision_count(sampler):
    sampler.sample(
        trace_id="trace-001",
    )

    assert sampler.decision_count >= 1


def test_parent_sample_count(create_sampler):
    value = create_sampler(
        sampler_type=SamplerType.PARENT_BASED,
        parent_based=True,
    )

    value.sample(
        trace_id="trace-001",
        parent_sampled=True,
    )

    assert value.parent_sample_count >= 0


def test_forced_sample_count(sampler):
    assert sampler.forced_sample_count >= 0


def test_last_latency(sampler):
    sampler.sample(
        trace_id="trace-001",
    )

    assert sampler.last_latency >= 0.0


def test_minimum_latency(sampler):
    sampler.sample(
        trace_id="trace-001",
    )

    assert sampler.minimum_latency >= 0.0


def test_maximum_latency(sampler):
    sampler.sample(
        trace_id="trace-001",
    )

    assert sampler.maximum_latency >= sampler.minimum_latency


def test_statistics(sampler):
    value = sampler.statistics

    assert isinstance(
        value,
        SamplingStatistics,
    )


def test_statistics_update(sampler):
    before = sampler.sample_count

    sampler.sample(
        trace_id="trace-001",
    )

    assert sampler.statistics.samples == before + 1


def test_acceptance_rate(always_on):
    always_on.sample(
        trace_id="trace-001",
    )

    assert 0.0 <= always_on.statistics.acceptance_rate <= 1.0


def test_rejection_rate(always_off):
    always_off.sample(
        trace_id="trace-001",
    )

    assert 0.0 <= always_off.statistics.rejection_rate <= 1.0


def test_history_update(sampler):
    sampler.sample(
        trace_id="trace-001",
    )

    assert sampler.history


def test_history_limit(create_sampler):
    value = create_sampler()

    for index in range(
        min(value.history_limit + 5, 20),
    ):
        value.sample(
            trace_id=f"trace-{index}",
        )

    assert len(value.history) <= value.history_limit


def test_cache_update(sampler):
    sampler.sample(
        trace_id="trace-001",
    )

    assert sampler.cache is not None


# ==============================================================================
# Part 12. Diagnostics
# ==============================================================================


def test_diagnostics(sampler):
    value = sampler.diagnostics()

    assert isinstance(value, dict)


def test_health(sampler):
    assert isinstance(
        sampler.health(),
        bool,
    )


def test_metrics(sampler):
    value = sampler.metrics()

    assert isinstance(value, dict)


def test_summary(sampler):
    value = sampler.summary()

    assert isinstance(value, dict)


def test_healthy_sampler(sampler):
    assert sampler.health() is True


def test_disabled_sampler(create_sampler):
    value = create_sampler(
        options={"enabled": False},
    )

    assert value.enabled is False or value.health() is False


def test_closed_sampler(sampler):
    sampler.close()

    assert sampler.closed is True
    assert sampler.health() is False


def test_failed_sampler(sampler):
    sampler._state = SamplerState.FAILED

    assert sampler.health() is False


# ==============================================================================
# Part 13. Persistence
# ==============================================================================


def test_to_dict(sampler):
    value = sampler.to_dict()

    assert isinstance(value, dict)
    assert value["id"] == sampler.id
    assert value["name"] == sampler.name


def test_from_dict(sampler):
    data = sampler.to_dict()

    value = TraceSampler.from_dict(
        data,
    )

    assert isinstance(value, TraceSampler)
    assert value.name == sampler.name
    assert value.sample_rate == sampler.sample_rate


def test_to_json(sampler):
    value = sampler.to_json()

    assert isinstance(value, str)

    decoded = json.loads(value)

    assert isinstance(decoded, dict)


def test_from_json(sampler):
    data = sampler.to_json()

    value = TraceSampler.from_json(
        data,
    )

    assert isinstance(value, TraceSampler)
    assert value.name == sampler.name


def test_snapshot(sampler):
    value = sampler.snapshot()

    assert isinstance(value, dict)
    assert value["id"] == sampler.id


def test_restore(sampler):
    snapshot = sampler.snapshot()

    sampler.set_rate(0.25)

    sampler.restore(snapshot)

    assert sampler.sample_rate == snapshot["sample_rate"]


def test_restore_configuration(sampler):
    snapshot = sampler.snapshot()

    sampler.set_rate(0.25)

    sampler.restore(snapshot)

    assert sampler.sample_rate == snapshot["sample_rate"]


def test_restore_runtime(sampler):
    sampler.initialize()
    sampler.start()

    snapshot = sampler.snapshot()

    sampler.stop()
    sampler.restore(snapshot)

    assert sampler.state in {
        SamplerState.RUNNING,
        SamplerState.READY,
        SamplerState.INITIALIZED,
        SamplerState.CREATED,
    }


def test_restore_statistics(sampler):
    sampler.sample(
        trace_id="trace-001",
    )

    snapshot = sampler.snapshot()

    restored = TraceSampler.from_dict(
        snapshot,
    )

    assert restored.sample_count == sampler.sample_count


def test_restore_counters(sampler):
    sampler.sample(
        trace_id="trace-001",
    )

    snapshot = sampler.snapshot()

    restored = TraceSampler.from_dict(
        snapshot,
    )

    assert restored.accepted_count == sampler.accepted_count
    assert restored.rejected_count == sampler.rejected_count


def test_restore_performance(sampler):
    sampler.sample(
        trace_id="trace-001",
    )

    snapshot = sampler.snapshot()

    restored = TraceSampler.from_dict(
        snapshot,
    )

    assert restored.last_latency == sampler.last_latency


def test_restore_metadata(create_sampler):
    sampler = create_sampler(
        metadata={"environment": "test"},
    )

    snapshot = sampler.snapshot()

    restored = TraceSampler.from_dict(
        snapshot,
    )

    assert restored.metadata["environment"] == "test"


# ==============================================================================
# Part 14. Copying
# ==============================================================================


def test_clone(sampler):
    value = sampler.clone()

    assert isinstance(value, TraceSampler)
    assert value.id == sampler.id


def test_copy(sampler):
    value = sampler.copy()

    assert isinstance(value, TraceSampler)
    assert value.id == sampler.id


def test_clone_is_independent(sampler):
    sampler.set_context(
        trace_id="trace-001",
    )

    clone = sampler.clone()

    clone.set_context(
        trace_id="trace-002",
    )

    assert sampler.current_context["trace_id"] == "trace-001"
    assert clone.current_context["trace_id"] == "trace-002"


def test_copy_is_independent(sampler):
    sampler.set_context(
        trace_id="trace-001",
    )

    value = sampler.copy()

    value.set_context(
        trace_id="trace-002",
    )

    assert sampler.current_context["trace_id"] == "trace-001"
    assert value.current_context["trace_id"] == "trace-002"


# ==============================================================================
# Part 15. Utilities
# ==============================================================================


def test_set_rate(sampler):
    result = sampler.set_rate(0.25)

    assert result is sampler
    assert sampler.sample_rate == 0.25


def test_get_rate(sampler):
    sampler.set_rate(0.25)

    assert sampler.get_rate() == 0.25


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (-1.0, 0.0),
        (0.0, 0.0),
        (0.25, 0.25),
        (0.5, 0.5),
        (1.0, 1.0),
        (2.0, 1.0),
    ],
)
def test_clamp_rate(sampler, value, expected):
    assert sampler.clamp_rate(value) == expected


def test_touch(sampler):
    before = sampler.updated_at

    time.sleep(0.001)

    result = sampler.touch()

    assert result is sampler
    assert sampler.updated_at >= before


def test_age(sampler):
    assert sampler.age() >= 0.0


def test_timestamp(sampler):
    value = sampler.timestamp()

    assert isinstance(value, float)


def test_is_ready(sampler):
    assert isinstance(
        sampler.is_ready(),
        bool,
    )


def test_is_sampling(sampler):
    assert isinstance(
        sampler.is_sampling(),
        bool,
    )


def test_reset_seed(create_sampler):
    value = create_sampler(
        seed=42,
    )

    result = value.reset_seed()

    assert result is value


def test_reseed(create_sampler):
    value = create_sampler()

    result = value.reseed(42)

    assert result is value
    assert value.seed == 42


def test_compact(sampler):
    result = sampler.compact()

    assert result is sampler


# ==============================================================================
# Part 16. Python Protocols
# ==============================================================================


def test_repr(sampler):
    value = repr(sampler)

    assert isinstance(value, str)
    assert "TraceSampler" in value


def test_str(sampler):
    value = str(sampler)

    assert isinstance(value, str)
    assert sampler.name in value


def test_bool(sampler):
    assert bool(sampler) is True


def test_call(sampler):
    value = sampler(
        trace_id="trace-001",
    )

    assert isinstance(
        value,
        SamplingResult,
    )


def test_len(sampler):
    assert len(sampler) == len(sampler.history)


def test_iter(sampler):
    sampler.sample(
        trace_id="trace-001",
    )

    values = list(iter(sampler))

    assert values


def test_contains(sampler):
    result = sampler.sample(
        trace_id="trace-001",
    )

    assert result in sampler


def test_eq(sampler):
    clone = sampler.clone()

    assert sampler == clone


def test_hash(sampler):
    value = hash(sampler)

    assert isinstance(value, int)


# ==============================================================================
# Part 17. Integration
# ==============================================================================


def test_sampler_complete_workflow(create_sampler):
    value = create_sampler(
        name="workflow-sampler",
        sample_rate=1.0,
        sampler_type=SamplerType.ALWAYS_ON,
        deterministic=True,
    )

    assert value.validate() is True

    value.initialize()
    value.start()

    result = value.sample(
        trace_id="trace-workflow",
        span_id="span-workflow",
    )

    assert isinstance(
        result,
        SamplingResult,
    )

    assert result.sampled is True
    assert value.sample_count == 1
    assert value.accepted_count == 1

    value.stop()

    assert value.running is False


def test_sampler_lifecycle_workflow(create_sampler):
    value = create_sampler()

    assert value.state is SamplerState.CREATED

    value.initialize()

    assert value.initialized is True

    value.start()

    assert value.running is True

    value.freeze()

    assert value.frozen is True

    value.unfreeze()

    assert value.frozen is False

    value.stop()

    assert value.running is False

    value.restart()

    assert value.running is True

    value.close()

    assert value.closed is True


def test_sampler_sampling_workflow(create_sampler):
    value = create_sampler(
        sampler_type=SamplerType.ALWAYS_ON,
        sample_rate=1.0,
    )

    results = value.sample_many(
        [
            {"trace_id": "trace-001"},
            {"trace_id": "trace-002"},
            {"trace_id": "trace-003"},
        ],
    )

    assert len(results) == 3
    assert all(
        result.sampled
        for result in results
    )

    assert value.sample_count == 3
    assert value.accepted_count == 3
    assert value.rejected_count == 0


def test_sampler_persistence_workflow(create_sampler):
    value = create_sampler(
        name="persistent",
        sample_rate=0.75,
        seed=42,
        metadata={
            "environment": "test",
        },
        options={
            "strict": True,
        },
    )

    value.sample(
        trace_id="trace-001",
    )

    snapshot = value.snapshot()

    restored = TraceSampler.from_dict(
        snapshot,
    )

    assert restored.name == value.name
    assert restored.sample_rate == value.sample_rate
    assert restored.seed == value.seed
    assert restored.sample_count == value.sample_count
    assert restored.metadata == value.metadata


def test_sampler_clone_workflow(create_sampler):
    value = create_sampler(
        name="clone-source",
        sample_rate=0.5,
        metadata={
            "environment": "test",
        },
    )

    value.sample(
        trace_id="trace-001",
    )

    clone = value.clone()

    assert clone == value
    assert clone is not value

    clone.set_rate(0.25)

    assert clone.sample_rate == 0.25
    assert value.sample_rate == 0.5


# ==============================================================================
# End
# ==============================================================================
