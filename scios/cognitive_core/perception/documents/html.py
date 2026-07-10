# html.py
# HTML Loader & Processor cho SciOS Cognitive Core

from bs4 import BeautifulSoup
from typing import Dict

class HTMLProcessor:
    """
    HTMLProcessor chịu trách nhiệm:
    - Nạp file hoặc chuỗi HTML
    - Trích xuất plain text
    - Trích xuất metadata (title, headings, links)
    """

    def __init__(self):
        pass

    def load_html(self, file_path: str) -> str:
        """Nạp nội dung từ file HTML."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def parse_html(self, html_text: str) -> BeautifulSoup:
        """Phân tích HTML bằng BeautifulSoup."""
        return BeautifulSoup(html_text, "html.parser")

    def extract_text(self, soup: BeautifulSoup) -> str:
        """Trích xuất plain text từ HTML."""
        return soup.get_text(separator=" ", strip=True)

    def extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """Trích xuất metadata cơ bản từ HTML."""
        title = soup.title.string if soup.title else ""
        headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])]
        links = [a["href"] for a in soup.find_all("a", href=True)]
        return {"title": title, "headings": headings, "links": links}

    def to_dict(self, file_path: str) -> Dict:
        """Chuẩn hóa output dưới dạng dict."""
        html_text = self.load_html(file_path)
        soup = self.parse_html(html_text)
        text = self.extract_text(soup)
        metadata = self.extract_metadata(soup)
        return {"html_text": html_text, "plain_text": text, "metadata": metadata}
