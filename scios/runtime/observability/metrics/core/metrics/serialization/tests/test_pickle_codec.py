"""
Tests for pickle_codec.py
"""

from __future__ import annotations

import inspect
import pickle

from scios.runtime.observability.metrics.core.metrics.serialization.pickle_codec import (
    DEFAULT_BUFFER_CALLBACK,
    DEFAULT_BUFFERS,
    DEFAULT_FIX_IMPORTS,
    DEFAULT_PROTOCOL,
    PickleCodec,
)


# ==============================================================================
# Part 1. Constructor
# ==============================================================================


def test_default_constructor():

    codec = PickleCodec()

    assert codec.protocol == DEFAULT_PROTOCOL
    assert codec.fix_imports is DEFAULT_FIX_IMPORTS
    assert codec.buffer_callback is DEFAULT_BUFFER_CALLBACK
    assert codec.buffers is DEFAULT_BUFFERS
    assert codec.options == {}


def test_custom_constructor():

    codec = PickleCodec(
        protocol=3,
        fix_imports=False,
        buffer_callback=lambda *_: None,
        buffers=[],
        options={"x": 1},
    )

    assert codec.protocol == 3
    assert codec.fix_imports is False
    assert callable(codec.buffer_callback)
    assert codec.buffers == []
    assert codec.options == {"x": 1}


def test_slots():

    assert hasattr(PickleCodec, "__slots__")


def test_annotations():

    assert isinstance(
        PickleCodec.__annotations__,
        dict,
    )


def test_signature():

    sig = inspect.signature(
        PickleCodec,
    )

    assert "protocol" in sig.parameters
    assert "fix_imports" in sig.parameters
    assert "buffer_callback" in sig.parameters
    assert "buffers" in sig.parameters
    assert "options" in sig.parameters


# ==============================================================================
# Part 2. Properties
# ==============================================================================


def test_protocol_property():

    codec = PickleCodec(protocol=2)

    assert codec.protocol == 2


def test_fix_imports_property():

    codec = PickleCodec(
        fix_imports=False,
    )

    assert codec.fix_imports is False


def test_buffer_callback_property():

    cb = lambda *_: None

    codec = PickleCodec(
        buffer_callback=cb,
    )

    assert codec.buffer_callback is cb


def test_buffers_property():

    buf = []

    codec = PickleCodec(
        buffers=buf,
    )

    assert codec.buffers is buf


def test_options_property():

    codec = PickleCodec(
        options={
            "a": 1,
        }
    )

    assert codec.options == {
        "a": 1,
    }


def test_state_property():

    codec = PickleCodec()

    state = codec.state

    assert state["protocol"] == codec.protocol
    assert state["fix_imports"] == codec.fix_imports
    assert "options" in state


# ==============================================================================
# Part 3. Encode
# ==============================================================================


def test_encode():

    codec = PickleCodec()

    data = codec.encode(
        {
            "a": 1,
        }
    )

    assert isinstance(
        data,
        bytes,
    )


def test_encode_dict():

    codec = PickleCodec()

    data = codec.encode_dict(
        {
            "x": 10,
        }
    )

    assert pickle.loads(data) == {
        "x": 10,
    }


class Dummy:

    def __init__(self):
        self.value = 123


def test_encode_object():

    codec = PickleCodec()

    data = codec.encode_object(Dummy())

    obj = pickle.loads(data)

    assert obj.value == 123

def test_encode_bytes():

    codec = PickleCodec()

    raw = b"abc"

    data = codec.encode_bytes(raw)

    assert pickle.loads(data) == raw


def test_dumps():

    codec = PickleCodec()

    payload = {
        "a": [1, 2],
    }

    assert pickle.loads(codec.dumps(payload)) == payload


def test_snapshot():

    codec = PickleCodec()

    snapshot = codec.snapshot()

    state = pickle.loads(snapshot)

    assert state == codec.state


# ==============================================================================
# Part 4. Decode
# ==============================================================================


def test_decode():

    codec = PickleCodec()

    obj = {
        "x": 1,
    }

    assert codec.decode(
        pickle.dumps(obj),
    ) == obj


def test_decode_dict():

    codec = PickleCodec()

    result = codec.decode_dict(
        pickle.dumps(
            {
                "a": 5,
            }
        )
    )

    assert result == {
        "a": 5,
    }


def test_decode_object():

    codec = PickleCodec()

    obj = [1, 2, 3]

    assert codec.decode_object(
        pickle.dumps(obj),
    ) == obj


def test_decode_bytes():

    codec = PickleCodec()

    raw = b"xyz"

    assert codec.decode_bytes(
        pickle.dumps(raw),
    ) == raw


def test_loads():

    codec = PickleCodec()

    obj = (
        1,
        2,
    )

    assert codec.loads(
        pickle.dumps(obj),
    ) == obj


