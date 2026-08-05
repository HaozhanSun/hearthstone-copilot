"""Optional metadata/cache boundary; kept separate from card definitions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ArchetypeStats:
    archetype: str
    games: int = 0
    win_rate: float = 0.0
