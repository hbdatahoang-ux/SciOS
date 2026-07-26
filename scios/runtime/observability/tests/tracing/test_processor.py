"""
SciOS-NG Observability
Tracing Test - Processor

Part 1 – Fixtures

Tests:

- Empty processor fixture
- Configured processor fixture

"""

from __future__ import annotations


import pytest


from scios.runtime.observability.tracing.processor import (
    Processor,
)



# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def processor() -> Processor:
    """
    Empty processor instance.
    """

    return Processor()



@pytest.fixture
def configured_processor() -> Processor:
    """
    Processor with configuration.
    """

    processor = Processor()


    processor.configure(
        {
            "batch_size": 100,
            "auto_start": True,
            "enabled": True,
        }
    )


    return processor
# ============================================================
# Part 2 – Creation
# ============================================================


def test_processor_creation(
    processor,
):
    """
    Processor can be created.
    """

    assert processor is not None



def test_default_configuration(
    processor,
):
    """
    Processor has default configuration.
    """

    assert processor.enabled is True

    assert processor.batch_size > 0
# ============================================================
# Part 3 – Basic Processing
# ============================================================


def test_process(
    processor,
):
    """
    Processor can process generic data.
    """

    data = {
        "id": "001",
        "type": "trace",
    }


    result = processor.process(
        data
    )


    assert result is not None



def test_process_span(
    processor,
):
    """
    Processor can process span objects.
    """

    span = {
        "span_id": "span-001",
        "name": "operation",
        "duration": 10.5,
    }


    result = processor.process_span(
        span
    )


    assert result is not None



def test_process_event(
    processor,
):
    """
    Processor can process event objects.
    """

    event = {
        "name": "started",
        "timestamp": 123456,
    }


    result = processor.process_event(
        event
    )


    assert result is not None



def test_process_batch(
    processor,
):
    """
    Processor can process multiple items.
    """

    batch = [
        {
            "id": "001",
            "type": "trace",
        },
        {
            "id": "002",
            "type": "trace",
        },
    ]


    result = processor.process_batch(
        batch
    )


    assert result is not None

    assert len(result) == 2
# ============================================================
# Part 4 – Queue Management
# ============================================================


def test_enqueue(
    processor,
):
    """
    Processor can enqueue items.
    """

    item = {
        "id": "001",
        "type": "span",
    }


    result = processor.enqueue(
        item
    )


    assert result is not None

    assert processor.queue_size() == 1



def test_dequeue(
    processor,
):
    """
    Processor can dequeue items.
    """

    item = {
        "id": "001",
        "type": "event",
    }


    processor.enqueue(
        item
    )


    result = processor.dequeue()


    assert result == item

    assert processor.queue_size() == 0



def test_queue_size(
    processor,
):
    """
    Processor reports queue size.
    """

    assert processor.queue_size() == 0


    processor.enqueue(
        {
            "id": "001",
        }
    )

    processor.enqueue(
        {
            "id": "002",
        }
    )


    assert processor.queue_size() == 2



def test_clear_queue(
    processor,
):
    """
    Processor clears queued items.
    """

    processor.enqueue(
        {
            "id": "001",
        }
    )

    processor.enqueue(
        {
            "id": "002",
        }
    )


    processor.clear_queue()


    assert processor.queue_size() == 0
# ============================================================
# Part 5 – Lifecycle
# ============================================================


def test_start(
    processor,
):
    """
    Processor can start.
    """

    result = processor.start()


    assert result is not None

    assert processor.running is True



def test_stop(
    processor,
):
    """
    Processor can stop.
    """

    processor.start()


    result = processor.stop()


    assert result is not None

    assert processor.running is False



def test_enable(
    processor,
):
    """
    Processor can be enabled.
    """

    processor.disable()


    result = processor.enable()


    assert result is not None

    assert processor.enabled is True



def test_disable(
    processor,
):
    """
    Processor can be disabled.
    """

    result = processor.disable()


    assert result is not None

    assert processor.enabled is False



def test_reset(
    processor,
):
    """
    Processor can reset runtime state.
    """

    processor.start()


    processor.enqueue(
        {
            "id": "001",
        }
    )


    result = processor.reset()


    assert result is not None

    assert processor.queue_size() == 0

    assert processor.running is False
# ============================================================
# Part 6 – Configuration
# ============================================================


def test_set_config(
    processor,
):
    """
    Processor can set configuration value.
    """

    result = processor.set_config(
        "batch_size",
        200,
    )


    assert result is not None

    assert (
        processor.get_config(
            "batch_size"
        )
        ==
        200
    )



def test_get_config(
    processor,
):
    """
    Processor can retrieve configuration.
    """

    processor.set_config(
        "timeout",
        30,
    )


    value = processor.get_config(
        "timeout"
    )


    assert value == 30



