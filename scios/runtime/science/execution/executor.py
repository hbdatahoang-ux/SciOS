# ==============================================================================
# SciOS Runtime Science
# Scientific Executor
# ==============================================================================

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from scios.runtime.science.experiment.models import (
    Experiment,
    Observation,
)
from scios.runtime.science.synthetic_world.models import (
    WorldResult,
    WorldState,
)

from .context import ExecutionContext
from .errors import (
    ExecutionCancelledError,
    ExecutionFailedError,
    InvalidExecutionError,
    WorldExecutionError,
)
from .result import ExecutionResult, ExecutionStatus


# ==============================================================================
# Executor
# ==============================================================================


class ScientificExecutor:
    """
    Deterministic orchestrator for the scientific execution loop.

    Public contract
    ---------------

        Experiment
            ↓
        execute()
            ↓
        ExecutionContext
            ↓
        execute_context()
            ↓
        SyntheticWorld
            ↓
        WorldResult
            ↓
        Observation
            ↓
        ExecutionResult

    Semantic boundary
    -----------------

    The executor executes experiments.

    It does NOT:

        - evaluate hypotheses
        - create Knowledge
        - mutate Hypothesis
        - mutate Experiment
        - interpret scientific meaning
        - perform probabilistic inference
        - perform fuzzy comparison

    Hypothesis evaluation belongs exclusively to Evaluator.
    """

    # ==========================================================================
    # Construction
    # ==========================================================================

    def __init__(
        self,
        world: Any | None = None,
    ) -> None:
        """
        Create a scientific executor.

        Parameters
        ----------
        world:
            Optional world implementation.

            If omitted, a default SyntheticWorld is created lazily.
        """

        if world is None:
            world = self._create_default_world()

        self._validate_world(world)

        self.world = world

        # Number of successfully completed executions.
        #
        # Important:
        #   - validation failures do not increment it
        #   - world failures do not increment it
        #   - invalid world results do not increment it
        #   - cancelled executions do not increment it
        self._execution_count = 0

    # ==========================================================================
    # Public properties
    # ==========================================================================

    @property
    def execution_count(self) -> int:
        """
        Number of successfully completed executions.
        """
        return self._execution_count

    # ==========================================================================
    # Public API
    # ==========================================================================

    def execute(
        self,
        experiment_or_context: (
            Experiment
            | ExecutionContext
            | Mapping[str, Any]
            | None
        ) = None,
        experiment: (
            Experiment
            | Mapping[str, Any]
            | None
        ) = None,
    ) -> ExecutionResult:
        """
        Execute an experiment.

        Preferred API
        -------------

            executor.execute(experiment)

        Compatibility API
        ------------------

        An ExecutionContext may also be supplied directly:

            executor.execute(context)

        The latter delegates directly to ``execute_context()``.

        A legacy two-argument form is also accepted:

            executor.execute(context, experiment)

        In that form the supplied experiment is validated against the
        context before execution.

        Returns
        -------
        ExecutionResult
            Immutable result containing the produced Observation.
        """

        # ------------------------------------------------------------------
        # No argument
        # ------------------------------------------------------------------

        if experiment_or_context is None:
            raise InvalidExecutionError(
                "experiment must not be None"
            )

        # ------------------------------------------------------------------
        # Context-based execution
        # ------------------------------------------------------------------

        if isinstance(
            experiment_or_context,
            ExecutionContext,
        ):
            context = experiment_or_context

            if experiment is not None:
                self._validate_experiment(
                    experiment,
                    context,
                )

            return self.execute_context(context)

        # ------------------------------------------------------------------
        # Experiment-based execution
        # ------------------------------------------------------------------

        if experiment is not None:
            raise InvalidExecutionError(
                "experiment argument is only valid when the first "
                "argument is an ExecutionContext"
            )

        normalized_experiment = self._normalize_experiment(
            experiment_or_context,
        )

        context = self._create_context(
            normalized_experiment,
        )

        return self.execute_context(context)

    # --------------------------------------------------------------------------
    # Context API
    # --------------------------------------------------------------------------

    def execute_context(
        self,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Execute an existing ExecutionContext.

        This is the canonical execution primitive.

        Contract
        --------

            ExecutionContext → ExecutionResult

        The context is never mutated.
        """

        self._validate_context(context)

        experiment = self._get_context_experiment(
            context,
        )

        self._validate_experiment(
            experiment,
            context,
        )

        parameters = self._resolve_context_parameters(
            context,
            experiment,
        )

        try:
            # --------------------------------------------------------------
            # World execution
            # --------------------------------------------------------------

            world_result = self._execute_world(
                parameters,
            )

            # --------------------------------------------------------------
            # Observation boundary
            # --------------------------------------------------------------

            observation = self._create_observation(
                context=context,
                world_result=world_result,
            )

            # --------------------------------------------------------------
            # Result boundary
            # --------------------------------------------------------------

            result = ExecutionResult(
                execution_id=context.execution_id,
                experiment_id=context.experiment_id,
                hypothesis_id=context.hypothesis_id,
                status=ExecutionStatus.COMPLETED,
                observation=observation,
                created_at=context.created_at,
                metadata=context.metadata,
            )

        except ExecutionCancelledError:
            raise

        except WorldExecutionError:
            raise

        except InvalidExecutionError:
            raise

        except Exception as exc:
            raise ExecutionFailedError(
                f"scientific execution failed: {exc}"
            ) from exc

        # ------------------------------------------------------------------
        # Commit execution count only after complete success.
        # ------------------------------------------------------------------

        self._execution_count += 1

        return result

    # ==========================================================================
    # Context creation
    # ==========================================================================

    @staticmethod
    def _create_context(
        experiment: Experiment,
    ) -> ExecutionContext:
        """
        Create a fresh immutable execution context for an experiment.
        """

        return ExecutionContext(
            experiment=experiment,
            state=WorldState(),
        )

    # ==========================================================================
    # Experiment normalization
    # ==========================================================================

    @staticmethod
    def _normalize_experiment(
        experiment: Experiment | Mapping[str, Any],
    ) -> Experiment:
        """
        Normalize an Experiment or mapping into Experiment.

        The original object is never mutated.
        """

        if isinstance(experiment, Experiment):
            return experiment

        if not isinstance(experiment, Mapping):
            raise InvalidExecutionError(
                "experiment must be an Experiment or mapping"
            )

        experiment_id = experiment.get("id")

        if (
            not isinstance(experiment_id, str)
            or not experiment_id.strip()
        ):
            raise InvalidExecutionError(
                "experiment must provide a non-empty string id"
            )

        hypothesis_id = experiment.get(
            "hypothesis_id",
        )

        if (
            hypothesis_id is not None
            and not isinstance(hypothesis_id, str)
        ):
            raise InvalidExecutionError(
                "experiment hypothesis_id must be a string or None"
            )

        parameters = experiment.get(
            "parameters",
            {},
        )

        if parameters is None:
            parameters = {}

        if not isinstance(parameters, Mapping):
            raise InvalidExecutionError(
                "experiment parameters must be a mapping"
            )

        metadata = experiment.get(
            "metadata",
            {},
        )

        if metadata is None:
            metadata = {}

        if not isinstance(metadata, Mapping):
            raise InvalidExecutionError(
                "experiment metadata must be a mapping"
            )

        return Experiment(
            id=experiment_id,
            hypothesis_id=hypothesis_id,
            parameters=parameters,
            metadata=metadata,
        )

    # ==========================================================================
    # Validation
    # ==========================================================================

    @staticmethod
    def _validate_context(
        context: ExecutionContext,
    ) -> None:
        """
        Validate an execution context.
        """

        if not isinstance(
            context,
            ExecutionContext,
        ):
            raise InvalidExecutionError(
                "context must be an ExecutionContext"
            )

    @staticmethod
    def _get_context_experiment(
        context: ExecutionContext,
    ) -> Experiment:
        """
        Extract the experiment from an ExecutionContext.
        """

        experiment = getattr(
            context,
            "experiment",
            None,
        )

        if not isinstance(
            experiment,
            Experiment,
        ):
            raise InvalidExecutionError(
                "execution context must provide an Experiment"
            )

        return experiment

    @staticmethod
    def _validate_experiment(
        experiment: Experiment | Mapping[str, Any],
        context: ExecutionContext,
    ) -> None:
        """
        Validate experiment identity against execution context.
        """

        if isinstance(experiment, Experiment):
            if experiment.id != context.experiment_id:
                raise InvalidExecutionError(
                    "experiment id does not match execution context"
                )

            if (
                experiment.hypothesis_id
                != context.hypothesis_id
            ):
                raise InvalidExecutionError(
                    "experiment hypothesis_id does not match "
                    "execution context"
                )

            return

        if isinstance(experiment, Mapping):
            experiment_id = experiment.get("id")

            if (
                not isinstance(experiment_id, str)
                or not experiment_id.strip()
            ):
                raise InvalidExecutionError(
                    "experiment must provide a non-empty string id"
                )

            if experiment_id != context.experiment_id:
                raise InvalidExecutionError(
                    "experiment id does not match execution context"
                )

            hypothesis_id = experiment.get(
                "hypothesis_id",
            )

            if (
                hypothesis_id is not None
                and hypothesis_id != context.hypothesis_id
            ):
                raise InvalidExecutionError(
                    "experiment hypothesis_id does not match "
                    "execution context"
                )

            return

        raise InvalidExecutionError(
            "experiment must be an Experiment or mapping"
        )

    # ==========================================================================
    # Parameter resolution
    # ==========================================================================

    @staticmethod
    def _resolve_context_parameters(
        context: ExecutionContext,
        experiment: Experiment,
    ) -> Mapping[str, Any]:
        """
        Resolve experiment parameters without mutation.
        """

        parameters = experiment.parameters

        if not isinstance(
            parameters,
            Mapping,
        ):
            raise InvalidExecutionError(
                "experiment parameters must be a mapping"
            )

        return parameters

    # ==========================================================================
    # World
    # ==========================================================================

    @staticmethod
    def _create_default_world() -> Any:
        """
        Create the default SyntheticWorld.

        Import is intentionally local so that execution package import
        remains lightweight and avoids unnecessary circular imports.
        """

        from scios.runtime.science.synthetic_world import (
            SyntheticWorld,
        )

        return SyntheticWorld()

    @staticmethod
    def _validate_world(
        world: Any,
    ) -> None:
        """
        Validate the world execution boundary.
        """

        if world is None:
            raise InvalidExecutionError(
                "world must not be None"
            )

        if not hasattr(world, "run") and not hasattr(
            world,
            "execute",
        ):
            raise InvalidExecutionError(
                "world must provide run() or execute()"
            )

    def _execute_world(
        self,
        parameters: Mapping[str, Any],
    ) -> WorldResult:
        """
        Execute the world exactly once.

        Preferred world API:

            world.run(parameters)

        Compatibility API:

            world.execute(parameters)
        """

        try:
            run = getattr(
                self.world,
                "run",
                None,
            )

            if callable(run):
                result = run(parameters)

            else:
                execute = getattr(
                    self.world,
                    "execute",
                    None,
                )

                if not callable(execute):
                    raise WorldExecutionError(
                        "world must provide callable run() "
                        "or execute()"
                    )

                result = execute(parameters)

        except ExecutionCancelledError:
            raise

        except WorldExecutionError:
            raise

        except Exception as exc:
            raise WorldExecutionError(
                f"synthetic world execution failed: {exc}"
            ) from exc

        if not isinstance(
            result,
            WorldResult,
        ):
            raise WorldExecutionError(
                "synthetic world must return WorldResult"
            )

        if not isinstance(
            result.values,
            Mapping,
        ):
            raise WorldExecutionError(
                "world result values must be a mapping"
            )

        return result

    # ==========================================================================
    # Observation
    # ==========================================================================

    @staticmethod
    def _create_observation(
        context: ExecutionContext,
        world_result: WorldResult,
    ) -> Observation:
        """
        Convert WorldResult into the scientific Observation boundary.
        """

        values = world_result.values

        if not isinstance(
            values,
            Mapping,
        ):
            raise WorldExecutionError(
                "world result values must be a mapping"
            )

        return Observation(
            id=f"{context.execution_id}:observation",
            experiment_id=context.experiment_id,
            values=values,
            observed_at=context.created_at,
            metadata={
                "execution_id": context.execution_id,
                "hypothesis_id": context.hypothesis_id,
            },
        )


# ==============================================================================
# Compatibility Alias
# ==============================================================================

Executor = ScientificExecutor


__all__ = [
    "ScientificExecutor",
    "Executor",
]