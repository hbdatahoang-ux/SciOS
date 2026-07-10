"""
SciOS Tool Engine
=================

Quản lý toàn bộ vòng đời của một tool call:
- Đăng ký và tra cứu tool
- Kiểm tra request (validator)
- Kiểm soát quyền (permission)
- Thực thi trong sandbox
- Gọi executor để chạy tool
"""

from typing import Any, Dict
from scios.cognitive_core.tool_use.registry import ToolRegistry
from scios.cognitive_core.tool_use.validator import ToolValidator
from scios.cognitive_core.tool_use.permission import PermissionManager
from scios.cognitive_core.tool_use.sandbox import ToolSandbox
from scios.cognitive_core.tool_use.executor import ToolExecutor


class ToolEngine:
    """
    ToolEngine quản lý toàn bộ vòng đời của một tool call.
    """

    def __init__(self) -> None:
        self.registry = ToolRegistry()
        self.validator = ToolValidator()
        self.permission = PermissionManager()
        self.sandbox = ToolSandbox()
        self.executor = ToolExecutor()

    def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Nhận request, chọn tool phù hợp và thực thi.
        """
        tool_name = request.get("tool")
        tool = self.registry.get(tool_name)

        if not tool:
            return {"status": "error", "message": f"Tool '{tool_name}' not found"}

        if not self.validator.validate(request):
            return {"status": "error", "message": "Invalid request"}

        if not self.permission.check(tool_name, request):
            return {"status": "error", "message": "Permission denied"}

        try:
            # Thực thi trong sandbox để đảm bảo an toàn
            result = self.sandbox.run(lambda: self.executor.execute(tool, request))
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