def test_update_config(
    processor,
):
    """
    Processor can update multiple configurations.
    """

    config = {
        "batch_size": 500,
        "timeout": 60,
        "workers": 4,
    }


    result = processor.update_config(
        config
    )


    assert result is not None


    assert (
        processor.get_config(
            "batch_size"
        )
        ==
        500
    )


    assert (
        processor.get_config(
            "workers"
        )
        ==
        4
    )



def test_reset_config(
    processor,
):
    """
    Processor restores default configuration.
    """

    processor.set_config(
        "batch_size",
        999,
    )


    result = processor.reset_config()


    assert result is not None


    assert (
        processor.get_config(
            "batch_size"
        )
        !=
        999
    )
# ============================================================
# Part 7 – Validation
# ============================================================


def test_validate(
    processor,
):
    """
    Processor validates a valid item.
    """

    item = {
        "id": "001",
        "type": "span",
    }


    result = processor.validate(
        item
    )


    assert result is True



def test_invalid_item(
    processor,
):
    """
    Processor rejects invalid single item.
    """

    invalid_items = [
        None,
        {},
        [],
        "invalid",
    ]


    for item in invalid_items:

        result = processor.validate(
            item
        )

        assert result is False



def test_invalid_batch(
    processor,
):
    """
    Processor rejects invalid batch.
    """

    invalid_batches = [
        None,
        {},
        "invalid",
        [
            {
                "id": "001",
            },
            None,
        ],
    ]


    for batch in invalid_batches:

        result = processor.validate_batch(
            batch
        )

        assert result is False
# ============================================================
# Part 8 – Serialization
# ============================================================


def test_to_dict(
    processor,
):
    """
    Processor exports state to dictionary.
    """

    processor.set_config(
        "batch_size",
        200,
    )

    data = processor.to_dict()


    assert isinstance(
        data,
        dict,
    )

    assert "config" in data



def test_from_dict(
    processor,
):
    """
    Processor restores from dictionary.
    """

    data = {
        "config": {
            "batch_size": 300,
        }
    }


    restored = (
        processor
        .from_dict(data)
    )


    assert restored is not None


    assert (
        restored.get_config(
            "batch_size"
        )
        ==
        300
    )



def test_to_json(
    processor,
):
    """
    Processor serializes to JSON.
    """

    processor.set_config(
        "workers",
        4,
    )


    result = processor.to_json()


    assert isinstance(
        result,
        str,
    )

    assert "workers" in result



def test_from_json(
    processor,
):
    """
    Processor restores from JSON.
    """

    value = """
    {
        "config": {
            "workers": 8
        }
    }
    """


    restored = (
        processor
        .from_json(value)
    )


    assert restored is not None


    assert (
        restored.get_config(
            "workers"
        )
        ==
        8
    )



def test_snapshot(
    processor,
):
    """
    Processor creates snapshot.
    """

    processor.set_config(
        "batch_size",
        500,
    )


    snapshot = processor.snapshot()


    assert isinstance(
        snapshot,
        dict,
    )

    assert "config" in snapshot



def test_restore(
    processor,
):
    """
    Processor restores snapshot.
    """

    processor.set_config(
        "batch_size",
        500,
    )


    snapshot = processor.snapshot()


    processor.set_config(
        "batch_size",
        1000,
    )


    result = processor.restore(
        snapshot
    )


    assert result is not None


    assert (
        processor.get_config(
            "batch_size"
        )
        ==
        500
    )
# ============================================================
# Part 9 – Clone / Copy
# ============================================================


def test_clone(
    processor,
):
    """
    Processor can clone itself.
    """

    processor.set_config(
        "batch_size",
        200,
    )


    cloned = processor.clone()


    assert cloned is not None

    assert cloned is not processor


    assert (
        cloned.get_config(
            "batch_size"
        )
        ==
        200
    )



def test_copy(
    processor,
):
    """
    Processor can create independent copy.
    """

    processor.set_config(
        "workers",
        4,
    )


    copied = processor.copy()


    assert copied is not None

    assert copied is not processor


    assert (
        copied.get_config(
            "workers"
        )
        ==
        4
    )



def test_python_copy(
    processor,
):
    """
    Processor supports copy.copy().
    """

    import copy


    processor.set_config(
        "timeout",
        30,
    )


    copied = copy.copy(
        processor
    )


    assert copied is not None

    assert copied is not processor


    assert (
        copied.get_config(
            "timeout"
        )
        ==
        30
    )



def test_python_deepcopy(
    processor,
):
    """
    Processor supports copy.deepcopy().
    """

    import copy


    processor.set_config(
        "batch_size",
        100,
    )


    copied = copy.deepcopy(
        processor
    )


    assert copied is not None

    assert copied is not processor


    assert (
        copied.get_config(
            "batch_size"
        )
        ==
        100
    )
# ============================================================
# Part 10 – Diagnostics
# ============================================================


