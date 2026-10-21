"""
SciOS-NG Runtime Metrics Pipeline Integration

Integration layer for composing and executing metric middleware pipelines.

SciOS-NG v0.2
"""

from __future__ import annotations

from typing import Any, Iterable


# ==============================================================
# MetricPipelineIntegration
# ==============================================================


class MetricPipelineIntegration:
    """
    Integration layer for the Metrics Middleware Pipeline subsystem.

    Responsibilities
    ----------------
    - Compose multiple middleware pipelines
    - Execute pipelines in deterministic order
    - Process individual metrics
    - Process batches of metrics
    - Validate pipeline chains
    - Track integration statistics
    """

    def __init__(
        self,
        pipelines: Iterable[Any] | None = None,
        name: str = "MetricPipelineIntegration",
        description: str = "",
    ) -> None:

        self._name = name
        self._description = description

        self._pipelines: list[Any] = []

        self._executions = 0
        self._success = 0
        self._failures = 0

        self._last_result: Any = None
        self._last_error: Exception | None = None

        if pipelines is not None:
            for pipeline in pipelines:
                self.add_pipeline(pipeline)

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
    def pipelines_count(self) -> int:
        return len(self._pipelines)

    @property
    def last_result(self) -> Any:
        return self._last_result

    @property
    def last_error(self) -> Exception | None:
        return self._last_error

    # ==========================================================
    # Pipeline Management
    # ==========================================================

    def add_pipeline(
        self,
        pipeline: Any,
    ) -> "MetricPipelineIntegration":
        """
        Add a pipeline to the ordered integration chain.
        """

        if pipeline is None:
            raise ValueError(
                "pipeline must not be None"
            )

        if not (
            callable(pipeline)
            or hasattr(pipeline, "execute")
            or hasattr(pipeline, "process")
            or hasattr(pipeline, "run")
        ):
            raise TypeError(
                "pipeline must be callable or expose "
                "execute(), process(), or run()"
            )

        self._pipelines.append(pipeline)

        return self

    def remove_pipeline(
        self,
        pipeline: Any,
    ) -> "MetricPipelineIntegration":
        """
        Remove a pipeline if present.
        """

        if pipeline in self._pipelines:
            self._pipelines.remove(pipeline)

        return self

    def clear_pipelines(
        self,
    ) -> "MetricPipelineIntegration":
        """
        Remove all registered pipelines.
        """

        self._pipelines.clear()

        return self

    def pipelines(self) -> list[Any]:
        """
        Return a copy of the pipeline chain.
        """

        return list(self._pipelines)

    def get_pipeline(
        self,
        index: int,
    ) -> Any:
        """
        Return a pipeline at a specific position.
        """

        return self._pipelines[index]

    # ==========================================================
    # Execution
    # ==========================================================

    def execute(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute all registered pipelines sequentially.

        Each pipeline receives the result produced by
        the previous pipeline.
        """

        result = metric

        try:

            for pipeline in self._pipelines:

                result = self._execute_pipeline(
                    pipeline,
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
        Execute the complete pipeline chain for multiple metrics.
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
    # Pipeline Execution
    # ==========================================================

    @staticmethod
    def _execute_pipeline(
        pipeline: Any,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute one pipeline according to its public API.

        Preference order:
            execute()
            process()
            run()
            callable
        """

        if hasattr(pipeline, "execute"):
            return pipeline.execute(
                metric,
                **kwargs,
            )

        if hasattr(pipeline, "process"):
            return pipeline.process(
                metric,
                **kwargs,
            )

        if hasattr(pipeline, "run"):
            return pipeline.run(
                metric,
                **kwargs,
            )

        if callable(pipeline):
            return pipeline(
                metric,
                **kwargs,
            )

        raise TypeError(
            "Pipeline does not expose a supported execution API"
        )

    # ==========================================================
    # Validation
    # ==========================================================

    def validate_chain(self) -> bool:
        """
        Validate that all registered pipelines expose
        a supported execution API.
        """

        for pipeline in self._pipelines:

            if not (
                callable(pipeline)
                or hasattr(pipeline, "execute")
                or hasattr(pipeline, "process")
                or hasattr(pipeline, "run")
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
            "pipelines": len(self._pipelines),
            "executions": self._executions,
            "success": self._success,
            "failures": self._failures,
        }

    def status(self) -> dict[str, Any]:
        """
        Return integration status.
        """

        return {
            "pipelines": len(self._pipelines),
            "active": bool(self._pipelines),
            "valid": self.validate_chain(),
        }

    def reset(
        self,
    ) -> "MetricPipelineIntegration":
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
        return len(self._pipelines)

    def __iter__(self):
        return iter(self._pipelines)

    def __contains__(
        self,
        pipeline: Any,
    ) -> bool:
        return pipeline in self._pipelines

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
            f"MetricPipelineIntegration("
            f"name={self._name!r}, "
            f"pipelines={len(self._pipelines)}, "
            f"executions={self._executions}, "
            f"success={self._success}, "
            f"failures={self._failures}"
            f")"
        )

    def __str__(self) -> str:
        return self._name