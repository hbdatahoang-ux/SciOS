"""
SciOS-NG Observability
Tracing Test - Sampler

Tests:

- Creation
- Sampling decisions
- Configuration
- Serialization
- Diagnostics
- Protocols
"""


from __future__ import annotations


import copy
import json

import pytest


from scios.runtime.observability.tracing.sampler import (
    Sampler,
)



# ============================================================
# Part 1 – Fixtures
# ============================================================


@pytest.fixture
def sampler() -> Sampler:
    """
    Empty/default sampler.

    Expected:
    - default configuration
    - ready for sampling
    """

    return Sampler()



@pytest.fixture
def configured_sampler() -> Sampler:
    """
    Sampler with custom configuration.

    Example:
    - probability sampling
    - rate = 0.5
    """

    sampler = Sampler(
        rate=0.5,
    )

    return sampler
# ============================================================
# Part 2 – Creation
# ============================================================


def test_sampler_creation(
    sampler,
):
    """
    Test sampler object creation.
    """

    assert sampler is not None



def test_default_configuration(
    sampler,
):
    """
    Test default sampler configuration.

    Expected:
    - valid default rate
    - enabled sampling
    """

    assert sampler.validate() is True


    assert sampler.rate is not None


    assert (
        0.0
        <=
        sampler.rate
        <=
        1.0
    )
# ============================================================
# Part 3 – Basic Sampling
# ============================================================


def test_should_sample(
    configured_sampler,
):
    """
    Sampler should return True
    when sampling probability allows it.
    """

    result = configured_sampler.should_sample()

    assert isinstance(
        result,
        bool,
    )


def test_should_not_sample(
    sampler,
):
    """
    Default sampler should be able
    to reject sampling.
    """

    sampler.rate = 0.0

    result = sampler.should_sample()

    assert (
        result
        is False
    )


def test_sample_rate_zero(
    sampler,
):
    """
    Sampling rate 0 means
    nothing is sampled.
    """

    sampler.set_rate(
        0.0
    )

    for _ in range(100):
        assert (
            sampler.should_sample()
            is False
        )


def test_sample_rate_one(
    sampler,
):
    """
    Sampling rate 1 means
    everything is sampled.
    """

    sampler.set_rate(
        1.0
    )

    for _ in range(100):
        assert (
            sampler.should_sample()
            is True
        )
# ============================================================
# Part 4 – Decision API
# ============================================================


def test_sample(
    configured_sampler,
):
    """
    Basic sampling decision API.
    """

    result = configured_sampler.sample()

    assert isinstance(
        result,
        bool,
    )



def test_sample_with_context(
    configured_sampler,
):
    """
    Sampling with execution context.
    """

    context = {
        "service": "scios",
        "operation": "runtime",
    }


    result = configured_sampler.sample(
        context=context,
    )


    assert isinstance(
        result,
        bool,
    )



def test_sample_trace_id(
    configured_sampler,
):
    """
    Sampling decision based on trace id.
    """

    trace_id = (
        "trace-123456"
    )


    result = configured_sampler.sample(
        trace_id=trace_id,
    )


    assert isinstance(
        result,
        bool,
    )



def test_sample_span_id(
    configured_sampler,
):
    """
    Sampling decision based on span id.
    """

    span_id = (
        "span-abcdef"
    )


    result = configured_sampler.sample(
        span_id=span_id,
    )


    assert isinstance(
        result,
        bool,
    )
# ============================================================
# Part 5 – Configuration
# ============================================================


def test_set_rate(
    sampler,
):
    """
    Test updating sampling rate.
    """

    sampler.set_rate(
        0.5
    )

    assert (
        sampler.get_rate()
        ==
        0.5
    )



def test_get_rate(
    sampler,
):
    """
    Test reading sampling rate.
    """

    rate = (
        sampler.get_rate()
    )

    assert isinstance(
        rate,
        float,
    )



def test_update_config(
    sampler,
):
    """
    Test bulk configuration update.
    """

    sampler.update_config(
        {
            "rate": 0.25,
            "enabled": True,
        }
    )


    assert (
        sampler.get_rate()
        ==
        0.25
    )


    assert (
        sampler.enabled
        is True
    )



def test_reset_config(
    configured_sampler,
):
    """
    Test restoring default configuration.
    """

    configured_sampler.reset_config()


    assert (
        configured_sampler.get_rate()
        ==
        1.0
    )


    assert (
        configured_sampler.enabled
        is True
    )
