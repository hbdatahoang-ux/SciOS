"""
Tests for decoder.py

Python 3.11+
"""

from __future__ import annotations

# ==============================================================================
# Part 1. Imports & Fixtures
# ==============================================================================

import inspect
import pickle

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

import pytest

from scios.runtime.observability.metrics.core.metrics.serialization.decoder import (
    DEFAULT_ENCODING,
    DEFAULT_OBJECT_HOOK,
    DEFAULT_PARSE_FLOAT,
    DEFAULT_PARSE_INT,
    DEFAULT_STRICT,
    Decoder,
)


@pytest.fixture(scope="function")
def decoder() -> Decoder:
    """Default decoder."""
    return Decoder()


@pytest.fixture(scope="function")
def relaxed_decoder() -> Decoder:
    """Relaxed decoder."""
    return Decoder(strict=False)


@pytest.fixture(scope="function")
def custom_hook():
    """Simple object hook."""

    def hook(obj: dict):
        obj["hooked"] = True
        return obj

    return hook


@pytest.fixture(scope="function")
def custom_decoder(custom_hook) -> Decoder:
    """Decoder with custom configuration."""
    return Decoder(
        encoding="utf-16",
        strict=False,
        object_hook=custom_hook,
        parse_float=float,
        parse_int=int,
    )


# ==============================================================================
# Part 2. Dummy Data
# ==============================================================================


class DummyEnum(Enum):
    A = 1
    B = 2
    C = 3


@dataclass(slots=True)
class DummyData:
    name: str
    value: int


class DummyObject:
    """Dummy custom object."""

    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value

    def to_dict(self):
        return {
            "name": self.name,
            "value": self.value,
        }

    def __eq__(self, other):
        return (
            isinstance(other, DummyObject)
            and self.name == other.name
            and self.value == other.value
        )


@pytest.fixture(scope="function")
def dummy_dict():
    return {
        "name": "SciOS",
        "value": 123,
        "flag": True,
    }


@pytest.fixture(scope="function")
def dummy_json():
    return '{"name":"SciOS","value":123,"flag":true}'


@pytest.fixture(scope="function")
def dummy_list():
    return [1, 2, 3, 4]


@pytest.fixture(scope="function")
def dummy_tuple():
    return (1, 2, 3)


@pytest.fixture(scope="function")
def dummy_set():
    return {1, 2, 3}


@pytest.fixture(scope="function")
def dummy_bytes():
    return b"hello world"


@pytest.fixture(scope="function")
def dummy_path():
    return Path("example.txt")


@pytest.fixture(scope="function")
def dummy_datetime():
    return datetime(2026, 1, 1, 12, 0, 0)


@pytest.fixture(scope="function")
def dummy_dataclass():
    return DummyData(
        name="SciOS",
        value=42,
    )


@pytest.fixture(scope="function")
def dummy_object():
    return DummyObject(
        "SciOS",
        999,
    )


# ==============================================================================
# Part 3. Construction
# ==============================================================================


def test_default_constructor(decoder):
    """Default constructor."""
    assert isinstance(decoder, Decoder)

    assert decoder.encoding == DEFAULT_ENCODING
    assert decoder.strict is DEFAULT_STRICT
    assert decoder.object_hook is DEFAULT_OBJECT_HOOK
    assert decoder.parse_float is DEFAULT_PARSE_FLOAT
    assert decoder.parse_int is DEFAULT_PARSE_INT


def test_custom_constructor(custom_decoder, custom_hook):
    """Custom constructor."""

    assert custom_decoder.encoding == "utf-16"
    assert custom_decoder.strict is False
    assert custom_decoder.object_hook is custom_hook
    assert custom_decoder.parse_float is float
    assert custom_decoder.parse_int is int


def test_constructor_keywords():
    """Keyword constructor."""

    decoder = Decoder(
        encoding="ascii",
        strict=False,
    )

    assert decoder.encoding == "ascii"
    assert decoder.strict is False


def test_slots():
    """Slots."""

    assert hasattr(Decoder, "__slots__")

    expected = {
        "_encoding",
        "_strict",
        "_object_hook",
        "_parse_float",
        "_parse_int",
    }

    assert set(Decoder.__slots__) == expected


def test_annotations():
    """Annotations."""

    annotations = Decoder.__annotations__

    assert "_encoding" in annotations
    assert "_strict" in annotations
    assert "_object_hook" in annotations
    assert "_parse_float" in annotations
    assert "_parse_int" in annotations


def test_signature():
    """Constructor signature."""

    sig = inspect.signature(Decoder)

    assert "encoding" in sig.parameters
    assert "strict" in sig.parameters
    assert "object_hook" in sig.parameters
    assert "parse_float" in sig.parameters
    assert "parse_int" in sig.parameters


# ==============================================================================
# Part 4. Properties
# ==============================================================================


def test_encoding_property(decoder):
    assert decoder.encoding == DEFAULT_ENCODING

    decoder.encoding = "utf-16"

    assert decoder.encoding == "utf-16"


