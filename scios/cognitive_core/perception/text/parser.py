# parser.py
# TextPerceptor cho SciOS Cognitive Core

from typing import Dict, Any
from ..base import BasePerceptor

class TextPerceptor(BasePerceptor):
    """
    TextPerceptor xử lý dữ liệu đầu vào dạng text.
    Nó kế thừa BasePerceptor và hiện thực các bước load, parse, clean, normalize, embed.
    """

    def load(self, raw_input: Any, metadata: Dict = None) -> Dict:
        """Nạp dữ liệu text thô."""
        return {"text": str(raw_input)}

    def parse(self, processed: Dict) -> Dict:
        """Phân tích text thành token đơn giản."""
        text = processed.get("text", "")
        tokens = text.split()
        return {"tokens": tokens}

    def clean(self, processed: Dict) -> Dict:
        """Làm sạch token (loại bỏ ký tự thừa, chuẩn hóa)."""
        tokens = processed.get("tokens", [])
        cleaned = [t.strip().lower() for t in tokens if t.strip()]
        return {"clean_tokens": cleaned}

    def normalize(self, processed: Dict) -> Dict:
        """Chuẩn hóa text thành dạng thống nhất."""
        normalized = " ".join(processed.get("clean_tokens", []))
        return {"normalized_text": normalized}

    def extract_entities(self, processed: Dict):
        """Trích xuất entity cơ bản (ví dụ: từ viết hoa)."""
        tokens = processed.get("tokens", [])
        entities = [{"entity": t} for t in tokens if t.istitle()]
        return entities

    def extract_relations(self, processed: Dict):
        """Trích xuất quan hệ đơn giản (placeholder)."""
        return []

    def embed(self, processed: Dict) -> Dict:
        """Sinh embedding đơn giản (ví dụ: độ dài text)."""
        normalized = processed.get("normalized_text", "")
        return {"text_embedding": [len(normalized)]}

    def confidence(self, processed: Dict) -> float:
        """Đánh giá độ tin cậy (placeholder)."""
        return 0.95 if processed.get("normalized_text") else 0.5
