# base.py
# Base Sensor class cho SciOS Cognitive Core

from typing import Dict, Any

class BaseSensor:
    """
    BaseSensor là lớp cơ sở cho tất cả các loại cảm biến.
    Nó định nghĩa interface chung:
    - initialize(): khởi tạo cảm biến
    - read(): đọc dữ liệu từ cảm biến
    - shutdown(): tắt cảm biến
    """

    def __init__(self, sensor_id: str, sensor_type: str):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.active = False

    def initialize(self) -> None:
        """Khởi tạo cảm biến."""
        self.active = True
        print(f"Sensor {self.sensor_id} ({self.sensor_type}) initialized.")

    def read(self) -> Dict[str, Any]:
        """Đọc dữ liệu từ cảm biến (placeholder)."""
        if not self.active:
            raise RuntimeError("Sensor chưa được khởi tạo.")
        return {"sensor_id": self.sensor_id, "data": None}

    def shutdown(self) -> None:
        """Tắt cảm biến."""
        self.active = False
        print(f"Sensor {self.sensor_id} shutdown.")

    def to_dict(self) -> Dict[str, Any]:
        """Chuẩn hóa trạng thái cảm biến dưới dạng dict."""
        return {
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type,
            "active": self.active
        }
