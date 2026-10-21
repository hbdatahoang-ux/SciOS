# ==============================================================================
# Part 1. Imports
# ==============================================================================

import pytest

from scios.runtime.observability.metrics.core.labels import (
    LABEL_KEY_MAX_LENGTH,
    LABEL_VALUE_MAX_LENGTH,
    LabelValidationError,
    MetricLabels,
)


# ==============================================================================
# Part 2. Construction
# ==============================================================================

def test_default_labels():
    labels = MetricLabels()

    assert isinstance(labels, MetricLabels)
    assert labels.labels == {}
    assert len(labels) == 0


def test_custom_labels():
    labels = MetricLabels(
        {
            "host": "localhost",
            "service": "api",
        }
    )

    assert labels.labels == {
        "host": "localhost",
        "service": "api",
    }


# ==============================================================================
# Part 3. Defaults
# ==============================================================================

def test_empty_labels():
    labels = MetricLabels()

    assert labels.labels == {}
    assert labels.is_empty
    assert labels.size == 0


# ==============================================================================
# Part 4. Validation
# ==============================================================================

def test_invalid_labels():
    with pytest.raises(TypeError):
        MetricLabels(
            ["invalid"]
        )


def test_invalid_key():
    labels = MetricLabels()

    with pytest.raises(LabelValidationError):
        labels.add("", "value")

    with pytest.raises(LabelValidationError):
        labels.add(" " * 4, "value")

    with pytest.raises(LabelValidationError):
        labels.add(
            "a" * (LABEL_KEY_MAX_LENGTH + 1),
            "value",
        )


def test_invalid_value():
    labels = MetricLabels()

    with pytest.raises(LabelValidationError):
        labels.add(
            "key",
            "v" * (LABEL_VALUE_MAX_LENGTH + 1),
        )


# ==============================================================================
# Part 5. Properties
# ==============================================================================

def test_labels():
    labels = MetricLabels(
        {
            "env": "prod",
        }
    )

    assert labels.labels == {
        "env": "prod",
    }

    assert labels.size == 1
    assert not labels.is_empty

# ==============================================================================
# Part 6. Operations
# ==============================================================================

def test_add():
    labels = MetricLabels()

    labels.add("host", "localhost")

    assert labels["host"] == "localhost"


def test_update():
    labels = MetricLabels(
        {"a": "1"}
    )

    labels.update(
        {
            "b": "2",
            "c": "3",
        }
    )

    assert labels.labels == {
        "a": "1",
        "b": "2",
        "c": "3",
    }


def test_remove():
    labels = MetricLabels(
        {"a": "1"}
    )

    labels.remove("a")

    assert "a" not in labels


def test_pop():
    labels = MetricLabels(
        {"a": "1"}
    )

    value = labels.pop("a")

    assert value == "1"
    assert len(labels) == 0


def test_clear():
    labels = MetricLabels(
        {
            "a": "1",
            "b": "2",
        }
    )

    labels.clear()

    assert labels.labels == {}


def test_has():
    labels = MetricLabels(
        {"a": "1"}
    )

    assert labels.has("a")
    assert not labels.has("b")


def test_get():
    labels = MetricLabels(
        {"a": "1"}
    )

    assert labels.get("a") == "1"
    assert labels.get("b") is None
    assert labels.get("b", "x") == "x"


# ==============================================================================
# Part 7. Mapping Protocol
# ==============================================================================

def test_getitem():
    labels = MetricLabels(
        {"x": "10"}
    )

    assert labels["x"] == "10"


def test_setitem():
    labels = MetricLabels()

    labels["x"] = "10"

    assert labels["x"] == "10"


def test_delitem():
    labels = MetricLabels(
        {"x": "10"}
    )

    del labels["x"]

    assert "x" not in labels


def test_contains():
    labels = MetricLabels(
        {"x": "10"}
    )

    assert "x" in labels
    assert "y" not in labels


def test_iter():
    labels = MetricLabels(
        {
            "a": "1",
            "b": "2",
        }
    )

    assert list(iter(labels)) == [
        "a",
        "b",
    ]


def test_len():
    labels = MetricLabels(
        {
            "a": "1",
            "b": "2",
        }
    )

    assert len(labels) == 2


# ==============================================================================
# Part 8. Serialization
# ==============================================================================

def test_to_dict():
    labels = MetricLabels(
        {"a": "1"}
    )

    assert labels.to_dict() == {
        "a": "1"
    }


def test_from_dict():
    labels = MetricLabels.from_dict(
        {"a": "1"}
    )

    assert labels["a"] == "1"


def test_to_json():
    labels = MetricLabels(
        {"a": "1"}
    )

    text = labels.to_json()

    assert '"a"' in text
    assert '"1"' in text


def test_from_json():
    labels = MetricLabels.from_json(
        '{"a":"1"}'
    )

    assert labels["a"] == "1"


# ==============================================================================
# Part 9. Copy
# ==============================================================================

def test_copy():
    labels = MetricLabels(
        {"a": "1"}
    )

    copied = labels.copy()

    assert copied == labels
    assert copied is not labels


def test_clone():
    labels = MetricLabels(
        {"a": "1"}
    )

    cloned = labels.clone()

    assert cloned == labels
    assert cloned is not labels


# ==============================================================================
# Part 10. Equality
# ==============================================================================

def test_eq():
    a = MetricLabels(
        {"x": "1"}
    )

    b = MetricLabels(
        {"x": "1"}
    )

    assert a == b


def test_hash():
    labels = MetricLabels(
        {"x": "1"}
    )

    assert isinstance(hash(labels), int)


# ==============================================================================
# Part 11. Representation
# ==============================================================================

def test_repr():
    labels = MetricLabels(
        {"x": "1"}
    )

    assert "MetricLabels" in repr(labels)


def test_str():
    labels = MetricLabels(
        {"x": "1"}
    )

    assert "x" in str(labels)


# ==============================================================================
# Part 12. Public API
# ==============================================================================

def test_all():
    from scios.runtime.observability.metrics.core.labels import __all__

    assert "MetricLabels" in __all__
    assert "LabelValidationError" in __all__


def test_version():
    from scios.runtime.observability.metrics.core.labels import __version__

    assert isinstance(__version__, str)
    assert __version__


# ==============================================================================
# Part 13. Regression
# ==============================================================================

def test_labels_are_copied():
    source = {
        "a": "1",
    }

    labels = MetricLabels(source)

    source["a"] = "2"

    assert labels["a"] == "1"


def test_json_roundtrip():
    labels = MetricLabels(
        {
            "a": "1",
            "b": "2",
        }
    )

    restored = MetricLabels.from_json(
        labels.to_json()
    )

    assert restored == labels


def test_dict_roundtrip():
    labels = MetricLabels(
        {
            "a": "1",
            "b": "2",
        }
    )

    restored = MetricLabels.from_dict(
        labels.to_dict()
    )

    assert restored == labels


def test_order_is_preserved():
    labels = MetricLabels()

    labels.add("first", "1")
    labels.add("second", "2")
    labels.add("third", "3")

    assert list(labels.keys()) == [
        "first",
        "second",
        "third",
    ]    