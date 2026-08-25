"""
SciOS Runtime Observability
===========================

Stdout Exporter Tests
---------------------

Tests for:

    scios.runtime.observability.exporters.stdout

Python 3.11+
"""

from __future__ import annotations

import io
import sys

import pytest

from scios.runtime.observability.exporters.base import (
    ExportFormat,
    ExportPayload,
    ExportResult,
)

from scios.runtime.observability.exporters.stdout import (
    DEFAULT_AUTO_FLUSH,
    DEFAULT_PREFIX,
    DEFAULT_SEPARATOR,
    DEFAULT_STREAM,
    DEFAULT_SUFFIX,
    STDOUT_EXPORTER_VERSION,
    StdoutExportOptions,
    StdoutExporter,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def stream() -> io.StringIO:
    return io.StringIO()


@pytest.fixture
def exporter(
    stream: io.StringIO,
) -> StdoutExporter:
    return StdoutExporter(
        name="stdout",
        stream=stream,
    )


@pytest.fixture
def payload() -> ExportPayload:
    return ExportPayload(
        name="request_total",
        value=42,
        labels={
            "method": "GET",
            "status": "200",
        },
    )


@pytest.fixture
def payloads() -> list[ExportPayload]:
    return [
        ExportPayload(name="one", value=1),
        ExportPayload(name="two", value=2),
        ExportPayload(name="three", value=3),
    ]


# ==============================================================================
# Part 1. Construction
# ==============================================================================


def test_default_name() -> None:
    exporter = StdoutExporter()

    assert exporter.name == "stdout"


def test_custom_name(
    stream: io.StringIO,
) -> None:
    exporter = StdoutExporter(
        name="custom",
        stream=stream,
    )

    assert exporter.name == "custom"


def test_default_stream() -> None:
    exporter = StdoutExporter()

    assert exporter.stream is DEFAULT_STREAM


def test_custom_stream(
    stream: io.StringIO,
) -> None:
    exporter = StdoutExporter(
        stream=stream,
    )

    assert exporter.stream is stream


def test_export_format(
    exporter: StdoutExporter,
) -> None:
    # ``format`` is the stable base-class property.
    assert exporter.format is ExportFormat.TEXT


def test_encoding(
    exporter: StdoutExporter,
) -> None:
    assert exporter.encoding == "utf-8"


def test_version(
    exporter: StdoutExporter,
) -> None:
    assert exporter.version == STDOUT_EXPORTER_VERSION


def test_default_configuration(
    exporter: StdoutExporter,
) -> None:
    assert exporter.separator == DEFAULT_SEPARATOR
    assert exporter.prefix == DEFAULT_PREFIX
    assert exporter.suffix == DEFAULT_SUFFIX
    assert exporter.auto_flush is DEFAULT_AUTO_FLUSH


def test_custom_options(
    stream: io.StringIO,
) -> None:
    options = StdoutExportOptions(
        stream=stream,
        separator="|",
        prefix="[TEST] ",
        suffix="<END>",
        auto_flush=False,
    )

    exporter = StdoutExporter(
        name="custom",
        options=options,
    )

    assert exporter.stream is stream
    assert exporter.separator == "|"
    assert exporter.prefix == "[TEST] "
    assert exporter.suffix == "<END>"
    assert exporter.auto_flush is False


def test_options_are_exposed_through_base_property(
    exporter: StdoutExporter,
) -> None:
    options = exporter.options

    assert options["separator"] == DEFAULT_SEPARATOR
    assert options["prefix"] == DEFAULT_PREFIX
    assert options["suffix"] == DEFAULT_SUFFIX
    assert options["auto_flush"] is DEFAULT_AUTO_FLUSH


# ==============================================================================
# Part 2. Formatting
# ==============================================================================


def test_format_string(
    exporter: StdoutExporter,
) -> None:
    assert exporter.format_string("hello") == "hello\n"


def test_format_integer(
    exporter: StdoutExporter,
) -> None:
    assert exporter.format_string(42) == "42\n"


def test_format_float(
    exporter: StdoutExporter,
) -> None:
    assert exporter.format_string(3.14) == "3.14\n"


def test_format_mapping(
    exporter: StdoutExporter,
) -> None:
    assert exporter.format_string({"a": 1}) == "{'a': 1}\n"


def test_format_list(
    exporter: StdoutExporter,
) -> None:
    assert exporter.format_string([1, 2, 3]) == "[1, 2, 3]\n"


def test_format_with_prefix(
    exporter: StdoutExporter,
) -> None:
    exporter.set_prefix("[INFO] ")

    assert exporter.format_string("hello") == "[INFO] hello\n"


def test_format_with_suffix(
    exporter: StdoutExporter,
) -> None:
    exporter.set_suffix("<END>")

    assert exporter.format_string("hello") == "hello<END>"


def test_format_with_prefix_and_suffix(
    exporter: StdoutExporter,
) -> None:
    exporter.set_prefix("[")
    exporter.set_suffix("]\n")

    assert exporter.format_string("hello") == "[hello]\n"


def test_format_empty_string(
    exporter: StdoutExporter,
) -> None:
    assert exporter.format_string("") == "\n"


def test_encode_matches_format(
    exporter: StdoutExporter,
) -> None:
    value = {"name": "test"}

    assert exporter.encode(value) == exporter.format_string(value)


def test_decode_identity(
    exporter: StdoutExporter,
) -> None:
    text = "hello world\n"

    assert exporter.decode(text) == text


def test_deserialize_identity(
    exporter: StdoutExporter,
) -> None:
    text = "hello world\n"

    assert exporter.deserialize(text) == text


def test_decode_rejects_non_string(
    exporter: StdoutExporter,
) -> None:
    with pytest.raises(TypeError):
        exporter.decode(123)  # type: ignore[arg-type]


# ==============================================================================
# Part 3. Validation
# ==============================================================================


def test_validate_stream(
    exporter: StdoutExporter,
) -> None:
    assert exporter.validate_stream()


def test_validate_output_accepts_string(
    exporter: StdoutExporter,
) -> None:
    assert exporter.validate_output("hello")


def test_validate_output_rejects_non_string(
    exporter: StdoutExporter,
) -> None:
    assert exporter.validate_output(123) is False


def test_validate_output_raise_error(
    exporter: StdoutExporter,
) -> None:
    with pytest.raises(TypeError):
        exporter.validate_output(
            123,
            raise_error=True,
        )


def test_validate_payload(
    exporter: StdoutExporter,
    payload: ExportPayload,
) -> None:
    assert exporter.validate_payload(payload)


def test_validate_mapping_payload(
    exporter: StdoutExporter,
) -> None:
    assert exporter.validate_payload(
        {
            "name": "test",
            "value": 42,
        }
    )


# ==============================================================================
# Part 4. Writing
# ==============================================================================


def test_write_returns_utf8_byte_count(
    exporter: StdoutExporter,
    stream: io.StringIO,
) -> None:
    text = "hello\n"

    result = exporter.write(text)

    assert result == len(text.encode("utf-8"))
    assert stream.getvalue() == text


def test_write_unicode_byte_count(
    exporter: StdoutExporter,
    stream: io.StringIO,
) -> None:
    text = "Xin chào\n"

    result = exporter.write(text)

    assert result == len(text.encode("utf-8"))
    assert stream.getvalue() == text


def test_write_empty_string(
    exporter: StdoutExporter,
    stream: io.StringIO,
) -> None:
    assert exporter.write("") == 0
    assert stream.getvalue() == ""


def test_write_updates_statistics(
    exporter: StdoutExporter,
) -> None:
    exporter.write("one\n")

    assert exporter.bytes_written == 4
    assert exporter.lines_written == 1
    assert exporter.objects_exported == 1


def test_multiple_writes_update_statistics(
    exporter: StdoutExporter,
) -> None:
    exporter.write("one\n")
    exporter.write("two\n")
    exporter.write("three\n")

    assert exporter.bytes_written == 14
    assert exporter.lines_written == 3
    assert exporter.objects_exported == 3


def test_write_preserves_order(
    exporter: StdoutExporter,
    stream: io.StringIO,
) -> None:
    exporter.write("one\n")
    exporter.write("two\n")
    exporter.write("three\n")

    assert stream.getvalue() == (
        "one\n"
        "two\n"
        "three\n"
    )


def test_write_rejects_non_string(
    exporter: StdoutExporter,
) -> None:
    with pytest.raises(TypeError):
        exporter.write(123)  # type: ignore[arg-type]


def test_write_stream_custom_target(
    exporter: StdoutExporter,
) -> None:
    target = io.StringIO()

    written = exporter.write_stream(
        "hello\n",
        target,
    )

    assert written == 6
    assert target.getvalue() == "hello\n"


def test_flush(
    exporter: StdoutExporter,
    stream: io.StringIO,
) -> None:
    exporter.write("hello\n")

    assert exporter.flush() is exporter
    assert stream.getvalue() == "hello\n"


# ==============================================================================
# Part 5. Export API
# ==============================================================================


def test_export_returns_export_result(
    exporter: StdoutExporter,
    payload: ExportPayload,
) -> None:
    result = exporter.export(payload)

    assert isinstance(result, ExportResult)
    assert result.success is True
    assert result.exporter == "stdout"
    assert result.count == 1
    assert result.bytes_exported > 0


def test_export_writes_output(
    exporter: StdoutExporter,
    stream: io.StringIO,
    payload: ExportPayload,
) -> None:
    result = exporter.export(payload)

    assert result.success
    assert stream.getvalue()


def test_export_contains_payload_name(
    exporter: StdoutExporter,
    stream: io.StringIO,
    payload: ExportPayload,
) -> None:
    exporter.export(payload)

    assert "request_total" in stream.getvalue()


def test_export_mapping_payload(
    exporter: StdoutExporter,
    stream: io.StringIO,
) -> None:
    exporter.export(
        {
            "name": "request_total",
            "value": 42,
        }
    )

    output = stream.getvalue()

    assert "request_total" in output
    assert "42" in output


def test_export_updates_base_statistics(
    exporter: StdoutExporter,
    payload: ExportPayload,
) -> None:
    exporter.export(payload)

    assert exporter.export_count == 1
    assert exporter.success_count == 1
    assert exporter.error_count == 0
    assert exporter.bytes_exported > 0


def test_export_updates_stdout_statistics(
    exporter: StdoutExporter,
    payload: ExportPayload,
) -> None:
    exporter.export(payload)

    assert exporter.objects_exported == 1
    assert exporter.bytes_written > 0
    assert exporter.lines_written == 1


def test_export_text(
    exporter: StdoutExporter,
    stream: io.StringIO,
) -> None:
    result = exporter.export_text("hello")

    assert result.success
    assert stream.getvalue() == "hello\n"


def test_export_object(
    exporter: StdoutExporter,
    stream: io.StringIO,
) -> None:
    result = exporter.export_object({"value": 42})

    assert result.success
    assert stream.getvalue() == "{'value': 42}\n"


def test_export_dict(
    exporter: StdoutExporter,
    stream: io.StringIO,
) -> None:
    exporter.export_dict({"value": 42})

    assert "42" in stream.getvalue()


def test_export_list(
    exporter: StdoutExporter,
    stream: io.StringIO,
) -> None:
    exporter.export_list([1, 2, 3])

    assert stream.getvalue() == "[1, 2, 3]\n"


def test_export_payload(
    exporter: StdoutExporter,
    payload: ExportPayload,
) -> None:
    result = exporter.export_payload(payload)

    assert result.success


def test_export_many(
    exporter: StdoutExporter,
    stream: io.StringIO,
    payloads: list[ExportPayload],
) -> None:
    results = exporter.export_many(payloads)

    assert len(results) == 3
    assert all(result.success for result in results)

    output = stream.getvalue()

    assert "one" in output
    assert "two" in output
    assert "three" in output


def test_call_exports_object(
    exporter: StdoutExporter,
    stream: io.StringIO,
) -> None:
    result = exporter("hello")

    assert result.success
    assert stream.getvalue() == "hello\n"


# ==============================================================================
# Part 6. Configuration
# ==============================================================================


def test_set_stream(
    exporter: StdoutExporter,
) -> None:
    new_stream = io.StringIO()

    result = exporter.set_stream(new_stream)

    assert result is exporter
    assert exporter.stream is new_stream


def test_set_stream_rejects_none(
    exporter: StdoutExporter,
) -> None:
    with pytest.raises(ValueError):
        exporter.set_stream(None)  # type: ignore[arg-type]


def test_set_stream_rejects_invalid_value(
    exporter: StdoutExporter,
) -> None:
    with pytest.raises(TypeError):
        exporter.set_stream(123)  # type: ignore[arg-type]


def test_set_prefix(
    exporter: StdoutExporter,
) -> None:
    result = exporter.set_prefix("[TEST] ")

    assert result is exporter
    assert exporter.prefix == "[TEST] "


def test_set_prefix_rejects_invalid_value(
    exporter: StdoutExporter,
) -> None:
    with pytest.raises(TypeError):
        exporter.set_prefix(123)  # type: ignore[arg-type]


def test_set_suffix(
    exporter: StdoutExporter,
) -> None:
    result = exporter.set_suffix("<END>")

    assert result is exporter
    assert exporter.suffix == "<END>"


def test_set_suffix_rejects_invalid_value(
    exporter: StdoutExporter,
) -> None:
    with pytest.raises(TypeError):
        exporter.set_suffix(123)  # type: ignore[arg-type]


def test_set_separator(
    exporter: StdoutExporter,
) -> None:
    result = exporter.set_separator("|")

    assert result is exporter
    assert exporter.separator == "|"


def test_set_separator_rejects_invalid_value(
    exporter: StdoutExporter,
) -> None:
    with pytest.raises(TypeError):
        exporter.set_separator(123)  # type: ignore[arg-type]


def test_set_auto_flush(
    exporter: StdoutExporter,
) -> None:
    result = exporter.set_auto_flush(False)

    assert result is exporter
    assert exporter.auto_flush is False


def test_set_auto_flush_rejects_invalid_value(
    exporter: StdoutExporter,
) -> None:
    with pytest.raises(TypeError):
        exporter.set_auto_flush(1)  # type: ignore[arg-type]


def test_options_dict(
    exporter: StdoutExporter,
    stream: io.StringIO,
) -> None:
    options = exporter.options_dict()

    assert options["stream"] == "StringIO"
    assert options["separator"] == " "
    assert options["prefix"] == ""
    assert options["suffix"] == "\n"
    assert options["auto_flush"] is True


# ==============================================================================
# Part 7. Statistics
# ==============================================================================


def test_initial_statistics(
    exporter: StdoutExporter,
) -> None:
    assert exporter.bytes_written == 0
    assert exporter.lines_written == 0
    assert exporter.objects_exported == 0
    assert exporter.average_size == 0.0


def test_average_size(
    exporter: StdoutExporter,
) -> None:
    exporter.write("1234")
    exporter.write("123456")

    assert exporter.objects_exported == 2
    assert exporter.bytes_written == 10
    assert exporter.average_size == 5.0


def test_last_output(
    exporter: StdoutExporter,
) -> None:
    exporter.write("first\n")
    exporter.write("second\n")

    assert exporter.last_output == "second\n"


def test_last_output_time(
    exporter: StdoutExporter,
) -> None:
    assert exporter.last_output_time is None

    exporter.write("hello\n")

    assert isinstance(
        exporter.last_output_time,
        float,
    )


def test_clear_statistics(
    exporter: StdoutExporter,
) -> None:
    exporter.write("hello\n")

    exporter.clear_statistics()

    assert exporter.bytes_written == 0
    assert exporter.lines_written == 0
    assert exporter.objects_exported == 0
    assert exporter.last_output is None
    assert exporter.last_output_time is None


# ==============================================================================
# Part 8. Reset
# ==============================================================================


def test_reset_stdout(
    exporter: StdoutExporter,
) -> None:
    exporter.set_prefix("[")
    exporter.set_suffix("]")
    exporter.set_separator("|")
    exporter.set_auto_flush(False)

    exporter.write("hello")

    exporter.reset_stdout()

    assert exporter.stream is DEFAULT_STREAM
    assert exporter.prefix == DEFAULT_PREFIX
    assert exporter.suffix == DEFAULT_SUFFIX
    assert exporter.separator == DEFAULT_SEPARATOR
    assert exporter.auto_flush is DEFAULT_AUTO_FLUSH

    assert exporter.bytes_written == 0
    assert exporter.lines_written == 0
    assert exporter.objects_exported == 0


# ==============================================================================
# Part 9. Snapshot / Restore
# ==============================================================================


def test_snapshot_contains_stdout_state(
    exporter: StdoutExporter,
    payload: ExportPayload,
) -> None:
    exporter.export(payload)

    snapshot = exporter.snapshot()

    assert snapshot["format"] == "text"
    assert snapshot["version"] == STDOUT_EXPORTER_VERSION
    assert "stdout" in snapshot

    state = snapshot["stdout"]

    assert state["bytes_written"] > 0
    assert state["lines_written"] == 1
    assert state["objects_exported"] == 1
    assert state["last_output"] is not None


def test_snapshot_does_not_serialize_stream_object(
    exporter: StdoutExporter,
) -> None:
    snapshot = exporter.snapshot()

    assert snapshot["stdout"]["stream"] == "StringIO"
    assert snapshot["stdout"]["stream"] is not exporter.stream


def test_restore_stdout_state(
    exporter: StdoutExporter,
    payload: ExportPayload,
) -> None:
    exporter.export(payload)

    snapshot = exporter.snapshot()

    restored_stream = io.StringIO()

    restored = StdoutExporter(
        name="restored",
        stream=restored_stream,
    )

    restored.restore(snapshot)

    assert restored.bytes_written == exporter.bytes_written
    assert restored.lines_written == exporter.lines_written
    assert restored.objects_exported == exporter.objects_exported
    assert restored.last_output == exporter.last_output


def test_restore_preserves_current_stream(
    stream: io.StringIO,
    payload: ExportPayload,
) -> None:
    exporter = StdoutExporter(
        stream=stream,
    )

    exporter.export(payload)

    snapshot = exporter.snapshot()

    new_stream = io.StringIO()

    restored = StdoutExporter(
        stream=new_stream,
    )

    restored.restore(snapshot)

    assert restored.stream is new_stream


# ==============================================================================
# Part 10. Enabled / Disabled
# ==============================================================================


def test_enabled_by_default(
    exporter: StdoutExporter,
) -> None:
    assert exporter.enabled is True


def test_disabled_export_does_not_write(
    exporter: StdoutExporter,
    stream: io.StringIO,
    payload: ExportPayload,
) -> None:
    exporter.enabled = False

    result = exporter.export(payload)

    assert result.success is False
    assert stream.getvalue() == ""
    assert exporter.bytes_written == 0
    assert exporter.objects_exported == 0


def test_disabled_export_updates_base_attempt_count(
    exporter: StdoutExporter,
    payload: ExportPayload,
) -> None:
    exporter.enabled = False

    exporter.export(payload)

    assert exporter.export_count == 1
    assert exporter.success_count == 0


def test_enabled_rejects_non_bool(
    exporter: StdoutExporter,
) -> None:
    with pytest.raises(TypeError):
        exporter.enabled = 1  # type: ignore[assignment]


# ==============================================================================
# Part 11. Lifecycle
# ==============================================================================


def test_initial_lifecycle_state(
    exporter: StdoutExporter,
) -> None:
    assert exporter.started is False
    assert exporter.closed is False
    assert exporter.state == "stopped"


def test_start(
    exporter: StdoutExporter,
) -> None:
    assert exporter.start() is exporter
    assert exporter.started is True
    assert exporter.state == "started"


def test_start_is_idempotent(
    exporter: StdoutExporter,
) -> None:
    exporter.start()

    assert exporter.start() is exporter
    assert exporter.started is True


def test_stop(
    exporter: StdoutExporter,
) -> None:
    exporter.start()

    assert exporter.stop() is exporter
    assert exporter.started is False
    assert exporter.state == "stopped"


def test_close_returns_self(
    exporter: StdoutExporter,
) -> None:
    assert exporter.close() is exporter
    assert exporter.closed is True
    assert exporter.state == "closed"


def test_close_is_idempotent(
    exporter: StdoutExporter,
) -> None:
    exporter.close()

    assert exporter.close() is exporter


def test_cleanup_preserves_configuration(
    exporter: StdoutExporter,
) -> None:
    exporter.set_prefix("[TEST] ")

    exporter.cleanup()

    assert exporter.prefix == "[TEST] "


def test_cleanup_clears_last_output(
    exporter: StdoutExporter,
) -> None:
    exporter.write("hello\n")

    exporter.cleanup()

    assert exporter.last_output is None
    assert exporter.last_output_time is None


# ==============================================================================
# Part 12. Close / Stream Ownership
# ==============================================================================


def test_close_stdout_does_not_close_sys_stdout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_stdout = io.StringIO()

    monkeypatch.setattr(
        sys,
        "stdout",
        fake_stdout,
    )

    exporter = StdoutExporter(
        stream=fake_stdout,
    )

    exporter.close()

    assert fake_stdout.closed is False


def test_close_stderr_does_not_close_sys_stderr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_stderr = io.StringIO()

    monkeypatch.setattr(
        sys,
        "stderr",
        fake_stderr,
    )

    exporter = StdoutExporter(
        stream=fake_stderr,
    )

    exporter.close()

    assert fake_stderr.closed is False


def test_close_custom_stream(
    stream: io.StringIO,
) -> None:
    exporter = StdoutExporter(
        stream=stream,
    )

    exporter.close()

    assert stream.closed is True


# ==============================================================================
# Part 13. Prefix / Suffix
# ==============================================================================


def test_prefix_is_used_during_export(
    exporter: StdoutExporter,
    stream: io.StringIO,
    payload: ExportPayload,
) -> None:
    exporter.set_prefix("[SCI] ")

    exporter.export(payload)

    assert stream.getvalue().startswith("[SCI] ")


def test_suffix_is_used_during_export(
    exporter: StdoutExporter,
    stream: io.StringIO,
    payload: ExportPayload,
) -> None:
    exporter.set_suffix("<END>\n")

    exporter.export(payload)

    assert stream.getvalue().endswith("<END>\n")


def test_separator_configuration(
    exporter: StdoutExporter,
) -> None:
    exporter.set_separator("|")

    assert exporter.separator == "|"
    assert exporter.options["separator"] == "|"


# ==============================================================================
# Part 14. Representation
# ==============================================================================


def test_repr(
    exporter: StdoutExporter,
) -> None:
    value = repr(exporter)

    assert "StdoutExporter" in value
    assert "stdout" in value
    assert "text" in value


def test_str(
    exporter: StdoutExporter,
) -> None:
    value = str(exporter)

    assert "stdout" in value
    assert "STDOUT" in value


def test_len(
    exporter: StdoutExporter,
    payload: ExportPayload,
) -> None:
    assert len(exporter) == 0

    exporter.export(payload)

    assert len(exporter) == 1


# ==============================================================================
# Part 15. Diagnostics
# ==============================================================================


def test_report_contains_stdout_state(
    exporter: StdoutExporter,
) -> None:
    report = exporter.report()

    assert report["name"] == "stdout"
    assert report["format"] == "text"
    assert report["version"] == STDOUT_EXPORTER_VERSION
    assert "stdout" in report


def test_report_contains_stream_type(
    exporter: StdoutExporter,
) -> None:
    report = exporter.report()

    assert report["stdout"]["stream"] == "StringIO"


def test_diagnostics_contains_stream_state(
    exporter: StdoutExporter,
) -> None:
    diagnostics = exporter.diagnostics()

    assert "stdout" in diagnostics
    assert diagnostics["stdout"]["stream"] == "StringIO"
    assert diagnostics["stdout"]["valid_stream"] is True


def test_base_diagnostics(
    exporter: StdoutExporter,
) -> None:
    diagnostics = exporter.diagnostics()

    assert diagnostics["name"] == "stdout"
    assert diagnostics["format"] == "text"
    assert diagnostics["enabled"] is True
    assert diagnostics["state"] == "stopped"


def test_health_initial(
    exporter: StdoutExporter,
) -> None:
    health = exporter.health()

    assert health["name"] == "stdout"
    assert health["enabled"] is True
    assert health["healthy"] is True


# ==============================================================================
# Part 16. Invalid Payloads
# ==============================================================================


def test_export_rejects_invalid_payload(
    exporter: StdoutExporter,
) -> None:
    result = exporter.export(123)  # type: ignore[arg-type]

    assert result.success is False
    assert exporter.error_count == 1


def test_export_rejects_mapping_without_name(
    exporter: StdoutExporter,
) -> None:
    result = exporter.export(
        {
            "value": 42,
        }
    )

    assert result.success is False
    assert exporter.error_count == 1


def test_export_after_close_fails(
    exporter: StdoutExporter,
    payload: ExportPayload,
) -> None:
    exporter.close()

    result = exporter.export(payload)

    assert result.success is False
    assert "closed" in (result.error or "")


def test_reset_after_close_rejected(
    exporter: StdoutExporter,
) -> None:
    exporter.close()

    with pytest.raises(RuntimeError):
        exporter.reset_stdout()


# ==============================================================================
# Part 17. Unicode
# ==============================================================================


def test_export_unicode(
    exporter: StdoutExporter,
    stream: io.StringIO,
) -> None:
    result = exporter.export_text("Xin chào Việt Nam")

    assert result.success
    assert stream.getvalue() == "Xin chào Việt Nam\n"


def test_unicode_statistics(
    exporter: StdoutExporter,
) -> None:
    text = "Xin chào"

    exporter.export_text(text)

    expected = len(
        f"{text}\n".encode("utf-8")
    )

    assert exporter.bytes_written == expected


# ==============================================================================
# Part 18. Ordering
# ==============================================================================


def test_export_many_preserves_order(
    exporter: StdoutExporter,
    stream: io.StringIO,
) -> None:
    payloads = [
        ExportPayload(name="first", value=1),
        ExportPayload(name="second", value=2),
        ExportPayload(name="third", value=3),
    ]

    exporter.export_many(payloads)

    output = stream.getvalue()

    assert output.index("first") < output.index("second")
    assert output.index("second") < output.index("third")


# ==============================================================================
# Part 19. Public Properties
# ==============================================================================


def test_public_properties(
    exporter: StdoutExporter,
) -> None:
    assert exporter.name == "stdout"
    assert exporter.format == ExportFormat.TEXT
    assert exporter.encoding == "utf-8"
    assert exporter.enabled is True
    assert exporter.stream is not None
    assert exporter.version == STDOUT_EXPORTER_VERSION


def test_result_properties(
    exporter: StdoutExporter,
) -> None:
    result = exporter.export_text("hello")

    assert result.success is True
    assert result.failed is False
    assert result.exporter == "stdout"
    assert result.count == 1
    assert result.bytes_exported == len(
        "hello\n".encode("utf-8")
    )
    assert result.error is None