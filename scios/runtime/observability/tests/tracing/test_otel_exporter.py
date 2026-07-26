# ============================================================
# test_otel_exporter.py
# Part 1 – Fixtures
# ============================================================

import pytest


from scios.runtime.observability.exporters.otel import (
    OTelExporter,
)



@pytest.fixture
def exporter():
    """
    Create empty OpenTelemetry exporter.
    """

    return OTelExporter()



@pytest.fixture
def populated_exporter():
    """
    Create OTel exporter with sample telemetry data.
    """

    exporter = OTelExporter()


    exporter.export_trace(
        {
            "id": "trace-001",
            "trace_id": "abc123",
            "type": "trace",
            "name": "http.request",
            "duration": 120,
        }
    )


    exporter.export_span(
        {
            "id": "span-001",
            "span_id": "span123",
            "trace_id": "abc123",
            "type": "span",
            "name": "database.query",
            "duration": 40,
        }
    )


    exporter.export_event(
        {
            "id": "event-001",
            "type": "event",
            "name": "user.login",
            "attributes": {
                "user_id": "user-001",
            },
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
    Test OTelExporter object creation.
    """

    assert isinstance(
        exporter,
        OTelExporter,
    )


    assert (
        exporter is not None
    )


    assert hasattr(
        exporter,
        "export",
    )


    assert hasattr(
        exporter,
        "export_trace",
    )


    assert hasattr(
        exporter,
        "export_span",
    )


    assert hasattr(
        exporter,
        "export_event",
    )


    assert hasattr(
        exporter,
        "export_batch",
    )



def test_default_configuration(
    exporter,
):
    """
    Test default OpenTelemetry exporter configuration.
    """

    config = (
        exporter.get_config()
    )


    assert isinstance(
        config,
        dict,
    )


    assert "service_name" in config

    assert "endpoint" in config

    assert "protocol" in config

    assert "batch_size" in config

    assert "enabled" in config



    assert (
        config["enabled"]
        is True
    )


    assert (
        config["protocol"]
        in [
            "otlp",
            "grpc",
            "http/protobuf",
        ]
    )


    assert (
        config["batch_size"]
        > 0
    )
# ============================================================
# Part 3 – OpenTelemetry Export
# ============================================================


def test_export(
    exporter,
):
    """
    Test generic telemetry export.
    """

    item = {
        "id": "trace-001",
        "type": "trace",
        "trace_id": "abc123",
        "name": "http.request",
    }


    result = (
        exporter.export(
            item
        )
    )


    assert result is not None


    assert (
        exporter.count()
        ==
        1
    )


    stored = (
        exporter.get(
            "trace-001"
        )
    )


    assert stored is not None


    assert (
        stored["trace_id"]
        ==
        "abc123"
    )



def test_export_trace(
    exporter,
):
    """
    Test trace export.
    """

    trace = {
        "id": "trace-001",
        "type": "trace",
        "trace_id": "abc123",
        "name": "api.request",
        "duration": 120,
    }


    result = (
        exporter.export_trace(
            trace
        )
    )


    assert result is not None


    assert (
        exporter.count()
        ==
        1
    )


    stored = (
        exporter.get(
            "trace-001"
        )
    )


    assert (
        stored["type"]
        ==
        "trace"
    )


    assert (
        stored["trace_id"]
        ==
        "abc123"
    )



def test_export_span(
    exporter,
):
    """
    Test span export.
    """

    span = {
        "id": "span-001",
        "type": "span",
        "trace_id": "abc123",
        "span_id": "span123",
        "name": "database.query",
        "duration": 50,
    }


    result = (
        exporter.export_span(
            span
        )
    )


    assert result is not None


    assert (
        exporter.count()
        ==
        1
    )


    stored = (
        exporter.get(
            "span-001"
        )
    )


    assert (
        stored["type"]
        ==
        "span"
    )


    assert (
        stored["span_id"]
        ==
        "span123"
    )



def test_export_event(
        exporter,
):
    """
    Test event export.
    """

    event = {
        "id": "event-001",
        "type": "event",
        "name": "user.login",
        "attributes": {
            "user_id": "user-001",
        },
    }


    result = (
        exporter.export_event(
            event
        )
    )


    assert result is not None


    assert (
        exporter.count()
        ==
        1
    )


    stored = (
        exporter.get(
            "event-001"
        )
    )


    assert (
        stored["type"]
        ==
        "event"
    )


    assert (
        stored["attributes"]["user_id"]
        ==
        "user-001"
    )



def test_export_batch(
    exporter,
):
    """
    Test batch telemetry export.
    """

    batch = [
        {
            "id": "trace-001",
            "type": "trace",
            "trace_id": "abc123",
        },
        {
            "id": "span-001",
            "type": "span",
            "span_id": "span123",
        },
        {
            "id": "event-001",
            "type": "event",
        },
    ]


    result = (
        exporter.export_batch(
            batch
        )
    )


    assert result is not None


    assert (
        exporter.count()
        ==
        3
    )


    assert (
        exporter.get(
            "trace-001"
        )
        is not None
    )


    assert (
        exporter.get(
            "span-001"
        )
        is not None
    )


    assert (
        exporter.get(
            "event-001"
        )
        is not None
    )
# ============================================================
# Part 4 – OTLP Data Conversion
# ============================================================


def test_convert_trace(
    exporter,
):
    """
    Test trace to OTLP conversion.
    """

    trace = {
        "id": "trace-001",
        "type": "trace",
        "trace_id": "abc123",
        "name": "http.request",
        "duration": 120,
        "attributes": {
            "method": "GET",
            "path": "/api",
        },
    }


    result = (
        exporter.convert_trace(
            trace
        )
    )


    assert isinstance(
        result,
        dict,
    )


    assert "trace_id" in result

    assert "name" in result

    assert "attributes" in result

    assert "duration" in result



    assert (
        result["trace_id"]
        ==
        "abc123"
    )


    assert (
        result["name"]
        ==
        "http.request"
    )


    assert (
        result["attributes"]["method"]
        ==
        "GET"
    )



def test_convert_span(
    exporter,
):
    """
    Test span to OTLP conversion.
    """

    span = {
        "id": "span-001",
        "type": "span",
        "trace_id": "abc123",
        "span_id": "span123",
        "name": "database.query",
        "duration": 50,
        "status": "OK",
    }


    result = (
        exporter.convert_span(
            span
        )
    )


    assert isinstance(
        result,
        dict,
    )


    assert "trace_id" in result

    assert "span_id" in result

    assert "name" in result

    assert "status" in result



    assert (
        result["trace_id"]
        ==
        "abc123"
    )


    assert (
        result["span_id"]
        ==
        "span123"
    )


    assert (
        result["name"]
        ==
        "database.query"
    )



def test_convert_event(
    exporter,
):
    """
    Test event to OTLP conversion.
    """

    event = {
        "id": "event-001",
        "type": "event",
        "name": "user.login",
        "timestamp": 123456,
        "attributes": {
            "user_id": "user-001",
        },
    }


    result = (
        exporter.convert_event(
            event
        )
    )


    assert isinstance(
        result,
        dict,
    )


    assert "name" in result

    assert "timestamp" in result

    assert "attributes" in result



    assert (
        result["name"]
        ==
        "user.login"
    )


    assert (
        result["attributes"]["user_id"]
        ==
        "user-001"
    )



def test_convert_batch(
    exporter,
):
    """
    Test batch telemetry conversion.
    """

    batch = [
        {
            "id": "trace-001",
            "type": "trace",
            "trace_id": "abc123",
        },
        {
            "id": "span-001",
            "type": "span",
            "trace_id": "abc123",
            "span_id": "span123",
        },
        {
            "id": "event-001",
            "type": "event",
            "name": "login",
        },
    ]


    result = (
        exporter.convert_batch(
            batch
        )
    )


    assert isinstance(
        result,
        list,
    )


    assert (
        len(result)
        ==
        3
    )


    assert (
        result[0]["trace_id"]
        ==
        "abc123"
    )


    assert (
        result[1]["span_id"]
        ==
        "span123"
    )


    assert (
        result[2]["name"]
        ==
        "login"
    )
# ============================================================
# Part 5 – Queue Management
# ============================================================


def test_enqueue(
    exporter,
):
    """
    Test adding telemetry item to queue.
    """

    item = {
        "id": "trace-001",
        "type": "trace",
        "trace_id": "abc123",
    }


    result = (
        exporter.enqueue(
            item
        )
    )


    assert result is not None


    assert (
        exporter.queue_size()
        ==
        1
    )


    queued = (
        exporter.queue[0]
    )


    assert (
        queued["id"]
        ==
        "trace-001"
    )



def test_dequeue(
    exporter,
):
    """
    Test removing telemetry item from queue.
    """

    item = {
        "id": "span-001",
        "type": "span",
        "span_id": "span123",
    }


    exporter.enqueue(
        item
    )


    assert (
        exporter.queue_size()
        ==
        1
    )


    result = (
        exporter.dequeue()
    )


    assert result is not None


    assert (
        result["id"]
        ==
        "span-001"
    )


    assert (
        exporter.queue_size()
        ==
        0
    )



def test_queue_size(
    exporter,
):
    """
    Test queue size tracking.
    """

    assert (
        exporter.queue_size()
        ==
        0
    )


    exporter.enqueue(
        {
            "id": "trace-001",
            "type": "trace",
        }
    )


    exporter.enqueue(
        {
            "id": "span-001",
            "type": "span",
        }
    )


    exporter.enqueue(
        {
            "id": "event-001",
            "type": "event",
        }
    )


    assert (
        exporter.queue_size()
        ==
        3
    )



def test_clear_queue(
    exporter,
):
    """
    Test clearing telemetry queue.
    """

    exporter.enqueue(
        {
            "id": "trace-001",
            "type": "trace",
        }
    )


    exporter.enqueue(
        {
            "id": "span-001",
            "type": "span",
        }
    )


    assert (
        exporter.queue_size()
        ==
        2
    )


    result = (
        exporter.clear_queue()
    )


    assert result is not None


    assert (
        exporter.queue_size()
        ==
        0
    )


    assert (
        exporter.queue
        ==
        []
    )
# ============================================================
# Part 6 – Lifecycle
# ============================================================


def test_start(
    exporter,
):
    """
    Test starting exporter lifecycle.
    """

    assert (
        exporter.running
        is False
    )


    result = (
        exporter.start()
    )


    assert result is not None


    assert (
        exporter.running
        is True
    )


    assert (
        exporter.closed
        is False
    )



def test_stop(
    exporter,
):
    """
    Test stopping exporter lifecycle.
    """

    exporter.start()


    assert (
        exporter.running
        is True
    )


    result = (
        exporter.stop()
    )


    assert result is not None


    assert (
        exporter.running
        is False
    )



def test_enable(
    exporter,
):
    """
    Test enabling exporter.
    """

    exporter.disable()


    assert (
        exporter.enabled
        is False
    )


    result = (
        exporter.enable()
    )


    assert result is not None


    assert (
        exporter.enabled
        is True
    )



def test_disable(
    exporter,
):
    """
    Test disabling exporter.
    """

    assert (
        exporter.enabled
        is True
    )


    result = (
        exporter.disable()
    )


    assert result is not None


    assert (
        exporter.enabled
        is False
    )


    export_result = (
        exporter.export(
            {
                "id": "disabled-test",
                "type": "trace",
            }
        )
    )


    assert (
        export_result is False
        or
        export_result is None
    )



def test_reset(
    populated_exporter,
):
    """
    Test exporter reset lifecycle.
    """

    assert (
        populated_exporter.count()
        ==
        3
    )


    populated_exporter.start()


    result = (
        populated_exporter.reset()
    )


    assert result is not None


    assert (
        populated_exporter.count()
        ==
        0
    )


    assert (
        populated_exporter.queue_size()
        ==
        0
    )


    assert (
        populated_exporter.running
        is False
    )


    assert (
        populated_exporter.closed
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
    Test setting exporter configuration.
    """

    config = {
        "service_name": "scios-test",
        "endpoint": "http://localhost:4317",
        "protocol": "grpc",
        "batch_size": 256,
    }


    result = (
        exporter.set_config(
            config
        )
    )


    assert result is not None


    current = (
        exporter.get_config()
    )


    assert (
        current["service_name"]
        ==
        "scios-test"
    )


    assert (
        current["endpoint"]
        ==
        "http://localhost:4317"
    )


    assert (
        current["protocol"]
        ==
        "grpc"
    )


    assert (
        current["batch_size"]
        ==
        256
    )



def test_get_config(
    exporter,
):
    """
    Test retrieving exporter configuration.
    """

    config = (
        exporter.get_config()
    )


    assert isinstance(
        config,
        dict,
    )


    assert "service_name" in config

    assert "endpoint" in config

    assert "protocol" in config

    assert "batch_size" in config

    assert "enabled" in config



    assert (
        config["enabled"]
        is True
    )



def test_update_config(
    exporter,
):
    """
    Test partial configuration update.
    """

    original = (
        exporter.get_config()
    )


    result = (
        exporter.update_config(
            {
                "batch_size": 1024,
                "timeout": 30,
            }
        )
    )


    assert result is not None


    updated = (
        exporter.get_config()
    )


    assert (
        updated["batch_size"]
        ==
        1024
    )


    assert (
        updated["timeout"]
        ==
        30
    )


    assert (
        updated["service_name"]
        ==
        original["service_name"]
    )



def test_reset_config(
    exporter,
):
    """
    Test restoring default configuration.
    """

    exporter.set_config(
        {
            "service_name": "custom-service",
            "endpoint": "http://custom",
            "batch_size": 999,
        }
    )


    modified = (
        exporter.get_config()
    )


    assert (
        modified["service_name"]
        ==
        "custom-service"
    )


    result = (
        exporter.reset_config()
    )


    assert result is not None


    restored = (
        exporter.get_config()
    )


    assert (
        restored["service_name"]
        !=
        "custom-service"
    )


    assert (
        restored["batch_size"]
        !=
        999
    )


    assert (
        restored["enabled"]
        is True
    )
# ============================================================
# Part 8 – Validation
# ============================================================


def test_validate(
    exporter,
):
    """
    Test valid telemetry validation.
    """

    valid_trace = {
        "id": "trace-001",
        "type": "trace",
        "trace_id": "abc123",
        "name": "http.request",
    }


    result = (
        exporter.validate(
            valid_trace
        )
    )


    assert (
        result
        is True
    )



def test_invalid_item(
    exporter,
):
    """
    Test invalid telemetry item validation.
    """

    invalid_items = [
        None,
        {},
        [],
        "",
        123,
    ]


    for item in invalid_items:

        result = (
            exporter.validate(
                item
            )
        )


        assert (
            result
            is False
        )



def test_invalid_context(
    exporter,
):
    """
    Test invalid OpenTelemetry context.
    """

    invalid_contexts = [
        None,
        {},
        {
            "trace_id": None,
        },
        {
            "span_id": "",
        },
        {
            "trace_id": 123,
        },
    ]


    for context in invalid_contexts:

        item = {
            "id": "invalid-context",
            "type": "span",
            "context": context,
        }


        result = (
            exporter.validate(
                item
            )
        )


        assert (
            result
            is False
        )



def test_invalid_resource(
    exporter,
):
    """
    Test invalid OpenTelemetry resource validation.
    """

    invalid_resources = [
        None,
        {},
        "",
        [],
        {
            "service.name": None,
        },
        {
            "service.name": "",
        },
    ]


    for resource in invalid_resources:

        item = {
            "id": "resource-test",
            "type": "trace",
            "trace_id": "abc123",
            "resource": resource,
        }


        result = (
            exporter.validate(
                item
            )
        )


        assert (
            result
            is False
        )
# ============================================================
# Part 9 – Serialization
# ============================================================


def test_to_dict(
    populated_exporter,
):
    """
    Test exporter serialization to dictionary.
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

    assert "queue" in data

    assert "config" in data

    assert "statistics" in data

    assert "state" in data



    assert (
        len(data["items"])
        ==
        3
    )


    assert (
        data["config"]
        is not None
    )



def test_from_dict(
    exporter,
):
    """
    Test restoring exporter from dictionary.
    """

    data = {
        "items": [
            {
                "id": "trace-001",
                "type": "trace",
                "trace_id": "abc123",
            }
        ],
        "queue": [
            {
                "id": "span-001",
                "type": "span",
                "span_id": "span123",
            }
        ],
        "config": {
            "service_name": "restore-test",
            "protocol": "otlp",
            "batch_size": 128,
        },
        "statistics": {
            "export_count": 1,
            "failed_count": 0,
        },
        "state": {
            "enabled": True,
            "running": False,
            "closed": False,
        },
    }


    result = (
        exporter
        .from_dict(
            data
        )
    )


    assert result is not None


    assert (
        exporter.count()
        ==
        1
    )


    assert (
        exporter.queue_size()
        ==
        1
    )


    config = (
        exporter.get_config()
    )


    assert (
        config["service_name"]
        ==
        "restore-test"
    )



def test_snapshot(
    populated_exporter,
):
    """
    Test creating exporter snapshot.
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

    assert "queue" in snapshot

    assert "config" in snapshot

    assert "statistics" in snapshot



    assert (
        len(snapshot["items"])
        ==
        3
    )



def test_restore(
    exporter,
):
    """
    Test restoring exporter from snapshot.
    """

    source = {
        "items": [
            {
                "id": "event-001",
                "type": "event",
                "name": "user.login",
            }
        ],
        "queue": [],
        "config": {
            "service_name": "scios",
            "protocol": "otlp",
        },
        "statistics": {
            "export_count": 1,
            "failed_count": 0,
        },
        "state": {
            "enabled": True,
            "running": False,
            "closed": False,
        },
    }


    exporter.restore(
        source
    )


    assert (
        exporter.count()
        ==
        1
    )


    item = (
        exporter.get(
            "event-001"
        )
    )


    assert item is not None


    assert (
        item["type"]
        ==
        "event"
    )


    assert (
        exporter.closed
        is False
    )
# ============================================================
# Part 10 – Clone / Copy
# ============================================================

import copy



def test_copy(
    populated_exporter,
):
    """
    Test exporter copy() method.
    """

    copied = (
        populated_exporter.copy()
    )


    assert copied is not None


    assert isinstance(
        copied,
        OTelExporter,
    )


    assert (
        copied
        ==
        populated_exporter
    )


    assert (
        copied
        is not
        populated_exporter
    )



    copied.export_event(
        {
            "id": "event-copy",
            "type": "event",
            "name": "copy.test",
        }
    )


    assert (
        copied.count()
        ==
        4
    )


    assert (
        populated_exporter.count()
        ==
        3
    )



def test_clone(
    populated_exporter,
):
    """
    Test exporter clone() method.
    """

    cloned = (
        populated_exporter.clone()
    )


    assert cloned is not None


    assert isinstance(
        cloned,
        OTelExporter,
    )


    assert (
        cloned
        ==
        populated_exporter
    )


    assert (
        cloned
        is not
        populated_exporter
    )


    assert (
        cloned.count()
        ==
        populated_exporter.count()
    )


    assert (
        cloned.get_config()
        ==
        populated_exporter.get_config()
    )



def test_python_copy(
    populated_exporter,
):
    """
    Test Python copy.copy protocol.
    """

    copied = copy.copy(
        populated_exporter
    )


    assert copied is not None


    assert isinstance(
        copied,
        OTelExporter,
    )


    assert (
        copied
        ==
        populated_exporter
    )


    assert (
        copied
        is not
        populated_exporter
    )



    copied.export_trace(
        {
            "id": "trace-copy",
            "type": "trace",
            "trace_id": "copy123",
        }
    )


    assert (
        copied.count()
        ==
        4
    )


    assert (
        populated_exporter.count()
        ==
        3
    )



def test_python_deepcopy(
    populated_exporter,
):
    """
    Test Python copy.deepcopy protocol.
    """

    copied = copy.deepcopy(
        populated_exporter
    )


    assert copied is not None


    assert isinstance(
        copied,
        OTelExporter,
    )


    assert (
        copied
        ==
        populated_exporter
    )


    assert (
        copied
        is not
        populated_exporter
    )


    copied.update_config(
        {
            "service_name": "deep-copy-test"
        }
    )


    assert (
        copied.get_config()["service_name"]
        ==
        "deep-copy-test"
    )


    assert (
        populated_exporter
        .get_config()["service_name"]
        !=
        "deep-copy-test"
    )
# ============================================================
# Part 11 – Diagnostics
# ============================================================


def test_diagnostics(
    populated_exporter,
):
    """
    Test exporter diagnostics information.
    """

    diagnostics = (
        populated_exporter
        .diagnostics()
    )


    assert isinstance(
        diagnostics,
        dict,
    )


    assert "name" in diagnostics

    assert "status" in diagnostics

    assert "items" in diagnostics

    assert "queue_size" in diagnostics

    assert "config" in diagnostics

    assert "statistics" in diagnostics



    assert (
        diagnostics["name"]
        ==
        "OTelExporter"
    )


    assert (
        diagnostics["items"]
        ==
        3
    )


    assert (
        diagnostics["queue_size"]
        >=
        0
    )


    assert (
        diagnostics["status"]
        in [
            "active",
            "running",
            "idle",
            "enabled",
        ]
    )



def test_summary(
    populated_exporter,
):
    """
    Test human-readable exporter summary.
    """

    summary = (
        populated_exporter
        .summary()
    )


    assert isinstance(
        summary,
        dict,
    )


    assert "name" in summary

    assert "total_items" in summary

    assert "exports" in summary

    assert "failures" in summary

    assert "enabled" in summary

    assert "closed" in summary



    assert (
        summary["name"]
        ==
        "OTelExporter"
    )


    assert (
        summary["total_items"]
        ==
        3
    )


    assert (
        summary["exports"]
        ==
        3
    )


    assert (
        summary["failures"]
        ==
        0
    )


    assert (
        summary["enabled"]
        is True
    )


    assert (
        summary["closed"]
        is False
    )
# ============================================================
# Part 12 – Python Protocols
# ============================================================


def test_repr(
    exporter,
):
    """
    Test __repr__ protocol.
    """

    result = repr(
        exporter
    )


    assert isinstance(
        result,
        str,
    )


    assert (
        "OTelExporter"
        in result
    )



def test_str(
    exporter,
):
    """
    Test __str__ protocol.
    """

    result = str(
        exporter
    )


    assert isinstance(
        result,
        str,
    )


    assert (
        len(result)
        >
        0
    )


    assert (
        "OTelExporter"
        in result
    )



def test_len(
    populated_exporter,
):
    """
    Test __len__ protocol.
    """

    result = len(
        populated_exporter
    )


    assert (
        result
        ==
        3
    )



def test_iter(
    populated_exporter,
):
    """
    Test __iter__ protocol.
    """

    items = list(
        iter(
            populated_exporter
        )
    )


    assert isinstance(
        items,
        list,
    )


    assert (
        len(items)
        ==
        3
    )


    assert (
        items[0]["id"]
        ==
        "trace-001"
    )



def test_contains(
    populated_exporter,
):
    """
    Test __contains__ protocol.
    """

    assert (
        "trace-001"
        in
        populated_exporter
    )


    assert (
        "span-001"
        in
        populated_exporter
    )


    assert (
        "missing-id"
        not
        in
        populated_exporter
    )



def test_eq(
    exporter,
):
    """
    Test equality comparison.
    """

    other = OTelExporter()


    assert (
        exporter
        ==
        other
    )


    exporter.export_trace(
        {
            "id": "trace-001",
            "type": "trace",
            "trace_id": "abc123",
        }
    )


    assert (
        exporter
        !=
        other
    )



def test_hash(
    exporter,
):
    """
    Test hash protocol.
    """

    result = hash(
        exporter
    )


    assert isinstance(
        result,
        int,
    )


    assert (
        hash(exporter)
        ==
        result
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


    assert "export_count" in stats


    assert (
        stats["export_count"]
        ==
        3
    )



    populated_exporter.export_trace(
        {
            "id": "trace-extra",
            "type": "trace",
            "trace_id": "extra123",
        }
    )


    updated = (
        populated_exporter
        .statistics()
    )


    assert (
        updated["export_count"]
        ==
        4
    )



def test_failed_count(
    exporter,
):
    """
    Test failed export counter.
    """

    stats = (
        exporter
        .statistics()
    )


    assert "failed_count" in stats


    assert (
        stats["failed_count"]
        ==
        0
    )


    exporter.export(
        None
    )


    failed = (
        exporter
        .statistics()
    )


    assert (
        failed["failed_count"]
        >=
        1
    )



def test_statistics(
    populated_exporter,
):
    """
    Test complete exporter statistics.
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

    assert "queue_size" in stats

    assert "item_count" in stats

    assert "uptime" in stats



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
        stats["queue_size"]
        >=
        0
    )


    assert (
        stats["uptime"]
        >=
        0
    )
# ============================================================
# Part 14 – Edge Cases
# ============================================================


def test_empty_exporter(
    exporter,
):
    """
    Test behavior of empty exporter.
    """

    assert (
        exporter.count()
        ==
        0
    )


    assert (
        exporter.queue_size()
        ==
        0
    )


    assert (
        len(exporter)
        ==
        0
    )


    stats = (
        exporter.statistics()
    )


    assert (
        stats["export_count"]
        ==
        0
    )


    assert (
        stats["failed_count"]
        ==
        0
    )



def test_large_batch(
    exporter,
):
    """
    Test exporting large telemetry batch.
    """

    batch = []

    for i in range(1000):

        batch.append(
            {
                "id": f"trace-{i}",
                "type": "trace",
                "trace_id": f"id-{i}",
                "name": "large.batch.test",
            }
        )


    result = (
        exporter.export_batch(
            batch
        )
    )


    assert result is not None


    assert (
        exporter.count()
        ==
        1000
    )


    stats = (
        exporter.statistics()
    )


    assert (
        stats["export_count"]
        ==
        1000
    )



def test_missing_trace_id(
    exporter,
):
    """
    Test telemetry item without trace_id.
    """

    invalid_trace = {
        "id": "trace-missing-id",
        "type": "trace",
        "name": "missing.trace",
    }


    result = (
        exporter.validate(
            invalid_trace
        )
    )


    assert (
        result
        is False
    )


    export_result = (
        exporter.export(
            invalid_trace
        )
    )


    assert (
        export_result
        is False
        or
        export_result is None
    )


    assert (
        exporter.statistics()
        ["failed_count"]
        >=
        1
    )



def test_invalid_span(
    exporter,
):
    """
    Test invalid span handling.
    """

    invalid_span = {
        "id": "span-invalid",
        "type": "span",
        "trace_id": "abc123",
        # missing span_id
        "name": "database.query",
    }


    assert (
        exporter.validate(
            invalid_span
        )
        is False
    )


    result = (
        exporter.export_span(
            invalid_span
        )
    )


    assert (
        result
        is False
        or
        result is None
    )


    stats = (
        exporter.statistics()
    )


    assert (
        stats["failed_count"]
        >=
        1
    )



def test_closed_exporter(
    exporter,
):
    """
    Test exporter behavior after close.
    """

    exporter.start()


    exporter.close()


    assert (
        exporter.closed
        is True
    )


    assert (
        exporter.running
        is False
    )


    result = (
        exporter.export(
            {
                "id": "after-close",
                "type": "trace",
                "trace_id": "closed123",
            }
        )
    )


    assert (
        result
        is False
        or
        result is None
    )


    assert (
        exporter.count()
        ==
        0
    )                                                        