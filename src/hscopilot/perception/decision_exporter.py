from __future__ import annotations

from hearthstone.entities import Card
from hslog.export import EntityTreeExporter
from hslog.packets import Options, SendOption

from hscopilot.legality.options import LegalAction
from hscopilot.perception.decision import ActualChoice, DecisionPoint
from hscopilot.perception.snapshot import EntitySnapshot, GameSnapshot


class DecisionPointExporter(EntityTreeExporter):
    """Entity export plus a frozen decision-point trace in one packet pass."""

    def __init__(self, packet_tree):
        super().__init__(packet_tree)
        self.decision_points: list[DecisionPoint] = []
        self.player_names: list[str] = []

    def handle_player(self, packet):
        player = super().handle_player(packet)
        if packet.name:
            self.player_names.append(packet.name)
        return player

    def _snapshot(self) -> GameSnapshot:
        entities = tuple(
            EntitySnapshot(
                id=entity.id,
                card_id=entity.card_id if isinstance(entity, Card) else None,
                tags=tuple(sorted((int(key), int(value)) for key, value in entity.tags.items())),
            )
            for entity in self.game.entities
        )
        return GameSnapshot(entities=entities)

    def handle_options(self, packet: Options):
        super().handle_options(packet)
        actions = tuple(
            LegalAction(
                option_id=option.id,
                entity=option.entity,
                optype=str(option.optype),
                sub_option_ids=tuple(sub_option.id for sub_option in option.options),
            )
            for option in packet.options
            if option.error is None
        )
        self.decision_points.append(DecisionPoint(len(self.decision_points), self._snapshot(), actions))

    def handle_send_option(self, packet: SendOption):
        super().handle_send_option(packet)
        if self.decision_points:
            point = self.decision_points[-1]
            self.decision_points[-1] = DecisionPoint(
                point.index,
                point.snapshot,
                point.legal_actions,
                ActualChoice(packet.option, packet.suboption, packet.target, packet.position),
            )
