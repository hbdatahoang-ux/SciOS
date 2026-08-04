# ==========================================================
# Part 1. Imports & Fixtures
# ==========================================================

from __future__ import annotations

import dataclasses
import enum
import io
import json
import pickle
from datetime import UTC, datetime
from pathlib import Path

import pytest

from scios.runtime.observability.metrics.core.metrics.serialization.encoder import (
    MetricEncoder,
    DEFAULT_INDENT,
    DEFAULT_SORT_KEYS,
    DEFAULT_ASCII,
    DEFAULT_ENCODING,
    DEFAULT_COMPACT,
)


@pytest.fixture
def encoder() -> MetricEncoder:
    return MetricEncoder()


@pytest.fixture
def custom_encoder() -> MetricEncoder:
    return MetricEncoder(
        indent=4,
        sort_keys=False,
        ensure_ascii=False,
        encoding="utf-16",
        compact=True,
    )


# ==========================================================
# Part 2. Dummy Data
# ==========================================================


class DummyEnum(enum.Enum):
    A = "a"
    B = "b"


@dataclasses.dataclass
class DummyData:
    x: int
    y: str


DUMMY_NONE = None
DUMMY_BOOL = True
DUMMY_INT = 123
DUMMY_FLOAT = 3.14
DUMMY_STR = "hello"
DUMMY_BYTES = b"abc"

DUMMY_LIST = [1, 2, 3]
DUMMY_TUPLE = (1, 2)
DUMMY_SET = {1, 2}
DUMMY_DICT = {"a": 1, "b": 2}

DUMMY_ENUM = DummyEnum.A
DUMMY_DATACLASS = DummyData(1, "x")
DUMMY_DATETIME = datetime(2024, 1, 1, tzinfo=UTC)
DUMMY_PATH = Path("demo.txt")

DUMMY_OBJECT = {
    "enum": DUMMY_ENUM,
    "data": DUMMY_DATACLASS,
    "time": DUMMY_DATETIME,
    "path": DUMMY_PATH,
}

DUMMY_METADATA = {
    "author": "SciOS",
    "version": "1.0",
}


# ==========================================================
# Part 3. Construction
# ==========================================================


class TestConstruction:

    def test_create_default(self):
        enc = MetricEncoder()

        assert enc.indent == DEFAULT_INDENT
        assert enc.sort_keys is DEFAULT_SORT_KEYS
        assert enc.ensure_ascii is DEFAULT_ASCII
        assert enc.encoding == DEFAULT_ENCODING
        assert enc.compact is DEFAULT_COMPACT

    def test_create_custom(self, custom_encoder):
        assert custom_encoder.indent == 4
        assert custom_encoder.sort_keys is False
        assert custom_encoder.ensure_ascii is False
        assert custom_encoder.encoding == "utf-16"
        assert custom_encoder.compact is True


# ==========================================================
# Part 4. Properties
# ==========================================================


class TestProperties:

    def test_indent(self, encoder):
        assert encoder.indent == DEFAULT_INDENT

    def test_sort_keys(self, encoder):
        assert encoder.sort_keys is DEFAULT_SORT_KEYS

    def test_ascii(self, encoder):
        assert encoder.ensure_ascii is DEFAULT_ASCII

    def test_encoding(self, encoder):
        assert encoder.encoding == DEFAULT_ENCODING

    def test_compact(self, encoder):
        assert encoder.compact is DEFAULT_COMPACT

# ==========================================================
# Part 5. Primitive Encoding
# ==========================================================


class TestPrimitiveEncoding:

    def test_encode_none(self, encoder):
        assert encoder.encode_none(None) is None

    def test_encode_bool(self, encoder):
        assert encoder.encode_bool(DUMMY_BOOL) is True

    def test_encode_int(self, encoder):
        assert encoder.encode_int(DUMMY_INT) == 123

    def test_encode_float(self, encoder):
        assert encoder.encode_float(DUMMY_FLOAT) == pytest.approx(3.14)

    def test_encode_str(self, encoder):
        assert encoder.encode_str(DUMMY_STR) == "hello"

    def test_encode_bytes(self, encoder):
        assert encoder.encode_bytes(DUMMY_BYTES) == "YWJj"


# ==========================================================
# Part 6. Container Encoding
# ==========================================================


class TestContainerEncoding:

    def test_encode_list(self, encoder):
        assert encoder.encode_list(DUMMY_LIST) == [1, 2, 3]

    def test_encode_tuple(self, encoder):
        assert encoder.encode_tuple(DUMMY_TUPLE) == [1, 2]

    def test_encode_set(self, encoder):
        assert sorted(encoder.encode_set(DUMMY_SET)) == [1, 2]

    def test_encode_dict(self, encoder):
        assert encoder.encode_dict(DUMMY_DICT) == DUMMY_DICT

    def test_encode_mapping(self, encoder):
        assert encoder.encode_mapping(DUMMY_DICT) == DUMMY_DICT


# ==========================================================
# Part 7. Object Encoding
# ==========================================================


