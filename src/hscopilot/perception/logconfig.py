from __future__ import annotations

from pathlib import Path

DEFAULT_POWER_STANZA = """[Power]\nLogLevel=1\nFilePrinting=True\nConsolePrinting=False\n"""


def write_log_config(path: str | Path, stanza: str = DEFAULT_POWER_STANZA) -> Path:
    """Write the minimal Power.log stanza, without touching other log settings."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(stanza.rstrip() + "\n", encoding="utf-8")
    return target
