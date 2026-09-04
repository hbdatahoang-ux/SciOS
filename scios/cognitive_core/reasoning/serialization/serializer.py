"""Serialization for the Reasoning subsystem."""

from uuid import UUID

from ..core.problem import ReasoningProblem
from ..core.result import ReasoningResult
from ..core.step import ReasoningStep
from ..core.types import ReasoningType


class ReasoningSerializer:
    """Serialize and deserialize reasoning results."""

    def serialize(self, result: ReasoningResult) -> dict:
        """Convert a ReasoningResult into a dictionary."""
        if not isinstance(result, ReasoningResult):
            raise TypeError("result must be a ReasoningResult")

        return {
            "id": str(result.id),
            "problem": {
                "id": str(result.problem.id),
                "query": result.problem.query,
                "context": dict(result.problem.context),
                "reasoning_type": result.problem.reasoning_type.value,
            },
            "steps": [
                {
                    "id": str(step.id),
                    "description": step.description,
                    "reasoning_type": step.reasoning_type.value,
                    "input": step.input,
                    "output": step.output,
                    "metadata": dict(step.metadata),
                }
                for step in result.steps
            ],
            "conclusion": result.conclusion,
            "accepted": result.accepted,
            "metadata": dict(result.metadata),
        }

    def deserialize(self, data: dict) -> ReasoningResult:
        """Convert a dictionary into a ReasoningResult."""
        if not isinstance(data, dict):
            raise TypeError("data must be a dict")

        problem_data = data["problem"]

        problem = ReasoningProblem(
            query=problem_data["query"],
            context=dict(problem_data["context"]),
            reasoning_type=ReasoningType(problem_data["reasoning_type"]),
            id=UUID(problem_data["id"]),
        )

        steps = [
            ReasoningStep(
                description=step_data["description"],
                reasoning_type=ReasoningType(step_data["reasoning_type"]),
                input=step_data["input"],
                output=step_data["output"],
                metadata=dict(step_data["metadata"]),
                id=UUID(step_data["id"]),
            )
            for step_data in data["steps"]
        ]

        return ReasoningResult(
            problem=problem,
            steps=steps,
            conclusion=data["conclusion"],
            accepted=data["accepted"],
            metadata=dict(data["metadata"]),
            id=UUID(data["id"]),
        )


__all__ = [
    "ReasoningSerializer",
]