def test_restore():

    codec = PickleCodec()

    snapshot = codec.snapshot()

    restored = codec.restore(
        snapshot,
    )

    assert restored == codec.state


# ==============================================================================
# Part 5. Validation
# ==============================================================================


def test_validate_pickle():

    codec = PickleCodec()

    assert codec.validate_pickle(
        pickle.dumps(
            {
                "a": 1,
            }
        )
    )


def test_validate_bytes():

    codec = PickleCodec()

    assert codec.validate_bytes(
        b"abc",
    )

    assert not codec.validate_bytes(
        "abc",
    )


def test_validate_mapping():

    codec = PickleCodec()

    assert codec.validate_mapping(
        {
            "a": 1,
        }
    )

    assert not codec.validate_mapping(
        [],
    )


def test_validate_protocol():

    codec = PickleCodec()

    assert codec.validate_protocol(
        DEFAULT_PROTOCOL,
    )

    assert not codec.validate_protocol(
        999,
    )


def test_validate_options():

    codec = PickleCodec()

    assert codec.validate_options(
        {
            "a": 1,
        }
    )

    assert not codec.validate_options(
        [],
    )


def test_validate():

    codec = PickleCodec()

    assert codec.validate(
        {
            "a": 1,
        }
    )

# ==============================================================================
# Part 6. Utilities
# ==============================================================================


def test_copy():

    codec = PickleCodec(
        options={
            "a": 1,
        }
    )

    other = codec.copy()

    assert other == codec
    assert other is not codec


def test_deepcopy():

    codec = PickleCodec(
        options={
            "a": {
                "b": 1,
            }
        }
    )

    other = codec.deepcopy()

    assert other == codec
    assert other is not codec

    other["a"]["b"] = 99

    assert codec["a"]["b"] == 1


def test_clone():

    codec = PickleCodec(
        options={
            "x": 1,
        }
    )

    clone = codec.clone()

    assert clone == codec
    assert clone is not codec


def test_clear():

    codec = PickleCodec(
        options={
            "a": 1,
        }
    )

    codec.clear()

    assert codec.options == {}
    assert len(codec) == 0


def test_update():

    codec = PickleCodec()

    codec.update(
        {
            "a": 1,
        },
        b=2,
    )

    assert codec.options == {
        "a": 1,
        "b": 2,
    }


def test_merge():

    codec = PickleCodec(
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
# Part 7. Protocols
# ==============================================================================


def test_contains_protocol():

    codec = PickleCodec(
        options={
            "x": 1,
        }
    )

    assert "x" in codec
    assert "y" not in codec


def test_getitem():

    codec = PickleCodec(
        options={
            "a": 5,
        }
    )

    assert codec["a"] == 5


def test_setitem():

    codec = PickleCodec()

    codec["a"] = 10

    assert codec["a"] == 10


def test_delitem():

    codec = PickleCodec(
        options={
            "a": 1,
        }
    )

    del codec["a"]

    assert "a" not in codec


def test_iter():

    codec = PickleCodec(
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

    codec = PickleCodec(
        options={
            "a": 1,
            "b": 2,
        }
    )

    assert len(codec) == 2


def test_bool():

    assert not PickleCodec()

    assert PickleCodec(
        options={
            "x": 1,
        }
    )


def test_repr():

    codec = PickleCodec()

    assert "PickleCodec" in repr(codec)


def test_str():

    codec = PickleCodec()

    assert "PickleCodec" in str(codec)


def test_eq():

    a = PickleCodec(
        options={
            "x": 1,
        }
    )

    b = PickleCodec(
        options={
            "x": 1,
        }
    )

    assert a == b


def test_hash():

    codec = PickleCodec()

    assert isinstance(
        hash(codec),
        int,
    )


def test_pickle():

    codec = PickleCodec(
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

    codec = PickleCodec()

    summary = codec.summary()

    assert summary["codec"] == "PickleCodec"


def test_diagnostics():

    codec = PickleCodec()

    diagnostics = codec.diagnostics()

    assert diagnostics["valid_protocol"] is True
    assert diagnostics["valid_options"] is True


def test_codec_report():

    codec = PickleCodec()

    report = codec.codec_report()

    assert "summary" in report
    assert "diagnostics" in report


def test_overall_status():

    codec = PickleCodec()

    assert codec.overall_status() == "ok"


# ==============================================================================
# Part 9. Public API
# ==============================================================================


def test_public_api():

    from scios.runtime.observability.metrics.core.metrics.serialization import (
        pickle_codec,
    )

    assert "PickleCodec" in pickle_codec.__all__
    assert "DEFAULT_PROTOCOL" in pickle_codec.__all__
    assert "DEFAULT_FIX_IMPORTS" in pickle_codec.__all__    