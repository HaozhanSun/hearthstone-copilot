from __future__ import annotations

from pathlib import Path


def power_logs(root: str | Path) -> list[Path]:
    return sorted(Path(root).glob("*.log"))
