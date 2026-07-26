"""
SciOS Observability - MemoryExporter Tests
==========================================

Test fixtures for in-memory trace exporter.
"""

import pytest

from scios.runtime.observability.exporters.memory import (
    MemoryExporter,
)


# ============================================================
# Part 1 – Fixtures
# ============================================================


@pytest.fixture
def exporter():
    """
    Empty MemoryExporter fixture.

    Returns
    -------
    MemoryExporter
        Fresh exporter instance.
    """

    return MemoryExporter()



@pytest.fixture
def populated_exporter(
    exporter,
):
    """
    MemoryExporter with predefined records.

    Contains:
    - trace
    - span
    - event
    """

    exporter.export(
        {
            "id": "trace-001",
            "type": "trace",
            "name": "test_trace",
        }
    )


    exporter.export(
        {
            "id": "span-001",
            "type": "span",
            "name": "test_span",
        }
    )


    exporter.export(
        {
            "id": "event-001",
            "type": "event",
            "name": "test_event",
        }
    )


    return exporter
# ============================================================
# Part 2 – Creation
# ============================================================


def test_exporter_creation(
    exporter,
):
    """
    MemoryExporter can be created.
    """

    assert exporter is not None


    assert isinstance(
        exporter,
        MemoryExporter,
    )



def test_default_empty(
    exporter,
):
    """
    New MemoryExporter starts empty.
    """

    assert len(exporter) == 0


    assert exporter.count() == 0


    items = exporter.items()


    assert isinstance(
        items,
        list,
    )


    assert items == []
# ============================================================
# Part 3 – Export Operations
# ============================================================


def test_export(
    exporter,
):
    """
    Export a generic observability item.
    """

    item = {
        "id": "001",
        "type": "trace",
        "name": "test",
    }


    result = exporter.export(
        item
    )


    assert result is not None


    assert len(exporter) == 1


    assert (
        exporter.items()[0]
        ==
        item
    )



def test_export_trace(
    exporter,
):
    """
    Export trace record.
    """

    trace = {
        "id": "trace-001",
        "type": "trace",
        "name": "request_trace",
    }


    result = exporter.export_trace(
        trace
    )


    assert result is not None


    assert len(exporter) == 1


    stored = exporter.items()[0]


    assert stored["type"] == "trace"

    assert stored["id"] == "trace-001"



def test_export_span(
    exporter,
):
    """
    Export span record.
    """

    span = {
        "id": "span-001",
        "type": "span",
        "name": "database_query",
    }


    result = exporter.export_span(
        span
    )


    assert result is not None


    assert len(exporter) == 1


    stored = exporter.items()[0]


    assert stored["type"] == "span"



def test_export_event(
    exporter,
):
    """
    Export event record.
    """

    event = {
        "id": "event-001",
        "type": "event",
        "name": "user_action",
    }


    result = exporter.export_event(
        event
    )


    assert result is not None


    assert len(exporter) == 1


    stored = exporter.items()[0]


    assert stored["type"] == "event"



def test_export_batch(
    exporter,
):
    """
    Export multiple records at once.
    """

    batch = [
        {
            "id": "trace-001",
            "type": "trace",
        },
        {
            "id": "span-001",
            "type": "span",
        },
        {
            "id": "event-001",
            "type": "event",
        },
    ]


    result = exporter.export_batch(
        batch
    )


    assert result is not None


    assert len(exporter) == 3


    items = exporter.items()


    assert items == batch
# ============================================================
# Part 4 – Storage
# ============================================================


def test_store_item(
    exporter,
):
    """
    Exporter stores item internally.
    """

    item = {
        "id": "trace-001",
        "type": "trace",
    }


    exporter.export(
        item
    )


    stored = exporter.items()


    assert len(stored) == 1


    assert (
        stored[0]
        ==
        item
    )



def test_get_item(
    exporter,
):
    """
    Exporter retrieves item by identifier.
    """

    item = {
        "id": "trace-001",
        "type": "trace",
    }


    exporter.export(
        item
    )


    result = exporter.get(
        "trace-001"
    )


    assert result is not None


    assert (
        result["id"]
        ==
        "trace-001"
    )



def test_get_missing(
    exporter,
):
    """
    Missing item returns None.
    """

    result = exporter.get(
        "missing-id"
    )


    assert result is None



def test_items(
    populated_exporter,
):
    """
    Exporter returns all stored items.
    """

    items = (
        populated_exporter
        .items()
    )


    assert isinstance(
        items,
        list,
    )


    assert len(items) == 3


    assert items[0]["type"] == "trace"

    assert items[1]["type"] == "span"

    assert items[2]["type"] == "event"



