# extractor.py
# Video Feature Extractor cho SciOS Cognitive Core

import cv2
import numpy as np
from typing import Dict, List

class VideoExtractor:
    """
    VideoExtractor chịu trách nhiệm trích xuất đặc trưng từ frame video:
    - Histogram màu
    - Optical Flow (chuyển động)
    - CNN features (placeholder)
    """

    def __init__(self, method: str = "histogram"):
        self.method = method

    def extract_features(self, frames: List[np.ndarray]) -> np.ndarray:
        """
        Trích xuất đặc trưng từ danh sách frame.

        Args:
            frames (List[np.ndarray]): danh sách frame video

        Returns:
            np.ndarray: đặc trưng đã trích xuất
        """
        if self.method == "histogram":
            # Tính histogram màu trung bình cho tất cả frame
            histograms = []
            for frame in frames:
                hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8],
                                    [0, 256, 0, 256, 0, 256])
                histograms.append(cv2.normalize(hist, hist).flatten())
            return np.mean(histograms, axis=0)

        elif self.method == "optical_flow":
            # Tính optical flow giữa các frame liên tiếp (placeholder)
            flows = []
            prev_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
            for frame in frames[1:]:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                flow = cv2.calcOpticalFlowFarneback(prev_gray, gray,
                                                    None, 0.5, 3, 15, 3, 5, 1.2, 0)
                flows.append(np.mean(flow))
                prev_gray = gray
            return np.array([np.mean(flows)])

        elif self.method == "cnn":
            # Placeholder cho CNN feature extractor
            return np.array([0.0])

        else:
            return np.array([])

    def to_dict(self, frames: List[np.ndarray]) -> Dict:
        """Chuẩn hóa output dưới dạng dict."""
        features = self.extract_features(frames)
        return {"video_features": features.tolist()}
