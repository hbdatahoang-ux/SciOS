"""
SciOS-NG Runtime Metrics Exporter Integration

Integration layer for composing and executing metric exporters.

SciOS-NG v0.2
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable


# ==============================================================
# MetricExporterIntegration
# ==============================================================


class MetricExporterIntegration:
    """
    Integration layer for the Metrics Exporter subsystem.

    Responsibilities
    ----------------
    - Compose multiple metric exporters
    - Execute exporters in deterministic order
    - Export individual metrics
    - Export batches of metrics
    - Validate exporter configuration
    - Track integration statistics
    - Provide runtime diagnostics
    """

    def __init__(
        self,
        exporters: Iterable[Any] | None = None,
        name: str = "MetricExporterIntegration",
        description: str = "",
    ) -> None:

        self._name = name
        self._description = description

        self._exporters: list[Any] = []

        self._executions = 0
        self._success = 0
        self._failures = 0

        self._last_result: Any = None
        self._last_error: Exception | None = None

        self._created_at = datetime.utcnow()
        self._updated_at = self._created_at

        if exporters is not None:
            for exporter in exporters:
                self.add_exporter(exporter)

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def exporters_count(self) -> int:
        return len(self._exporters)

    @property
    def last_result(self) -> Any:
        return self._last_result

    @property
    def last_error(self) -> Exception | None:
        return self._last_error

    # ==========================================================
    # Exporter Management
    # ==========================================================

    def add_exporter(
        self,
        exporter: Any,
    ) -> "MetricExporterIntegration":
        """
        Add an exporter to the ordered integration chain.
        """

        if exporter is None:
            raise ValueError(
                "exporter must not be None"
            )

        if not (
            callable(exporter)
            or hasattr(exporter, "export")
            or hasattr(exporter, "process")
            or hasattr(exporter, "execute")
        ):
            raise TypeError(
                "exporter must expose a supported execution API: "
                "export(), process(), execute(), or be callable"
            )

        self._exporters.append(exporter)

        return self

    def remove_exporter(
        self,
        exporter: Any,
    ) -> "MetricExporterIntegration":
        """
        Remove an exporter if present.
        """

        if exporter in self._exporters:
            self._exporters.remove(exporter)

        self._updated_at = datetime.utcnow()

        return self

    def clear_exporters(
        self,
    ) -> "MetricExporterIntegration":
        """
        Remove all exporters.
        """

        self._exporters.clear()
        self._updated_at = datetime.utcnow()

        return self

    def exporters(self) -> list[Any]:
        """
        Return a copy of the exporter chain.
        """

        return list(self._exporters)

    def get_exporter(
        self,
        index: int,
    ) -> Any:
        """
        Return exporter at a specific position.
        """

        return self._exporters[index]

    # ==========================================================
    # Execution
    # ==========================================================

    def execute(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute the metric through all configured exporters.

        Each exporter receives the result produced by the
        previous exporter.

        This creates a deterministic exporter chain:

            metric
            ↓
            exporter_1
            ↓
            exporter_2
            ↓
            final result

        If no exporters are configured, the original metric
        is returned unchanged.
        """

        result = metric

        try:
            if not self._exporters:
                self._executions += 1
                self._success += 1

                self._last_result = metric
                self._last_error = None

                return metric

            for exporter in self._exporters:

                result = self._execute_exporter(
                    exporter,
                    result,
                    **kwargs,
                )

            self._executions += 1
            self._success += 1

            self._last_result = result
            self._last_error = None

            return result

        except Exception as exc:

            self._executions += 1
            self._failures += 1

            self._last_error = exc
            self._last_result = None

            raise

        finally:

            self._updated_at = datetime.utcnow()


    def export(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Primary exporter API.

        Alias for execute().
        """

        return self.execute(
            metric,
            **kwargs,
        )

    def process(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Alias for execute().
        """

        return self.execute(
            metric,
            **kwargs,
        )

    def run(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Alias for execute().
        """

        return self.execute(
            metric,
            **kwargs,
        )

    # ==========================================================
    # Batch Execution
    # ==========================================================

    def execute_many(
        self,
        metrics: Iterable[Any],
        **kwargs: Any,
    ) -> list[Any]:
        """
        Execute the exporter integration for multiple metrics.
        """

        return [
            self.execute(
                metric,
                **kwargs,
            )
            for metric in metrics
        ]

    def export_many(
        self,
        metrics: Iterable[Any],
        **kwargs: Any,
    ) -> list[Any]:
        """
        Export multiple metrics.
        """

        return self.execute_many(
            metrics,
            **kwargs,
        )

    def process_many(
        self,
        metrics: Iterable[Any],
        **kwargs: Any,
    ) -> list[Any]:
        """
        Alias for execute_many().
        """

        return self.execute_many(
            metrics,
            **kwargs,
        )

    # ==========================================================
    # Exporter Execution
    # ==========================================================

    @staticmethod
    def _execute_exporter(
        exporter: Any,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute one exporter according to its public API.

        Preference order:
            export()
            process()
            execute()
            callable
        """

        if hasattr(exporter, "export"):
            return exporter.export(
                metric,
                **kwargs,
            )

        if hasattr(exporter, "process"):
            return exporter.process(
                metric,
                **kwargs,
            )

        if hasattr(exporter, "execute"):
            return exporter.execute(
                metric,
                **kwargs,
            )

        if callable(exporter):
            return exporter(
                metric,
                **kwargs,
            )

        raise TypeError(
            "Exporter does not expose a supported execution API"
        )

    # ==========================================================
    # Validation
    # ==========================================================

    def validate_chain(self) -> bool:
        """
        Validate all registered exporters.
        """

        for exporter in self._exporters:
            if not (
                callable(exporter)
                or hasattr(exporter, "export")
                or hasattr(exporter, "process")
                or hasattr(exporter, "execute")
            ):
                return False

        return True

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def close(self) -> "MetricExporterIntegration":
        """
        Close all exporters that expose close().
        """

        for exporter in self._exporters:
            close = getattr(
                exporter,
                "close",
                None,
            )

            if callable(close):
                close()

        self._updated_at = datetime.utcnow()

        return self

    def flush(self) -> "MetricExporterIntegration":
        """
        Flush all exporters that expose flush().
        """

        for exporter in self._exporters:
            flush = getattr(
                exporter,
                "flush",
                None,
            )

            if callable(flush):
                flush()

        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Diagnostics
    # ==========================================================

    def statistics(self) -> dict[str, Any]:
        """
        Return integration execution statistics.
        """

        return {
            "name": self._name,
            "exporters": len(self._exporters),
            "executions": self._executions,
            "success": self._success,
            "failures": self._failures,
        }

    def status(self) -> dict[str, Any]:
        """
        Return integration status.
        """

        return {
            "exporters": len(self._exporters),
            "active": bool(self._exporters),
            "valid": self.validate_chain(),
        }

    def reset(self) -> "MetricExporterIntegration":
        """
        Reset runtime statistics while preserving configuration.
        """

        self._executions = 0
        self._success = 0
        self._failures = 0

        self._last_result = None
        self._last_error = None

        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __len__(self) -> int:
        return len(self._exporters)

    def __iter__(self):
        return iter(self._exporters)

    def __contains__(self, exporter: Any) -> bool:
        return exporter in self._exporters

    def __call__(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        return self.execute(
            metric,
            **kwargs,
        )

    def __repr__(self) -> str:
        return (
            f"MetricExporterIntegration("
            f"name={self._name!r}, "
            f"exporters={len(self._exporters)}, "
            f"executions={self._executions}, "
            f"success={self._success}, "
            f"failures={self._failures}"
            f")"
        )

    def __str__(self) -> str:
        return self._name