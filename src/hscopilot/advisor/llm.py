from __future__ import annotations

from hscopilot.legality.options import LegalAction
from hscopilot.perception.snapshot import GameSnapshot
from .base import Advice


def constrained_prompt(snapshot: GameSnapshot, actions: tuple[LegalAction, ...]) -> str:
    return "Return JSON with action_index chosen from this list only: " + str([a.to_dict() for a in actions])


def advice_from_index(index: int, actions: tuple[LegalAction, ...], rationale: str = "") -> Advice:
    if index not in {action.index for action in actions}:
        raise ValueError("Advisor index is not legal")
    return Advice(index, 0.0, rationale)
