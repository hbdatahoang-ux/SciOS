# scios/cognitive_core/tool_use/dispatcher.py

"""
SciOS Tool Dispatcher
=====================

Điều phối việc gọi tool sau khi đã được chọn.
"""

from typing import Dict, Any
from scios.cognitive_core.tool_use.base import Tool
from scios.cognitive_core.tool_use.executor import ToolExecutor


class ToolDispatcher:
    """
    ToolDispatcher nhận tool đã chọn và request,
    sau đó gọi ToolExecutor để thực thi.
    """

    def __init__(self) -> None:
        self.executor = ToolExecutor()

    def dispatch(self, tool: Tool, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Điều phối việc gọi tool.
        - Nhận tool đã chọn và request.
        - Gọi executor để thực thi.
        - Trả về response chuẩn hóa.
        """
        if not tool:
            return {"status": "error", "message": "No tool provided"}

        try:
            result = self.executor.execute(tool, request)
            return {"status": "success", "tool": tool.name, "result": result}
        except Exception as e:
            return {"status": "error", "tool": tool.name, "message": str(e)}
