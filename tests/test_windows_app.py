from __future__ import annotations

import time

from hscopilot.windows_app import run_app


class _WebView:
    def __init__(self) -> None:
        self.created: tuple[str, str] | None = None
        self.started = False

    def create_window(self, title: str, url: str, **_kwargs: object) -> None:
        self.created = (title, url)

    def start(self, **_kwargs: object) -> None:
        time.sleep(0.6)
        self.started = True


def test_windows_app_wraps_the_existing_debug_ui_server() -> None:
    webview = _WebView()
    run_app(["--host", "127.0.0.1", "--port", "0"], webview_module=webview)
    assert webview.created is not None
    assert webview.created[0] == "Hearthstone Copilot — Debug UI"
    assert webview.created[1].startswith("http://127.0.0.1:")
    assert webview.started is True
