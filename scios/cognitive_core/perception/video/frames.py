# frames.py
# Video Frames Handler cho SciOS Cognitive Core

import cv2
from typing import Dict, List

class VideoFrames:
    """
    VideoFrames chịu trách nhiệm:
    - Trích xuất frame từ video
    - Lấy keyframes (ví dụ mỗi N frame)
    - Quản lý danh sách frame để phục vụ pipeline perception
    """

    def __init__(self, step: int = 30):
        # step: khoảng cách giữa các frame được lấy (ví dụ mỗi 30 frame)
        self.step = step

    def extract_frames(self, video_path: str) -> List:
        """Trích xuất frame từ video theo step."""
        cap = cv2.VideoCapture(video_path)
        frames = []
        idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if idx % self.step == 0:
                frames.append(frame)
            idx += 1
        cap.release()
        return frames

    def to_dict(self, video_path: str) -> Dict:
        """Chuẩn hóa output dưới dạng dict."""
        frames = self.extract_frames(video_path)
        return {"frames": frames, "frame_count": len(frames)}
