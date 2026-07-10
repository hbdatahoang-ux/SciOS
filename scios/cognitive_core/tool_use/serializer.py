# scios/cognitive_core/tool_use/serializer.py

"""
SciOS Serializer
================

Quản lý import/export dữ liệu tool:
- Chuẩn hóa request/response/history thành JSON
- Lưu ra file
- Nạp lại từ file
"""

import json
from typing import Any, Dict, List


class ToolSerializer:
    """
    ToolSerializer chịu trách nhiệm serialize/deserialize dữ liệu tool.
    """

    @staticmethod
    def to_json(data: Dict[str, Any]) -> str:
        """
        Chuyển dict thành JSON string.
        """
        return json.dumps(data, ensure_ascii=False, indent=2)

    @staticmethod
    def from_json(json_str: str) -> Dict[str, Any]:
        """
        Chuyển JSON string thành dict.
        """
        return json.loads(json_str)

    @staticmethod
    def save_to_file(data: Dict[str, Any], filename: str) -> None:
        """
        Lưu dữ liệu ra file JSON.
        """
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_from_file(filename: str) -> Dict[str, Any]:
        """
        Nạp dữ liệu từ file JSON.
        """
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def export_history(history: List[Dict[str, Any]], filename: str) -> None:
        """
        Xuất toàn bộ history ra file JSON.
        """
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    @staticmethod
    def import_history(filename: str) -> List[Dict[str, Any]]:
        """
        Nạp history từ file JSON.
        """
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
