"""
SciOS-NG Runtime Metrics Middleware Integration

Integration helpers for composing and executing metric middleware.

SciOS-NG v0.2
"""

from __future__ import annotations

from typing import Any, Iterable


# ==============================================================
# MetricMiddlewareIntegration
# ==============================================================


class MetricMiddlewareIntegration:
    """
    Integration layer for the Metrics Middleware subsystem.

    Responsibilities
    ----------------
    - Compose multiple middleware components
    - Execute middleware in deterministic order
    - Process individual metrics
    - Process batches of metrics
    - Validate middleware chains
    - Track integration statistics
    """

    def __init__(
        self,
        middlewares: Iterable[Any] | None = None,
        name: str = "MetricMiddlewareIntegration",
        description: str = "",
    ) -> None:

        self._name = name
        self._description = description

        self._middlewares: list[Any] = []

        self._executions = 0
        self._success = 0
        self._failures = 0

        self._last_result: Any = None
        self._last_error: Exception | None = None

        if middlewares is not None:
            for middleware in middlewares:
                self.add_middleware(middleware)

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
    def middlewares_count(self) -> int:
        return len(self._middlewares)

    @property
    def last_result(self) -> Any:
        return self._last_result

    @property
    def last_error(self) -> Exception | None:
        return self._last_error

    # ==========================================================
    # Middleware Management
    # ==========================================================

    def add_middleware(
        self,
        middleware: Any,
    ) -> "MetricMiddlewareIntegration":
        """
        Add middleware to the ordered execution chain.
        """

        if middleware is None:
            raise ValueError(
                "middleware must not be None"
            )

        if not self._is_supported(middleware):
            raise TypeError(
                "middleware must be callable or expose "
                "execute(), process(), or run()"
            )

        self._middlewares.append(middleware)

        return self

    def remove_middleware(
        self,
        middleware: Any,
    ) -> "MetricMiddlewareIntegration":
        """
        Remove middleware if present.
        """

        if middleware in self._middlewares:
            self._middlewares.remove(middleware)

        return self

    def clear_middlewares(
        self,
    ) -> "MetricMiddlewareIntegration":
        """
        Remove all middleware components.
        """

        self._middlewares.clear()

        return self

    def middlewares(self) -> list[Any]:
        """
        Return a copy of the middleware chain.
        """

        return list(self._middlewares)

    def get_middleware(
        self,
        index: int,
    ) -> Any:
        """
        Return middleware at the specified index.
        """

        return self._middlewares[index]

    # ==========================================================
    # Execution
    # ==========================================================

    def execute(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute the complete middleware chain.

        The output of each middleware becomes the input
        of the next middleware.
        """

        result = metric

        try:
            for middleware in self._middlewares:
                result = self._execute_middleware(
                    middleware,
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

            self._last_result = None
            self._last_error = exc

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
        Execute the middleware chain for multiple metrics.
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
    # Middleware Execution
    # ==========================================================

    @staticmethod
    def _execute_middleware(
        middleware: Any,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute one middleware using its public API.

        Preference order:
            execute()
            process()
            run()
            callable
        """

        if hasattr(middleware, "execute"):
            return middleware.execute(
                metric,
                **kwargs,
            )

        if hasattr(middleware, "process"):
            return middleware.process(
                metric,
                **kwargs,
            )

        if hasattr(middleware, "run"):
            return middleware.run(
                metric,
                **kwargs,
            )

        if callable(middleware):
            return middleware(
                metric,
                **kwargs,
            )

        raise TypeError(
            "Middleware does not expose a supported execution API"
        )

    @staticmethod
    def _is_supported(
        middleware: Any,
    ) -> bool:
        """
        Return whether middleware exposes a supported API.
        """

        return (
            callable(middleware)
            or hasattr(middleware, "execute")
            or hasattr(middleware, "process")
            or hasattr(middleware, "run")
        )

    # ==========================================================
    # Validation
    # ==========================================================

    def validate_chain(self) -> bool:
        """
        Validate all registered middleware components.
        """

        return all(
            self._is_supported(middleware)
            for middleware in self._middlewares
        )

    # ==========================================================
    # Diagnostics
    # ==========================================================

    def statistics(self) -> dict[str, Any]:
        """
        Return integration execution statistics.
        """

        return {
            "name": self._name,
            "middlewares": len(self._middlewares),
            "executions": self._executions,
            "success": self._success,
            "failures": self._failures,
        }

    def status(self) -> dict[str, Any]:
        """
        Return integration status.
        """

        return {
            "middlewares": len(self._middlewares),
            "active": bool(self._middlewares),
            "valid": self.validate_chain(),
        }

    def reset(
        self,
    ) -> "MetricMiddlewareIntegration":
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
        return len(self._middlewares)

    def __iter__(self):
        return iter(self._middlewares)

    def __contains__(
        self,
        middleware: Any,
    ) -> bool:
        return middleware in self._middlewares

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
            f"MetricMiddlewareIntegration("
            f"name={self._name!r}, "
            f"middlewares={len(self._middlewares)}, "
            f"executions={self._executions}, "
            f"success={self._success}, "
            f"failures={self._failures}"
            f")"
        )

    def __str__(self) -> str:
        return self._name