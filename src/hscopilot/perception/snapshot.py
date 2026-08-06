from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping

SNAPSHOT_VERSION = 2


@dataclass(frozen=True, slots=True)
class EntitySnapshot:
    id: int
    card_id: str | None = None
    tags: tuple[tuple[int, int], ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "tags", tuple(sorted(self.tags, key=lambda pair: pair[0])))

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "card_id": self.card_id, "tags": self.tags}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "EntitySnapshot":
        return cls(
            id=int(data["id"]),
            card_id=data.get("card_id"),
            tags=tuple((int(key), int(value)) for key, value in data.get("tags", ())),
        )


@dataclass(frozen=True, slots=True)
class GameSnapshot:
    version: int = SNAPSHOT_VERSION
    scene: str = "unknown"
    turn: int | None = None
    entities: tuple[EntitySnapshot, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "entities", tuple(self.entities))

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "scene": self.scene,
            "turn": self.turn,
            "entities": tuple(entity.to_dict() for entity in self.entities),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    @property
    def snapshot_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "GameSnapshot":
        return cls(
            version=int(data.get("version", SNAPSHOT_VERSION)),
            scene=str(data.get("scene", "unknown")),
            turn=data.get("turn"),
            entities=tuple(EntitySnapshot.from_dict(entity) for entity in data.get("entities", ())),
        )
