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

Python 3.11+
"""

from __future__ import annotations


from typing import Iterable, Any


from .context import ExecutionContext
from .stage import Stage



__all__ = [
    "Pipeline",
]



class Pipeline:
    """
    Sequential execution pipeline.

    Pipeline owns stages only.

    ExecutionEngine owns:
    - pipeline lifecycle
    - runtime state
    - global hooks
    - events
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
    def stages(
        self,
    ) -> tuple[Stage, ...]:

        return tuple(
            self._stages
        )



    @property
    def stage_count(
        self,
    ) -> int:

        return len(
            self._stages
        )



    # ==========================================================
    # Stage Management
    # ==========================================================

    def add_stage(
        self,
        stage: Stage,
    ) -> None:


        if stage not in self._stages:

            self._stages.append(
                stage
            )



    def remove_stage(
        self,
        stage: Stage,
    ) -> None:


        if stage in self._stages:

            self._stages.remove(
                stage
            )



    def clear(
        self,
    ) -> None:

        self._stages.clear()



    # ==========================================================
    # Execution
    # ==========================================================

    def execute(
        self,
        context: ExecutionContext,
    ) -> ExecutionContext:
        """
        Execute pipeline stages sequentially.

        Pipeline preserves existing logs.
        """

        if context is None:

            raise ValueError(
                "ExecutionContext is required"
            )



        for stage in self._stages:


            name = self._stage_name(
                stage
            )


            # ----------------------------------------------
            # Lifecycle event
            # ----------------------------------------------

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



                # ------------------------------------------
                # Capture stage output
                # ------------------------------------------

                self._capture_output(
                    context,
                    output,
                )



            except Exception as exc:


                context.add_event(
                    f"{name}.failed"
                )


                context.fail(
                    exc
                )


                raise



            context.add_event(
                f"{name}.completed"
            )



        return context



    def run(
        self,
        context: ExecutionContext,
    ) -> ExecutionContext:

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
        Store stage output into execution trace.

        Supported:

        str:
            "planner"

        dict:
            {"status":"success"}

        None:
            ignored
        """

        if output is None:

            return



        if isinstance(
            output,
            str,
        ):

            context.log(
                output
            )

            return



        if isinstance(
            output,
            dict,
        ):

            context.metadata.update(
                output
            )

            return



        context.log(
            str(output)
        )



    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _stage_name(
        stage: Stage,
    ) -> str:


        name = getattr(
            stage,
            "name",
            None,
        )


        if name:

            return name



        return stage.__class__.__name__



    # ==========================================================
    # Diagnostics
    # ==========================================================

    def summary(
        self,
    ) -> dict[str, object]:


        return {

            "stage_count":
                len(self._stages),


            "stages":
            [
                self._stage_name(stage)
                for stage in self._stages
            ],

        }



    # ==========================================================
    # Protocols
    # ==========================================================

    def __len__(
        self,
    ) -> int:

        return len(
            self._stages
        )



    def __iter__(
        self,
    ):

        return iter(
            self._stages
        )



    def __contains__(
        self,
        stage: Stage,
    ) -> bool:

        return stage in self._stages



    def __repr__(
        self,
    ) -> str:

        return (
            "Pipeline("
            f"stages={len(self._stages)}"
            ")"
        )