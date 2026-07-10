# factory.py
# Factory cho SciOS Cognitive Core Perception

from typing import Optional
from .registry import InputRegistry
from .base import BasePerceptor

class PerceptorFactory:
    """
    PerceptorFactory tạo Perceptor instance dựa trên modality.
    Nó sử dụng InputRegistry để tra cứu class và khởi tạo đối tượng.
    """

    def __init__(self, registry: Optional[InputRegistry] = None):
        self.registry = registry or InputRegistry()

    def create(self, modality: str) -> BasePerceptor:
        """
        Tạo Perceptor instance cho modality cụ thể.

        Args:
            modality (str): loại dữ liệu ("text", "image", "audio", "video", "document", "sensor")

        Returns:
            BasePerceptor: instance xử lý input tương ứng
        """
        perceptor_cls = self.registry.get(modality)
        if not perceptor_cls:
            raise ValueError(f"Không tìm thấy Perceptor cho modality: {modality}")
        return perceptor_cls()
