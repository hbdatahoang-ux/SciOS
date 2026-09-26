"""
Tests for SciOS Runtime Metrics BatchingProcessor.
"""

from __future__ import annotations

import pytest

from ..batching import BatchingProcessor


# ======================================================================
# Fixtures
# ======================================================================


@pytest.fixture
def processor() -> BatchingProcessor:
    return BatchingProcessor()


# ======================================================================
# Construction
# ======================================================================


def test_default_construction(processor):
    assert processor.name == "BatchingProcessor"
    assert processor.batch_size == 10
    assert processor.pending() == 0
    assert len(processor) == 0
    assert not processor


def test_custom_construction():
    processor = BatchingProcessor(
        batch_size=3,
        name="custom",
        description="test",
    )

    assert processor.batch_size == 3
    assert processor.name == "custom"
    assert processor.description == "test"


def test_batch_size_must_be_integer():
    with pytest.raises(TypeError):
        BatchingProcessor(batch_size=1.5)


def test_batch_size_must_be_positive():
    with pytest.raises(ValueError):
        BatchingProcessor(batch_size=0)

    with pytest.raises(ValueError):
        BatchingProcessor(batch_size=-1)


# ======================================================================
# Configuration
# ======================================================================


def test_set_batch_size(processor):
    assert processor.set_batch_size(5) is processor
    assert processor.batch_size == 5


def test_set_batch_size_rejects_invalid_value(processor):
    with pytest.raises(TypeError):
        processor.set_batch_size(1.5)

    with pytest.raises(ValueError):
        processor.set_batch_size(0)


def test_set_batch_size_preserves_buffer(processor):
    processor.set_batch_size(3)

    processor.transform({"id": 1})

    assert processor.pending() == 1

    processor.set_batch_size(5)

    assert processor.pending() == 1
    assert processor.batch_size == 5


# ======================================================================
# Transform
# ======================================================================


def test_transform_buffers_metric(processor):
    processor.set_batch_size(3)

    assert processor.transform(
        {"id": 1}
    ) is None

    assert processor.pending() == 1


def test_transform_emits_full_batch(processor):
    processor.set_batch_size(3)

    assert processor.transform({"id": 1}) is None
    assert processor.transform({"id": 2}) is None

    batch = processor.transform(
        {"id": 3}
    )

    assert batch == [
        {"id": 1},
        {"id": 2},
        {"id": 3},
    ]

    assert processor.pending() == 0


def test_transform_multiple_batches(processor):
    processor.set_batch_size(2)

    first = processor.transform({"id": 1})
    assert first is None

    first = processor.transform({"id": 2})

    assert first == [
        {"id": 1},
        {"id": 2},
    ]

    second = processor.transform({"id": 3})
    assert second is None

    second = processor.transform({"id": 4})

    assert second == [
        {"id": 3},
        {"id": 4},
    ]

    assert processor.pending() == 0


def test_transform_does_not_mutate_input(processor):
    processor.set_batch_size(2)

    metric = {
        "name": "requests",
        "metadata": {
            "host": "node-1",
        },
    }

    processor.transform(metric)

    metric["metadata"]["host"] = "node-2"

    batch = processor.transform(
        {"name": "other"}
    )

    assert batch[0]["metadata"]["host"] == "node-1"


def test_transform_deepcopies_nested_values(processor):
    processor.set_batch_size(1)

    metadata = {
        "host": "node-1",
    }

    batch = processor.transform(
        {
            "name": "requests",
            "metadata": metadata,
        }
    )

    batch[0]["metadata"]["host"] = "node-2"

    assert metadata["host"] == "node-1"


def test_transform_accepts_non_dict_metrics(processor):
    processor.set_batch_size(2)

    assert processor.transform("metric") is None

    batch = processor.transform(42)

    assert batch == [
        "metric",
        42,
    ]


# ======================================================================
# Flush
# ======================================================================


