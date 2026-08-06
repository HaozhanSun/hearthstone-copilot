from __future__ import annotations

import json
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from hscopilot.debug_ui import DebugState, serve_debug_ui
from hscopilot.windows_automation import AutomationResult, CloseResult, WindowsUiAutomation


def test_debug_ui_state_and_discrepancy_endpoint(tmp_path: Path) -> None:
    state = DebugState(); state.update(raw_lines=["hello\n"])
    server = serve_debug_ui(state, port=0, fixture_dir=tmp_path)
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        with urlopen(base + "/api/state") as response:
            assert json.load(response)["raw_tail"] == ["hello\n"]
        request = Request(base + "/api/discrepancy", data=b'{"note":"wrong scene"}', headers={"content-type": "application/json"}, method="POST")
        with urlopen(request) as response:
            assert json.load(response)["saved"] is True
        assert list(tmp_path.glob("discrepancy-*.json"))
    finally:
        server.shutdown(); server.server_close()


def test_debug_ui_accepts_clipboard_screenshot(tmp_path: Path) -> None:
    state = DebugState()
    server = serve_debug_ui(state, port=0, fixture_dir=tmp_path)
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        with urlopen(base) as response:
            html = response.read().decode("utf-8")
        assert 'id=paste-zone' in html
        assert "event.clipboardData.items" in html

        image = b"\x89PNG\r\nclipboard-fixture"
        request = Request(base + "/api/screenshot", data=image, headers={"content-type": "image/png"}, method="POST")
        with urlopen(request) as response:
            payload = json.load(response)
        assert payload["accepted"] is True

        with urlopen(base + "/api/state") as response:
            saved_state = json.load(response)
        screenshot = Path(saved_state["screenshot"])
        assert screenshot.parent == tmp_path
        assert screenshot.read_bytes() == image
        with urlopen(base + "/screenshot") as response:
            assert response.headers["content-type"] == "image/png"
            assert response.read() == image
    finally:
        server.shutdown(); server.server_close()


def test_debug_ui_rejects_non_image_clipboard_payload(tmp_path: Path) -> None:
    server = serve_debug_ui(DebugState(), port=0, fixture_dir=tmp_path)
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        request = Request(base + "/api/screenshot", data=b"not an image", headers={"content-type": "text/plain"}, method="POST")
        try:
            urlopen(request)
        except HTTPError as error:
            assert error.code == 415
        else:
            raise AssertionError("non-image clipboard payload was accepted")
    finally:
        server.shutdown(); server.server_close()


class _Control:
    def __init__(self, text: str, kind: str, children: list["_Control"] | None = None, visible: bool = True) -> None:
        self._text = text
        self.element_info = type("Info", (), {"control_type": kind})()
        self._children = children or []
        self._visible = visible
        self.invoked = False
        self.closed = False

    def window_text(self) -> str:
        return self._text

    def descendants(self) -> list["_Control"]:
        return self._children

    def is_visible(self) -> bool:
        return self._visible

    def invoke(self) -> None:
        self.invoked = True

    def close(self) -> None:
        self.closed = True


class _Desktop:
    def __init__(self, window: _Control) -> None:
        self.window = window

    def windows(self) -> list[_Control]:
        return [self.window]


def test_windows_driver_finds_only_observed_modal_and_play_controls() -> None:
    close = _Control("Close", "Button")
    modal = _Control("What's New?", "Dialog", [close])
    play = _Control("Play: Hearthstone, Version: 36.2.0", "Button")
    window = _Control("Battle.net", "Pane", [modal, play])
    observation = WindowsUiAutomation(desktop=_Desktop(window)).inspect_battle_net()
    assert observation.modal_title == "What's New?"
    assert observation.close_available is True
    assert observation.play_available is True
    driver = WindowsUiAutomation(desktop=_Desktop(window))
    driver._click(observation._close_control)
    assert close.invoked is True


def test_windows_driver_ignores_hidden_login_label() -> None:
    hidden_login = _Control("Battle.net Login", "Text", visible=False)
    play = _Control("Play: Hearthstone, Version: 36.2.0", "Button")
    window = _Control("Battle.net", "Pane", [hidden_login, play])
    observation = WindowsUiAutomation(desktop=_Desktop(window)).inspect_battle_net()
    assert observation.blocking_text is None
    assert observation.play_available is True


def test_windows_driver_allows_authenticated_battlenet_login_handoff() -> None:
    progress = _Control("Logging in...", "Text")
    window = _Control("Battle.net Login", "Pane", [progress])
    observation = WindowsUiAutomation(desktop=_Desktop(window)).inspect_battle_net()
    assert observation.blocking_text is None


def test_windows_driver_stops_on_actionable_login_text() -> None:
    password = _Control("Password", "Text")
    window = _Control("Battle.net Login", "Pane", [password])
    observation = WindowsUiAutomation(desktop=_Desktop(window)).inspect_battle_net()
    assert observation.blocking_text == "Battle.net Login"


def test_windows_driver_closes_observed_whats_new_window_when_x_is_not_named() -> None:
    modal = _Control("What's New?", "Window")
    window = _Control("Battle.net", "Pane", [modal])
    driver = WindowsUiAutomation(desktop=_Desktop(window))
    observation = driver.inspect_battle_net()
    assert observation.close_available is False
    driver._dismiss_battle_net_modal(observation)
    assert modal.closed is True


def test_debug_ui_launch_endpoint_runs_in_background(tmp_path: Path) -> None:
    class Driver:
        def __init__(self, on_event):
            self.on_event = on_event

        def run(self):
            self.on_event("Closing observed Battle.net What’s New? modal")
            return AutomationResult("Battle.net.exe", "Hearthstone.exe", ("action",), "LoadingScreen HUB scene")

        def close_hearthstone(self):
            self.on_event("Closing observed Hearthstone window")
            return CloseResult("Hearthstone.exe", True, ("Closing observed Hearthstone window",))

        def close_battle_net(self):
            self.on_event("Closing observed Battle.net window")
            return CloseResult("Battle.net.exe", True, ("Closing observed Battle.net window",))

    server = serve_debug_ui(DebugState(), port=0, fixture_dir=tmp_path, automation_factory=Driver)
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        with urlopen(Request(base + "/api/automation/launch", data=b"", method="POST")) as response:
            assert json.load(response)["accepted"] is True
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            with urlopen(base + "/api/automation") as response:
                status = json.load(response)
            if status["status"] == "complete":
                break
            time.sleep(0.01)
        assert status["status"] == "complete"
        assert status["result"]["home_evidence"] == "LoadingScreen HUB scene"
        with urlopen(Request(base + "/api/automation/close/hearthstone", data=b"", method="POST")) as response:
            assert json.load(response)["accepted"] is True
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            with urlopen(base + "/api/automation") as response:
                close_status = json.load(response)
            if close_status["stage"] == "closed":
                break
            time.sleep(0.01)
        assert close_status["status"] == "complete"
        assert close_status["result"]["target"] == "Hearthstone.exe"
    finally:
        server.shutdown(); server.server_close()
