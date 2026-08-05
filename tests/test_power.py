from __future__ import annotations

import sys
import types


def test_parse_power_log_populates_snapshots(tmp_path, monkeypatch):
    class Entity:
        id = 7
        card_id = "CS2_029"
        tags = {"CONTROLLER": 1}

    class Options:
        def __init__(self):
            self.options = [
                types.SimpleNamespace(
                    id=4, entity=7, type="PLAY", optype="POWER",
                    error=None, error_param=0, options=[],
                ),
                types.SimpleNamespace(
                    id=5, entity=7, type="PLAY", optype="POWER",
                    error="NOT_ENOUGH_MANA", error_param=0, options=[],
                ),
            ]

    class SendOption:
        option = 4
        suboption = 0
        target = 9
        position = 0

    class SendChoices:
        id = 3
        type = "MULLIGAN"
        choices = [11, 12]

    class PacketTree:
        def export(self):
            return types.SimpleNamespace(entities=[Entity()])

        def recursive_iter(self):
            return iter([Options(), SendOption(), SendChoices()])

    class LogParser:
        games = [PacketTree()]

        def read(self, fp):
            assert fp.read() == "fixture"

        def flush(self):
            return None

    hslog = types.ModuleType("hslog")
    parser_module = types.ModuleType("hslog.parser")
    packets_module = types.ModuleType("hslog.packets")
    parser_module.LogParser = LogParser
    packets_module.Options = Options
    packets_module.SendOption = SendOption
    packets_module.SendChoices = SendChoices
    monkeypatch.setitem(sys.modules, "hslog", hslog)
    monkeypatch.setitem(sys.modules, "hslog.parser", parser_module)
    monkeypatch.setitem(sys.modules, "hslog.packets", packets_module)

    from hscopilot.perception.power import parse_power_log

    fixture = tmp_path / "sample.log"
    fixture.write_text("fixture", encoding="utf-8")
    snapshots = parse_power_log(fixture)

    assert len(snapshots) == 1
    assert len(snapshots[0].entities) == 1
    assert len(snapshots[0].legal_actions) == 1
    assert snapshots[0].legal_actions[0]["error"] is None
    assert snapshots[0].actual_choices[0]["target"] == 9
    assert snapshots[0].actual_choices[1]["choices"] == (11, 12)
