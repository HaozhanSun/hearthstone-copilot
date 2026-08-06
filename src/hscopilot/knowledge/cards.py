from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True, slots=True)
class CardDefinition:
    card_id: str
    dbf_id: int
    name: str
    cost: int | None = None
    atk: int | None = None
    health: int | None = None
    type: str = ""
    card_class: str = ""
    description: str = ""
    collectible: bool = False
    rarity: str = ""


class CardKnowledge:
    def __init__(self, cards: dict[str, CardDefinition]):
        self.cards = cards

    @classmethod
    @lru_cache(maxsize=1)
    def load(cls) -> "CardKnowledge":
        from hearthstone import cardxml

        card_db, _ = cardxml.load()
        cards = {
            card.card_id: CardDefinition(
                card_id=card.card_id,
                dbf_id=card.dbf_id,
                name=card.name,
                cost=card.cost,
                atk=card.atk,
                health=card.health,
                type=card.type,
                card_class=card.card_class,
                description=card.description,
                collectible=card.collectible,
                rarity=card.rarity,
            )
            for card in card_db.values()
        }
        return cls(cards)

    def lookup(self, card_id: str) -> CardDefinition | None:
        return self.cards.get(card_id)
