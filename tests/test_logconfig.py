from __future__ import annotations

from hscopilot.perception.logconfig import write_log_config


def test_log_config_merge_preserves_existing_sections(tmp_path) -> None:
    path = tmp_path / "log.config"
    original = "[HDT]\nLogLevel=4\nFilePrinting=True\n\n[Power]\nLogLevel=9\n"
    path.write_text(original, encoding="utf-8")

    write_log_config(path)
    merged = path.read_text(encoding="utf-8")

    assert "[HDT]\nLogLevel=4\nFilePrinting=True\n" in merged
    assert "[Power]\nLogLevel=9\nFilePrinting=True\n" in merged
    assert any(item.name.startswith("log.config.") for item in tmp_path.iterdir())


def test_log_config_dry_run_does_not_write(tmp_path) -> None:
    path = tmp_path / "log.config"
    path.write_text("[HDT]\nLogLevel=4\n", encoding="utf-8")

    write_log_config(path, dry_run=True)

    assert path.read_text(encoding="utf-8") == "[HDT]\nLogLevel=4\n"
    assert len(list(tmp_path.iterdir())) == 1
