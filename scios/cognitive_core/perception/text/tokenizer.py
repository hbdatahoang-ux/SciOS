# tokenizer.py
# Text Tokenizer cho SciOS Cognitive Core

import re
from typing import List, Dict

class TextTokenizer:
    """
    TextTokenizer chịu trách nhiệm tách text thành token.
    Có thể mở rộng bằng regex, NLP libraries (spaCy, NLTK, HuggingFace).
    """

    def __init__(self, language: str = "vi"):
        self.language = language

    def tokenize(self, text: str) -> List[str]:
        """
        Tách text thành token cơ bản bằng regex.
        
        Args:
            text (str): chuỗi đầu vào
        
        Returns:
            List[str]: danh sách token
        """
        # Regex đơn giản: tách theo khoảng trắng và ký tự đặc biệt
        tokens = re.findall(r"\w+|\S", text)
        return tokens

    def to_dict(self, text: str) -> Dict:
        """
        Trả về kết quả tokenization dưới dạng dict.
        """
        tokens = self.tokenize(text)
        return {"tokens": tokens}
