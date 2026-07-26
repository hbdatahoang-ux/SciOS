"""
SciOS Observability - JSON Trace Exporter
=========================================

Export traces to JSON files.

Responsibilities
----------------
- Export Trace objects
- Persist JSON documents
- Support append/overwrite mode
- UTF-8 encoding
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .exporter import TraceExporter
from .serialization import TraceSerializer
from .trace import Trace

__all__ = [
    "JsonTraceExporter",
]


class JsonTraceExporter(TraceExporter):
    """
    Export traces to JSON.

    Parameters
    ----------
    output_dir:
        Directory where traces are stored.

    filename:
        Default output filename.

    indent:
        JSON indentation.

    ensure_ascii:
        Whether to escape unicode.

    append:
        Append JSON lines instead of overwriting.
    """

    def __init__(
        self,
        output_dir: str | Path = "traces",
        filename: str = "trace.json",
        *,
        indent: int = 2,
        ensure_ascii: bool = False,
        append: bool = False,
    ) -> None:

        self.output_dir = Path(output_dir)

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.filename = filename

        self.indent = indent

        self.ensure_ascii = ensure_ascii

        self.append = append

        self._closed = False

    # ======================================================
    # Properties
    # ======================================================

    @property
    def path(self) -> Path:
        return self.output_dir / self.filename

    # ======================================================
    # Export
    # ======================================================

    def export_trace(
        self,
        trace: Trace,
    ) -> Path:
        """
        Export a single trace.

        Returns
        -------
        Path
            Output file path.
        """

        self._ensure_open()

        payload = TraceSerializer.serialize_trace(
            trace
        )

        mode = "a" if self.append else "w"

        with self.path.open(
            mode,
            encoding="utf-8",
        ) as fp:

            json.dump(
                payload,
                fp,
                indent=self.indent,
                ensure_ascii=self.ensure_ascii,
            )

            if self.append:
                fp.write("\n")

        return self.path

    # ======================================================

    def export_many(
        self,
        traces: Iterable[Trace],
        filename: str | None = None,
    ) -> Path:
        """
        Export multiple traces.

        Stored as a JSON array.
        """

        self._ensure_open()

        path = (
            self.output_dir / filename
            if filename
            else self.path
        )

        payload = [
            TraceSerializer.serialize_trace(trace)
            for trace in traces
        ]

        with path.open(
            "w",
            encoding="utf-8",
        ) as fp:

            json.dump(
                payload,
                fp,
                indent=self.indent,
                ensure_ascii=self.ensure_ascii,
            )

        return path

    # ======================================================

    def export_span(
        self,
        span,
        filename: str = "span.json",
    ) -> Path:
        """
        Export a single span.
        """

        self._ensure_open()

        path = self.output_dir / filename

        payload = TraceSerializer.serialize_span(
            span
        )

        with path.open(
            "w",
            encoding="utf-8",
        ) as fp:

            json.dump(
                payload,
                fp,
                indent=self.indent,
                ensure_ascii=self.ensure_ascii,
            )

        return path

    # ======================================================

    def flush(self) -> None:
        """
        Flush exporter.

        Reserved for compatibility with buffered exporters.
        """

        return

    # ======================================================

    def close(self) -> None:
        """
        Close exporter.
        """

        self._closed = True

    # ======================================================

    @property
    def closed(self) -> bool:
        return self._closed

    # ======================================================

    def _ensure_open(self) -> None:

        if self._closed:
            raise RuntimeError(
                "Exporter has been closed."
            )

    # ======================================================

    def __enter__(self):

        return self

    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:

        self.close()

    # ======================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"path='{self.path}', "
            f"append={self.append})"
        )