"""
Tests for snapshot_codec.py

Part 1–5
"""

from __future__ import annotations

import inspect
import pickle

import pytest

from scios.runtime.observability.metrics.core.metrics.serialization.snapshot_codec import (
    DEFAULT_COMPRESS,
    DEFAULT_ENCODING,
    DEFAULT_PROTOCOL,
    SnapshotCodec,
)


# ==============================================================================
# Helpers
# ==============================================================================


def create_codec() -> SnapshotCodec:
    return SnapshotCodec()


# ==============================================================================
# Part 1. Constructor
# ==============================================================================


def test_default_constructor():

    codec = SnapshotCodec()

    assert codec.encoding == DEFAULT_ENCODING
    assert codec.protocol == DEFAULT_PROTOCOL
    assert codec.compress == DEFAULT_COMPRESS
    assert codec.options == {}


def test_custom_constructor():

    codec = SnapshotCodec(
        encoding="utf-16",
        protocol=3,
        compress=True,
        options={"x": 1},
    )

    assert codec.encoding == "utf-16"
    assert codec.protocol == 3
    assert codec.compress is True
    assert codec.options == {"x": 1}


def test_slots():

    assert hasattr(SnapshotCodec, "__slots__")

    expected = {
        "_encoding",
        "_protocol",
        "_compress",
        "_options",
    }

    assert expected.issubset(set(SnapshotCodec.__slots__))


def test_annotations():

    ann = SnapshotCodec.__annotations__

    assert "_encoding" in ann
    assert "_protocol" in ann
    assert "_compress" in ann
    assert "_options" in ann


def test_signature():

    sig = inspect.signature(SnapshotCodec)

    assert "encoding" in sig.parameters
    assert "protocol" in sig.parameters
    assert "compress" in sig.parameters
    assert "options" in sig.parameters


# ==============================================================================
# Part 2. Properties
# ==============================================================================


def test_encoding_property():

    assert create_codec().encoding == DEFAULT_ENCODING


def test_protocol_property():

    assert create_codec().protocol == DEFAULT_PROTOCOL


def test_compress_property():

    assert create_codec().compress == DEFAULT_COMPRESS


def test_options_property():

    codec = create_codec()

    assert codec.options == {}
    assert codec.options is not codec._options


def test_config_property():

    codec = create_codec()

    cfg = codec.config

    assert cfg["encoding"] == codec.encoding
    assert cfg["protocol"] == codec.protocol
    assert cfg["compress"] == codec.compress


def test_state_property():

    codec = create_codec()

    state = codec.state

    assert isinstance(state, dict)
    assert state == codec.snapshot()


# ==============================================================================
# Part 3. Encode
# ==============================================================================


def test_encode():

    codec = create_codec()

    data = {"a": 1}

    encoded = codec.encode(data)

    assert isinstance(encoded, bytes)


def test_encode_dict():

    codec = create_codec()

    encoded = codec.encode_dict({"x": 10})

    assert isinstance(encoded, bytes)


def test_encode_object():

    codec = create_codec()

    encoded = codec.encode_object([1, 2, 3])

    assert isinstance(encoded, bytes)


def test_encode_bytes():

    codec = create_codec()

    raw = b"hello"

    encoded = codec.encode_bytes(raw)

    assert isinstance(encoded, bytes)


def test_dumps():

    codec = create_codec()

    result = codec.dumps({"value": 100})

    assert isinstance(result, bytes)


def test_snapshot():

    codec = create_codec()

    snap = codec.snapshot()

    assert isinstance(snap, dict)

    assert snap["encoding"] == codec.encoding
    assert snap["protocol"] == codec.protocol
    assert snap["compress"] == codec.compress


# ==============================================================================
# Part 4. Decode
# ==============================================================================


def test_decode():

    codec = create_codec()

    obj = {"a": 1}

    data = codec.encode(obj)

    assert codec.decode(data) == obj


def test_decode_dict():

    codec = create_codec()

    obj = {"x": 5}

    data = codec.encode_dict(obj)

    assert codec.decode_dict(data) == obj


def test_decode_object():

    codec = create_codec()

    obj = [1, 2, 3]

    data = codec.encode_object(obj)

    assert codec.decode_object(data) == obj


def test_decode_bytes():

    codec = create_codec()

    raw = b"abc"

    encoded = codec.encode_bytes(raw)

    assert codec.decode_bytes(encoded) == raw


def test_loads():

    codec = create_codec()

    obj = {"v": 9}

    data = codec.dumps(obj)

    assert codec.loads(data) == obj


def test_restore():

    codec = create_codec()

    state = codec.snapshot()

    other = SnapshotCodec()

    other.restore(state)

    assert other == codec


# ==============================================================================
# Part 5. Validation
# ==============================================================================


def test_validate_snapshot():

    value = {"a": 1}

    assert SnapshotCodec.validate_snapshot(value) == value

    with pytest.raises(TypeError):
        SnapshotCodec.validate_snapshot(123)


