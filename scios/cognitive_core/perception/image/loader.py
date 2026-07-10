# loader.py
# Image Loader cho SciOS Cognitive Core

from typing import Dict, Any
from PIL import Image
import requests
from io import BytesIO
import os

class ImageLoader:
    """
    ImageLoader chịu trách nhiệm nạp dữ liệu hình ảnh từ nhiều nguồn:
    - File path
    - URL
    - Bytes/stream
    """

    def __init__(self):
        pass

    def load_from_file(self, file_path: str) -> Dict:
        """Nạp ảnh từ file path."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Không tìm thấy file: {file_path}")
        img = Image.open(file_path)
        return {"image": img}

    def load_from_url(self, url: str) -> Dict:
        """Nạp ảnh từ URL."""
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Không thể tải ảnh từ URL: {url}")
        img = Image.open(BytesIO(response.content))
        return {"image": img}

    def load_from_bytes(self, data: bytes) -> Dict:
        """Nạp ảnh từ dữ liệu bytes."""
        img = Image.open(BytesIO(data))
        return {"image": img}

    def to_dict(self, source: Any, source_type: str = "file") -> Dict:
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
