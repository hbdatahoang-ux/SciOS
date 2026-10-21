import math


class Compatibility:
    def __init__(self, value: float) -> None:
        if not math.isfinite(value):
            raise ValueError("Compatibility must be finite")
        if not -1.0 <= value <= 1.0:
            raise ValueError("Compatibility must be in [-1, 1]")
        self.value = value


class Coupling:
    def __init__(self, value: float) -> None:
        if not math.isfinite(value):
            raise ValueError("Coupling must be finite")
        if value < 0.0:
            raise ValueError("Coupling must be non-negative")
        self.value = value
