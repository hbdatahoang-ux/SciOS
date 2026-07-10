# pdf.py
# PDF Loader & Processor cho SciOS Cognitive Core

import fitz  # PyMuPDF
from typing import Dict, List

class PDFProcessor:
    """
    PDFProcessor chịu trách nhiệm:
    - Nạp file PDF
    - Trích xuất text từ các trang
    - Trích xuất metadata (số trang, tiêu đề, tác giả)
    """

    def __init__(self):
        pass

    def load_pdf(self, file_path: str) -> fitz.Document:
        """Nạp file PDF từ đường dẫn."""
        return fitz.open(file_path)

    def extract_text(self, doc: fitz.Document) -> List[str]:
        """Trích xuất text từ tất cả các trang."""
        texts = []
        for page in doc:
            texts.append(page.get_text())
        return texts

    def extract_metadata(self, doc: fitz.Document) -> Dict:
        """Trích xuất metadata từ PDF."""
        meta = doc.metadata
        return {
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
            "page_count": doc.page_count
        }

    def to_dict(self, file_path: str) -> Dict:
        """Chuẩn hóa output dưới dạng dict."""
        doc = self.load_pdf(file_path)
        texts = self.extract_text(doc)
        metadata = self.extract_metadata(doc)
        return {"texts": texts, "metadata": metadata}
