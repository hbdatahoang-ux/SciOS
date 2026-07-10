# scios/cognitive_core/memory/serializer.py

import json
from typing import List
from .record import MemoryRecord

class MemorySerializer:
    """
    MemorySerializer: hỗ trợ import/export memory records.
    Dùng để lưu trữ lâu dài hoặc chia sẻ giữa các hệ thống.
    """

    @staticmethod
    def export(records: List[MemoryRecord], filepath: str) -> None:
        """Xuất danh sách MemoryRecord ra file JSON."""
        data = [rec.to_dict() for rec in records]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def import_records(filepath: str) -> List[MemoryRecord]:
        """Nhập danh sách MemoryRecord từ file JSON."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [MemoryRecord.from_dict(rec) for rec in data]
