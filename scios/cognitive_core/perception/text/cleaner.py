# cleaner.py
# Text Cleaner cho SciOS Cognitive Core

import re
from typing import List, Dict

class TextCleaner:
    """
    TextCleaner chịu trách nhiệm làm sạch token:
    - Loại bỏ ký tự thừa
    - Chuẩn hóa chữ hoa/thường
    - Loại bỏ stopwords (nếu có)
    - Giữ lại token hợp lệ
    """

    def __init__(self, stopwords: List[str] = None):
        self.stopwords = set(stopwords or [])

    def clean_tokens(self, tokens: List[str]) -> List[str]:
        """
        Làm sạch danh sách token.

        Args:
            tokens (List[str]): danh sách token thô

        Returns:
            List[str]: danh sách token đã làm sạch
        """
        cleaned = []
        for t in tokens:
            # Loại bỏ ký tự không phải chữ/số
            token = re.sub(r"[^\w]", "", t).lower()
            if token and token not in self.stopwords:
                cleaned.append(token)
        return cleaned

    def to_dict(self, tokens: List[str]) -> Dict:
        """
        Trả về kết quả cleaning dưới dạng dict.
        """
        return {"clean_tokens": self.clean_tokens(tokens)}
