# dispatcher.py
# Dispatcher cho SciOS Cognitive Core - Perception

from typing import Dict, Any

class Dispatcher:
    """
    Dispatcher chịu trách nhiệm:
    - Quản lý mapping giữa modality và processor
    - Nhận dữ liệu đầu vào từ pipeline
    - Phân phối đến đúng processor theo modality
    """

    def __init__(self):
        # routes: {modality: processor}
        self.routes: Dict[str, Any] = {}

    def register(self, modality: str, processor: Any) -> None:
        """
        Đăng ký processor cho một modality.
        Args:
            modality (str): tên modality (video, documents, sensors, images…)
            processor (Any): đối tượng xử lý
        """
        self.routes[modality] = processor

    def unregister(self, modality: str) -> None:
        """Hủy đăng ký processor cho một modality."""
        if modality in self.routes:
            del self.routes[modality]

    def route(self, modality: str, data: Any) -> Dict[str, Any]:
        """
        Phân phối dữ liệu đến processor tương ứng.
        Args:
            modality (str): tên modality
            data (Any): dữ liệu đầu vào
        Returns:
            Dict[str, Any]: dữ liệu đã xử lý
        """
        if modality not in self.routes:
            raise ValueError(f"Unsupported modality: {modality}")

        processor = self.routes[modality]

        # Ưu tiên interface chuẩn hóa
        if hasattr(processor, "to_dict"):
            return processor.to_dict(data)
        elif hasattr(processor, "process"):
            return processor.process(data)
        elif callable(processor):
            return processor(data)
        else:
            raise TypeError(f"Processor for {modality} không hợp lệ.")

    def summary(self) -> Dict[str, Any]:
        """Trả về thông tin các routes đã đăng ký."""
        return {"routes": list(self.routes.keys())}
