from __future__ import annotations

from enum import StrEnum


class Scene(StrEnum):
    UNKNOWN = "unknown"
    MENU = "menu"
    MULLIGAN = "mulligan"
    PLAY = "play"
    BATTLEGROUNDS_SHOP = "battlegrounds_shop"
    ARENA = "arena"


class SceneFSM:
    def __init__(self) -> None:
        self.state = Scene.UNKNOWN

    def observe(self, line: str) -> Scene:
        text = line.lower()
        patterns = (
            (Scene.MULLIGAN, ("mulligan", "choose starting")),
            (Scene.BATTLEGROUNDS_SHOP, ("battlegrounds", "recruit phase", "shop phase")),
            (Scene.ARENA, ("arena", "draft")),
            (Scene.PLAY, ("gameplay", "game state", "play screen")),
            (Scene.MENU, ("main menu", "collection", "lobby")),
        )
        for state, needles in patterns:
            if any(needle in text for needle in needles):
                self.state = state
                break
        return self.state
