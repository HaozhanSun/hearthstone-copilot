from __future__ import annotations


def create_app():
    try:
        from fastapi import FastAPI
    except ImportError as exc:
        raise RuntimeError("Install the optional 'server' dependency to run the web UI") from exc
    app = FastAPI(title="Hearthstone Copilot", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "mode": "read-only"}

    return app