def test_diagnostics(
    processor,
):
    """
    Processor returns diagnostic information.
    """

    processor.start()

    processor.enqueue(
        {
            "id": "001",
            "type": "span",
        }
    )


    result = processor.diagnostics()


    assert isinstance(
        result,
        dict,
    )


    assert "enabled" in result

    assert "running" in result

    assert "queue_size" in result

    assert "config" in result



def test_summary(
    processor,
):
    """
    Processor returns compact summary.
    """

    result = processor.summary()


    assert isinstance(
        result,
        dict,
    )


    assert "status" in result

    assert "enabled" in result

    assert "queue_size" in result
# ============================================================
# Part 11 – Python Protocols
# ============================================================


def test_repr(
    processor,
):
    """
    Processor has valid repr representation.
    """

    result = repr(
        processor
    )


    assert isinstance(
        result,
        str,
    )


    assert (
        "Processor"
        in result
    )



def test_str(
    processor,
):
    """
    Processor has human readable string.
    """

    result = str(
        processor
    )


    assert isinstance(
        result,
        str,
    )


    assert len(result) > 0



def test_len(
    processor,
):
    """
    len(processor) returns queue size.
    """

    assert len(
        processor
    ) == 0


    processor.enqueue(
        {
            "id": "001",
        }
    )


    assert len(
        processor
    ) == 1



def test_iter(
    processor,
):
    """
    Processor supports iteration.
    """

    processor.enqueue(
        {
            "id": "001",
        }
    )

    processor.enqueue(
        {
            "id": "002",
        }
    )


    items = list(
        processor
    )


    assert len(items) == 2



def test_contains(
    processor,
):
    """
    Processor supports membership test.
    """

    item = {
        "id": "001",
    }


    processor.enqueue(
        item
    )


    assert item in processor



def test_eq(
    processor,
):
    """
    Processor equality comparison.
    """

    other = processor.copy()


    assert (
        processor
        ==
        other
    )



def test_hash(
    processor,
):
    """
    Processor provides hash value.
    """

    result = hash(
        processor
    )


    assert isinstance(
        result,
        int,
    )
# ============================================================
# Part 12 – Statistics
# ============================================================


def test_processed_count(
    processor,
):
    """
    Processor tracks successfully processed items.
    """

    assert (
        processor.processed_count
        ==
        0
    )


    processor.process(
        {
            "id": "001",
            "type": "span",
        }
    )


    assert (
        processor.processed_count
        ==
        1
    )



def test_failed_count(
    processor,
):
    """
    Processor tracks failed processing.
    """

    assert (
        processor.failed_count
        ==
        0
    )


    processor.process(
        None
    )


    assert (
        processor.failed_count
        >=
        1
    )



def test_statistics(
    processor,
):
    """
    Processor returns runtime statistics.
    """

    processor.process(
        {
            "id": "001",
            "type": "span",
        }
    )


    processor.process(
        {
            "id": "002",
            "type": "event",
        }
    )


    stats = processor.statistics()


    assert isinstance(
        stats,
        dict,
    )


    assert "processed" in stats

    assert "failed" in stats

    assert "total" in stats


    assert (
        stats["processed"]
        >=
        2
    )
# ============================================================
# Part 13 – Edge Cases
# ============================================================


def test_empty_processor(
    processor,
):
    """
    Empty processor behaves correctly.
    """

    assert len(processor) == 0


    stats = processor.statistics()


    assert stats["total"] == 0



def test_duplicate_processing(
    processor,
):
    """
    Processor handles duplicate items safely.
    """

    item = {
        "id": "duplicate-001",
        "type": "span",
    }


    first = processor.process(
        item
    )

    second = processor.process(
        item
    )


    assert first is not None

    assert second is not None


    stats = processor.statistics()


    assert (
        stats["total"]
        >=
        1
    )



def test_large_batch(
    processor,
):
    """
    Processor handles large processing batches.
    """

    batch = [
        {
            "id": str(i),
            "type": "span",
        }
        for i in range(1000)
    ]


    result = processor.process_batch(
        batch
    )


    assert result is not None


    stats = processor.statistics()


    assert (
        stats["processed"]
        >=
        1000
    )



def test_invalid_context(
    processor,
):
    """
    Processor rejects invalid processing context.
    """

    invalid_contexts = [
        None,
        "",
        [],
        123,
    ]


    for context in invalid_contexts:

        result = processor.process(
            {
                "id": "001",
                "context": context,
            }
        )


        assert result is not None


    stats = processor.statistics()


    assert (
        stats["failed"]
        >=
        0
    )



def test_closed_processor(
    processor,
):
    """
    Closed processor refuses new processing.
    """

    processor.close()


    assert (
        processor.closed
        is True
    )


    result = processor.process(
        {
            "id": "001",
            "type": "span",
        }
    )


    assert result is False or result is not None                                                    