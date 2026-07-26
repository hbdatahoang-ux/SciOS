"""
SciOS-NG Runtime Metrics JSON Exporter

JSON persistence exporter for Runtime Metrics.

SciOS-NG v0.2
"""


from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from typing import Any


from .exporter import MetricExporter



# ==================================================================
# JSONExporter
# ==================================================================


class JSONExporter(
    MetricExporter
):
    """
    Runtime JSON Metrics Exporter.

    Responsibilities
    ----------------
    - Serialize metrics into JSON
    - Persist runtime metrics
    - Support append/export modes
    - Provide JSON observability boundary
    """



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        path: str | None = None,
        name: str = "JSONExporter",
        description: str = "",
        indent: int = 2,
        append: bool = True,
    ) -> None:


        super().__init__(
            name=name,
            description=description,
        )


        # ----------------------------------------------------------
        # Storage Configuration
        # ----------------------------------------------------------

        self._path = (
            Path(path)
            if path
            else None
        )


        self._indent = indent

        self._append = append



        # ----------------------------------------------------------
        # Runtime Buffer
        # ----------------------------------------------------------

        self._buffer: list[dict[str, Any]] = []



    # ==============================================================
    # Export API
    # ==============================================================

    def export(
        self,
        metrics: Any,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Export metrics into JSON.
        """

        with self._lock:

            self._ensure_enabled()


            record = {

                "timestamp":
                    datetime.utcnow().isoformat(),

                "metrics":
                    metrics,

                "metadata":
                    kwargs,

            }


            self._buffer.append(
                record
            )


            self._exports += 1


            self._last_export = (
                datetime.utcnow()
            )


            self._touch()



            if self._path:

                self._write()



        return record



    # ==============================================================
    # File Operations
    # ==============================================================

    def _write(
        self,
    ):
        """
        Write buffer to JSON file.
        """

        if self._path is None:

            return



        self._path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )



        if self._append and self._path.exists():

            existing = self.read()

        else:

            existing = []



        data = (
            existing
            +
            self._buffer
        )


        with open(
            self._path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=self._indent,
                default=str,
            )


        self._buffer.clear()



    def read(
        self,
    ) -> list[dict[str, Any]]:
        """
        Read JSON metrics file.
        """

        if (
            self._path is None
            or
            not self._path.exists()
        ):

            return []



        with open(
            self._path,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(
                file
            )



    def flush(
        self,
    ):
        """
        Flush pending JSON buffer.
        """

        with self._lock:

            self._write()


        return self



    def clear(
        self,
    ):
        """
        Clear JSON buffer and file.
        """

        with self._lock:

            self._buffer.clear()


            if self._path and self._path.exists():

                self._path.unlink()


        return self



    # ==============================================================
    # Serialization Helpers
    # ==============================================================

    def dumps(
        self,
        metrics: Any,
    ) -> str:
        """
        Convert metrics to JSON string.
        """

        return json.dumps(
            metrics,
            indent=self._indent,
            default=str,
        )



    def loads(
        self,
        data: str,
    ) -> Any:
        """
        Load metrics from JSON string.
        """

        return json.loads(
            data
        )



    # ==============================================================
    # Statistics
    # ==============================================================

    def summary(
        self,
    ) -> dict[str, Any]:
        """
        JSON exporter summary.
        """

        return {

            "name":
                self._name,

            "path":
                str(self._path)
                if self._path
                else None,


            "buffer_size":
                len(self._buffer),


            "exports":
                self._exports,


            "failures":
                self._failures,


            "last_export":
                self._last_export,


            "enabled":
                self._enabled,

        }



    # ==============================================================
    # Python Protocols
    # ==============================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"JSONExporter("
            f"path={str(self._path)!r}, "
            f"exports={self._exports}"
            f")"
        )



    def __len__(
        self,
    ) -> int:

        return len(
            self._buffer
        )