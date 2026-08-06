from __future__ import annotations

import json
import mimetypes
import tempfile
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .perception.decision import DecisionPoint
from .perception.scene import Scene


@dataclass
class DebugState:
    """Small in-memory state object shared by the UI and live observers."""

    scene: str = Scene.UNKNOWN
    screenshot: str | None = None
    raw_tail: list[str] = field(default_factory=list)
    point: dict[str, Any] | None = None
    updated_at: str | None = None

    def update(self, point: DecisionPoint | None = None, *, scene: Scene | str | None = None, raw_lines: list[str] = (), screenshot: str | None = None) -> None:
        if point is not None:
            self.point = point.to_dict()
        if scene is not None:
            self.scene = str(scene)
        if screenshot is not None:
            self.screenshot = screenshot
        self.raw_tail.extend(raw_lines)
        self.raw_tail = self.raw_tail[-200:]
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _html() -> str:
    return """<!doctype html><meta charset=utf-8><title>Hearthstone perception debugger</title>
<style>body{font:14px system-ui;margin:0;background:#17191d;color:#eee}main{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 220px;height:100vh}section{padding:16px;border:1px solid #30343b;overflow:auto}#raw{grid-column:1/3;white-space:pre-wrap;font-family:monospace;color:#b8c0cc}pre{white-space:pre-wrap}button{padding:8px 12px}#paste-zone{min-height:180px;border:2px dashed #596273;border-radius:8px;padding:12px;display:grid;place-items:center;text-align:center;outline:none}#paste-zone:focus{border-color:#73a7ff;box-shadow:0 0 0 2px #73a7ff55}#shot{max-width:100%;max-height:45vh}#upload-status{display:block;color:#b8c0cc;margin-top:8px}</style>
<main><section><h2>Screenshot</h2><div id=paste-zone tabindex=0 contenteditable=true spellcheck=false role=button aria-label="Screenshot paste area"><p id=paste-help>Click here, then press Ctrl+V to paste a screenshot from your clipboard.</p><img id=shot alt="no screenshot supplied"></div><output id=upload-status></output></section><section><h2>Parsed state</h2><button onclick=discrepancy()>Report discrepancy</button><pre id=state>loading…</pre></section><section id=raw><h2>Raw log tail</h2><div id=tail></div></section></main>
<script>const zone=document.getElementById('paste-zone');const status=document.getElementById('upload-status');const img=document.getElementById('shot');zone.addEventListener('click',()=>zone.focus());zone.addEventListener('paste',async event=>{const item=[...event.clipboardData.items].find(item=>item.type.startsWith('image/'));if(!item){status.textContent='Clipboard does not contain an image.';return;}event.preventDefault();const file=item.getAsFile();if(!file){status.textContent='Could not read the clipboard image.';return;}img.src=URL.createObjectURL(file);status.textContent='Uploading screenshot…';try{const response=await fetch('/api/screenshot',{method:'POST',headers:{'content-type':file.type||'image/png'},body:file});if(!response.ok)throw new Error('upload failed');status.textContent='Screenshot accepted.';await refresh();}catch(error){status.textContent='Screenshot upload failed: '+error.message;}});async function refresh(){let r=await fetch('/api/state');let s=await r.json();document.getElementById('state').textContent=JSON.stringify(s.point,null,2);document.getElementById('tail').textContent=s.raw_tail.join('');img.src=s.screenshot?'/screenshot?ts='+Date.now():'';img.alt=s.screenshot||'no screenshot supplied';}async function discrepancy(){let note=prompt('What disagrees?');if(note)await fetch('/api/discrepancy',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({note})});}refresh();setInterval(refresh,1000);</script>"""


class _Handler(BaseHTTPRequestHandler):
    state: DebugState
    fixture_dir: Path | None
    screenshot_dir: Path
    max_upload_bytes = 20 * 1024 * 1024

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/state":
            self._send_json(self.state.to_dict())
        elif path == "/screenshot" and self.state.screenshot:
            image = Path(self.state.screenshot)
            if image.is_file():
                body = image.read_bytes(); self.send_response(200); self.send_header("content-type", mimetypes.guess_type(image.name)[0] or "application/octet-stream"); self.send_header("content-length", str(len(body))); self.end_headers(); self.wfile.write(body); return
            self.send_error(404)
        else:
            body = _html().encode("utf-8")
            self.send_response(200); self.send_header("content-type", "text/html; charset=utf-8"); self.send_header("content-length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/screenshot":
            self._receive_screenshot()
            return
        if path != "/api/discrepancy":
            self.send_error(404); return
        length = int(self.headers.get("content-length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        target = self.fixture_dir
        if target is not None:
            target.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            (target / f"discrepancy-{stamp}.json").write_text(json.dumps({"note": payload.get("note", ""), "state": self.state.to_dict()}, indent=2), encoding="utf-8")
        self._send_json({"saved": target is not None})

    def _receive_screenshot(self) -> None:
        content_type = self.headers.get("content-type", "").split(";", 1)[0].strip().casefold()
        if not content_type.startswith("image/"):
            self.send_error(415, "clipboard payload must be an image")
            return
        try:
            length = int(self.headers.get("content-length", "0"))
        except ValueError:
            self.send_error(400, "invalid content length")
            return
        if length <= 0 or length > self.max_upload_bytes:
            self.send_error(413, "screenshot is empty or too large")
            return
        body = self.rfile.read(length)
        if len(body) != length:
            self.send_error(400, "incomplete screenshot")
            return
        extension = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/gif": ".gif"}.get(content_type, ".bin")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        target = self.screenshot_dir / f"clipboard-{stamp}{extension}"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
        self.state.update(screenshot=str(target))
        self._send_json({"accepted": True, "screenshot": str(target)})

    def _send_json(self, value: Any) -> None:
        body = json.dumps(value, default=str).encode("utf-8")
        self.send_response(200); self.send_header("content-type", "application/json"); self.send_header("content-length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def log_message(self, *_args: object) -> None:
        return


def serve_debug_ui(state: DebugState | None = None, *, host: str = "127.0.0.1", port: int = 8765, fixture_dir: str | Path | None = None) -> ThreadingHTTPServer:
    state = state or DebugState()
    screenshot_dir = Path(fixture_dir) if fixture_dir else Path(tempfile.mkdtemp(prefix="hscopilot-debug-"))
    handler = type("DebugHandler", (_Handler,), {"state": state, "fixture_dir": Path(fixture_dir) if fixture_dir else None, "screenshot_dir": screenshot_dir})
    server = ThreadingHTTPServer((host, port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server
