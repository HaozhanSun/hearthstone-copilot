from __future__ import annotations

from hscopilot.actuation import ClickAction, CoordinateModel, DryRunActuator, execute
from hscopilot import launcher


def test_dry_run_actuation_never_clicks() -> None:
    actuator = DryRunActuator()
    events = execute([ClickAction(10, 20, "play")], actuator)
    assert events[0].dry_run is True
    assert actuator.events == list(events)


def test_coordinate_model_is_deterministic() -> None:
    model = CoordinateModel(1920, 1080)
    assert model.hand_card(0, 3) == (850, 983)
    assert model.hand_card(2, 3) == (1070, 983)
    assert model.end_turn() == (1747, 562)


def test_launcher_defaults_to_dry_run(monkeypatch) -> None:
    monkeypatch.setattr(launcher, "discover", lambda: {"battle_net": {"executable": r"E:\Battle.net\Battle.net.exe"}, "hearthstone": {"executable": r"E:\Battle.net\Hearthstone\Hearthstone.exe"}, "logs": {"directory": "logs"}})
    monkeypatch.setattr(launcher, "process_running", lambda _path: False)
    report = launcher.launch()
    assert report.dry_run is True
    assert report.hearthstone_running is False


def test_launcher_execute_starts_only_explicitly(monkeypatch) -> None:
    started: list[list[str]] = []
    monkeypatch.setattr(launcher, "discover", lambda: {"battle_net": {"executable": None}, "hearthstone": {"executable": "Hearthstone.exe"}})
    monkeypatch.setattr(launcher, "process_running", lambda _path: False)
    monkeypatch.setattr(launcher.subprocess, "Popen", lambda command, **_kwargs: started.append(command))
    class Window:
        def find(self, _title: str) -> bool:
            return True

    monkeypatch.setattr(launcher, "wait_for_scene", lambda *_args, **_kwargs: launcher.Scene.PLAY)
    monkeypatch.setattr(launcher, "NativeActuator", lambda **_kwargs: DryRunActuator())
    monkeypatch.setattr(launcher, "process_running", lambda path: path == "Hearthstone.exe" or path == "Battle.net.exe")
    monkeypatch.setattr(launcher, "discover", lambda: {"battle_net": {"executable": "Battle.net.exe"}, "hearthstone": {"executable": "Hearthstone.exe"}, "logs": {"directory": "logs"}})
    report = launcher.launch(dry_run=False, play_x=100, play_y=200, window=Window())
    assert started == []
    assert report.dry_run is False
    assert report.scene == "play"
