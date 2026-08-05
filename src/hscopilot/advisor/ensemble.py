from .base import Advice


def choose_best(candidates: list[Advice]) -> Advice:
    if not candidates:
        raise ValueError("No advisor candidates")
    return max(candidates, key=lambda advice: advice.confidence)