def test_validate_bytes():

    raw = b"abc"

    assert SnapshotCodec.validate_bytes(raw) == raw

    with pytest.raises(TypeError):
        SnapshotCodec.validate_bytes("abc")


def test_validate_mapping():

    mapping = {"x": 1}

    assert SnapshotCodec.validate_mapping(mapping) == mapping

    with pytest.raises(TypeError):
        SnapshotCodec.validate_mapping([])


def test_validate_encoding():

    assert SnapshotCodec.validate_encoding("utf-8") == "utf-8"

    with pytest.raises(TypeError):
        SnapshotCodec.validate_encoding(123)

    with pytest.raises(ValueError):
        SnapshotCodec.validate_encoding("")


def test_validate_protocol():

    assert SnapshotCodec.validate_protocol(5) == 5

    with pytest.raises(TypeError):
        SnapshotCodec.validate_protocol("5")

    with pytest.raises(ValueError):
        SnapshotCodec.validate_protocol(-1)


def test_validate():

    codec = create_codec()

    assert codec.validate() is True

# ==============================================================================
# Part 6. Utilities
# ==============================================================================


def test_copy():

    codec = SnapshotCodec(options={"a": 1})

    other = codec.copy()

    assert other == codec
    assert other is not codec


def test_deepcopy():

    codec = SnapshotCodec(
        options={
            "a": {"b": 1},
        }
    )

    other = codec.deepcopy()

    assert other == codec
    assert other is not codec
    assert other.options is not codec.options


def test_clone():

    codec = SnapshotCodec(options={"x": 1})

    clone = codec.clone()

    assert clone == codec
    assert clone is not codec


def test_clear():

    codec = SnapshotCodec(options={"a": 1})

    codec.clear()

    assert codec.options == {}
    assert len(codec) == 0


def test_update():

    codec = create_codec()

    codec.update(
        {
            "x": 1,
            "y": 2,
        }
    )

    assert codec["x"] == 1
    assert codec["y"] == 2


def test_merge():

    codec = create_codec()

    returned = codec.merge(
        {
            "a": 10,
        }
    )

    assert returned is codec
    assert codec["a"] == 10


# ==============================================================================
# Part 7. Protocols
# ==============================================================================


def test_contains_protocol():

    codec = SnapshotCodec(options={"x": 1})

    assert "x" in codec
    assert "y" not in codec


def test_getitem():

    codec = SnapshotCodec(options={"a": 5})

    assert codec["a"] == 5


def test_setitem():

    codec = create_codec()

    codec["answer"] = 42

    assert codec["answer"] == 42


def test_delitem():

    codec = SnapshotCodec(options={"a": 1})

    del codec["a"]

    assert "a" not in codec


def test_iter():

    codec = SnapshotCodec(
        options={
            "a": 1,
            "b": 2,
        }
    )

    assert set(iter(codec)) == {"a", "b"}


def test_len():

    codec = SnapshotCodec(
        options={
            "a": 1,
            "b": 2,
        }
    )

    assert len(codec) == 2


def test_bool():

    assert bool(create_codec()) is False
    assert bool(SnapshotCodec(options={"x": 1})) is True


def test_repr():

    codec = create_codec()

    text = repr(codec)

    assert "SnapshotCodec" in text


def test_str():

    codec = create_codec()

    assert str(codec) == repr(codec)


def test_eq():

    a = SnapshotCodec(options={"x": 1})
    b = SnapshotCodec(options={"x": 1})

    assert a == b


def test_hash():

    codec = create_codec()

    assert isinstance(hash(codec), int)


def test_pickle():

    codec = SnapshotCodec(
        options={
            "a": 1,
        }
    )

    restored = pickle.loads(
        pickle.dumps(codec)
    )

    assert restored == codec


# ==============================================================================
# Part 8. Diagnostics
# ==============================================================================


def test_summary():

    codec = create_codec()

    result = codec.summary()

    assert isinstance(result, dict)
    assert result["encoding"] == codec.encoding
    assert result["protocol"] == codec.protocol


def test_diagnostics():

    codec = create_codec()

    result = codec.diagnostics()

    assert isinstance(result, dict)
    assert result["valid"] is True
    assert result["status"] == "ready"


def test_codec_report():

    codec = create_codec()

    result = codec.codec_report()

    assert isinstance(result, dict)
    assert "codec" in result
    assert "options" in result
    assert "status" in result


def test_overall_status():

    codec = create_codec()

    assert codec.overall_status() == "ready"


# ==============================================================================
# Part 9. Public API
# ==============================================================================


def test_public_api():

    from scios.runtime.observability.metrics.core.metrics.serialization.snapshot_codec import (
        __all__,
    )

    expected = {
        "SnapshotCodec",
        "DEFAULT_ENCODING",
        "DEFAULT_PROTOCOL",
        "DEFAULT_COMPRESS",
    }

    assert expected.issubset(set(__all__))    