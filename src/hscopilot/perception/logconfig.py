from __future__ import annotations

import configparser
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_KEYS = {
    "Power": ("LogLevel=1", "FilePrinting=True", "ConsolePrinting=False", "ScreenPrinting=False", "Verbose=True"),
    "LoadingScreen": ("LogLevel=1", "FilePrinting=True", "ConsolePrinting=False", "ScreenPrinting=False", "Verbose=True"),
    "Zone": ("LogLevel=1", "FilePrinting=True", "ConsolePrinting=False", "ScreenPrinting=False", "Verbose=True"),
    "Decks": ("LogLevel=1", "FilePrinting=True", "ConsolePrinting=False", "ScreenPrinting=False", "Verbose=True"),
    "Arena": ("LogLevel=1", "FilePrinting=True", "ConsolePrinting=False", "ScreenPrinting=False", "Verbose=True"),
}
DEFAULT_POWER_STANZA = "[Power]\n" + "\n".join(REQUIRED_KEYS["Power"]) + "\n"
_SECTION = re.compile(r"^\s*\[([^]]+)\]\s*$")


def _merge_text(original: str) -> str:
    separator = "\r\n" if "\r\n" in original else "\n"
    lines = original.splitlines()
    spans: dict[str, tuple[int, int]] = {}
    current: tuple[str, int] | None = None
    for index, line in enumerate(lines):
        match = _SECTION.match(line)
        if match:
            if current:
                spans[current[0].casefold()] = (current[1], index)
            current = (match.group(1), index)
    if current:
        spans[current[0].casefold()] = (current[1], len(lines))

    additions: list[str] = []
    for section, required in REQUIRED_KEYS.items():
        span = spans.get(section.casefold())
        if span is None:
            additions.extend(([""] if lines or additions else []) + [f"[{section}]", *required])
            continue
        start, end = span
        existing_keys = {
            line.split("=", 1)[0].strip().casefold()
            for line in lines[start + 1 : end]
            if "=" in line and not line.lstrip().startswith(("#", ";"))
        }
        missing = [entry for entry in required if entry.split("=", 1)[0].casefold() not in existing_keys]
        if missing:
            lines[end:end] = missing
            # Recompute spans after insertion so subsequent sections remain correct.
            return _merge_text(separator.join(lines) + separator)
    if not additions:
        return separator.join(lines) + (separator if original.endswith(("\n", "\r")) else "")
    merged = separator.join(lines)
    return merged.rstrip("\r\n") + separator + separator.join(additions) + separator


def write_log_config(
    path: str | Path,
    stanza: str = DEFAULT_POWER_STANZA,
    *,
    dry_run: bool = False,
    backup: bool = True,
) -> Path:
    """Merge required Hearthstone sections without discarding other log settings.

    ``stanza`` is retained for API compatibility; the managed sections are the
    explicit ``REQUIRED_KEYS`` above. Existing unrelated sections are preserved
    byte-for-byte. A backup is made immediately before a real write.
    """
    del stanza
    target = Path(path)
    original = target.read_text(encoding="utf-8") if target.exists() else ""
    merged = _merge_text(original)
    if dry_run or merged == original:
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    if backup and target.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        shutil.copy2(target, target.with_name(f"{target.name}.{stamp}.bak"))
    target.write_text(merged, encoding="utf-8", newline="")
    return target


def validate_log_config(path: str | Path) -> dict[str, object]:
    """Return sections and keys currently present, without changing the file."""
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(path, encoding="utf-8")
    return {section: sorted(parser[section].keys()) for section in parser.sections()}