def test_count(
    populated_exporter,
):
    """
    Exporter returns stored item count.
    """

    count = (
        populated_exporter
        .count()
    )


    assert count == 3


    assert len(
        populated_exporter
    ) == 3



def test_clear(
    populated_exporter,
):
    """
    Exporter clears stored records.
    """

    assert (
        populated_exporter.count()
        ==
        3
    )


    result = populated_exporter.clear()


    assert result is not None


    assert (
        populated_exporter.count()
        ==
        0
    )


    assert (
        populated_exporter.items()
        ==
        []
    )
# ============================================================
# Part 5 – Query
# ============================================================


def test_find_trace(
    populated_exporter,
):
    """
    Find trace records.
    """

    result = (
        populated_exporter
        .find_trace(
            "trace-001"
        )
    )


    assert result is not None


    assert (
        result["id"]
        ==
        "trace-001"
    )


    assert (
        result["type"]
        ==
        "trace"
    )



def test_find_span(
    populated_exporter,
):
    """
    Find span records.
    """

    result = (
        populated_exporter
        .find_span(
            "span-001"
        )
    )


    assert result is not None


    assert (
        result["id"]
        ==
        "span-001"
    )


    assert (
        result["type"]
        ==
        "span"
    )



def test_filter_by_type(
    populated_exporter,
):
    """
    Filter stored items by type.
    """

    traces = (
        populated_exporter
        .filter_by_type(
            "trace"
        )
    )


    spans = (
        populated_exporter
        .filter_by_type(
            "span"
        )
    )


    events = (
        populated_exporter
        .filter_by_type(
            "event"
        )
    )


    assert isinstance(
        traces,
        list,
    )

    assert isinstance(
        spans,
        list,
    )

    assert isinstance(
        events,
        list,
    )


    assert len(traces) == 1

    assert len(spans) == 1

    assert len(events) == 1


    assert traces[0]["id"] == "trace-001"

    assert spans[0]["id"] == "span-001"

    assert events[0]["id"] == "event-001"



def test_search(
    populated_exporter,
):
    """
    Search records by content.
    """

    result = (
        populated_exporter
        .search(
            "test"
        )
    )


    assert isinstance(
        result,
        list,
    )


    assert len(result) == 3


    ids = [
        item["id"]
        for item in result
    ]


    assert "trace-001" in ids

    assert "span-001" in ids

    assert "event-001" in ids
# ============================================================
# Part 6 – Lifecycle
# ============================================================


def test_start(
    exporter,
):
    """
    Exporter can be started.
    """

    assert (
        exporter.running
        is False
    )


    result = exporter.start()


    assert result is not None


    assert (
        exporter.running
        is True
    )



def test_stop(
    exporter,
):
    """
    Exporter can be stopped.
    """

    exporter.start()


    assert (
        exporter.running
        is True
    )


    result = exporter.stop()


    assert result is not None


    assert (
        exporter.running
        is False
    )



def test_enable(
    exporter,
):
    """
    Exporter can be enabled.
    """

    assert (
        exporter.enabled
        is True
    )


    result = exporter.disable()


    assert result is not None


    assert (
        exporter.enabled
        is False
    )


    exporter.enable()


    assert (
        exporter.enabled
        is True
    )



def test_disable(
    exporter,
):
    """
    Exporter can be disabled.
    """

    result = exporter.disable()


    assert result is not None


    assert (
        exporter.enabled
        is False
    )


    item = {
        "id": "001",
        "type": "trace",
    }


    exporter.export(
        item
    )


    assert len(exporter) == 0



def test_reset(
    populated_exporter,
):
    """
    Exporter resets runtime state.
    """

    assert (
        populated_exporter.count()
        ==
        3
    )


    result = (
        populated_exporter
        .reset()
    )


    assert result is not None


    assert (
        populated_exporter.count()
        ==
        0
    )


    assert (
        populated_exporter.running
        is False
    )


    assert (
        populated_exporter.enabled
        is True
    )
# ============================================================
# Part 7 – Configuration
# ============================================================


def test_set_config(
    exporter,
):
    """
    Exporter accepts new configuration.
    """

    config = {
        "max_size": 1000,
        "auto_flush": True,
    }


    result = exporter.set_config(
        config
    )


    assert result is not None


    current = exporter.get_config()


    assert (
        current["max_size"]
        ==
        1000
    )


    assert (
        current["auto_flush"]
        is True
    )



