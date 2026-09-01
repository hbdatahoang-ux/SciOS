"""
SciOS Stage Registry
====================

Registry quản lý các stage của CognitivePipeline.

Responsibilities
-----------------
- Register cognitive stages
- Prevent duplicate stage names
- Retrieve stages by name
- Remove stages
- Enumerate registered stages
- Clear registry
- Provide mapping-like access
- Preserve plugin-loading extension point

Python 3.11+
"""

from __future__ import annotations

from typing import Any

from .stage import CognitiveStage


__all__ = [
    "StageRegistry",
]


class StageRegistry:
    """
    Registry quản lý toàn bộ CognitiveStage của SciOS.

    Registry giữ nguyên object stage được đăng ký; không tự động
    initialize hoặc execute stage.
    """

    def __init__(self) -> None:
        self._stages: dict[str, CognitiveStage] = {}

    # =========================================================
    # Registration
    # =========================================================

    def register(
        self,
        stage: CognitiveStage,
    ) -> CognitiveStage:
        """
        Đăng ký một stage.

        Parameters
        ----------
        stage:
            CognitiveStage cần đăng ký.

        Returns
        -------
        CognitiveStage
            Chính object vừa được đăng ký.

        Raises
        ------
        TypeError
            Nếu object không phải CognitiveStage.

        ValueError
            Nếu stage name rỗng hoặc đã tồn tại.
        """

        if not isinstance(stage, CognitiveStage):
            raise TypeError(
                "stage must be an instance of CognitiveStage"
            )

        name = stage.name

        if not isinstance(name, str):
            raise TypeError(
                "stage.name must be a string"
            )

        if not name:
            raise ValueError(
                "stage.name cannot be empty"
            )

        if name in self._stages:
            raise ValueError(
                f"stage already registered: {name!r}"
            )

        self._stages[name] = stage

        return stage

    # =========================================================
    # Removal
    # =========================================================

    def unregister(
        self,
        name: str,
    ) -> CognitiveStage | None:
        """
        Xóa stage theo tên.

        Returns
        -------
        CognitiveStage | None
            Stage đã được xóa, hoặc None nếu không tồn tại.
        """

        return self._stages.pop(name, None)

    # =========================================================
    # Lookup
    # =========================================================

    def get(
        self,
        name: str,
    ) -> CognitiveStage | None:
        """
        Lấy stage theo tên.

        Không raise exception nếu stage không tồn tại.
        """

        return self._stages.get(name)

    def __getitem__(
        self,
        name: str,
    ) -> CognitiveStage:
        """
        Truy cập stage bằng cú pháp registry[name].

        Raises
        ------
        KeyError
            Nếu stage không tồn tại.
        """

        return self._stages[name]

    def contains(
        self,
        name: str,
    ) -> bool:
        """Kiểm tra stage có được đăng ký hay không."""

        return name in self._stages

    def __contains__(
        self,
        name: str,
    ) -> bool:
        return self.contains(name)

    # =========================================================
    # Inspection
    # =========================================================

    @property
    def is_empty(self) -> bool:
        """Whether registry contains no stages."""

        return not self._stages

    def names(self) -> list[str]:
        """
        Trả về danh sách tên stage theo thứ tự đăng ký.
        """

        return list(self._stages.keys())

    def values(self) -> list[CognitiveStage]:
        """
        Trả về danh sách stage theo thứ tự đăng ký.
        """

        return list(self._stages.values())

    def items(
        self,
    ) -> list[tuple[str, CognitiveStage]]:
        """
        Trả về các cặp (name, stage) theo thứ tự đăng ký.
        """

        return list(self._stages.items())

    def all(self) -> dict[str, CognitiveStage]:
        """
        Trả về bản sao mapping nội bộ.

        Thay đổi mapping trả về không làm thay đổi registry.
        """

        return dict(self._stages)

    # =========================================================
    # Lifecycle
    # =========================================================

    def clear(self) -> None:
        """Xóa toàn bộ stage khỏi registry."""

        self._stages.clear()

    # =========================================================
    # Plugin Loading
    # =========================================================

    def load_plugins(
        self,
        path: str,
    ) -> None:
        """
        Extension point cho plugin stage.

        Hiện tại chưa thực hiện discovery/loading.
        """

        _ = path

    # =========================================================
    # Python Protocols
    # =========================================================

    def __len__(self) -> int:
        return len(self._stages)

    def __iter__(self):
        return iter(self._stages)

    def __repr__(self) -> str:
        return (
            f"<StageRegistry "
            f"count={len(self._stages)}>"
        )