def test_flush_empty_returns_none(processor):
    assert processor.flush() is None


def test_flush_partial_batch(processor):
    processor.set_batch_size(5)

    processor.transform({"id": 1})
    processor.transform({"id": 2})

    batch = processor.flush()

    assert batch == [
        {"id": 1},
        {"id": 2},
    ]

    assert processor.pending() == 0


def test_flush_full_batch_is_not_available_after_emit(processor):
    processor.set_batch_size(2)

    processor.transform({"id": 1})
    processor.transform({"id": 2})

    assert processor.flush() is None


def test_flush_can_be_called_repeatedly(processor):
    processor.set_batch_size(5)

    processor.transform({"id": 1})

    first = processor.flush()

    assert first == [{"id": 1}]
    assert processor.flush() is None

    processor.transform({"id": 2})

    second = processor.flush()

    assert second == [{"id": 2}]


# ======================================================================
# Buffer Inspection
# ======================================================================


def test_pending(processor):
    processor.set_batch_size(3)

    processor.transform({"id": 1})
    processor.transform({"id": 2})

    assert processor.pending() == 2


def test_buffered_returns_copy(processor):
    processor.set_batch_size(3)

    processor.transform(
        {
            "id": 1,
            "metadata": {
                "host": "node-1",
            },
        }
    )

    buffered = processor.buffered()

    buffered[0]["metadata"]["host"] = "node-2"

    assert processor.buffered()[0]["metadata"]["host"] == "node-1"


def test_is_empty(processor):
    assert processor.is_empty()

    processor.set_batch_size(2)
    processor.transform({"id": 1})

    assert not processor.is_empty()


def test_is_full(processor):
    processor.set_batch_size(2)

    assert not processor.is_full()

    processor.transform({"id": 1})

    assert not processor.is_full()

    processor.transform({"id": 2})

    assert processor.is_full()


# ======================================================================
# Statistics
# ======================================================================


def test_statistics(processor):
    processor.set_batch_size(2)

    processor.transform({"id": 1})
    processor.transform({"id": 2})
    processor.transform({"id": 3})

    stats = processor.statistics()

    assert stats["batch_size"] == 2
    assert stats["pending"] == 1
    assert stats["processed"] == 3
    assert stats["batches"] == 1
    assert stats["flushed"] == 0


def test_statistics_after_flush(processor):
    processor.set_batch_size(5)

    processor.transform({"id": 1})
    processor.transform({"id": 2})

    processor.flush()

    stats = processor.statistics()

    assert stats["processed"] == 2
    assert stats["batches"] == 1
    assert stats["flushed"] == 1
    assert stats["pending"] == 0


# ======================================================================
# Reset
# ======================================================================


def test_reset(processor):
    processor.set_batch_size(3)

    processor.transform({"id": 1})
    processor.transform({"id": 2})

    assert processor.pending() == 2
    assert processor.statistics()["processed"] == 2

    assert processor.reset() is processor

    stats = processor.statistics()

    assert stats["batch_size"] == 3
    assert stats["pending"] == 0
    assert stats["processed"] == 0
    assert stats["batches"] == 0
    assert stats["flushed"] == 0


def test_reset_preserves_configuration(processor):
    processor.set_batch_size(7)

    processor.transform({"id": 1})

    processor.reset()

    assert processor.batch_size == 7


# ======================================================================
# Python Protocols
# ======================================================================


def test_len(processor):
    processor.set_batch_size(3)

    assert len(processor) == 0

    processor.transform({"id": 1})
    processor.transform({"id": 2})

    assert len(processor) == 2


def test_bool(processor):
    processor.set_batch_size(2)

    assert not processor

    processor.transform({"id": 1})

    assert processor


def test_repr(processor):
    text = repr(processor)

    assert text.startswith(
        "BatchingProcessor("
    )
    assert "batch_size=10" in text
    assert "pending=0" in text
    assert "processed=0" in text
    assert "batches=0" in text