def test_strict_property(decoder):
    assert decoder.strict is True

    decoder.strict = False

    assert decoder.strict is False


def test_object_hook_property(decoder, custom_hook):
    decoder.object_hook = custom_hook

    assert decoder.object_hook is custom_hook


def test_parse_float_property(decoder):
    decoder.parse_float = float

    assert decoder.parse_float is float


def test_parse_int_property(decoder):
    decoder.parse_int = int

    assert decoder.parse_int is int


def test_property_roundtrip(custom_decoder, custom_hook):
    """All properties remain consistent."""

    assert custom_decoder.encoding == "utf-16"
    assert custom_decoder.strict is False
    assert custom_decoder.object_hook is custom_hook
    assert custom_decoder.parse_float is float
    assert custom_decoder.parse_int is int


def test_pickle_constructor(decoder):
    """Decoder can be pickled."""

    restored = pickle.loads(pickle.dumps(decoder))

    assert restored == decoder
    assert restored.encoding == decoder.encoding
    assert restored.strict == decoder.strict

# ==============================================================================
# Part 5. Primitive Decoding
# ==============================================================================


def test_decode_none(decoder):
    assert decoder.decode_none(None) is None


def test_decode_bool(decoder):
    assert decoder.decode_bool(True) is True
    assert decoder.decode_bool(False) is False


def test_decode_int(decoder):
    assert decoder.decode_int(10) == 10
    assert decoder.decode_int("20") == 20


def test_decode_float(decoder):
    assert decoder.decode_float(1.5) == 1.5
    assert decoder.decode_float("3.14") == pytest.approx(3.14)


def test_decode_str(decoder):
    assert decoder.decode_str("abc") == "abc"
    assert decoder.decode_str(b"abc") == "abc"


def test_decode_bytes(decoder):
    assert decoder.decode_bytes(b"abc") == b"abc"
    assert decoder.decode_bytes("abc") == b"abc"


# ==============================================================================
# Part 6. Container Decoding
# ==============================================================================


def test_decode_list(decoder, dummy_list):
    result = decoder.decode_list(dummy_list)

    assert result == dummy_list
    assert isinstance(result, list)


def test_decode_tuple(decoder, dummy_tuple):
    result = decoder.decode_tuple(dummy_tuple)

    assert result == dummy_tuple
    assert isinstance(result, tuple)


def test_decode_set(decoder, dummy_set):
    result = decoder.decode_set(dummy_set)

    assert result == dummy_set
    assert isinstance(result, set)


def test_decode_dict(decoder, dummy_dict):
    result = decoder.decode_dict(dummy_dict)

    assert result == dummy_dict
    assert isinstance(result, dict)


def test_decode_mapping(decoder, dummy_dict):
    result = decoder.decode_mapping(dummy_dict)

    assert result == dummy_dict
    assert isinstance(result, dict)


# ==============================================================================
# Part 7. Object Decoding
# ==============================================================================


def test_decode_dataclass(decoder):
    value = {
        "name": "SciOS",
        "value": 100,
    }

    obj = decoder.decode_dataclass(DummyData, value)

    assert isinstance(obj, DummyData)
    assert obj.name == "SciOS"
    assert obj.value == 100


def test_decode_enum(decoder):
    assert decoder.decode_enum(DummyEnum, 1) is DummyEnum.A
    assert decoder.decode_enum(DummyEnum, 2) is DummyEnum.B


def test_decode_datetime(decoder):
    value = "2026-01-01T12:00:00"

    dt = decoder.decode_datetime(value)

    assert isinstance(dt, datetime)
    assert dt.year == 2026
    assert dt.month == 1
    assert dt.day == 1


def test_decode_path(decoder):
    path = decoder.decode_path("example.txt")

    assert isinstance(path, Path)
    assert path.name == "example.txt"


def test_decode_object(decoder, dummy_dict):
    result = decoder.decode_object(dummy_dict)

    assert result == dummy_dict


# ==============================================================================
# Part 8. Generic API
# ==============================================================================


def test_decode(decoder):
    assert decoder.decode(None) is None
    assert decoder.decode(True) is True
    assert decoder.decode(10) == 10
    assert decoder.decode(3.5) == 3.5
    assert decoder.decode("abc") == "abc"
    assert decoder.decode([1, 2]) == [1, 2]
    assert decoder.decode({"a": 1}) == {"a": 1}


def test_loads(decoder, dummy_json):
    result = decoder.loads(dummy_json)

    assert result["name"] == "SciOS"
    assert result["value"] == 123
    assert result["flag"] is True


def test_load(decoder, tmp_path):
    file = tmp_path / "sample.json"

    file.write_text(
        '{"name":"SciOS","value":1}',
        encoding="utf-8",
    )

    with file.open("r", encoding="utf-8") as fp:
        result = decoder.load(fp)

    assert result["name"] == "SciOS"
    assert result["value"] == 1


