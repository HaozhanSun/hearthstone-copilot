from __future__ import annotations

from pathlib import Path
import time
from typing import Iterator


class LogTailer:
    """Small, testable reader used for both saved logs and live tailing."""

    def __init__(self, path: str | Path, *, encoding: str = "utf-8"):
        self.path = Path(path)
        self.encoding = encoding
        self.offset = 0

    def read_new_lines(self) -> list[str]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding=self.encoding, errors="replace") as fh:
            fh.seek(self.offset)
            lines = fh.readlines()
            self.offset = fh.tell()
        return lines

    def follow(self, *, poll_seconds: float = 0.25) -> Iterator[str]:
        while True:
            lines = self.read_new_lines()
            if lines:
                yield from lines
            else:
                time.sleep(poll_seconds)
