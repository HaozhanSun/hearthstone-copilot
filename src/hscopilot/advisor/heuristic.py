from __future__ import annotations

from .base import Advice
from hscopilot.legality.options import LegalAction
from hscopilot.perception.snapshot import GameSnapshot


class HeuristicAdvisor:
    """Zero-cost baseline. It can only select an index supplied by the server."""

    def advise(self, snapshot: GameSnapshot, legal_actions: tuple[LegalAction, ...]) -> Advice:
        if not legal_actions:
            raise ValueError("No legal actions were supplied")
        action = legal_actions[0]
        return Advice(action.index, 0.1, "Baseline: selected the first server-provided legal action.")
