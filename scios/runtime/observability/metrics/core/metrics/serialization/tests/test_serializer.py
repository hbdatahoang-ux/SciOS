"""
Tests for serializer.py

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

from scios.runtime.observability.metrics.core.metrics.serialization.encoder import (
    Encoder,
)
from scios.runtime.observability.metrics.core.metrics.serialization.decoder import (
    Decoder,
)
from scios.runtime.observability.metrics.core.metrics.serialization.serializer import (
    DEFAULT_ASCII,
    DEFAULT_COMPACT,
    DEFAULT_ENCODING,
    DEFAULT_INDENT,
    DEFAULT_SORT_KEYS,
    DEFAULT_STRICT,
    Serializer,
)


@pytest.fixture(scope="function")
def serializer() -> Serializer:
    return Serializer()


@pytest.fixture(scope="function")
def compact_serializer() -> Serializer:
    return Serializer(
        compact=True,
    )


@pytest.fixture(scope="function")
def relaxed_serializer() -> Serializer:
    return Serializer(
        strict=False,
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

    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value

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
        "value": 100,
        "flag": True,
    }


@pytest.fixture(scope="function")
def dummy_json():
    return '{"name":"SciOS","value":100,"flag":true}'


@pytest.fixture(scope="function")
def dummy_list():
    return [1, 2, 3]


@pytest.fixture(scope="function")
def dummy_tuple():
    return (1, 2, 3)


@pytest.fixture(scope="function")
def dummy_set():
    return {1, 2, 3}


@pytest.fixture(scope="function")
def dummy_path():
    return Path("example.json")


@pytest.fixture(scope="function")
def dummy_datetime():
    return datetime(2026, 1, 1, 12, 0, 0)


@pytest.fixture(scope="function")
def dummy_dataclass():
    return DummyData(
        "SciOS",
        100,
    )


@pytest.fixture(scope="function")
def dummy_object():
    return DummyObject(
        "SciOS",
        100,
    )


# ==============================================================================
# Part 3. Construction
# ==============================================================================


def test_default_constructor(serializer):
    assert isinstance(serializer, Serializer)

    assert isinstance(serializer.encoder, Encoder)
    assert isinstance(serializer.decoder, Decoder)

    assert serializer.encoding == DEFAULT_ENCODING
    assert serializer.compact is DEFAULT_COMPACT
    assert serializer.strict is DEFAULT_STRICT


def test_custom_constructor():
    s = Serializer(
        encoding="utf-16",
        indent=4,
        sort_keys=False,
        ensure_ascii=False,
        compact=True,
        strict=False,
    )

    assert s.encoding == "utf-16"
    assert s.compact is True
    assert s.strict is False

    assert isinstance(s.encoder, Encoder)
    assert isinstance(s.decoder, Decoder)


def test_slots():
    assert hasattr(Serializer, "__slots__")

    assert Serializer.__slots__ == (
        "_encoder",
        "_decoder",
        "_encoding",
        "_compact",
        "_strict",
    )


def test_annotations():
    annotations = Serializer.__annotations__

    assert "_encoder" in annotations
    assert "_decoder" in annotations
    assert "_encoding" in annotations
    assert "_compact" in annotations
    assert "_strict" in annotations


def test_signature():
    signature = inspect.signature(Serializer)

    expected = (
        "encoding",
        "indent",
        "sort_keys",
        "ensure_ascii",
        "compact",
        "strict",
    )

    for parameter in expected:
        assert parameter in signature.parameters


# ==============================================================================
# Part 4. Properties
# ==============================================================================


def test_encoder_property(serializer):
    assert isinstance(serializer.encoder, Encoder)


def test_decoder_property(serializer):
    assert isinstance(serializer.decoder, Decoder)


def test_encoding_property(serializer):
    assert serializer.encoding == DEFAULT_ENCODING

    serializer.encoding = "utf-16"

    assert serializer.encoding == "utf-16"
    assert serializer.encoder.encoding == "utf-16"
    assert serializer.decoder.encoding == "utf-16"


def test_compact_property(serializer):
    serializer.compact = True

    assert serializer.compact is True
    assert serializer.encoder.compact is True


def test_strict_property(serializer):
    serializer.strict = False

    assert serializer.strict is False
    assert serializer.decoder.strict is False


def test_property_roundtrip(serializer):
    serializer.encoding = "utf-16"
    serializer.compact = True
    serializer.strict = False

    assert serializer.encoding == "utf-16"
    assert serializer.compact is True
    assert serializer.strict is False

    assert serializer.encoder.encoding == "utf-16"
    assert serializer.encoder.compact is True
    assert serializer.decoder.encoding == "utf-16"
    assert serializer.decoder.strict is False


def test_pickle_constructor(serializer):
    restored = pickle.loads(
        pickle.dumps(serializer)
    )

    assert restored == serializer
    assert restored.encoding == serializer.encoding
    assert restored.compact == serializer.compact
    assert restored.strict == serializer.strict

# ==============================================================================
# Part 5. Encode API
# ==============================================================================


def test_encode(serializer, dummy_dict):
    result = serializer.encode(dummy_dict)

    assert isinstance(result, dict)
    assert result == dummy_dict


def test_dumps(serializer, dummy_dict):
    text = serializer.dumps(dummy_dict)

    assert isinstance(text, str)
    assert '"name"' in text
    assert '"SciOS"' in text


def test_dump(serializer, dummy_dict, tmp_path):
    path = tmp_path / "data.json"

    with path.open("w", encoding="utf-8") as fp:
        serializer.dump(dummy_dict, fp)

    assert path.exists()
    assert path.read_text(encoding="utf-8")


def test_encode_many(serializer):
    values = [
        {"a": 1},
        {"b": 2},
    ]

    result = serializer.encode_many(values)

    assert isinstance(result, list)
    assert result == values


def test_encode_metadata(serializer):
    metadata = {
        "version": "1.0",
        "author": "SciOS",
    }

    result = serializer.encode_metadata(metadata)

    assert result == metadata


# ==============================================================================
# Part 6. Decode API
# ==============================================================================


def test_decode(serializer, dummy_dict):
    result = serializer.decode(dummy_dict)

    assert result == dummy_dict


def test_loads(serializer, dummy_json):
    result = serializer.loads(dummy_json)

    assert result["name"] == "SciOS"
    assert result["value"] == 100
    assert result["flag"] is True


def test_load(serializer, tmp_path):
    path = tmp_path / "sample.json"

    path.write_text(
        '{"name":"SciOS","value":10}',
        encoding="utf-8",
    )

    with path.open("r", encoding="utf-8") as fp:
        result = serializer.load(fp)

    assert result["name"] == "SciOS"
    assert result["value"] == 10


def test_decode_many(serializer):
    values = [
        {"a": 1},
        {"b": 2},
    ]

    result = serializer.decode_many(values)

    assert result == values


def test_decode_metadata(serializer):
    metadata = {
        "x": 1,
        "y": 2,
    }

    result = serializer.decode_metadata(metadata)

    assert result == metadata


# ==============================================================================
# Part 7. Roundtrip API
# ==============================================================================


def test_serialize(serializer, dummy_dict):
    text = serializer.serialize(dummy_dict)

    assert isinstance(text, str)
    assert '"name"' in text


def test_deserialize(serializer, dummy_json):
    result = serializer.deserialize(dummy_json)

    assert result["name"] == "SciOS"


def test_roundtrip(serializer, dummy_dict):
    result = serializer.roundtrip(dummy_dict)

    assert result == dummy_dict


def test_serialize_object(serializer, dummy_dict):
    text = serializer.serialize_object(dummy_dict)

    assert isinstance(text, str)


def test_deserialize_object(serializer, dummy_json):
    result = serializer.deserialize_object(dummy_json)

    assert result == serializer.loads(dummy_json)


# ==============================================================================
# Part 8. Generic API
# ==============================================================================


def test_save(serializer, dummy_dict, tmp_path):
    path = tmp_path / "save.json"

    returned = serializer.save(dummy_dict, path)

    assert returned == path
    assert path.exists()


def test_restore(serializer, dummy_dict, tmp_path):
    path = tmp_path / "restore.json"

    serializer.save(dummy_dict, path)

    restored = serializer.restore(path)

    assert restored == dummy_dict


def test_to_json(serializer, dummy_dict):
    text = serializer.to_json(dummy_dict)

    assert isinstance(text, str)
    assert '"SciOS"' in text


def test_from_json(serializer, dummy_json):
    obj = serializer.from_json(dummy_json)

    assert obj["name"] == "SciOS"


def test_convert(serializer, dummy_dict):
    result = serializer.convert(dummy_dict)

    assert result == dummy_dict


# ==============================================================================
# Part 9. Validation
# ==============================================================================


def test_validate(serializer, dummy_dict):
    assert serializer.validate(dummy_dict) is True


def test_is_serializable(serializer, dummy_dict):
    assert serializer.is_serializable(dummy_dict) is True


def test_is_deserializable(serializer, dummy_dict):
    assert serializer.is_deserializable(dummy_dict) is True


# ==============================================================================
# Part 10. Clone API
# ==============================================================================


def test_copy(serializer):
    copied = serializer.copy()

    assert copied == serializer
    assert copied is not serializer


def test_deepcopy(serializer):
    copied = serializer.deepcopy()

    assert copied == serializer
    assert copied is not serializer


def test_clone(serializer):
    cloned = serializer.clone()

    assert cloned == serializer
    assert cloned is not serializer


# ==============================================================================
# Part 11. Python Protocols
# ==============================================================================


def test_call(serializer, dummy_dict):
    assert serializer(dummy_dict) == serializer.encode(dummy_dict)


def test_repr(serializer):
    text = repr(serializer)

    assert isinstance(text, str)
    assert "Serializer" in text


def test_str(serializer):
    text = str(serializer)

    assert isinstance(text, str)
    assert "Serializer" in text


def test_eq():
    assert Serializer() == Serializer()


def test_hash():
    assert isinstance(hash(Serializer()), int)


def test_pickle(serializer):
    restored = pickle.loads(
        pickle.dumps(serializer)
    )

    assert restored == serializer


# ==============================================================================
# Part 12. Diagnostics
# ==============================================================================


def test_summary(serializer):
    summary = serializer.summary()

    assert isinstance(summary, dict)
    assert summary["encoding"] == serializer.encoding
    assert summary["compact"] == serializer.compact
    assert summary["strict"] == serializer.strict


def test_diagnostics(serializer):
    diagnostics = serializer.diagnostics()

    assert diagnostics["type"] == "Serializer"
    assert "summary" in diagnostics
    assert "hash" in diagnostics


def test_serializer_report(serializer):
    report = serializer.serializer_report()

    assert report["status"] == "ready"
    assert "serializer" in report
    assert "encoder" in report
    assert "decoder" in report


def test_overall_status(serializer):
    assert serializer.overall_status() == "ready"


# ==============================================================================
# Part 13. API Freeze
# ==============================================================================


def test_public_api():
    from scios.runtime.observability.metrics.core.metrics.serialization import (
        serializer as module,
    )

    expected = {
        "DEFAULT_ENCODING",
        "DEFAULT_INDENT",
        "DEFAULT_SORT_KEYS",
        "DEFAULT_ASCII",
        "DEFAULT_COMPACT",
        "DEFAULT_STRICT",
        "Serializable",
        "SerializedValue",
        "SerializerOptions",
        "MetadataType",
        "Serializer",
    }

    assert set(module.__all__) == expected


def test_annotations():
    expected = {
        "_encoder",
        "_decoder",
        "_encoding",
        "_compact",
        "_strict",
    }

    assert expected.issubset(Serializer.__annotations__)


def test_slots():
    assert Serializer.__slots__ == (
        "_encoder",
        "_decoder",
        "_encoding",
        "_compact",
        "_strict",
    )


def test_signature():
    signature = inspect.signature(Serializer)

    expected = (
        "encoding",
        "indent",
        "sort_keys",
        "ensure_ascii",
        "compact",
        "strict",
    )

    for parameter in expected:
        assert parameter in signature.parameters    