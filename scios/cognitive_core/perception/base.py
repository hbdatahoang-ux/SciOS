# base.py
# BasePerceptor cho SciOS Cognitive Core

from typing import Any, Dict, List

class BasePerceptor:
    """
    BasePerceptor là interface chung cho mọi Perceptor.
    Các class cụ thể (TextPerceptor, ImagePerceptor, AudioPerceptor, v.v.)
    sẽ kế thừa và hiện thực các phương thức này.
    """

    def load(self, raw_input: Any, metadata: Dict = None) -> Dict:
        """Nạp dữ liệu thô từ input (ví dụ: đọc file, lấy frame, stream)."""
        raise NotImplementedError

    def parse(self, processed: Dict) -> Dict:
        """Phân tích dữ liệu (ví dụ: tokenize text, decode image)."""
        raise NotImplementedError

    def clean(self, processed: Dict) -> Dict:
        """Làm sạch dữ liệu (ví dụ: loại bỏ noise, chuẩn hóa format)."""
        raise NotImplementedError

    def normalize(self, processed: Dict) -> Dict:
        """Chuẩn hóa dữ liệu (ví dụ: lowercasing text, resize image)."""
        raise NotImplementedError

    def extract_entities(self, processed: Dict) -> List[Dict]:
        """Trích xuất entity từ dữ liệu (ví dụ: tên, đối tượng, khái niệm)."""
        return []

    def extract_relations(self, processed: Dict) -> List[Dict]:
        """Trích xuất quan hệ giữa các entity."""
        return []

    def embed(self, processed: Dict) -> Dict:
        """Sinh embedding cho dữ liệu (text, image, audio, video)."""
        raise NotImplementedError

    def confidence(self, processed: Dict) -> float:
        """Tính toán độ tin cậy của kết quả perception."""
        return 1.0
