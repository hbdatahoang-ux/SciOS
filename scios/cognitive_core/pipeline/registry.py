# registry.py
# Stage Registry cho SciOS Cognitive Core - Pipeline

from typing import Any, Dict, Callable

class StageRegistry:
    """
    StageRegistry chịu trách nhiệm:
    - Quản lý mapping giữa tên stage và processor
    - Cho phép đăng ký, hủy đăng ký, và truy xuất stage
    - Hỗ trợ pipeline gọi stage theo tên
    """

    def __init__(self) -> None:
        self._registry: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}

    def register(self, name: str, stage: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """
        Đăng ký một stage vào registry.
        Args:
            name (str): tên stage
            stage (Callable): hàm hoặc đối tượng có method process
        """
        self._registry[name] = stage

    def unregister(self, name: str) -> None:
        """Hủy đăng ký một stage."""
        if name in self._registry:
            del self._registry[name]

    def get(self, name: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        Lấy stage theo tên.
        Args:
            name (str): tên stage
        Returns:
            Callable: stage đã đăng ký
        """
        if name not in self._registry:
            raise KeyError(f"Stage '{name}' chưa được đăng ký.")
        return self._registry[name]

    def list_stages(self) -> Dict[str, str]:
        """
        Trả về danh sách các stage đã đăng ký.
        """
        return {name: getattr(stage, "__name__", type(stage).__name__) for name, stage in self._registry.items()}
