# registry.py
# Input Registry cho SciOS Cognitive Core

from typing import Dict, Type
from .base import BasePerceptor

class InputRegistry:
    """
    InputRegistry lưu trữ mapping giữa modality và Perceptor class.
    Đây là nơi đăng ký và quản lý tất cả các Perceptor.
    """

    def __init__(self):
        # mapping: modality -> Perceptor class
        self._registry: Dict[str, Type[BasePerceptor]] = {}

    def register(self, modality: str, perceptor_cls: Type[BasePerceptor]) -> None:
        """
        Đăng ký một Perceptor cho modality cụ thể.

        Args:
            modality (str): loại dữ liệu ("text", "image", "audio", "video", "document", "sensor")
            perceptor_cls (Type[BasePerceptor]): class kế thừa BasePerceptor
        """
        if not issubclass(perceptor_cls, BasePerceptor):
            raise TypeError("Perceptor phải kế thừa BasePerceptor")
        self._registry[modality] = perceptor_cls

    def get(self, modality: str) -> Type[BasePerceptor]:
        """
        Lấy Perceptor class dựa trên modality.

        Args:
            modality (str): loại dữ liệu

        Returns:
            Type[BasePerceptor]: class xử lý input tương ứng
        """
        return self._registry.get(modality)

    def available_modalities(self) -> Dict[str, Type[BasePerceptor]]:
        """
        Trả về danh sách tất cả modality đã đăng ký.
        """
        return self._registry
