from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class CardDefinition:
    dbf_id: int
    card_id: str = ""
    name: str = ""
    cost: int | None = None
    attack: int | None = None
    health: int | None = None


class CardKnowledge:
    def __init__(self, cards: dict[int, CardDefinition] | None = None):
        self.cards = cards or {}

    @classmethod
    def from_carddefs_xml(cls, path: str | Path) -> "CardKnowledge":
        cards: dict[int, CardDefinition] = {}
        root = ET.parse(path).getroot()
        for node in root.findall(".//Entity"):
            try:
                dbf_id = int(node.attrib.get("ID", "0"))
            except ValueError:
                continue
            cards[dbf_id] = CardDefinition(dbf_id=dbf_id, card_id=node.attrib.get("CardID", ""))
        return cls(cards)
