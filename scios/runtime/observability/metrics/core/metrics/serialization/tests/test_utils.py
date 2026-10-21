"""
Unit tests for serialization utilities.
"""

from __future__ import annotations

import pickle

import scios.runtime.observability.metrics.core.metrics.serialization.utils as utils
from scios.runtime.observability.metrics.core.metrics.serialization.utils import (
    DEFAULT_COMPRESS_LEVEL,
    DEFAULT_ENCODING,
    DEFAULT_PROTOCOL,
    compress,
    compress_if_needed,
    compression_ratio,
    decode_text,
    decompress,
    decompress_if_needed,
    deep_copy,
    deep_merge,
    detect_encoding,
    diagnostics,
    encode_text,
    ensure_bytes,
    ensure_str,
    filter_mapping,
    flatten_mapping,
    is_json,
    is_pickle,
    json_dumps,
    json_loads,
    json_restore,
    json_snapshot,
    normalize_encoding,
    overall_status,
    pickle_dumps,
    pickle_loads,
    pickle_restore,
    pickle_snapshot,
    summary,
    unflatten_mapping,
    utility_report,
    validate,
    validate_bytes,
    validate_compression,
    validate_encoding,
    validate_json,
    validate_mapping,
    validate_options,
    validate_pickle,
    validate_protocol,
    validate_string,
)


# ==============================================================================
# Part 1. Encoding Helpers
# ==============================================================================


def test_ensure_bytes():

    assert ensure_bytes("hello") == b"hello"
    assert ensure_bytes(b"hello") == b"hello"
    assert ensure_bytes(bytearray(b"abc")) == b"abc"


def test_ensure_str():

    assert ensure_str("hello") == "hello"
    assert ensure_str(b"hello") == "hello"
    assert ensure_str(bytearray(b"abc")) == "abc"


def test_encode_text():

    data = encode_text("SciOS")

    assert isinstance(data, bytes)
    assert data == b"SciOS"


def test_decode_text():

    text = decode_text(b"SciOS")

    assert text == "SciOS"


def test_normalize_encoding():

    assert normalize_encoding("UTF-8") == "utf-8"
    assert normalize_encoding(None) == DEFAULT_ENCODING


def test_detect_encoding():

    assert detect_encoding(b"hello") == "utf-8"

    latin = "é".encode("latin-1")

    assert detect_encoding(latin) == "latin-1"


# ==============================================================================
# Part 2. JSON Helpers
# ==============================================================================


def test_json_dumps():

    text = json_dumps({"a": 1})

    assert isinstance(text, str)
    assert '"a"' in text


def test_json_loads():

    obj = json_loads('{"a":1}')

    assert obj == {"a": 1}


def test_json_snapshot():

    snapshot = json_snapshot({"x": 10})

    assert isinstance(snapshot, str)

    assert json_loads(snapshot)["x"] == 10


def test_json_restore():

    restored = json_restore('{"value":123}')

    assert restored["value"] == 123


def test_is_json():

    assert is_json('{"a":1}')
    assert not is_json("not-json")


def test_validate_json():

    assert validate_json('{"ok":true}')
    assert not validate_json("abc")


# ==============================================================================
# Part 3. Pickle Helpers
# ==============================================================================


def test_pickle_dumps():

    data = pickle_dumps({"a": 1})

    assert isinstance(data, bytes)


def test_pickle_loads():

    original = {"x": 2}

    data = pickle.dumps(original)

    assert pickle_loads(data) == original


def test_pickle_snapshot():

    snapshot = pickle_snapshot([1, 2, 3])

    assert pickle.loads(snapshot) == [1, 2, 3]


def test_pickle_restore():

    data = pickle.dumps({"value": 999})

    restored = pickle_restore(data)

    assert restored["value"] == 999


def test_is_pickle():

    assert is_pickle(pickle.dumps({"a": 1}))
    assert not is_pickle(b"abcdefg")


def test_validate_pickle():

    assert validate_pickle(pickle.dumps(123))
    assert not validate_pickle(b"invalid")


# ==============================================================================
# Part 4. Compression Helpers
# ==============================================================================


def test_compress():

    data = b"abcdef" * 100

    compressed = compress(data)

    assert isinstance(compressed, bytes)
    assert len(compressed) < len(data)


def test_decompress():

    original = b"hello world" * 50

    compressed = compress(original)

    restored = decompress(compressed)

    assert restored == original


def test_compress_if_needed():

    data = b"abc" * 100

    assert compress_if_needed(data, enabled=False) == data

    compressed = compress_if_needed(data, enabled=True)

    assert compressed != data


def test_decompress_if_needed():

    original = b"xyz" * 100

    compressed = compress(original)

    assert decompress_if_needed(
        compressed,
        compressed=True,
    ) == original

    assert decompress_if_needed(
        original,
        compressed=False,
    ) == original


