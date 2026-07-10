# markdown.py
# Markdown Loader & Processor cho SciOS Cognitive Core

import markdown
from typing import Dict

class MarkdownProcessor:
    """
    MarkdownProcessor chịu trách nhiệm:
    - Nạp file Markdown (.md)
    - Chuyển đổi sang HTML
    - Trích xuất plain text
    """

    def __init__(self):
        pass

    def load_markdown(self, file_path: str) -> str:
        """Nạp nội dung từ file Markdown."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def to_html(self, md_text: str) -> str:
        """Chuyển đổi Markdown sang HTML."""
        return markdown.markdown(md_text)

    def to_text(self, md_text: str) -> str:
        """Trích xuất plain text (loại bỏ cú pháp Markdown)."""
        # Placeholder: chỉ loại bỏ ký hiệu cơ bản
        return md_text.replace("#", "").replace("*", "").replace("`", "")

    def to_dict(self, file_path: str) -> Dict:
        """Chuẩn hóa output dưới dạng dict."""
        md_text = self.load_markdown(file_path)
        html = self.to_html(md_text)
        plain = self.to_text(md_text)
        return {"markdown_text": md_text, "html": html, "plain_text": plain}
