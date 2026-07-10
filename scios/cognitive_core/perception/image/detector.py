# detector.py
# Image Detector cho SciOS Cognitive Core

from typing import Dict, List, Tuple
from PIL import Image

class ImageDetector:
    """
    ImageDetector chịu trách nhiệm phát hiện đối tượng trong ảnh.
    Có thể mở rộng bằng các mô hình ML/DL (YOLO, Faster R-CNN, Detectron2).
    """

    def __init__(self, model: str = "mock"):
        # model: tên mô hình hoặc backend (placeholder)
        self.model = model

    def detect(self, img: Image.Image) -> List[Dict]:
        """
        Phát hiện đối tượng trong ảnh.
        
        Args:
            img (Image.Image): ảnh đầu vào
        
        Returns:
            List[Dict]: danh sách đối tượng với bounding box và nhãn
        """
        # Placeholder: giả lập phát hiện một đối tượng
        width, height = img.size
        detections = [
            {
                "label": "object",
                "confidence": 0.9,
                "bbox": (width//4, height//4, width//2, height//2)  # (x, y, w, h)
            }
        ]
        return detections

    def to_dict(self, img: Image.Image) -> Dict:
        """
        Trả về kết quả detection dưới dạng dict.
        """
        return {"detections": self.detect(img)}
