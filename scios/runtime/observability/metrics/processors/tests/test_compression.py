"""
Tests for SciOS Runtime Metrics CompressionProcessor.
"""

from __future__ import annotations

import pytest

from ..compression import CompressionProcessor


# ======================================================================
# Fixtures
# ======================================================================


@pytest.fixture
def processor() -> CompressionProcessor:
    return CompressionProcessor()


# ======================================================================
# Construction
# ======================================================================


def test_default_construction(processor):
    assert processor.name == "CompressionProcessor"
    assert processor.algorithm == "gzip"
    assert processor.level == 6
    assert len(processor) == 0


def test_custom_construction():
    processor = CompressionProcessor(
        algorithm="zlib",
        level=9,
        name="custom",
        description="test",
    )

    assert processor.algorithm == "zlib"
    assert processor.level == 9
    assert processor.name == "custom"
    assert processor.description == "test"


def test_invalid_algorithm():
    with pytest.raises(ValueError):
        CompressionProcessor(
            algorithm="invalid"
        )


def test_invalid_level_type():
    with pytest.raises(TypeError):
        CompressionProcessor(
            level=1.5
        )


def test_invalid_level_low():
    with pytest.raises(ValueError):
        CompressionProcessor(
            level=-1
        )


def test_invalid_level_high():
    with pytest.raises(ValueError):
        CompressionProcessor(
            level=10
        )


# ======================================================================
# Configuration
# ======================================================================


def test_set_algorithm(processor):
    assert processor.set_algorithm(
        "zlib"
    ) is processor

    assert processor.algorithm == "zlib"


def test_set_algorithm_invalid(processor):
    with pytest.raises(ValueError):
        processor.set_algorithm(
            "invalid"
        )


def test_set_level(processor):
    assert processor.set_level(
        9
    ) is processor

    assert processor.level == 9


def test_set_level_invalid(processor):
    with pytest.raises(TypeError):
        processor.set_level(
            1.5
        )

    with pytest.raises(ValueError):
        processor.set_level(
            -1
        )

    with pytest.raises(ValueError):
        processor.set_level(
            10
        )


# ======================================================================
# Transform
# ======================================================================


def test_transform_returns_bytes(processor):
    result = processor.transform(
        {
            "name": "requests",
            "value": 10,
        }
    )

    assert isinstance(
        result,
        bytes,
    )


def test_transform_round_trip(processor):
    metric = {
        "name": "requests",
        "value": 42,
        "labels": {
            "service": "runtime",
        },
    }

    compressed = processor.transform(
        metric
    )

    result = processor.decompress(
        compressed
    )

    assert result == metric


def test_transform_does_not_mutate_input(processor):
    metric = {
        "name": "requests",
        "metadata": {
            "host": "node-1",
        },
    }

    processor.transform(
        metric
    )

    assert metric == {
        "name": "requests",
        "metadata": {
            "host": "node-1",
        },
    }


def test_transform_handles_nested_data(processor):
    metric = {
        "name": "requests",
        "values": [
            1,
            2,
            3,
        ],
        "metadata": {
            "region": "hoa-binh",
        },
    }

    result = processor.decompress(
        processor.transform(metric)
    )

    assert result == metric


def test_transform_unicode(processor):
    metric = {
        "name": "nhiệt độ",
        "value": 25.5,
    }

    result = processor.decompress(
        processor.transform(metric)
    )

    assert result == metric


def test_transform_is_deterministic(processor):
    metric = {
        "b": 2,
        "a": 1,
    }

    first = processor.transform(
        metric
    )

    processor.reset()

    second = processor.transform(
        metric
    )

    assert first == second


# ======================================================================
# Algorithms
# ======================================================================


@pytest.mark.parametrize(
    "algorithm",
    [
        "gzip",
        "zlib",
    ],
)
def test_algorithms_round_trip(algorithm):
    processor = CompressionProcessor(
        algorithm=algorithm
    )

    metric = {
        "name": "requests",
        "value": 123,
    }

    payload = processor.transform(
        metric
    )

    assert processor.decompress(
        payload
    ) == metric


@pytest.mark.parametrize(
    "level",
    range(10),
)
def test_all_compression_levels(level):
    processor = CompressionProcessor(
        level=level
    )

    metric = {
        "name": "requests",
        "value": 100,
    }

    payload = processor.transform(
        metric
    )

    assert processor.decompress(
        payload
    ) == metric


# ======================================================================
# Decompression
# ======================================================================


def test_decompress_requires_bytes(processor):
    with pytest.raises(TypeError):
        processor.decompress(
            "invalid"
        )


def test_decompress_invalid_payload(processor):
    with pytest.raises(Exception):
        processor.decompress(
            b"invalid"
        )


def test_decompress_increments_statistics(processor):
    metric = {
        "name": "requests",
        "value": 1,
    }

    payload = processor.transform(
        metric
    )

    processor.decompress(
        payload
    )

    stats = processor.statistics()

    assert stats["compressed"] == 1
    assert stats["decompressed"] == 1


# ======================================================================
# Compression Statistics
# ======================================================================


def test_initial_statistics(processor):
    stats = processor.statistics()

    assert stats["algorithm"] == "gzip"
    assert stats["level"] == 6
    assert stats["compressed"] == 0
    assert stats["decompressed"] == 0
    assert stats["bytes_in"] == 0
    assert stats["bytes_out"] == 0
    assert stats["ratio"] == 0.0
    assert stats["saved_bytes"] == 0


def test_statistics_after_transform(processor):
    metric = {
        "name": "requests",
        "value": 42,
    }

    processor.transform(
        metric
    )

    stats = processor.statistics()

    assert stats["compressed"] == 1
    assert stats["bytes_in"] > 0
    assert stats["bytes_out"] > 0
    assert stats["ratio"] > 0


def test_ratio(processor):
    metric = {
        "name": "requests",
        "value": 42,
    }

    processor.transform(
        metric
    )

    assert processor.ratio() > 0


def test_saved_bytes(processor):
    metric = {
        "name": "requests",
        "value": 42,
    }

    processor.transform(
        metric
    )

    assert processor.saved_bytes() == (
        processor.statistics()["bytes_in"]
        - processor.statistics()["bytes_out"]
    )


# ======================================================================
# Reset
# ======================================================================


def test_reset(processor):
    metric = {
        "name": "requests",
        "value": 42,
    }

    payload = processor.transform(
        metric
    )

    processor.decompress(
        payload
    )

    assert processor.statistics()["compressed"] == 1
    assert processor.statistics()["decompressed"] == 1

    assert processor.reset() is processor

    stats = processor.statistics()

    assert stats["compressed"] == 0
    assert stats["decompressed"] == 0
    assert stats["bytes_in"] == 0
    assert stats["bytes_out"] == 0
    assert stats["ratio"] == 0.0
    assert stats["saved_bytes"] == 0


def test_reset_preserves_configuration(processor):
    processor.set_algorithm(
        "zlib"
    )
    processor.set_level(
        9
    )

    processor.transform(
        {"name": "requests"}
    )

    processor.reset()

    assert processor.algorithm == "zlib"
    assert processor.level == 9


# ======================================================================
# Protocols
# ======================================================================


def test_len(processor):
    assert len(processor) == 0

    processor.transform(
        {"name": "requests"}
    )

    assert len(processor) == 1


def test_repr(processor):
    text = repr(processor)

    assert text.startswith(
        "CompressionProcessor("
    )
    assert "algorithm='gzip'" in text
    assert "level=6" in text
    assert "compressed=0" in text
    assert "decompressed=0" in text