def test_decode_many(decoder):
    values = [
        1,
        "2",
        3.0,
        True,
        None,
    ]

    result = decoder.decode_many(values)

    assert result == [1, "2", 3.0, True, None]


def test_decode_metadata(decoder, dummy_dict):
    result = decoder.decode_metadata(dummy_dict)

    assert result == dummy_dict


def test_roundtrip_dict(decoder, dummy_dict):
    encoded = dummy_dict.copy()

    decoded = decoder.decode(encoded)

    assert decoded == dummy_dict


def test_roundtrip_json(decoder, dummy_json):
    decoded = decoder.loads(dummy_json)

    assert decoded["name"] == "SciOS"
    assert decoded["value"] == 123
    assert decoded["flag"] is True

# ==============================================================================
# Part 9. Validation
# ==============================================================================


def test_validate(decoder):
    assert decoder.validate(None) is True
    assert decoder.validate(True) is True
    assert decoder.validate(123) is True
    assert decoder.validate(3.14) is True
    assert decoder.validate("SciOS") is True
    assert decoder.validate([1, 2, 3]) is True
    assert decoder.validate({"a": 1}) is True


def test_is_decodable(decoder):
    assert decoder.is_decodable(None)
    assert decoder.is_decodable(False)
    assert decoder.is_decodable(42)
    assert decoder.is_decodable(1.23)
    assert decoder.is_decodable("hello")
    assert decoder.is_decodable({"x": 1})


# ==============================================================================
# Part 10. Clone API
# ==============================================================================


def test_copy(decoder):
    copied = decoder.copy()

    assert copied == decoder
    assert copied is not decoder
    assert isinstance(copied, Decoder)


def test_deepcopy(decoder):
    copied = decoder.deepcopy()

    assert copied == decoder
    assert copied is not decoder
    assert isinstance(copied, Decoder)


def test_clone(decoder):
    cloned = decoder.clone()

    assert cloned == decoder
    assert cloned is not decoder
    assert isinstance(cloned, Decoder)


# ==============================================================================
# Part 11. Python Protocols
# ==============================================================================


def test_call(decoder):
    assert decoder("hello") == "hello"
    assert decoder(123) == 123
    assert decoder({"a": 1}) == {"a": 1}


def test_repr(decoder):
    text = repr(decoder)

    assert isinstance(text, str)
    assert "Decoder" in text


def test_str(decoder):
    text = str(decoder)

    assert isinstance(text, str)
    assert "Decoder" in text


def test_eq():
    a = Decoder()
    b = Decoder()

    assert a == b
    assert not (a != b)


def test_hash():
    decoder = Decoder()

    assert isinstance(hash(decoder), int)


def test_pickle(decoder):
    restored = pickle.loads(
        pickle.dumps(decoder)
    )

    assert restored == decoder
    assert restored.encoding == decoder.encoding
    assert restored.strict == decoder.strict


# ==============================================================================
# Part 12. Diagnostics
# ==============================================================================


def test_summary(decoder):
    summary = decoder.summary()

    assert isinstance(summary, dict)

    assert summary["encoding"] == decoder.encoding
    assert summary["strict"] == decoder.strict


def test_diagnostics(decoder):
    diagnostics = decoder.diagnostics()

    assert isinstance(diagnostics, dict)

    assert diagnostics["type"] == "Decoder"
    assert "summary" in diagnostics
    assert "hash" in diagnostics


def test_decoder_report(decoder):
    report = decoder.decoder_report()

    assert isinstance(report, dict)

    assert report["status"] == "ready"
    assert "decoder" in report


def test_overall_status(decoder):
    assert decoder.overall_status() == "ready"


# ==============================================================================
# Part 13. API Freeze
# ==============================================================================


def test_public_api():
    from scios.runtime.observability.metrics.core.metrics.serialization import (
        decoder as module,
    )

    expected = {
        "DEFAULT_ENCODING",
        "DEFAULT_STRICT",
        "DEFAULT_OBJECT_HOOK",
        "DEFAULT_PARSE_FLOAT",
        "DEFAULT_PARSE_INT",
        "DecodedValue",
        "DecoderOptions",
        "ObjectHook",
        "MetadataType",
        "Decoder",
    }

    assert set(module.__all__) == expected


def test_annotations():
    annotations = Decoder.__annotations__

    expected = {
        "_encoding",
        "_strict",
        "_object_hook",
        "_parse_float",
        "_parse_int",
    }

    assert expected.issubset(annotations.keys())


def test_slots():
    expected = (
        "_encoding",
        "_strict",
        "_object_hook",
        "_parse_float",
        "_parse_int",
    )

    assert Decoder.__slots__ == expected


def test_signature():
    signature = inspect.signature(Decoder)

    expected = (
        "encoding",
        "strict",
        "object_hook",
        "parse_float",
        "parse_int",
    )

    for parameter in expected:
        assert parameter in signature.parameters        