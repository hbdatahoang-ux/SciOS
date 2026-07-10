# tool_stage.py
# Tool Stage cho SciOS Cognitive Core - Pipeline

from typing import Any, Dict
from scios.cognitive_core.pipeline.stage import BaseStage

class ToolStage(BaseStage):
    """
    ToolStage chịu trách nhiệm gọi và tích hợp các công cụ bên ngoài vào pipeline.
    Nó có thể wrap một tool callable hoặc một đối tượng có method execute.
    """

    def __init__(self, name: str = "tool_stage", tool: Any | None = None) -> None:
        self.name = name
        # tool có thể là một hàm, class, hoặc API client
        self.tool = tool

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gọi tool để xử lý dữ liệu.
        """
        if not self.tool:
            # Default: không có tool, chỉ gắn nhãn
            data["tool_result"] = "No tool configured"
        else:
            if callable(self.tool):
                data["tool_result"] = self.tool(data)
            elif hasattr(self.tool, "execute"):
                data["tool_result"] = self.tool.execute(data)
            else:
                raise TypeError(f"Tool cho stage '{self.name}' không hợp lệ.")
        return data

    def summary(self) -> Dict[str, Any]:
        """
        Trả về thông tin stage.
        """
        return {
            "stage": self.name,
            "tool": getattr(self.tool, "__name__", type(self.tool).__name__)
            if self.tool else "none"
        }