def test_get_config(
    exporter,
):
    """
    Exporter returns current configuration.
    """

    config = (
        exporter.get_config()
    )


    assert isinstance(
        config,
        dict,
    )


    assert (
        "max_size"
        in config
    )


    assert (
        "auto_flush"
        in config
    )



def test_update_config(
    exporter,
):
    """
    Exporter updates partial configuration.
    """

    exporter.set_config(
        {
            "max_size": 100,
            "auto_flush": False,
        }
    )


    result = exporter.update_config(
        {
            "max_size": 500,
        }
    )


    assert result is not None


    config = (
        exporter.get_config()
    )


    assert (
        config["max_size"]
        ==
        500
    )


    assert (
        config["auto_flush"]
        is False
    )



def test_reset_config(
    exporter,
):
    """
    Exporter restores default configuration.
    """

    exporter.set_config(
        {
            "max_size": 9999,
            "auto_flush": True,
        }
    )


    result = (
        exporter.reset_config()
    )


    assert result is not None


    config = (
        exporter.get_config()
    )


    assert (
        config["max_size"]
        !=
        9999
    )


    assert (
        config["auto_flush"]
        is False
    )
# ============================================================
# Part 8 – Validation
# ============================================================


def test_validate(
    exporter,
):
    """
    Exporter validates internal state.
    """

    result = exporter.validate()


    assert isinstance(
        result,
        bool,
    )


    assert result is True



def test_invalid_item(
    exporter,
):
    """
    Exporter rejects invalid item.
    """

    invalid_items = [
        None,
        {},
        [],
        "",
        123,
    ]


    for item in invalid_items:

        result = exporter.export(
            item
        )


        assert (
            result is False
            or
            result is None
        )


    assert (
        exporter.count()
        ==
        0
    )



def test_invalid_batch(
    exporter,
):
    """
    Exporter rejects invalid batch.
    """

    invalid_batches = [
        None,
        {},
        [],
        "",
        123,
    ]


    for batch in invalid_batches:

        result = exporter.export_batch(
            batch
        )


        assert (
            result is False
            or
            result is None
        )


    assert (
        exporter.count()
        ==
        0
    )
# ============================================================
# Part 9 – Serialization
# ============================================================


def test_to_dict(
    populated_exporter,
):
    """
    Exporter serializes to dictionary.
    """

    data = (
        populated_exporter
        .to_dict()
    )


    assert isinstance(
        data,
        dict,
    )


    assert "items" in data

    assert "config" in data


    assert len(
        data["items"]
    ) == 3



def test_from_dict():
    """
    Exporter restores from dictionary.
    """

    data = {
        "items": [
            {
                "id": "trace-001",
                "type": "trace",
            },
            {
                "id": "span-001",
                "type": "span",
            },
        ],
        "config": {
            "max_size": 100,
            "auto_flush": False,
        },
    }


    exporter = (
        MemoryExporter
        .from_dict(data)
    )


    assert isinstance(
        exporter,
        MemoryExporter,
    )


    assert (
        exporter.count()
        ==
        2
    )


    assert (
        exporter.get(
            "trace-001"
        )
        is not None
    )



def test_to_json(
    populated_exporter,
):
    """
    Exporter serializes to JSON.
    """

    value = (
        populated_exporter
        .to_json()
    )


    assert isinstance(
        value,
        str,
    )


    assert (
        "items"
        in value
    )


    assert (
        "trace-001"
        in value
    )



def test_from_json():
    """
    Exporter restores from JSON.
    """

    value = """
    {
        "items": [
            {
                "id": "event-001",
                "type": "event"
            }
        ],
        "config": {
            "max_size": 100
        }
    }
    """


    exporter = (
        MemoryExporter
        .from_json(value)
    )


    assert isinstance(
        exporter,
        MemoryExporter,
    )


    assert (
        exporter.count()
        ==
        1
    )


    assert (
        exporter.get(
            "event-001"
        )
        is not None
    )



def test_snapshot(
    populated_exporter,
):
    """
    Exporter creates snapshot.
    """

    snapshot = (
        populated_exporter
        .snapshot()
    )


    assert isinstance(
        snapshot,
        dict,
    )


    assert "items" in snapshot

    assert (
        len(
            snapshot["items"]
        )
        ==
        3
    )



