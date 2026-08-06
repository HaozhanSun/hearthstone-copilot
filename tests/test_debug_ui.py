from __future__ import annotations

import json
from pathlib import Path
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
