from __future__ import annotations
from typing import List

from .request import ToolRequest
from .response import ToolResponse
from .stage import ToolStage


class ToolPipeline:
    """
    Sequential Tool Pipeline.

    Executes ToolStages one by one and returns
    the final ToolResponse.
    """

    def __init__(self) -> None:
        self.stages: List[ToolStage] = []

    # -----------------------------------------------------
    # Pipeline management
    # -----------------------------------------------------

    def add_stage(self, stage: ToolStage) -> None:
        self.stages.append(stage)

    # -----------------------------------------------------
    # Execution
    # -----------------------------------------------------

    def run(self, request: ToolRequest) -> ToolResponse:
        """
        Run all stages sequentially.
        Return the ToolResponse of the last stage.
        Raise RuntimeError if any stage fails.
        """
        response: ToolResponse | None = None

        for stage in self.stages:
            response = stage.run(request)

            # Nếu stage báo lỗi, để nó raise RuntimeError
            if stage.status == "error":
                raise RuntimeError(stage.message or "Stage failed")

        if response is None:
            return ToolResponse.success(
                tool=request.tool,
                result=None,
            )

        return response

    # -----------------------------------------------------
    # Reset
    # -----------------------------------------------------

    def reset(self) -> None:
        for stage in self.stages:
            stage.reset()

    # -----------------------------------------------------
    # Serialization
    # -----------------------------------------------------

    def to_dict(self):
        return {
            "stages": [stage.to_dict() for stage in self.stages]
        }

    # -----------------------------------------------------
    # Magic
    # -----------------------------------------------------

    def __len__(self) -> int:
        return len(self.stages)

    def __repr__(self) -> str:
        return f"<ToolPipeline stages={len(self.stages)}>"
