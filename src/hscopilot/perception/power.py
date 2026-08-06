from __future__ import annotations

from pathlib import Path

from .decision import GameMeta, ReplayGame
from .decision_exporter import DecisionPointExporter


class PowerLogError(RuntimeError):
    pass


def parse_power_log(path: str | Path) -> list[ReplayGame]:
    """Parse a Power.log into replay games and per-decision-point snapshots."""
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

    games: list[ReplayGame] = []
    for packet_tree in parser.games:
        exporter = packet_tree.export(cls=DecisionPointExporter)
        games.append(
            ReplayGame(
                meta=GameMeta(source=str(path), player_names=tuple(exporter.player_names)),
                decision_points=tuple(exporter.decision_points),
            )
        )
    return games
