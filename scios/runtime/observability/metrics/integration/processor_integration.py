"""
SciOS-NG Runtime Metrics Processor Integration

Integration helpers for composing and executing metric processors.

SciOS-NG v0.2
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable, Sequence


# ==============================================================
# MetricProcessorIntegration
# ==============================================================


class MetricProcessorIntegration:
    """
    Integration layer for the Metrics Processor subsystem.

    Responsibilities
    ----------------
    - Compose multiple metric processors
    - Execute processors in deterministic order
    - Process individual metrics
    - Process batches of metrics
    - Preserve processor isolation
    - Track integration statistics
    """

    def __init__(
        self,
        processors: Iterable[Any] | None = None,
        name: str = "MetricProcessorIntegration",
        description: str = "",
    ) -> None:

        self._name = name
        self._description = description

        self._processors: list[Any] = []

        self._executions = 0
        self._success = 0
        self._failures = 0

        self._last_result: Any = None
        self._last_error: Exception | None = None

        if processors is not None:
            for processor in processors:
                self.add_processor(processor)

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
    def processors_count(self) -> int:
        return len(self._processors)

    @property
    def last_result(self) -> Any:
        return self._last_result

    @property
    def last_error(self) -> Exception | None:
        return self._last_error

    # ==========================================================
    # Processor Management
    # ==========================================================

    def add_processor(
        self,
        processor: Any,
    ) -> "MetricProcessorIntegration":
        """
        Add a processor to the ordered integration chain.
        """

        if processor is None:
            raise ValueError(
                "processor must not be None"
            )

        if not (
            callable(processor)
            or hasattr(processor, "transform")
            or hasattr(processor, "process")
            or hasattr(processor, "execute")
        ):
            raise TypeError(
                "processor must be callable or expose "
                "transform(), process(), or execute()"
            )

        self._processors.append(processor)

        return self

    def remove_processor(
        self,
        processor: Any,
    ) -> "MetricProcessorIntegration":
        """
        Remove a processor if present.
        """

        if processor in self._processors:
            self._processors.remove(processor)

        return self

    def clear_processors(
        self,
    ) -> "MetricProcessorIntegration":
        """
        Remove all processors.
        """

        self._processors.clear()

        return self

    def processors(self) -> list[Any]:
        """
        Return a copy of the processor chain.
        """

        return list(self._processors)

    def get_processor(
        self,
        index: int,
    ) -> Any:
        """
        Return processor at a specific position.
        """

        return self._processors[index]

    # ==========================================================
    # Execution
    # ==========================================================

    def execute(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute the complete processor chain.

        Each processor receives the result produced by
        the previous processor.
        """

        result = metric

        try:
            for processor in self._processors:
                result = self._execute_processor(
                    processor,
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
        Execute the processor chain for multiple metrics.
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
    # Processor Execution
    # ==========================================================

    @staticmethod
    def _execute_processor(
        processor: Any,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute one processor according to its public API.

        Preference order:
            transform()
            process()
            execute()
            callable
        """

        if hasattr(processor, "transform"):
            return processor.transform(
                metric,
                **kwargs,
            )

        if hasattr(processor, "process"):
            return processor.process(
                metric,
                **kwargs,
            )

        if hasattr(processor, "execute"):
            return processor.execute(
                metric,
                **kwargs,
            )

        if callable(processor):
            return processor(
                metric,
                **kwargs,
            )

        raise TypeError(
            "Processor does not expose a supported execution API"
        )

    # ==========================================================
    # Validation
    # ==========================================================

    def validate_chain(self) -> bool:
        """
        Validate that all registered processors expose
        a supported execution API.
        """

        for processor in self._processors:
            if not (
                callable(processor)
                or hasattr(processor, "transform")
                or hasattr(processor, "process")
                or hasattr(processor, "execute")
            ):
                return False

        return True

    # ==========================================================
    # Diagnostics
    # ==========================================================

    def statistics(self) -> dict[str, Any]:
        """
        Return integration execution statistics.
        """

        return {
            "name": self._name,
            "processors": len(self._processors),
            "executions": self._executions,
            "success": self._success,
            "failures": self._failures,
        }

    def status(self) -> dict[str, Any]:
        """
        Return integration status.
        """

        return {
            "processors": len(self._processors),
            "active": bool(self._processors),
            "valid": self.validate_chain(),
        }

    def reset(self) -> "MetricProcessorIntegration":
        """
        Reset runtime statistics while preserving configuration.
        """

        self._executions = 0
        self._success = 0
        self._failures = 0

        self._last_result = None
        self._last_error = None

        return self

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __len__(self) -> int:
        return len(self._processors)

    def __iter__(self):
        return iter(self._processors)

    def __contains__(self, processor: Any) -> bool:
        return processor in self._processors

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
            f"MetricProcessorIntegration("
            f"name={self._name!r}, "
            f"processors={len(self._processors)}, "
            f"executions={self._executions}, "
            f"success={self._success}, "
            f"failures={self._failures}"
            f")"
        )

    def __str__(self) -> str:
        return self._name