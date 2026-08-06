from __future__ import annotations

import argparse
from typing import Any

from .debug_ui import DebugState, serve_debug_ui


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="hscopilot-debug-ui-app")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--fixture-dir")
    return parser.parse_args(argv)


def run_app(argv: list[str] | None = None, *, webview_module: Any | None = None) -> None:
    """Run the debug UI in a native Windows WebView window.

    The HTTP server remains local-only and owns the existing debug UI state and
    automation worker. The WebView is only the visible desktop app shell, so a
    Launch Hearthstone click is executed by the UI worker rather than by this
    wrapper process.
    """

    args = _parse_args(argv)
    if webview_module is None:
        try:
            import webview as webview_module
        except ImportError as error:  # pragma: no cover - depends on Windows extra
            raise RuntimeError("install the windows-app extra: pywebview") from error

    state = DebugState()
    server = serve_debug_ui(
        state,
        host=args.host,
        port=args.port,
        fixture_dir=args.fixture_dir,
    )
    url = f"http://{args.host}:{server.server_port}/"
    webview_module.create_window(
        "Hearthstone Copilot — Debug UI",
        url,
        width=1440,
        height=920,
        min_size=(1024, 700),
    )
    try:
        webview_module.start(gui="edgechromium", debug=False)
    finally:
        server.shutdown()
        server.server_close()


def main() -> None:
    run_app()


if __name__ == "__main__":  # pragma: no cover
    main()
