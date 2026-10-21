"""
Tests for json_codec.py

Python 3.11+
"""

from __future__ import annotations

import inspect

from typing import Any

import pytest

from scios.runtime.observability.metrics.core.metrics.serialization.json_codec import (
    DEFAULT_ENCODING,
    JsonCodec,
)


# ==============================================================================
# Part 1. Constructor (5)
# ==============================================================================


def test_default_constructor():

    codec = JsonCodec()

    assert codec.encoding == DEFAULT_ENCODING
    assert codec.indent is None
    assert codec.sort_keys is False
    assert codec.ensure_ascii is False
    assert codec.options == {}


def test_custom_constructor():

    codec = JsonCodec(
        encoding="utf-16",
        indent=2,
        sort_keys=True,
        ensure_ascii=True,
        options={
            "x": 1,
        },
    )

    assert codec.encoding == "utf-16"
    assert codec.indent == 2
    assert codec.sort_keys is True
    assert codec.ensure_ascii is True
    assert codec.options == {"x": 1}


def test_slots():

    assert hasattr(
        JsonCodec,
        "__slots__",
    )


def test_annotations():

    assert isinstance(
        JsonCodec.__annotations__,
        dict,
    )


def test_signature():

    sig = inspect.signature(
        JsonCodec,
    )

    assert "encoding" in sig.parameters
    assert "indent" in sig.parameters
    assert "sort_keys" in sig.parameters
    assert "ensure_ascii" in sig.parameters
    assert "options" in sig.parameters


# ==============================================================================
# Part 2. Properties (6)
# ==============================================================================


def test_encoding_property():

    codec = JsonCodec()

    assert codec.encoding == DEFAULT_ENCODING


def test_indent_property():

    codec = JsonCodec(
        indent=4,
    )

    assert codec.indent == 4


def test_sort_keys_property():

    codec = JsonCodec(
        sort_keys=True,
    )

    assert codec.sort_keys is True


def test_ensure_ascii_property():

    codec = JsonCodec(
        ensure_ascii=True,
    )

    assert codec.ensure_ascii is True


def test_options_property():

    codec = JsonCodec(
        options={
            "a": 1,
        },
    )

    assert codec.options == {
        "a": 1,
    }


def test_state_property():

    codec = JsonCodec()

    state = codec.state

    assert isinstance(
        state,
        dict,
    )

    assert "encoding" in state


# ==============================================================================
# Part 3. Encode (6)
# ==============================================================================


def test_encode():

    codec = JsonCodec()

    value = codec.encode(
        {
            "x": 1,
        }
    )

    assert isinstance(
        value,
        str,
    )


def test_encode_dict():

    codec = JsonCodec()

    value = codec.encode_dict(
        {
            "x": 1,
        }
    )

    assert '"x"' in value


def test_encode_object():

    codec = JsonCodec()

    class Dummy:

        def __init__(self):

            self.value = 10

    result = codec.encode_object(
        Dummy(),
    )

    assert isinstance(
        result,
        str,
    )


def test_encode_bytes():

    codec = JsonCodec()

    data = codec.encode_bytes(
        {
            "x": 1,
        }
    )

    assert isinstance(
        data,
        bytes,
    )


def test_dumps():

    codec = JsonCodec()

    result = codec.dumps(
        {
            "a": 1,
        }
    )

    assert isinstance(
        result,
        str,
    )


def test_snapshot():

    codec = JsonCodec()

    snapshot = codec.snapshot()

    assert isinstance(
        snapshot,
        dict,
    )


# ==============================================================================
# Part 4. Decode (6)
# ==============================================================================


def test_decode():

    codec = JsonCodec()

    result = codec.decode(
        '{"x":1}'
    )

    assert result == {
        "x": 1,
    }


def test_decode_dict():

    codec = JsonCodec()

    result = codec.decode_dict(
        '{"a":2}'
    )

    assert result == {
        "a": 2,
    }


def test_decode_object():

    codec = JsonCodec()

    result = codec.decode_object(
        '{"x":5}'
    )

    assert result["x"] == 5


def test_decode_bytes():

    codec = JsonCodec()

    result = codec.decode_bytes(
        b'{"a":1}'
    )

    assert result == {
        "a": 1,
    }


def test_loads():

    codec = JsonCodec()

    result = codec.loads(
        '{"x":9}'
    )

    assert result["x"] == 9


def test_restore():

    codec = JsonCodec()

    snapshot = codec.snapshot()

    other = JsonCodec()

    other.restore(
        snapshot,
    )

    assert other == codec


# ==============================================================================
# Part 5. Validation (6)
# ==============================================================================


def test_validate_json():

    codec = JsonCodec()

    assert codec.validate_json(
        '{"x":1}'
    )

    with pytest.raises(
        ValueError,
    ):
        codec.validate_json(
            "{"
        )


