from __future__ import annotations

from hscopilot.perception.doctor import _config_report


def test_doctor_reports_config_sections_and_keys(tmp_path) -> None:
    path = tmp_path / "log.config"
    path.write_text("[Power]\nLogLevel=1\nFilePrinting=True\n", encoding="utf-8")

    report = _config_report(path)

    assert report["path"] == str(path)
    assert report["sections"] == {"Power": ["fileprinting", "loglevel"]}
    assert report["parse_error"] is None