class TestObjectEncoding:

    def test_encode_dataclass(self, encoder):
        value = encoder.encode_dataclass(DUMMY_DATACLASS)
        assert value == {"x": 1, "y": "x"}

    def test_encode_enum(self, encoder):
        assert encoder.encode_enum(DUMMY_ENUM) == "a"

    def test_encode_datetime(self, encoder):
        value = encoder.encode_datetime(DUMMY_DATETIME)
        assert value == DUMMY_DATETIME.isoformat()

    def test_encode_path(self, encoder):
        assert encoder.encode_path(DUMMY_PATH) == str(DUMMY_PATH)

    def test_encode_object(self, encoder):
        obj = encoder.encode_object(DUMMY_OBJECT)

        assert obj["enum"] == "a"
        assert obj["data"] == {"x": 1, "y": "x"}
        assert obj["time"] == DUMMY_DATETIME.isoformat()
        assert obj["path"] == str(DUMMY_PATH)


# ==========================================================
# Part 8. Generic API
# ==========================================================


class TestGenericAPI:

    def test_encode(self, encoder):
        assert encoder.encode(DUMMY_DICT) == DUMMY_DICT

    def test_dumps(self, encoder):
        text = encoder.dumps(DUMMY_DICT)
        assert isinstance(text, str)
        assert json.loads(text) == DUMMY_DICT

    def test_dump(self, encoder):
        stream = io.StringIO()
        encoder.dump(DUMMY_DICT, stream)

        stream.seek(0)
        assert json.loads(stream.read()) == DUMMY_DICT

    def test_encode_many(self, encoder):
        result = encoder.encode_many([DUMMY_INT, DUMMY_STR, DUMMY_DICT])

        assert result == [
            123,
            "hello",
            DUMMY_DICT,
        ]

    def test_encode_metadata(self, encoder):
        assert encoder.encode_metadata(DUMMY_METADATA) == DUMMY_METADATA

    def test_roundtrip_dict(self, encoder):
        encoded = encoder.encode(DUMMY_OBJECT)

        assert encoded["enum"] == "a"
        assert encoded["data"]["x"] == 1
        assert encoded["path"] == str(DUMMY_PATH)

    def test_roundtrip_json(self, encoder):
        text = encoder.dumps(DUMMY_OBJECT)

        decoded = json.loads(text)

        assert decoded["enum"] == "a"
        assert decoded["data"]["y"] == "x"
        assert decoded["path"] == str(DUMMY_PATH)

# ==========================================================
# Part 9. Validation
# ==========================================================


class TestValidation:

    def test_validate(self, encoder):
        assert encoder.validate(DUMMY_OBJECT) is True

    def test_is_serializable(self, encoder):
        assert encoder.is_serializable(DUMMY_OBJECT) is True
        assert encoder.is_serializable(DUMMY_DICT) is True


# ==========================================================
# Part 10. Clone API
# ==========================================================


class TestCloneAPI:

    def test_copy(self, encoder):
        other = encoder.copy()

        assert other == encoder
        assert other is not encoder

    def test_deepcopy(self, encoder):
        other = encoder.deepcopy()

        assert other == encoder
        assert other is not encoder

    def test_clone(self, encoder):
        other = encoder.clone()

        assert other == encoder
        assert other is not encoder


# ==========================================================
# Part 11. Python Protocols
# ==========================================================


class TestPythonProtocols:

    def test_call(self, encoder):
        assert encoder(DUMMY_DICT) == DUMMY_DICT

    def test_repr(self, encoder):
        assert "MetricEncoder" in repr(encoder)

    def test_str(self, encoder):
        assert isinstance(str(encoder), str)

    def test_eq(self, encoder):
        assert encoder == encoder.copy()

    def test_hash(self, encoder):
        assert isinstance(hash(encoder), int)

    def test_pickle(self, encoder):
        restored = pickle.loads(pickle.dumps(encoder))

        assert restored == encoder


# ==========================================================
# Part 12. Diagnostics
# ==========================================================


class TestDiagnostics:

    def test_summary(self, encoder):
        value = encoder.summary()

        assert isinstance(value, dict)

    def test_diagnostics(self, encoder):
        value = encoder.diagnostics()

        assert isinstance(value, dict)

    def test_encoder_report(self, encoder):
        value = encoder.encoder_report()

        assert isinstance(value, dict)

    def test_overall_status(self, encoder):
        assert encoder.overall_status() is not None


# ==========================================================
# Part 13. API Freeze
# ==========================================================


class TestAPIFreeze:

    def test_public_api(self):
        from scios.runtime.observability.metrics.core.metrics.serialization import encoder as module

        assert "MetricEncoder" in module.__all__

    def test_annotations(self):
        assert hasattr(MetricEncoder, "__annotations__")

    def test_slots(self):
        assert hasattr(MetricEncoder, "__slots__")

    def test_signature(self):
        import inspect

        sig = inspect.signature(MetricEncoder)

        assert "indent" in sig.parameters
        assert "sort_keys" in sig.parameters
        assert "ensure_ascii" in sig.parameters                