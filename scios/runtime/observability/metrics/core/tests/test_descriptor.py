# ==============================================================================
# Part 1. Imports
# ==============================================================================

import pytest

from scios.runtime.observability.metrics.core.descriptor import (
    DEFAULT_ENABLED,
    DEFAULT_MONOTONIC,
    DEFAULT_UNIT,
    InvalidMetricNameError,
    InvalidMetricTypeError,
    MetricDescriptor,
    MetricType,
    MetricUnit,
)


# ==============================================================================
# Part 2. Construction
# ==============================================================================


def test_default_descriptor():

    descriptor = MetricDescriptor(
        name="requests_total",
        metric_type=MetricType.COUNTER,
    )

    assert isinstance(descriptor, MetricDescriptor)


def test_custom_name():

    descriptor = MetricDescriptor(
        name="cpu_usage",
        metric_type=MetricType.GAUGE,
    )

    assert descriptor.name == "cpu_usage"


def test_custom_description():

    descriptor = MetricDescriptor(
        name="latency",
        metric_type=MetricType.HISTOGRAM,
        description="Request latency",
    )

    assert descriptor.description == "Request latency"


def test_custom_unit():

    descriptor = MetricDescriptor(
        name="latency",
        metric_type=MetricType.TIMER,
        unit=MetricUnit.MILLISECONDS,
    )

    assert descriptor.unit == MetricUnit.MILLISECONDS


def test_custom_metric_type():

    descriptor = MetricDescriptor(
        name="errors",
        metric_type=MetricType.COUNTER,
    )

    assert descriptor.metric_type == MetricType.COUNTER


# ==============================================================================
# Part 3. Defaults
# ==============================================================================


def test_default_unit():

    descriptor = MetricDescriptor(
        name="requests",
        metric_type=MetricType.COUNTER,
    )

    assert descriptor.unit == MetricUnit(DEFAULT_UNIT)


def test_default_enabled():

    descriptor = MetricDescriptor(
        name="requests",
        metric_type=MetricType.COUNTER,
    )

    assert descriptor.enabled is DEFAULT_ENABLED


def test_default_monotonic():

    descriptor = MetricDescriptor(
        name="requests",
        metric_type=MetricType.COUNTER,
    )

    assert descriptor.monotonic is DEFAULT_MONOTONIC


# ==============================================================================
# Part 4. Validation
# ==============================================================================


def test_invalid_name():

    with pytest.raises(InvalidMetricNameError):

        MetricDescriptor(
            name="",
            metric_type=MetricType.COUNTER,
        )


def test_invalid_metric_type():

    with pytest.raises(InvalidMetricTypeError):

        MetricDescriptor(
            name="requests",
            metric_type="unknown",
        )


def test_invalid_unit():

    descriptor = MetricDescriptor(
        name="requests",
        metric_type=MetricType.COUNTER,
        unit="whatever",
    )

    assert descriptor.unit == MetricUnit.CUSTOM


# ==============================================================================
# Part 5. Properties
# ==============================================================================


def test_name():

    descriptor = MetricDescriptor(
        name="requests",
        metric_type=MetricType.COUNTER,
    )

    assert descriptor.name == "requests"


def test_description():

    descriptor = MetricDescriptor(
        name="requests",
        metric_type=MetricType.COUNTER,
        description="Total requests",
    )

    assert descriptor.description == "Total requests"


def test_metric_type():

    descriptor = MetricDescriptor(
        name="cpu",
        metric_type=MetricType.GAUGE,
    )

    assert descriptor.metric_type == MetricType.GAUGE

    assert descriptor.is_gauge


def test_unit():

    descriptor = MetricDescriptor(
        name="latency",
        metric_type=MetricType.TIMER,
        unit=MetricUnit.MILLISECONDS,
    )

    assert descriptor.unit == MetricUnit.MILLISECONDS


def test_monotonic():

    descriptor = MetricDescriptor(
        name="requests",
        metric_type=MetricType.COUNTER,
        monotonic=True,
    )

    assert descriptor.monotonic is True

    assert descriptor.is_monotonic

# ==============================================================================
# Part 6. Serialization
# ==============================================================================

import json

from scios.runtime.observability.metrics.core.descriptor import (
    __all__,
    DESCRIPTOR_API_VERSION,
    DESCRIPTOR_VERSION,
)


