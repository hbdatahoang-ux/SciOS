def interference(
    *,
    amplitude_i: float,
    amplitude_j: float,
    coupling: float,
    compatibility: float,
    cos_phase: float,
) -> float:
    return (
        2
        * coupling
        * amplitude_i
        * amplitude_j
        * compatibility
        * cos_phase
    )
