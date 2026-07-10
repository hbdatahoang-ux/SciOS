# extractor.py
# Text Extractor cho SciOS Cognitive Core

import re
from typing import List, Dict

class TextExtractor:
    """
    TextExtractor chịu trách nhiệm trích xuất entity và relation từ text.
    Có thể mở rộng bằng NLP libraries (spaCy, Stanza, HuggingFace).
    """

    def __init__(self, language: str = "vi"):
        self.language = language

    def extract_entities(self, text: str) -> List[Dict]:
        """
        Trích xuất entity cơ bản từ text.
        Ví dụ: từ viết hoa, số, hoặc pattern regex.

        Args:
            text (str): chuỗi đầu vào

        Returns:
            List[Dict]: danh sách entity
        """
        entities = []
        # Regex tìm từ viết hoa (giả định là tên riêng)
        for match in re.finditer(r"\b[A-ZĐ][a-zà-ỹÀ-Ỹ]+\b", text):
            entities.append({"entity": match.group(), "type": "ProperNoun"})
        # Regex tìm số
        for match in re.finditer(r"\b\d+\b", text):
            entities.append({"entity": match.group(), "type": "Number"})
        return entities

    def extract_relations(self, tokens: List[str]) -> List[Dict]:
        """
        Trích xuất quan hệ đơn giản giữa các entity.
        Ví dụ: quan hệ "X liên quan đến Y" dựa trên khoảng cách token.

        Args:
            tokens (List[str]): danh sách token

        Returns:
            List[Dict]: danh sách quan hệ
        """
        relations = []
        for i in range(len(tokens) - 1):
            relations.append({
                "relation": "adjacent",
                "source": tokens[i],
                "target": tokens[i+1]
            })
        return relations

    def to_dict(self, text: str, tokens: List[str]) -> Dict:
        """
        Trả về kết quả entity và relation dưới dạng dict.
        """
        return {
            "entities": self.extract_entities(text),
            "relations": self.extract_relations(tokens)
        }
