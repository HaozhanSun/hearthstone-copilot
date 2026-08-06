from __future__ import annotations

import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from hscopilot.debug_ui import DebugState, serve_debug_ui


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
