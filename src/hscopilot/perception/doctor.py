"""Read-only discovery of the local Battle.net/Hearthstone installation."""

from __future__ import annotations

import configparser
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable


def _existing(paths: Iterable[Path], names: tuple[str, ...]) -> Path | None:
    for directory in paths:
        for name in names:
            candidate = directory / name
            if candidate.is_file():
                return candidate
    return None


def _registry_installations() -> tuple[Path | None, Path | None]:
    """Return Battle.net and Hearthstone executables from Windows uninstall data."""
    if os.name != "nt":
        return None, None
    try:
        import winreg
    except ImportError:
        return None, None

    roots = (
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    )
    battle_net: Path | None = None
    hearthstone: Path | None = None
    for hive, subkey in roots:
        try:
            with winreg.OpenKey(hive, subkey) as uninstall:
                for index in range(winreg.QueryInfoKey(uninstall)[0]):
                    try:
                        name = winreg.EnumKey(uninstall, index)
                        with winreg.OpenKey(uninstall, name) as entry:
                            values = {
                                winreg.EnumValue(entry, i)[0]: winreg.EnumValue(entry, i)[1]
                                for i in range(winreg.QueryInfoKey(entry)[1])
                            }
                    except OSError:
                        continue
                    display = str(values.get("DisplayName", ""))
                    location = str(values.get("InstallLocation", ""))
                    icon = str(values.get("DisplayIcon", ""))
                    icon = re.sub(r'^"|"(?:,\d+)?$', "", icon).strip()
                    candidate = Path(icon) if icon.lower().endswith(".exe") else None
                    if candidate is None and location:
                        location_path = Path(location)
                        if "battle.net" in display.lower() or "blizzard" in display.lower():
                            candidate = location_path / "Battle.net.exe"
                        elif "hearthstone" in display.lower():
                            candidate = location_path / "Hearthstone.exe"
                    if "battle.net" in display.lower() and candidate and candidate.is_file():
                        battle_net = battle_net or candidate
                    if "hearthstone" in display.lower() and candidate and candidate.is_file():
                        hearthstone = hearthstone or candidate
        except OSError:
            continue
    return battle_net, hearthstone


def _running_process(name: str) -> str | None:
    """Return a matching running process name as a last-resort discovery signal."""
    try:
        if os.name == "nt":
            result = subprocess.run(
                ["tasklist", "/fo", "csv", "/nh"],
                check=False,
                capture_output=True,
                text=True,
                timeout=3,
            )
            rows = result.stdout.splitlines()
            wanted = name.casefold()
            for row in rows:
                if row.split(",", 1)[0].strip('"').casefold() == wanted:
                    return name
        else:
            result = subprocess.run(["ps", "-A", "-o", "comm="], check=False, capture_output=True, text=True, timeout=3)
            if any(line.strip().casefold() == name.casefold() for line in result.stdout.splitlines()):
                return name
    except (OSError, subprocess.SubprocessError):
        return None
    return None


def _standard_directories() -> tuple[Path, ...]:
    if os.name == "nt":
        values = (
            os.environ.get("ProgramFiles"),
            os.environ.get("ProgramFiles(x86)"),
            os.environ.get("LOCALAPPDATA"),
            os.environ.get("ProgramData"),
        )
        return tuple(Path(value) for value in values if value)
    return (Path("/Applications"), Path.home() / "Applications")


def _find_logs(hearthstone: Path | None) -> Path | None:
    candidates: list[Path] = []
    if hearthstone:
        candidates.extend((hearthstone.parent / "Logs", hearthstone.parent.parent / "Logs"))
    if os.name == "nt":
        candidates.extend(
            Path(value) / relative
            for value in (os.environ.get("APPDATA"), os.environ.get("LOCALAPPDATA"))
            if value
            for relative in (Path("Blizzard/Hearthstone/Logs"), Path("Hearthstone/Logs"))
        )
    else:
        candidates.append(Path.home() / "Library/Logs/Blizzard/Hearthstone")
    return next((path for path in candidates if path.is_dir()), None)


def _find_log_config(hearthstone: Path | None, logs: Path | None) -> Path | None:
    roots: list[Path] = []
    if hearthstone:
        roots.extend((hearthstone.parent, hearthstone.parent.parent))
    if logs:
        roots.append(logs.parent)
    roots.extend((Path.home() / "Documents/Hearthstone", Path.home() / "AppData/Local/Blizzard/Hearthstone"))
    for root in roots:
        candidate = root / "log.config"
        if candidate.is_file():
            return candidate
    return None


def _config_report(path: Path | None) -> dict[str, object]:
    report: dict[str, object] = {"path": str(path) if path else None, "sections": {}, "parse_error": None}
    if path is None:
        return report
    parser = configparser.ConfigParser(interpolation=None)
    try:
        parser.read(path, encoding="utf-8")
        report["sections"] = {section: sorted(parser[section].keys()) for section in parser.sections()}
    except (OSError, configparser.Error) as error:
        report["parse_error"] = str(error)
    return report


def discover() -> dict[str, object]:
    """Build a JSON-serializable, read-only machine discovery report."""
    registry_battle_net, registry_hearthstone = _registry_installations()
    standard = _standard_directories()
    battle_net = registry_battle_net or _existing(
        tuple(directory / name for directory in standard for name in ("Battle.net", "Blizzard Entertainment")),
        ("Battle.net.exe", "Battle.net Launcher.exe"),
    )
    hearthstone = registry_hearthstone or _existing(
        tuple(directory / name / "Hearthstone" for directory in standard for name in ("Battle.net", "Blizzard Entertainment", "Hearthstone")),
        ("Hearthstone.exe",),
    )
    logs = _find_logs(hearthstone)
    newest_power = None
    if logs:
        power_logs = list(logs.glob("Power.log")) + list(logs.glob("**/Power.log"))
        if power_logs:
            newest_power = max(power_logs, key=lambda path: path.stat().st_mtime)
    config = _find_log_config(hearthstone, logs)
    return {
        "platform": {"system": sys.platform, "os_name": os.name},
        "battle_net": {"executable": str(battle_net) if battle_net else None, "running": _running_process("Battle.net.exe")},
        "hearthstone": {"executable": str(hearthstone) if hearthstone else None, "running": _running_process("Hearthstone.exe")},
        "logs": {"directory": str(logs) if logs else None, "newest_power_log": str(newest_power) if newest_power else None},
        "log_config": _config_report(config),
        "macos_permissions": {"screen_recording": "not_applicable" if os.name == "nt" else "not_checked", "accessibility": "not_applicable" if os.name == "nt" else "not_checked"},
    }


def main() -> None:
    print(json.dumps(discover(), indent=2, sort_keys=True))
