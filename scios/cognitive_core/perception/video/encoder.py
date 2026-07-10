# encoder.py
# Video Encoder cho SciOS Cognitive Core

import numpy as np
from typing import Dict

class VideoEncoder:
    """
    VideoEncoder chịu trách nhiệm mã hóa đặc trưng video thành embedding vector.
    Có thể mở rộng bằng mô hình học sâu (I3D, SlowFast, ViViT).
    """

    def __init__(self, method: str = "simple"):
        self.method = method

    def encode(self, frames: np.ndarray) -> np.ndarray:
        """
        Mã hóa danh sách frame thành embedding vector.

        Args:
            frames (np.ndarray): danh sách frame hoặc đặc trưng đã trích xuất

        Returns:
            np.ndarray: vector embedding
        """
        if self.method == "simple":
            # Placeholder: tính trung bình pixel để tạo embedding
            mean_frame = np.mean(frames, axis=(0, 1, 2))  # trung bình theo chiều H,W,C
            std_frame = np.std(frames, axis=(0, 1, 2))
            return np.array([mean_frame, std_frame])
        else:
            # Có thể mở rộng sang mô hình học sâu
            return np.array([0.0])

    def to_dict(self, frames: np.ndarray) -> Dict:
        """
        Chuẩn hóa output dưới dạng dict.
        """
        embedding = self.encode(frames)
        return {"video_embedding": embedding.tolist()}