def test_compression_ratio():

    original = b"a" * 1000

    compressed = compress(original)

    ratio = compression_ratio(
        original,
        compressed,
    )

    assert isinstance(ratio, float)
    assert ratio > 0


def test_validate_compression():

    original = b"abcdef" * 200

    compressed = compress(original)

    assert validate_compression(
        original,
        compressed,
    )

    assert not validate_compression(
        original,
        b"invalid-data",
    )

# ==============================================================================
# Part 5. Mapping Helpers
# ==============================================================================


def test_deep_merge():

    left = {
        "a": 1,
        "nested": {
            "x": 1,
        },
    }

    right = {
        "b": 2,
        "nested": {
            "y": 2,
        },
    }

    merged = deep_merge(
        left,
        right,
    )

    assert merged == {
        "a": 1,
        "b": 2,
        "nested": {
            "x": 1,
            "y": 2,
        },
    }


def test_deep_copy():

    original = {
        "a": {
            "b": 1,
        },
    }

    copied = deep_copy(original)

    assert copied == original
    assert copied is not original
    assert copied["a"] is not original["a"]


def test_flatten_mapping():

    mapping = {
        "a": {
            "b": {
                "c": 1,
            },
        },
    }

    assert flatten_mapping(mapping) == {
        "a.b.c": 1,
    }


def test_unflatten_mapping():

    mapping = {
        "a.b.c": 1,
    }

    assert unflatten_mapping(mapping) == {
        "a": {
            "b": {
                "c": 1,
            },
        },
    }


def test_filter_mapping():

    mapping = {
        "a": 1,
        "b": None,
        "c": 2,
    }

    assert filter_mapping(mapping) == {
        "a": 1,
        "c": 2,
    }

    assert filter_mapping(
        mapping,
        include_none=True,
    ) == mapping


def test_validate_mapping():

    assert validate_mapping({})
    assert validate_mapping({"a": 1})
    assert not validate_mapping([])
    assert not validate_mapping(None)


# ==============================================================================
# Part 6. Validation
# ==============================================================================


def test_validate_bytes():

    assert validate_bytes(b"abc")
    assert validate_bytes(bytearray(b"abc"))
    assert validate_bytes(memoryview(b"abc"))

    assert not validate_bytes("abc")


def test_validate_string():

    assert validate_string("hello")

    assert not validate_string(b"hello")


def test_validate_encoding():

    assert validate_encoding("utf-8")
    assert validate_encoding("ascii")

    assert not validate_encoding("unknown-encoding")


def test_validate_protocol():

    assert validate_protocol(0)
    assert validate_protocol(DEFAULT_PROTOCOL)

    assert not validate_protocol(-1)
    assert not validate_protocol(999)


def test_validate_options():

    assert validate_options({})
    assert validate_options({"a": 1})
    assert validate_options(None)

    assert not validate_options([])


def test_validate():

    assert validate(1)
    assert validate({})
    assert validate("abc")

    assert not validate(None)


# ==============================================================================
# Part 7. Diagnostics
# ==============================================================================


def test_summary():

    info = summary()

    assert isinstance(info, dict)

    assert info["encoding"] == DEFAULT_ENCODING
    assert info["pickle_protocol"] == DEFAULT_PROTOCOL


def test_diagnostics():

    info = diagnostics()

    assert isinstance(info, dict)

    assert info["json"] is True
    assert info["pickle"] is True
    assert info["compression"] is True


def test_utility_report():

    report = utility_report()

    assert report["status"] == "ok"
    assert "diagnostics" in report


def test_overall_status():

    assert overall_status() == "healthy"


# ==============================================================================
# Part 8. Public API
# ==============================================================================


def test_public_api():

    expected = {

        # Encoding
        "ensure_bytes",
        "ensure_str",
        "encode_text",
        "decode_text",
        "normalize_encoding",
        "detect_encoding",

        # JSON
        "json_dumps",
        "json_loads",
        "json_snapshot",
        "json_restore",
        "is_json",
        "validate_json",

        # Pickle
        "pickle_dumps",
        "pickle_loads",
        "pickle_snapshot",
        "pickle_restore",
        "is_pickle",
        "validate_pickle",

        # Compression
        "compress",
        "decompress",
        "compress_if_needed",
        "decompress_if_needed",
        "compression_ratio",
        "validate_compression",

        # Mapping
        "deep_merge",
        "deep_copy",
        "flatten_mapping",
        "unflatten_mapping",
        "filter_mapping",
        "validate_mapping",

        # Validation
        "validate_bytes",
        "validate_string",
        "validate_encoding",
        "validate_protocol",
        "validate_options",
        "validate",

        # Diagnostics
        "summary",
        "diagnostics",
        "utility_report",
        "overall_status",

    }

    for name in expected:
        assert name in utils.__all__    