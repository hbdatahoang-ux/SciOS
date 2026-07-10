# loader.py
# Video Loader cho SciOS Cognitive Core

import cv2
import os
import requests
import numpy as np
from typing import Dict
from io import BytesIO

class VideoLoader:
    """
    VideoLoader chịu trách nhiệm nạp dữ liệu video từ nhiều nguồn:
    - File path (.mp4, .avi, .mov)
    - URL
    - Bytes/stream
    """

    def __init__(self):
        pass

    def load_from_file(self, file_path: str) -> Dict:
        """Nạp video từ file path."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Không tìm thấy file: {file_path}")
        cap = cv2.VideoCapture(file_path)
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        cap.release()
        return {"frames": frames, "frame_count": len(frames)}

    def load_from_url(self, url: str) -> Dict:
        """Nạp video từ URL (placeholder)."""
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Không thể tải video từ URL: {url}")
        # Placeholder: chưa hiện thực decode trực tiếp từ bytes
        return {"video_bytes": BytesIO(response.content)}

    def load_from_bytes(self, data: bytes) -> Dict:
        """Nạp video từ dữ liệu bytes (placeholder)."""
        return {"video_bytes": BytesIO(data)}

    def to_dict(self, source: str, source_type: str = "file") -> Dict:
        """
        Chuẩn hóa output dưới dạng dict.
        source_type: "file", "url", "bytes"
        """
        if source_type == "file":
            return self.load_from_file(source)
        elif source_type == "url":
            return self.load_from_url(source)
        elif source_type == "bytes":
            return self.load_from_bytes(source)
        else:
            raise ValueError(f"Loại nguồn không hợp lệ: {source_type}")
