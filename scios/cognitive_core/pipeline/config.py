# config.py
# Runtime Config cho SciOS Cognitive Core - Pipeline

from typing import Any, Dict

class RuntimeConfig:
    """
    RuntimeConfig quản lý cấu hình động cho CognitivePipeline.
    Cho phép định nghĩa, tải, và cập nhật các tham số runtime.
    """

    def __init__(self, initial: Dict[str, Any] | None = None) -> None:
        # Cấu hình mặc định
        self._config: Dict[str, Any] = {
            "logging": True,
            "confidence_threshold": 0.5,
            "max_stages": 10,
            "enable_embeddings": True,
        }
        if initial:
            self._config.update(initial)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Lấy giá trị cấu hình theo key.
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Cập nhật giá trị cấu hình.
        """
        self._config[key] = value

    def update(self, new_config: Dict[str, Any]) -> None:
        """
        Cập nhật nhiều cấu hình cùng lúc.
        """
        self._config.update(new_config)

    def to_dict(self) -> Dict[str, Any]:
        """
        Xuất toàn bộ cấu hình dưới dạng dict.
        """
        return dict(self._config)

    def summary(self) -> Dict[str, Any]:
        """
        Trả về thông tin tóm tắt cấu hình runtime.
        """
        return {
            "logging": self._config.get("logging"),
            "confidence_threshold": self._config.get("confidence_threshold"),
            "max_stages": self._config.get("max_stages"),
            "enable_embeddings": self._config.get("enable_embeddings"),
        }
