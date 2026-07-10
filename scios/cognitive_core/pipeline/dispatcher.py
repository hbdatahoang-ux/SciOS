# dispatcher.py
# Stage Dispatcher cho SciOS Cognitive Core - Pipeline

from typing import Any, Dict, Callable, List

class StageDispatcher:
    """
    StageDispatcher chịu trách nhiệm:
    - Quản lý danh sách các stage (hàm hoặc đối tượng có method process)
    - Chạy dữ liệu qua từng stage theo thứ tự
    - Trả về kết quả cuối cùng sau khi tất cả stage đã xử lý
    """

    def __init__(self, name: str = "stage_dispatcher") -> None:
        self.name = name
        self.stages: List[Callable[[Dict[str, Any]], Dict[str, Any]]] = []

    def add_stage(self, stage: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """
        Thêm một stage vào dispatcher.
        Stage có thể là hàm hoặc đối tượng có method process(data).
        """
        self.stages.append(stage)

    def clear_stages(self) -> None:
        """Xóa toàn bộ stages đã đăng ký."""
        self.stages.clear()

    def dispatch(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chạy dữ liệu qua toàn bộ stages.
        Args:
            data (Dict): dữ liệu đầu vào
        Returns:
            Dict: dữ liệu đã xử lý cuối cùng
        """
        result = data
        for stage in self.stages:
            if callable(stage):
                result = stage(result)
            elif hasattr(stage, "process"):
                result = stage.process(result)
            else:
                raise TypeError(f"Stage {stage} không hợp lệ.")
        return result

    def summary(self) -> Dict[str, Any]:
        """Trả về thông tin các stages đã đăng ký."""
        return {
            "dispatcher": self.name,
            "stages": [getattr(s, "__name__", type(s).__name__) for s in self.stages]
        }
