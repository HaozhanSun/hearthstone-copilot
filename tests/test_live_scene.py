from __future__ import annotations

from hscopilot.perception.scene import Scene, SceneFSM, scene_from_line


def test_scene_parser_uses_loading_screen_modes() -> None:
    fsm = SceneFSM()
    assert fsm.observe("LoadingScreen.OnSceneLoaded() - prevMode=HUB currMode=GAMEPLAY") is Scene.PLAY
    assert fsm.observe("LoadingScreen.OnSceneLoaded() - prevMode=GAMEPLAY currMode=BACON") is Scene.BATTLEGROUNDS_SHOP
    assert fsm.observe("LoadingScreen.OnSceneLoaded() - prevMode=HUB currMode=DRAFT") is Scene.ARENA


def test_scene_parser_ignores_invented_substrings() -> None:
    fsm = SceneFSM()
    assert scene_from_line("Player chose mulligan in gameplay") is None
    assert fsm.observe("Player chose mulligan in gameplay") is Scene.UNKNOWN
