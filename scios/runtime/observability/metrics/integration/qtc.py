"""
SciOS-NG Runtime Metrics QTC Integration

Integration layer between Runtime Metrics and QTC subsystem.

SciOS-NG v0.2
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable


# ==============================================================
# MetricQTCIntegration
# ==============================================================


class MetricQTCIntegration:
    """
    Integration layer for connecting Metrics with QTC.

    Responsibilities
    ----------------
    - Execute metric operations through a QTC provider
    - Support common QTC provider APIs
    - Preserve QTC subsystem isolation
    - Track integration statistics
    - Provide runtime diagnostics
    """

    def __init__(
        self,
        qtc: Any = None,
        name: str = "MetricQTCIntegration",
        description: str = "",
    ) -> None:

        self._name = name
        self._description = description

        self._qtc = qtc

        self._executions = 0
        self._success = 0
        self._failures = 0

        self._last_result: Any = None
        self._last_error: Exception | None = None

        self._created_at = datetime.utcnow()
        self._updated_at = self._created_at

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
    def qtc(self) -> Any:
        return self._qtc

    @property
    def configured(self) -> bool:
        return self._qtc is not None

    @property
    def last_result(self) -> Any:
        return self._last_result

    @property
    def last_error(self) -> Exception | None:
        return self._last_error

    # ==========================================================
    # QTC Management
    # ==========================================================

    def set_qtc(
        self,
        qtc: Any,
    ) -> "MetricQTCIntegration":
        """
        Set the QTC provider.
        """

        self._qtc = qtc
        self._updated_at = datetime.utcnow()

        return self

    def clear_qtc(
        self,
    ) -> "MetricQTCIntegration":
        """
        Remove the current QTC provider.
        """

        self._qtc = None
        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Validation
    # ==========================================================

    def validate(self) -> bool:
        """
        Validate the configured QTC provider.

        A provider is considered valid when it exposes one of:

            evaluate()
            apply()
            execute()
            process()
            callable
        """

        if self._qtc is None:
            return True

        return bool(
            callable(self._qtc)
            or hasattr(self._qtc, "evaluate")
            or hasattr(self._qtc, "apply")
            or hasattr(self._qtc, "execute")
            or hasattr(self._qtc, "process")
        )

    # ==========================================================
    # Execution
    # ==========================================================

    def execute(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a metric through the configured QTC provider.

        Preference order:

            evaluate()
            apply()
            execute()
            process()
            callable

        When no QTC provider is configured, the metric is returned
        unchanged.
        """

        try:

            if self._qtc is None:
                result = metric

            else:
                result = self._execute_qtc(
                    metric,
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

            self._last_result = None
            self._last_error = exc

            raise

        finally:

            self._updated_at = datetime.utcnow()

    def evaluate(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Evaluate a metric through QTC.

        Alias for execute().
        """

        return self.execute(
            metric,
            **kwargs,
        )

    def apply(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Apply QTC processing to a metric.

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
        metrics: list[Any] | tuple[Any, ...],
        **kwargs: Any,
    ) -> list[Any]:
        """
        Execute multiple metrics through QTC.
        """

        return [
            self.execute(
                metric,
                **kwargs,
            )
            for metric in metrics
        ]

    def process_many(
        self,
        metrics: list[Any] | tuple[Any, ...],
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
    # QTC Provider Execution
    # ==========================================================

    def _execute_qtc(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute one operation through the QTC provider.
        """

        qtc = self._qtc

        evaluate = getattr(
            qtc,
            "evaluate",
            None,
        )

        if callable(evaluate):
            return evaluate(
                metric,
                **kwargs,
            )

        apply = getattr(
            qtc,
            "apply",
            None,
        )

        if callable(apply):
            return apply(
                metric,
                **kwargs,
            )

        execute = getattr(
            qtc,
            "execute",
            None,
        )

        if callable(execute):
            return execute(
                metric,
                **kwargs,
            )

        process = getattr(
            qtc,
            "process",
            None,
        )

        if callable(process):
            return process(
                metric,
                **kwargs,
            )

        if callable(qtc):
            return qtc(
                metric,
                **kwargs,
            )

        raise TypeError(
            "QTC provider does not expose a supported execution API"
        )

    # ==========================================================
    # Metadata
    # ==========================================================

    def record(
        self,
        key: str,
        value: Any,
    ) -> "MetricQTCIntegration":
        """
        Record metadata through the QTC provider when supported.
        """

        if self._qtc is None:
            return self

        recorder = getattr(
            self._qtc,
            "record",
            None,
        )

        if callable(recorder):
            recorder(
                key,
                value,
            )

        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def reset(
        self,
    ) -> "MetricQTCIntegration":
        """
        Reset integration statistics while preserving QTC.
        """

        self._executions = 0
        self._success = 0
        self._failures = 0

        self._last_result = None
        self._last_error = None

        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Diagnostics
    # ==========================================================

    def statistics(self) -> dict[str, Any]:
        """
        Return QTC integration statistics.
        """

        return {
            "name": self._name,
            "configured": self.configured,
            "executions": self._executions,
            "success": self._success,
            "failures": self._failures,
        }

    def status(self) -> dict[str, Any]:
        """
        Return QTC integration status.
        """

        return {
            "configured": self.configured,
            "active": self.configured,
            "valid": self.validate(),
        }

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __len__(self) -> int:
        return self._executions

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
            f"MetricQTCIntegration("
            f"name={self._name!r}, "
            f"configured={self.configured}, "
            f"executions={self._executions}, "
            f"success={self._success}, "
            f"failures={self._failures}"
            f")"
        )

    def __str__(self) -> str:
        return self._name