# simulator.py
# Sensor Simulator cho SciOS Cognitive Core

import random
import time
from typing import Dict, Any

class SensorSimulator:
    """
    SensorSimulator chịu trách nhiệm:
    - Mô phỏng dữ liệu từ cảm biến (camera, audio, temperature, v.v.)
    - Cho phép kiểm thử pipeline perception mà không cần phần cứng thực
    """

    def __init__(self, sensor_type: str = "temperature", interval: float = 1.0):
        self.sensor_type = sensor_type
        self.interval = interval
        self.active = False
        self.latest_data = None

    def start(self) -> None:
        """Bắt đầu mô phỏng dữ liệu."""
        self.active = True
        print(f"Simulator for {self.sensor_type} started.")

    def generate_data(self) -> Any:
        """Sinh dữ liệu giả lập tùy theo loại cảm biến."""
        if self.sensor_type == "temperature":
            return round(random.uniform(20.0, 35.0), 2)  # °C
        elif self.sensor_type == "camera":
            return f"Frame_{random.randint(1,100)}"
        elif self.sensor_type == "audio":
            return f"AudioSample_{random.randint(1,100)}"
        else:
            return f"Data_{random.randint(1,100)}"

    def read(self) -> Dict[str, Any]:
        """Đọc dữ liệu mô phỏng mới nhất."""
        if not self.active:
            raise RuntimeError("Simulator chưa được khởi động.")
        self.latest_data = self.generate_data()
        time.sleep(self.interval)
        return {"sensor_type": self.sensor_type, "data": self.latest_data}

    def stop(self) -> None:
        """Dừng mô phỏng."""
        self.active = False
        print(f"Simulator for {self.sensor_type} stopped.")
