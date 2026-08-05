from __future__ import annotations

from .options import LegalAction


def validate_choice(actions: tuple[LegalAction, ...], index: int) -> LegalAction:
    for action in actions:
        if action.index == index:
            return action
    raise ValueError(f"Action index {index} is not in the server-provided legal actions")
