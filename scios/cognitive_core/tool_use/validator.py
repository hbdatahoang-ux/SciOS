"""
SciOS Cognitive Tool Validator.

Validates semantic tool-use requests before they cross into runtime
execution infrastructure.
"""

from collections.abc import Mapping
from typing import Any

from .request import ToolRequest


class ToolValidator:
    """
    Validate canonical Cognitive ToolUse requests.

    Accepted inputs:
    - ToolRequest
    - Mapping[str, Any]

    This validator is semantic only. It does not resolve or execute tools,
    enforce runtime authorization, or provide sandboxing.
    """

    def __init__(self) -> None:
        pass

    def validate(
        self,
        request: ToolRequest | Mapping[str, Any],
    ) -> bool:
        """
        Validate a semantic tool request.

        Legacy `operation` is accepted only for mapping inputs.
        Canonical `action` takes precedence when both are present.
        """
        if isinstance(request, ToolRequest):
            tool_name = request.tool
            action = request.action
            params = request.params
            metadata = request.metadata
            payload = request.to_dict()

        elif isinstance(request, Mapping):
            tool_name = request.get("tool")
            action = request.get("action")

            if not action:
                action = request.get("operation")

            params = request.get("params", {})
            metadata = request.get("metadata", {})
            payload = dict(request)

        else:
            return False

        if not isinstance(tool_name, str) or not tool_name.strip():
            return False

        if not isinstance(action, str) or not action.strip():
            return False

        if not isinstance(params, dict):
            return False

        if not isinstance(metadata, dict):
            return False

        expr = str(payload)

        forbidden = [
            "__import__",
            "os.system",
            "subprocess",
            "eval",
            "exec",
        ]

        if any(item in expr for item in forbidden):
            return False

        return True