# ============================================================
# Part 6 – Modes
# ============================================================


def test_always_sampler():
    """
    Always sampler should always sample.
    """

    sampler = Sampler(
        mode="always"
    )


    assert (
        sampler.should_sample()
        is True
    )



def test_never_sampler():
    """
    Never sampler should never sample.
    """

    sampler = Sampler(
        mode="never"
    )


    assert (
        sampler.should_sample()
        is False
    )



def test_probability_sampler():
    """
    Probability sampler should follow configured rate.
    """

    sampler = Sampler(
        mode="probability",
        rate=1.0,
    )


    assert (
        sampler.should_sample()
        is True
    )


    sampler.set_rate(
        0.0
    )


    assert (
        sampler.should_sample()
        is False
    )



def test_parent_based_sampler():
    """
    Parent based sampler inherits parent decision.
    """

    sampler = Sampler(
        mode="parent_based"
    )


    parent_context = {
        "sampled": True,
    }


    assert (
        sampler.should_sample(
            context=parent_context
        )
        is True
    )


    parent_context = {
        "sampled": False,
    }


    assert (
        sampler.should_sample(
            context=parent_context
        )
        is False
    )
# ============================================================
# Part 7 – Validation
# ============================================================


def test_invalid_rate_negative(
    sampler,
):
    """
    Negative sampling rate must fail.
    """

    with pytest.raises(
        Exception
    ):
        sampler.set_rate(
            -0.1
        )



def test_invalid_rate_over_one(
    sampler,
):
    """
    Sampling rate greater than 1 must fail.
    """

    with pytest.raises(
        Exception
    ):
        sampler.set_rate(
            1.1
        )



def test_validate(
    configured_sampler,
):
    """
    Sampler configuration should be valid.
    """

    assert (
        configured_sampler
        .validate()
        is True
    )
# ============================================================
# Part 8 – Serialization
# ============================================================


def test_to_dict(
    configured_sampler,
):
    """
    Export sampler configuration.
    """

    data = (
        configured_sampler
        .to_dict()
    )

    assert isinstance(
        data,
        dict,
    )

    assert (
        "rate"
        in data
    )



def test_from_dict(
    configured_sampler,
):
    """
    Restore sampler from dictionary.
    """

    data = (
        configured_sampler
        .to_dict()
    )

    restored = (
        configured_sampler
        .from_dict(data)
    )

    assert (
        restored.get_rate()
        ==
        configured_sampler.get_rate()
    )



def test_to_json(
    configured_sampler,
):
    """
    Serialize sampler to JSON.
    """

    value = (
        configured_sampler
        .to_json()
    )

    assert isinstance(
        value,
        str,
    )

    assert (
        "rate"
        in value
    )



def test_from_json(
    configured_sampler,
):
    """
    Restore sampler from JSON.
    """

    value = (
        configured_sampler
        .to_json()
    )

    restored = (
        configured_sampler
        .from_json(value)
    )

    assert (
        restored.get_rate()
        ==
        configured_sampler.get_rate()
    )



def test_snapshot(
    configured_sampler,
):
    """
    Create sampler snapshot.
    """

    snapshot = (
        configured_sampler
        .snapshot()
    )

    assert isinstance(
        snapshot,
        dict,
    )

    assert (
        "rate"
        in snapshot
    )



def test_restore(
    configured_sampler,
):
    """
    Restore sampler from snapshot.
    """

    snapshot = (
        configured_sampler
        .snapshot()
    )


    restored = (
        configured_sampler
        .restore(snapshot)
    )


    assert (
        restored.get_rate()
        ==
        configured_sampler.get_rate()
    )
# ============================================================
# Part 9 – Clone / Copy
# ============================================================

import copy



def test_clone(
    configured_sampler,
):
    """
    Clone sampler instance.
    """

    cloned = (
        configured_sampler
        .clone()
    )


    assert cloned is not configured_sampler


    assert (
        cloned.get_rate()
        ==
        configured_sampler.get_rate()
    )



def test_copy(
    configured_sampler,
):
    """
    Explicit copy method.
    """

    copied = (
        configured_sampler
        .copy()
    )


    assert copied is not configured_sampler


    assert (
        copied.get_rate()
        ==
        configured_sampler.get_rate()
    )



def test_python_copy(
    configured_sampler,
):
    """
    Support copy.copy().
    """

    copied = copy.copy(
        configured_sampler
    )


    assert copied is not configured_sampler


    assert (
        copied.get_rate()
        ==
        configured_sampler.get_rate()
    )



