# loader.py
# Audio Loader cho SciOS Cognitive Core

import os
import requests
import soundfile as sf
from io import BytesIO
from typing import Dict, Any

class AudioLoader:
    """
    AudioLoader chịu trách nhiệm nạp dữ liệu âm thanh từ nhiều nguồn:
    - File path (.wav, .mp3, .flac)
    - URL
    - Bytes/stream
    """

    def __init__(self):
        pass

    def load_from_file(self, file_path: str) -> Dict:
        """Nạp audio từ file path."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Không tìm thấy file: {file_path}")
        audio, sample_rate = sf.read(file_path)
        return {"audio": audio, "sample_rate": sample_rate}

    def load_from_url(self, url: str) -> Dict:
        """Nạp audio từ URL."""
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Không thể tải audio từ URL: {url}")
        audio, sample_rate = sf.read(BytesIO(response.content))
        return {"audio": audio, "sample_rate": sample_rate}

    def load_from_bytes(self, data: bytes) -> Dict:
        """Nạp audio từ dữ liệu bytes."""
        audio, sample_rate = sf.read(BytesIO(data))
        return {"audio": audio, "sample_rate": sample_rate}

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
