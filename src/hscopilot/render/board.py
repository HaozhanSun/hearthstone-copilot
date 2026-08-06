from __future__ import annotations

from hearthstone.enums import CardType, GameTag, Zone

from hscopilot.knowledge.cards import CardKnowledge
from hscopilot.perception.decision import DecisionPoint, ReplayGame


def _tag(entity, tag: GameTag, default: int | None = None) -> int | None:
    values = dict(entity.tags)
    return values.get(int(tag), default)


def _card_name(card_id: str | None, cards: CardKnowledge) -> str:
    if card_id is None:
        return "??"
    card = cards.lookup(card_id)
    return card.name if card is not None else card_id


def render_board(game: ReplayGame, index: int) -> str:
    point: DecisionPoint = game.decision_points[index]
    cards = CardKnowledge.load()
    entities = point.snapshot.entities
    friendly_controller = min(
        (controller for entity in entities if (controller := _tag(entity, GameTag.CONTROLLER)) is not None),
        default=1,
    )
    hand = [entity for entity in entities if _tag(entity, GameTag.ZONE) == int(Zone.HAND) and _tag(entity, GameTag.CONTROLLER) == friendly_controller]
    board = [entity for entity in entities if _tag(entity, GameTag.ZONE) == int(Zone.PLAY)]
    heroes = [entity for entity in board if _tag(entity, GameTag.CARDTYPE) == int(CardType.HERO)]
    mana = next((entity for entity in entities if _tag(entity, GameTag.RESOURCES) is not None), None)
    legal = ", ".join(str(action.option_id) for action in point.legal_actions) or "none"
    actual = str(point.actual.option_id) if point.actual is not None else "none"
    lines = [f"Decision point {point.index} | turn {point.snapshot.turn or '?'}"]
    lines.append(f"Mana: {_tag(mana, GameTag.RESOURCES, 0) if mana is not None else '?'}")
    lines.append("Heroes: " + ", ".join(_card_name(hero.card_id, cards) for hero in heroes) if heroes else "Heroes: ??")
    lines.append("Board: " + ", ".join(_card_name(entity.card_id, cards) for entity in board) if board else "Board: empty")
    lines.append("Your hand: " + ", ".join(_card_name(entity.card_id, cards) for entity in hand) if hand else "Your hand: empty")
    lines.append(f"Legal actions: {legal}")
    lines.append(f"Actually played: {actual}")
    return "\n".join(lines)
