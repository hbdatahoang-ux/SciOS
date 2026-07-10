# scios/cognitive_core/tool_use/permission.py

"""
SciOS Permission Manager
========================

Quản lý quyền truy cập cho các Tool.
"""

from typing import Dict, Any


class PermissionManager:
    """
    PermissionManager kiểm soát quyền truy cập tool.
    """

    def __init__(self) -> None:
        # Bảng quyền mặc định: tool_name -> danh sách hành động cho phép
        self.permissions: Dict[str, set] = {
            "filesystem": {"read", "write"},   # không cho phép delete
            "web": {"get"},                    # chỉ cho phép GET request
            "calculator": {"evaluate"},        # chỉ cho phép tính toán
        }

    def grant(self, tool_name: str, action: str) -> None:
        """
        Cấp quyền cho tool.
        """
        if tool_name not in self.permissions:
            self.permissions[tool_name] = set()
        self.permissions[tool_name].add(action)

    def revoke(self, tool_name: str, action: str) -> None:
        """
        Thu hồi quyền của tool.
        """
        if tool_name in self.permissions and action in self.permissions[tool_name]:
            self.permissions[tool_name].remove(action)

    def check(self, tool_name: str, request: Dict[str, Any]) -> bool:
        """
        Kiểm tra request có được phép không.
        """
        action = request.get("action") or request.get("operation")
        if not action:
            return False

        allowed = self.permissions.get(tool_name, set())
        return action in allowed

    def list_permissions(self, tool_name: str) -> set:
        """
        Liệt kê quyền hiện có của tool.
        """
        return self.permissions.get(tool_name, set())
