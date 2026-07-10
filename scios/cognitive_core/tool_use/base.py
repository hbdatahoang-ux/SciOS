# scios/cognitive_core/tool_use/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict

class Tool(ABC):
    """
    Abstract base class cho mọi Tool trong SciOS-NG.
    """

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Thực thi tool với một request chuẩn hóa.
        Phải trả về response chuẩn hóa.
        """
        pass

    @abstractmethod
    def validate(self, request: Dict[str, Any]) -> bool:
        """
        Kiểm tra request có hợp lệ cho tool này không.
        """
        pass

    def __repr__(self) -> str:
        return f"<Tool name={self.name}>"
