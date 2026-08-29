"""
SciOS Runtime Pipeline
======================

Pipeline orchestration layer.

Responsibilities
-----------------
- Maintain ordered execution stages
- Execute runtime stages sequentially
- Preserve execution context
- Capture stage outputs
- Emit stage lifecycle events

The Pipeline deliberately does NOT own execution lifecycle state.

ExecutionEngine owns:
- execution lifecycle
- runtime state
- global hooks
- scheduler coordination
- worker coordination
- runtime-level events

Pipeline owns only:
- ordered stage execution
- stage-level events
- stage output capture

Python 3.11+
"""

from __future__ import annotations

from typing import Any, Iterable

from .context import ExecutionContext
from .stage import Stage


__all__ = [
    "Pipeline",
]


class Pipeline:
    """
    Sequential execution pipeline.

    Pipeline owns stages only.

    ExecutionEngine owns the execution lifecycle.
    Therefore Pipeline must never call:

        context.start()
        context.finish()
        context.fail()

    A stage exception is recorded as a stage-level failure event
    and then re-raised to the caller. ExecutionEngine is responsible
    for converting that exception into the runtime-level failure state.
    """

    # ==========================================================
    # Construction
    # ==========================================================

    def __init__(
        self,
        stages: Iterable[Stage] | None = None,
    ) -> None:
        self._stages: list[Stage] = list(
            stages or []
        )

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def stages(self) -> tuple[Stage, ...]:
        """
        Return the registered stages as an immutable snapshot.
        """
        return tuple(self._stages)

    @property
    def stage_count(self) -> int:
        """
        Number of registered stages.
        """
        return len(self._stages)

    # ==========================================================
    # Stage Management
    # ==========================================================

    def add_stage(
        self,
        stage: Stage,
    ) -> None:
        """
        Add a stage if it is not already registered.

        Stage identity is preserved; duplicate stage objects are
        ignored.
        """
        if not isinstance(stage, Stage):
            raise TypeError(
                "stage must be an instance of Stage"
            )

        if stage not in self._stages:
            self._stages.append(stage)

    def remove_stage(
        self,
        stage: Stage,
    ) -> None:
        """
        Remove a registered stage.

        Missing stages are ignored.
        """
        if stage in self._stages:
            self._stages.remove(stage)

    def clear(self) -> None:
        """
        Remove all registered stages.
        """
        self._stages.clear()

    # ==========================================================
    # Execution
    # ==========================================================

    def execute(
        self,
        context: ExecutionContext,
    ) -> ExecutionContext:
        """
        Execute all stages sequentially.

        Contract
        --------
        - Context is preserved.
        - Stage order is preserved.
        - Each stage emits ``<StageName>.started``.
        - Successful stages emit ``<StageName>.completed``.
        - Failed stages emit ``<StageName>.failed``.
        - Stage exceptions are re-raised unchanged.
        - Pipeline does NOT mutate execution lifecycle state.

        In particular, this method never calls ``context.fail()``.
        Runtime-level failure handling belongs to ExecutionEngine.
        """
        if context is None:
            raise ValueError(
                "ExecutionContext is required"
            )

        if not isinstance(context, ExecutionContext):
            raise TypeError(
                "context must be an ExecutionContext"
            )

        for stage in self._stages:
            name = self._stage_name(stage)

            # --------------------------------------------------
            # Stage started
            # --------------------------------------------------

            context.add_event(
                f"{name}.started"
            )

            context.log(
                f"Executing stage: {name}"
            )

            try:
                output = stage.execute(
                    context
                )

                # --------------------------------------------------
                # Capture stage output
                # --------------------------------------------------

                self._capture_output(
                    context,
                    output,
                )

            except Exception:
                # --------------------------------------------------
                # Stage failure
                #
                # IMPORTANT:
                # Do not call context.fail() here.
                #
                # Pipeline owns stage lifecycle only.
                # ExecutionEngine owns execution lifecycle.
                # --------------------------------------------------

                context.add_event(
                    f"{name}.failed"
                )

                raise

            # --------------------------------------------------
            # Stage completed
            # --------------------------------------------------

            context.add_event(
                f"{name}.completed"
            )

        return context

    def run(
        self,
        context: ExecutionContext,
    ) -> ExecutionContext:
        """
        Alias for execute().
        """
        return self.execute(
            context
        )

    # ==========================================================
    # Output Handling
    # ==========================================================

    @staticmethod
    def _capture_output(
        context: ExecutionContext,
        output: Any,
    ) -> None:
        """
        Capture stage output.

        Supported output types
        ----------------------
        ``None``
            Ignored.

        ``str``
            Appended to execution logs.

        ``dict``
            Merged into context metadata.

        Other values
            Converted to string and appended to logs.

        A stage is still free to explicitly call
        ``context.set_result()`` or ``context.set_artifact()``.
        """
        if output is None:
            return

        if isinstance(output, str):
            context.log(output)
            return

        if isinstance(output, dict):
            context.metadata.update(output)
            return

        context.log(str(output))

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _stage_name(
        stage: Stage,
    ) -> str:
        """
        Resolve the stable display/event name of a stage.
        """
        name = getattr(
            stage,
            "name",
            None,
        )

        if name:
            return str(name)

        return stage.__class__.__name__

    # ==========================================================
    # Diagnostics
    # ==========================================================

    def summary(
        self,
    ) -> dict[str, object]:
        """
        Return a compact pipeline description.
        """
        return {
            "stage_count": len(self._stages),
            "stages": [
                self._stage_name(stage)
                for stage in self._stages
            ],
        }

    # ==========================================================
    # Protocols
    # ==========================================================

    def __len__(self) -> int:
        return len(self._stages)

    def __iter__(self):
        return iter(self._stages)

    def __contains__(
        self,
        stage: Stage,
    ) -> bool:
        return stage in self._stages

    def __repr__(self) -> str:
        return (
            "Pipeline("
            f"stages={len(self._stages)}"
            ")"
        )