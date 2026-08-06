from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path

from .decision import DecisionPoint
from .decision_exporter import DecisionPointExporter
from .tailer import iter_power_lines


class IncrementalPowerParser:
    """Feed timestamped Power.log lines and emit newly visible decision points."""

    def __init__(self) -> None:
        try:
            from hslog.parser import LogParser
            from hslog.exceptions import MissingPlayerData
        except ImportError as exc:
            raise RuntimeError("Install hslog and hearthstone for live parsing") from exc
        self.parser = LogParser()
        self._incomplete_error = MissingPlayerData
        self._tree = None
        self._emitted = 0

    def feed(self, line: str) -> tuple[DecisionPoint, ...]:
        try:
            self.parser.read_line(line)
        except (ValueError, IndexError):
            # A live log can contain an incomplete line while the game is writing it.
            return ()
        # hslog 1.19 exposes the in-progress tree through its documented
        # ParsingState object; completed trees are surfaced by ``games``.
        # Export only at decision boundaries. Re-exporting the entire tree for
        # every tag line is needlessly expensive; SendOption is the first point
        # at which the preceding Options packet is complete and stable.
        if "GameState.SendOption()" not in line and "GameState.DebugPrintOptions() - id=" not in line:
            return ()
        tree = self.parser._parsing_state.packet_tree
        if tree is None:
            return ()
        if tree is not self._tree:
            self._tree = tree
            self._emitted = 0
        try:
            exporter = tree.export(cls=DecisionPointExporter)
        except (ValueError, IndexError, KeyError, self._incomplete_error):
            # The current packet tree is intentionally incomplete between lines.
            return ()
        points = tuple(exporter.decision_points)
        new = points[self._emitted :]
        self._emitted = len(points)
        return new

    def feed_lines(self, lines: Iterable[str]) -> Iterator[DecisionPoint]:
        for line in lines:
            yield from self.feed(line)


def replay_incrementally(path: str | Path, *, chunk_size: int = 256) -> tuple[DecisionPoint, ...]:
    """Replay a saved log through ``read_line`` in chunks, as a live session would."""
    parser = IncrementalPowerParser()
    emitted: list[DecisionPoint] = []
    with Path(path).open("r", encoding="utf-8", errors="replace") as handle:
        while chunk := list(next_chunk(handle, chunk_size)):
            emitted.extend(parser.feed_lines(chunk))
    return tuple(emitted)


def next_chunk(handle, size: int) -> Iterator[str]:
    for _ in range(size):
        line = handle.readline()
        if not line:
            return
        yield line


def watch_decisions(logs_dir: str | Path, *, poll_seconds: float = 0.25) -> Iterator[DecisionPoint]:
    parser = IncrementalPowerParser()
    yield from parser.feed_lines(iter_power_lines(logs_dir, poll_seconds=poll_seconds))
