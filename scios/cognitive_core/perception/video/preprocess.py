# preprocess.py
# Video Preprocessor cho SciOS Cognitive Core

import cv2
import numpy as np
from typing import Dict, List

class VideoPreprocessor:
    """
    VideoPreprocessor chịu trách nhiệm xử lý frame video:
    - Resize về kích thước chuẩn
    - Normalize màu sắc
    - Thay đổi FPS (frame rate)
    """

    def __init__(self, target_size: tuple = (224, 224), normalize: bool = True, target_fps: int = None):
        self.target_size = target_size
        self.normalize = normalize
        self.target_fps = target_fps

    def resize_frames(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        """Resize tất cả frame về target_size."""
        return [cv2.resize(frame, self.target_size) for frame in frames]

    def normalize_frames(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        """Chuẩn hóa màu sắc (0–1)."""
        if not self.normalize:
            return frames
        return [frame.astype(np.float32) / 255.0 for frame in frames]

    def adjust_fps(self, frames: List[np.ndarray], original_fps: int) -> List[np.ndarray]:
        """Thay đổi FPS bằng cách lấy mẫu lại frame."""
        if not self.target_fps or self.target_fps >= original_fps:
            return frames
        step = int(original_fps / self.target_fps)
        return frames[::step]

    def preprocess(self, frames: List[np.ndarray], original_fps: int) -> Dict:
        """Thực hiện toàn bộ pipeline preprocess."""
        resized = self.resize_frames(frames)
        normalized = self.normalize_frames(resized)
        adjusted = self.adjust_fps(normalized, original_fps)
        return {"preprocessed_frames": adjusted, "frame_count": len(adjusted), "fps": self.target_fps or original_fps}
