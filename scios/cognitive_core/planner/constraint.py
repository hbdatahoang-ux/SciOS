# scios/cognitive_core/planner/constraint.py

from typing import Any, Dict

class Constraint:
    """
    Constraint: biểu diễn một ràng buộc đơn lẻ.
    Ví dụ: deadline, resource limit, budget, logical condition.
    """

    def __init__(self, name: str, value: Any, constraint_type: str = "generic"):
        self.name = name
        self.value = value
        self.constraint_type = constraint_type

    def is_satisfied(self, context: Dict[str, Any]) -> bool:
        """
        Kiểm tra xem constraint có được thỏa mãn trong context không.
        Skeleton: chỉ kiểm tra key-value đơn giản.
        """
        return context.get(self.name) == self.value

    def __repr__(self) -> str:
        return f"<Constraint {self.name}={self.value} type={self.constraint_type}>"


class ConstraintSet:
    """
    ConstraintSet: tập hợp nhiều Constraint.
    Dùng để kiểm tra tính khả thi của kế hoạch hoặc Task.
    """

    def __init__(self):
        self.constraints: Dict[str, Constraint] = {}

    def add_constraint(self, constraint: Constraint) -> None:
        """Thêm một constraint vào tập hợp."""
        self.constraints[constraint.name] = constraint

    def is_satisfied(self, context: Dict[str, Any]) -> bool:
        """Kiểm tra xem tất cả constraint đều thỏa mãn trong context."""
        return all(c.is_satisfied(context) for c in self.constraints.values())

    def __repr__(self) -> str:
        return f"<ConstraintSet size={len(self.constraints)}>"
