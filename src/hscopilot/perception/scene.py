from __future__ import annotations

import re
from enum import StrEnum


class Scene(StrEnum):
    UNKNOWN = "unknown"
    MENU = "menu"
    MULLIGAN = "mulligan"
    PLAY = "play"
    BATTLEGROUNDS_SHOP = "battlegrounds_shop"
    ARENA = "arena"


_SCENE_LINE = re.compile(r"LoadingScreen\.OnSceneLoaded\(\)\s*-\s*prevMode=(\w+)\s+currMode=(\w+)", re.IGNORECASE)
_MODE_SCENES = {
    "HUB": Scene.MENU,
    "COLLECTIONMANAGER": Scene.MENU,
    "GAMEPLAY": Scene.PLAY,
    "BACON": Scene.BATTLEGROUNDS_SHOP,
    "DRAFT": Scene.ARENA,
    "TOURNAMENT": Scene.ARENA,
}


def scene_from_line(line: str) -> Scene | None:
    """Parse an actual LoadingScreen.OnSceneLoaded line, if present."""
    match = _SCENE_LINE.search(line)
    if match is None:
        return None
    return _MODE_SCENES.get(match.group(2).upper(), Scene.UNKNOWN)


class SceneFSM:
    def __init__(self) -> None:
        self.state = Scene.UNKNOWN

    def observe(self, line: str) -> Scene:
        scene = scene_from_line(line)
        if scene is not None:
            self.state = scene
        return self.state