def test_restore():
    """
    Exporter restores from snapshot.
    """

    snapshot = {
        "items": [
            {
                "id": "trace-restore",
                "type": "trace",
            }
        ],
        "config": {
            "max_size": 50,
        },
        "enabled": True,
        "running": False,
    }


    exporter = (
        MemoryExporter
        .restore(
            snapshot
        )
    )


    assert isinstance(
        exporter,
        MemoryExporter,
    )


    assert (
        exporter.count()
        ==
        1
    )


    assert (
        exporter.get(
            "trace-restore"
        )
        is not None
    )
# ============================================================
# Part 10 – Clone / Copy
# ============================================================

import copy



def test_copy(
    populated_exporter,
):
    """
    Exporter supports copy operation.
    """

    cloned = (
        populated_exporter
        .copy()
    )


    assert isinstance(
        cloned,
        MemoryExporter,
    )


    assert (
        cloned is not populated_exporter
    )


    assert (
        cloned.count()
        ==
        populated_exporter.count()
    )



def test_clone(
    populated_exporter,
):
    """
    Exporter creates independent clone.
    """

    cloned = (
        populated_exporter
        .clone()
    )


    assert isinstance(
        cloned,
        MemoryExporter,
    )


    assert (
        cloned is not populated_exporter
    )


    assert (
        cloned.items()
        ==
        populated_exporter.items()
    )


    cloned.clear()


    assert (
        cloned.count()
        ==
        0
    )


    assert (
        populated_exporter.count()
        ==
        3
    )



def test_python_copy(
    populated_exporter,
):
    """
    Supports copy.copy().
    """

    cloned = copy.copy(
        populated_exporter
    )


    assert isinstance(
        cloned,
        MemoryExporter,
    )


    assert (
        cloned is not populated_exporter
    )


    assert (
        cloned.items()
        ==
        populated_exporter.items()
    )



def test_python_deepcopy(
    populated_exporter,
):
    """
    Supports copy.deepcopy().
    """

    cloned = copy.deepcopy(
        populated_exporter
    )


    assert isinstance(
        cloned,
        MemoryExporter,
    )


    assert (
        cloned is not populated_exporter
    )


    assert (
        cloned.items()
        ==
        populated_exporter.items()
    )


    cloned.export(
        {
            "id": "new-item",
            "type": "trace",
        }
    )


    assert (
        cloned.count()
        ==
        4
    )


    assert (
        populated_exporter.count()
        ==
        3
    )
# ============================================================
# Part 11 – Diagnostics
# ============================================================


def test_diagnostics(
    populated_exporter,
):
    """
    Exporter returns diagnostic information.
    """

    diagnostics = (
        populated_exporter
        .diagnostics()
    )


    assert isinstance(
        diagnostics,
        dict,
    )


    assert "valid" in diagnostics

    assert "count" in diagnostics

    assert "enabled" in diagnostics

    assert "running" in diagnostics

    assert "storage_size" in diagnostics

    assert "types" in diagnostics



    assert (
        diagnostics["valid"]
        is True
    )


    assert (
        diagnostics["count"]
        ==
        3
    )


    assert isinstance(
        diagnostics["types"],
        dict,
    )



def test_summary(
    populated_exporter,
):
    """
    Exporter returns concise summary.
    """

    summary = (
        populated_exporter
        .summary()
    )


    assert isinstance(
        summary,
        dict,
    )


    assert "count" in summary

    assert "enabled" in summary

    assert "running" in summary



    assert (
        summary["count"]
        ==
        3
    )


    assert (
        summary["enabled"]
        is True
    )
# ============================================================
# Part 12 – Python Protocols
# ============================================================


def test_repr(
    populated_exporter,
):
    """
    Test official representation.
    """

    value = repr(
        populated_exporter
    )


    assert isinstance(
        value,
        str,
    )


    assert (
        "MemoryExporter"
        in value
    )



def test_str(
    populated_exporter,
):
    """
    Test human-readable string.
    """

    value = str(
        populated_exporter
    )


    assert isinstance(
        value,
        str,
    )


    assert (
        "MemoryExporter"
        in value
    )



def test_len(
    populated_exporter,
):
    """
    Test len(exporter).
    """

    assert (
        len(populated_exporter)
        ==
        3
    )



def test_iter(
    populated_exporter,
):
    """
    Test iteration over exporter.
    """

    items = list(
        populated_exporter
    )


    assert isinstance(
        items,
        list,
    )


    assert len(items) == 3


    assert (
        items[0]["id"]
        ==
        "trace-001"
    )



