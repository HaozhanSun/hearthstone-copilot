from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from .snapshot import GameSnapshot
from hscopilot.legality.options import extract_legal_actions


class PowerLogError(RuntimeError):
    pass


def parse_power_log(path: str | Path) -> GameSnapshot:
    """Parse a saved Power.log through hslog; no screenshots or input control."""
    try:
        from hslog.parser import LogParser
    except ImportError as exc:
        raise PowerLogError("Install hslog and hearthstone to parse Power.log") from exc
    parser = LogParser()
    try:
        with Path(path).open("r", encoding="utf-8", errors="replace") as stream:
            parser.read(stream)
            parser.flush()
    except Exception as exc:
        raise PowerLogError(f"Unable to parse {path}: {exc}") from exc
    packets: list[Any] = []
    for game in parser.games:
        packets.extend(getattr(game, "packets", ()))
    actions = tuple(action.to_dict() for action in extract_legal_actions(packets))
    return GameSnapshot(legal_actions=actions, source=str(path))
