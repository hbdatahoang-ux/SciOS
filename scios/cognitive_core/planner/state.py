# scios/cognitive_core/planner/state.py

from typing import Dict

class PlannerState:
    """
    PlannerState: quản lý trạng thái của Planner.
    Theo dõi vòng đời kế hoạch: initialized → planning → validating → executing → completed/failed.
    """

    def __init__(self):
        self.current_state: str = "initialized"
        self.metadata: Dict[str, str] = {}

    def set_state(self, state: str) -> None:
        """Cập nhật trạng thái hiện tại của Planner."""
        self.current_state = state
        self.metadata["last_state"] = state

    def get_state(self) -> str:
        """Trả về trạng thái hiện tại."""
        return self.current_state

    def is_terminal(self) -> bool:
        """Kiểm tra xem trạng thái đã kết thúc chưa (completed hoặc failed)."""
        return self.current_state in ["completed", "failed"]

    def __repr__(self) -> str:
        return f"<PlannerState current='{self.current_state}'>"