def test_validate_bytes():

    codec = JsonCodec()

    assert codec.validate_bytes(
        b"abc",
    )

    with pytest.raises(
        TypeError,
    ):
        codec.validate_bytes(
            "abc",
        )


def test_validate_mapping():

    codec = JsonCodec()

    assert codec.validate_mapping(
        {
            "a": 1,
        }
    )

    with pytest.raises(
        TypeError,
    ):
        codec.validate_mapping(
            [],
        )


def test_validate_encoding():

    codec = JsonCodec()

    assert codec.validate_encoding(
        "utf-8",
    ) == "utf-8"

    with pytest.raises(
        TypeError,
    ):
        codec.validate_encoding(
            1,
        )


def test_validate_options():

    codec = JsonCodec()

    assert codec.validate_options(
        {
            "x": 1,
        }
    ) == {
        "x": 1,
    }

    with pytest.raises(
        TypeError,
    ):
        codec.validate_options(
            [],
        )


def test_validate():

    codec = JsonCodec()

    assert codec.validate()

# ==============================================================================
# Part 6. Utilities (6)
# ==============================================================================


def test_copy():

    codec = JsonCodec(
        options={
            "a": 1,
        }
    )

    other = codec.copy()

    assert other == codec
    assert other is not codec


def test_deepcopy():

    codec = JsonCodec(
        options={
            "a": {
                "b": 1,
            }
        }
    )

    other = codec.deepcopy()

    assert other == codec
    assert other is not codec

    other.options["a"]["b"] = 99

    assert codec.options["a"]["b"] == 1


def test_clone():

    codec = JsonCodec(
        options={
            "x": 1,
        }
    )

    clone = codec.clone()

    assert clone == codec
    assert clone is not codec


def test_clear():

    codec = JsonCodec(
        options={
            "a": 1,
        }
    )

    codec.clear()

    assert codec.options == {}


def test_update():

    codec = JsonCodec()

    codec.update(
        {
            "a": 1,
        }
    )

    assert codec.options["a"] == 1


def test_merge():

    codec = JsonCodec(
        options={
            "a": 1,
        }
    )

    codec.merge(
        {
            "b": 2,
        }
    )

    assert codec.options == {
        "a": 1,
        "b": 2,
    }


# ==============================================================================
# Part 7. Protocols (12)
# ==============================================================================


def test_contains_protocol():

    codec = JsonCodec(
        options={
            "x": 1,
        }
    )

    assert "x" in codec


def test_getitem():

    codec = JsonCodec(
        options={
            "a": 5,
        }
    )

    assert codec["a"] == 5


def test_setitem():

    codec = JsonCodec()

    codec["x"] = 10

    assert codec["x"] == 10


def test_delitem():

    codec = JsonCodec(
        options={
            "a": 1,
        }
    )

    del codec["a"]

    assert "a" not in codec


def test_iter():

    codec = JsonCodec(
        options={
            "a": 1,
            "b": 2,
        }
    )

    assert set(iter(codec)) == {
        "a",
        "b",
    }


def test_len():

    codec = JsonCodec(
        options={
            "a": 1,
            "b": 2,
        }
    )

    assert len(codec) == 2


def test_bool():

    assert bool(JsonCodec()) is False
    assert bool(JsonCodec(options={"x": 1})) is True


def test_repr():

    codec = JsonCodec()

    assert "JsonCodec" in repr(codec)


def test_str():

    codec = JsonCodec()

    assert "JsonCodec" in str(codec)


def test_eq():

    left = JsonCodec(
        options={
            "a": 1,
        }
    )

    right = JsonCodec(
        options={
            "a": 1,
        }
    )

    assert left == right


def test_hash():

    codec = JsonCodec()

    assert isinstance(
        hash(codec),
        int,
    )


def test_pickle():

    import pickle

    codec = JsonCodec(
        options={
            "a": 1,
        }
    )

    restored = pickle.loads(
        pickle.dumps(codec)
    )

    assert restored == codec


# ==============================================================================
# Part 8. Diagnostics (4)
# ==============================================================================


def test_summary():

    codec = JsonCodec()

    result = codec.summary()

    assert isinstance(
        result,
        dict,
    )

    assert "encoding" in result


def test_diagnostics():

    codec = JsonCodec()

    result = codec.diagnostics()

    assert isinstance(
        result,
        dict,
    )

    assert "status" in result
    assert "valid" in result


def test_codec_report():

    codec = JsonCodec()

    result = codec.codec_report()

    assert isinstance(
        result,
        dict,
    )

    assert "codec" in result
    assert "status" in result


def test_overall_status():

    codec = JsonCodec()

    assert codec.overall_status() == "ready"


# ==============================================================================
# Part 9. Public API (1)
# ==============================================================================


def test_public_api():

    from scios.runtime.observability.metrics.core.metrics.serialization.json_codec import (
        __all__,
    )

    assert "JsonCodec" in __all__
    assert "DEFAULT_ENCODING" in __all__    