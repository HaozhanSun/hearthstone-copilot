from __future__ import annotations

from hscopilot.perception.tailer import LogTailer, newest_power_log


def test_tailer_recovers_from_truncation(tmp_path) -> None:
    path = tmp_path / "Power.log"
    path.write_text("one\n", encoding="utf-8")
    tailer = LogTailer(path)
    assert tailer.read_new_lines() == ["one\n"]
    path.write_text("two\n", encoding="utf-8")
    assert tailer.read_new_lines() == ["two\n"]


def test_newest_power_log_finds_session_folder(tmp_path) -> None:
    older = tmp_path / "session-old"; older.mkdir()
    newer = tmp_path / "session-new"; newer.mkdir()
    old_log = older / "Power.log"; old_log.write_text("old", encoding="utf-8")
    new_log = newer / "Power.log"; new_log.write_text("new", encoding="utf-8")
    old_log.touch()
    new_log.touch()
    assert newest_power_log(tmp_path) == new_log
