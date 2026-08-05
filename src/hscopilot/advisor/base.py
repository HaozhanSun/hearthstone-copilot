from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from hscopilot.legality.options import LegalAction
from hscopilot.perception.snapshot import GameSnapshot


@dataclass(frozen=True)
class Advice:
    action_index: int
    confidence: float
    rationale: str


class Advisor(Protocol):
    def advise(self, snapshot: GameSnapshot, legal_actions: tuple[LegalAction, ...]) -> Advice: ...
