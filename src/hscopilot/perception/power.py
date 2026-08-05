from __future__ import annotations

from pathlib import Path

from hscopilot.perception.snapshot import GameSnapshot


class PowerLogError(RuntimeError):
    pass


def _entity_dict(entity) -> dict:
    return {
        "id": entity.id,
        "card_id": entity.card_id,
        "tags": dict(entity.tags),
    }


def _option_dict(option, index: int) -> dict:
    return {
        "index": index,
        "id": option.id,
        "entity": option.entity,
        "type": str(option.type),
        "optype": str(option.optype),
        "error": option.error,
        "error_param": option.error_param,
        "targets": tuple(
            {
                "option": target.option,
                "suboption": target.suboption,
                "target": target.target,
                "position": target.position,
            }
            for target in option.options
        ),
    }


def parse_power_log(path: str | Path) -> list[GameSnapshot]:
    """Parse one saved Power.log into one immutable snapshot per game.

    The implementation uses only the public hslog surface: ``LogParser.read`` /
    ``flush``, ``PacketTree.export`` and ``PacketTree.recursive_iter``.
    """
    try:
        from hslog.parser import LogParser
        from hslog.packets import Options, SendChoices, SendOption
    except ImportError as exc:
        raise PowerLogError("Install hslog and hearthstone to parse Power.log") from exc

    parser = LogParser()
    try:
        with Path(path).open("r", encoding="utf-8", errors="replace") as stream:
            parser.read(stream)
            parser.flush()
    except Exception as exc:
        raise PowerLogError(f"Unable to parse {path}: {exc}") from exc

    snapshots: list[GameSnapshot] = []
    for packet_tree in parser.games:
        game = packet_tree.export()
        legal_actions: list[dict] = []
        actual_choices: list[dict] = []
        for packet in packet_tree.recursive_iter():
            if isinstance(packet, Options):
                for index, option in enumerate(packet.options):
                    if option.error is None:
                        legal_actions.append(_option_dict(option, index))
            elif isinstance(packet, SendOption):
                actual_choices.append({
                    "option": packet.option,
                    "suboption": packet.suboption,
                    "target": packet.target,
                    "position": packet.position,
                })
            elif isinstance(packet, SendChoices):
                actual_choices.append({"id": packet.id, "type": str(packet.type), "choices": tuple(packet.choices)})

        snapshot = GameSnapshot(
            entities=tuple(_entity_dict(entity) for entity in game.entities),
            legal_actions=tuple(legal_actions),
            source=str(path),
        )
        object.__setattr__(snapshot, "actual_choices", tuple(actual_choices))
        snapshots.append(snapshot)
    return snapshots
