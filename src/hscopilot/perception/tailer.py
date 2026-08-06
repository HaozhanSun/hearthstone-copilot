from __future__ import annotations

from pathlib import Path
import threading
import time
from typing import Iterator


def newest_power_log(logs_dir: str | Path) -> Path | None:
    """Return the newest Power.log, including timestamped session folders."""
    root = Path(logs_dir)
    if not root.is_dir():
        return None
    candidates = [path for path in root.glob("**/Power.log") if path.is_file()]
    return max(candidates, key=lambda path: path.stat().st_mtime_ns) if candidates else None


class LogTailer:
    """Incremental reader that survives truncation and log rotation."""

    def __init__(self, path: str | Path, *, encoding: str = "utf-8"):
        self.path = Path(path)
        self.encoding = encoding
        self.offset = 0
        self._identity: tuple[int, int] | None = None
        self._mtime_ns: int | None = None
        self._sample: bytes = b""

    def switch(self, path: str | Path) -> None:
        target = Path(path)
        if target != self.path:
            self.path = target
            self.offset = 0
            self._identity = None
            self._mtime_ns = None
            self._sample = b""

    def read_new_lines(self) -> list[str]:
        if not self.path.exists():
            return []
        stat = self.path.stat()
        identity = (stat.st_dev, stat.st_ino)
        replaced_at_same_size = stat.st_size == self.offset and self._mtime_ns not in (None, stat.st_mtime_ns)
        with self.path.open("rb") as sample_handle:
            sample_handle.seek(max(0, stat.st_size - 4096))
            sample = sample_handle.read()
        content_changed_at_same_size = stat.st_size == self.offset and self._sample != sample
        if self._identity != identity or stat.st_size < self.offset or replaced_at_same_size or content_changed_at_same_size:
            self.offset = 0
            self._identity = identity
        self._mtime_ns = stat.st_mtime_ns
        with self.path.open("r", encoding=self.encoding, errors="replace") as handle:
            handle.seek(self.offset)
            lines = handle.readlines()
            self.offset = handle.tell()
        self._sample = sample
        return lines

    def follow(self, *, poll_seconds: float = 0.25, stop: threading.Event | None = None) -> Iterator[str]:
        while stop is None or not stop.is_set():
            lines = self.read_new_lines()
            if lines:
                yield from lines
            else:
                time.sleep(poll_seconds)


def iter_power_lines(logs_dir: str | Path, *, poll_seconds: float = 0.25, stop: threading.Event | None = None) -> Iterator[str]:
    """Follow the newest session and automatically switch when a new one appears."""
    tailer: LogTailer | None = None
    while stop is None or not stop.is_set():
        latest = newest_power_log(logs_dir)
        if latest is not None:
            if tailer is None:
                tailer = LogTailer(latest)
            else:
                tailer.switch(latest)
            yield from tailer.read_new_lines()
        time.sleep(poll_seconds)