def test_to_dict():

    descriptor = MetricDescriptor(
        name="requests",
        metric_type=MetricType.COUNTER,
        description="Request counter",
        unit=MetricUnit.COUNT,
        monotonic=True,
    )

    data = descriptor.to_dict()

    assert data["name"] == "requests"
    assert data["metric_type"] == "counter"
    assert data["description"] == "Request counter"
    assert data["unit"] == "count"
    assert data["monotonic"] is True


def test_from_dict():

    data = {
        "name": "cpu",
        "metric_type": "gauge",
        "description": "CPU usage",
        "unit": "percent",
        "enabled": True,
        "monotonic": False,
    }

    descriptor = MetricDescriptor.from_dict(data)

    assert descriptor.name == "cpu"
    assert descriptor.metric_type == MetricType.GAUGE
    assert descriptor.unit == MetricUnit.PERCENT


def test_to_json():

    descriptor = MetricDescriptor(
        name="latency",
        metric_type=MetricType.TIMER,
    )

    text = descriptor.to_json()

    data = json.loads(text)

    assert data["name"] == "latency"


def test_from_json():

    text = json.dumps(
        {
            "name": "memory",
            "metric_type": "gauge",
            "unit": "bytes",
        }
    )

    descriptor = MetricDescriptor.from_json(text)

    assert descriptor.name == "memory"
    assert descriptor.metric_type == MetricType.GAUGE


# ==============================================================================
# Part 7. Copy
# ==============================================================================


def test_copy():

    descriptor = MetricDescriptor(
        name="requests",
        metric_type=MetricType.COUNTER,
    )

    copied = descriptor.copy()

    assert copied == descriptor

    assert copied is not descriptor


def test_clone():

    descriptor = MetricDescriptor(
        name="requests",
        metric_type=MetricType.COUNTER,
    )

    cloned = descriptor.clone()

    assert cloned == descriptor

    assert cloned is not descriptor


# ==============================================================================
# Part 8. Equality
# ==============================================================================


def test_eq():

    d1 = MetricDescriptor(
        name="requests",
        metric_type=MetricType.COUNTER,
    )

    d2 = MetricDescriptor(
        name="requests",
        metric_type=MetricType.COUNTER,
    )

    assert d1 == d2


def test_hash():

    d1 = MetricDescriptor(
        name="requests",
        metric_type=MetricType.COUNTER,
    )

    d2 = MetricDescriptor(
        name="requests",
        metric_type=MetricType.COUNTER,
    )

    assert hash(d1) == hash(d2)


# ==============================================================================
# Part 9. Representation
# ==============================================================================


def test_repr():

    descriptor = MetricDescriptor(
        name="requests",
        metric_type=MetricType.COUNTER,
    )

    text = repr(descriptor)

    assert "MetricDescriptor" in text

    assert "requests" in text


def test_str():

    descriptor = MetricDescriptor(
        name="requests",
        metric_type=MetricType.COUNTER,
    )

    assert str(descriptor) == "requests[counter]"


# ==============================================================================
# Part 10. Public API
# ==============================================================================


def test_all():

    assert "MetricDescriptor" in __all__

    assert "MetricType" in __all__

    assert "MetricUnit" in __all__


def test_version():

    assert DESCRIPTOR_VERSION

    assert DESCRIPTOR_API_VERSION


# ==============================================================================
# Part 11. Regression
# ==============================================================================


def test_name_is_trimmed():

    descriptor = MetricDescriptor(
        name="   requests   ",
        metric_type=MetricType.COUNTER,
    )

    assert descriptor.name == "requests"


def test_string_metric_type_is_converted():

    descriptor = MetricDescriptor(
        name="cpu",
        metric_type="gauge",
    )

    assert descriptor.metric_type is MetricType.GAUGE


def test_string_unit_is_converted():

    descriptor = MetricDescriptor(
        name="latency",
        metric_type=MetricType.TIMER,
        unit="milliseconds",
    )

    assert descriptor.unit is MetricUnit.MILLISECONDS


def test_unknown_unit_becomes_custom():

    descriptor = MetricDescriptor(
        name="custom",
        metric_type=MetricType.GAUGE,
        unit="frames",
    )

    assert descriptor.unit is MetricUnit.CUSTOM    