def test_python_deepcopy(
    configured_sampler,
):
    """
    Support copy.deepcopy().
    """

    copied = copy.deepcopy(
        configured_sampler
    )


    assert copied is not configured_sampler


    assert (
        copied.get_rate()
        ==
        configured_sampler.get_rate()
    )
# ============================================================
# Part 10 – Diagnostics
# ============================================================


def test_diagnostics(
    configured_sampler,
):
    """
    Validate diagnostic information.
    """

    result = (
        configured_sampler
        .diagnostics()
    )


    assert isinstance(
        result,
        dict,
    )


    assert (
        "rate"
        in result
    )


    assert (
        "mode"
        in result
    )


    assert (
        "valid"
        in result
    )


    assert (
        result["valid"]
        is True
    )



def test_summary(
    configured_sampler,
):
    """
    Validate sampler summary.
    """

    result = (
        configured_sampler
        .summary()
    )


    assert isinstance(
        result,
        dict,
    )


    assert (
        "rate"
        in result
    )


    assert (
        "mode"
        in result
    )
# ============================================================
# Part 11 – Python Protocols
# ============================================================


def test_repr(
    configured_sampler,
):
    """
    Test official representation.
    """

    value = repr(
        configured_sampler
    )


    assert isinstance(
        value,
        str,
    )


    assert (
        "Sampler"
        in value
    )



def test_str(
    configured_sampler,
):
    """
    Test human readable string.
    """

    value = str(
        configured_sampler
    )


    assert isinstance(
        value,
        str,
    )


    assert len(
        value
    ) > 0



def test_eq():
    """
    Test sampler equality.
    """

    from scios.runtime.observability.tracing.sampler import (
        Sampler,
    )


    first = Sampler(
        rate=0.5,
    )


    second = Sampler(
        rate=0.5,
    )


    assert (
        first
        ==
        second
    )



def test_hash(
    configured_sampler,
):
    """
    Test sampler hash.
    """

    value = hash(
        configured_sampler
    )


    assert isinstance(
        value,
        int,
    )
# ============================================================
# Part 12 – Statistics
# ============================================================


def test_sample_count(
    sampler,
):
    """
    Verify total sampling attempts counter.
    """

    assert (
        sampler.sample_count
        ==
        0
    )


    sampler.sample()


    assert (
        sampler.sample_count
        ==
        1
    )



def test_decision_count(
    sampler,
):
    """
    Verify sampling decision counters.
    """

    sampler.sample()


    stats = (
        sampler.statistics()
    )


    assert isinstance(
        stats,
        dict,
    )


    assert (
        "decisions"
        in stats
    )



def test_statistics(
    configured_sampler,
):
    """
    Verify statistics output.
    """

    configured_sampler.sample()


    result = (
        configured_sampler.statistics()
    )


    assert isinstance(
        result,
        dict,
    )


    assert (
        "sample_count"
        in result
    )


    assert (
        "decision_count"
        in result
    )
# ==========================================================
# Part 13 – Edge Cases
# ==========================================================


def test_zero_rate_sampler():
    """
    Sample rate = 0 must never sample.
    """

    sampler = Sampler(
        rate=0.0
    )

    for _ in range(100):
        assert (
            sampler.should_sample()
            is False
        )



def test_full_rate_sampler():
    """
    Sample rate = 1 must always sample.
    """

    sampler = Sampler(
        rate=1.0
    )

    for _ in range(100):
        assert (
            sampler.should_sample()
            is True
        )



def test_large_number_sampling():
    """
    Stress test with many sampling decisions.
    """

    sampler = Sampler(
        rate=0.5
    )

    decisions = []

    for _ in range(10000):
        decisions.append(
            sampler.should_sample()
        )


    assert len(decisions) == 10000


    assert all(
        isinstance(
            value,
            bool,
        )
        for value in decisions
    )



def test_empty_context():
    """
    Empty context should be accepted.
    """

    sampler = Sampler(
        rate=0.5
    )


    result = sampler.sample(
        context={}
    )


    assert isinstance(
        result,
        bool,
    )



def test_invalid_context():
    """
    Invalid context type should raise error.
    """

    sampler = Sampler(
        rate=0.5
    )


    with pytest.raises(
        Exception
    ):

        sampler.sample(
            context="invalid"
        )                                                    