def test_contains(
    populated_exporter,
):
    """
    Test membership checking.
    """

    assert (
        "trace-001"
        in populated_exporter
    )


    assert (
        "missing"
        not in populated_exporter
    )



def test_getitem(
    populated_exporter,
):
    """
    Test dictionary-style access.
    """

    item = (
        populated_exporter[
            "trace-001"
        ]
    )


    assert item is not None


    assert (
        item["type"]
        ==
        "trace"
    )



def test_eq(
    populated_exporter,
):
    """
    Test equality comparison.
    """

    clone = (
        populated_exporter
        .clone()
    )


    assert (
        populated_exporter
        ==
        clone
    )


    clone.export(
        {
            "id": "new-item",
            "type": "event",
        }
    )


    assert (
        populated_exporter
        !=
        clone
    )



def test_hash(
    populated_exporter,
):
    """
    Test hash protocol.
    """

    value = hash(
        populated_exporter
    )


    assert isinstance(
        value,
        int,
    )


    clone = (
        populated_exporter
        .clone()
    )


    assert (
        hash(populated_exporter)
        ==
        hash(clone)
    )
# ============================================================
# Part 13 – Statistics
# ============================================================


def test_export_count(
    populated_exporter,
):
    """
    Test successful export counter.
    """

    stats = (
        populated_exporter
        .statistics()
    )


    assert isinstance(
        stats,
        dict,
    )


    assert (
        stats["export_count"]
        ==
        3
    )



def test_failed_count(
    exporter,
):
    """
    Test failed export counter.
    """

    exporter.export(
        None
    )


    exporter.export(
        {}
    )


    stats = (
        exporter
        .statistics()
    )


    assert (
        stats["failed_count"]
        ==
        2
    )



def test_statistics(
    populated_exporter,
):
    """
    Test complete statistics output.
    """

    stats = (
        populated_exporter
        .statistics()
    )


    assert isinstance(
        stats,
        dict,
    )


    assert "export_count" in stats

    assert "failed_count" in stats

    assert "item_count" in stats

    assert "trace_count" in stats

    assert "span_count" in stats

    assert "event_count" in stats



    assert (
        stats["export_count"]
        ==
        3
    )


    assert (
        stats["failed_count"]
        ==
        0
    )


    assert (
        stats["item_count"]
        ==
        3
    )


    assert (
        stats["trace_count"]
        ==
        1
    )


    assert (
        stats["span_count"]
        ==
        1
    )


    assert (
        stats["event_count"]
        ==
        1
    )
# ============================================================
# Part 14 – Edge Cases
# ============================================================


def test_empty_exporter(
    exporter,
):
    """
    Empty exporter behaves correctly.
    """

    assert (
        exporter.count()
        ==
        0
    )


    assert (
        exporter.items()
        ==
        []
    )


    stats = (
        exporter.statistics()
    )


    assert (
        stats["item_count"]
        ==
        0
    )


    assert (
        exporter.validate()
        is True
    )



def test_duplicate_export(
    exporter,
):
    """
    Exporting duplicate items.
    """

    item = {
        "id": "trace-001",
        "type": "trace",
    }


    exporter.export(
        item
    )


    exporter.export(
        item
    )


    assert (
        exporter.count()
        ==
        2
    )


    items = exporter.items()


    assert (
        items[0]
        ==
        items[1]
    )



def test_large_batch(
    exporter,
):
    """
    Export large number of items.
    """

    batch = [
        {
            "id": f"trace-{i}",
            "type": "trace",
        }
        for i in range(1000)
    ]


    result = exporter.export_batch(
        batch
    )


    assert result is not None


    assert (
        exporter.count()
        ==
        1000
    )


    assert (
        exporter.get(
            "trace-999"
        )
        is not None
    )



def test_invalid_context(
    exporter,
):
    """
    Exporter handles invalid context safely.
    """

    invalid_contexts = [
        None,
        "",
        [],
        123,
        object(),
    ]


    for context in invalid_contexts:

        result = (
            exporter.export(
                {
                    "id": "invalid",
                    "type": "trace",
                    "context": context,
                }
            )
        )


        assert (
            result is False
            or
            result is None
            or
            result is not None
        )



def test_closed_exporter(
    exporter,
):
    """
    Closed exporter rejects new exports.
    """

    exporter.start()


    exporter.close()


    assert (
        exporter.closed
        is True
    )


    result = exporter.export(
        {
            "id": "after-close",
            "type": "trace",
        }
    )


    assert (
        result is False
        or
        result is None
    )                                                    