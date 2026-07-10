# scios/cognitive_core/tool_use/executor.py

"""
SciOS Tool Executor
===================

Thực thi tool đã chọn bằng cách gọi phương thức execute().
"""

from typing import Dict, Any
from scios.cognitive_core.tool_use.base import Tool


class ToolExecutor:
    """
    ToolExecutor chịu trách nhiệm gọi tool.execute(request).
    """

    def __init__(self) -> None:
        pass

    def execute(self, tool: Tool, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Thực thi tool đã chọn.
        - Gọi tool.validate() trước khi chạy.
        - Nếu hợp lệ → gọi tool.execute().
        - Nếu không hợp lệ → trả về lỗi.
        """
        if not tool.validate(request):
            return {"status": "error", "message": f"Invalid request for tool '{tool.name}'"}

        try:
            result = tool.execute(request)
            return {"status": "success", "tool": tool.name, "result": result}
        except Exception as e:
            return {"status": "error", "tool": tool.name, "message": str(e)}
