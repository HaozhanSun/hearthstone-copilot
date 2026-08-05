from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from typing import Any, Mapping

SNAPSHOT_VERSION = 1


@dataclass(frozen=True)
class GameSnapshot:
    """Immutable boundary object; everything after perception is pure."""

    version: int = SNAPSHOT_VERSION
    scene: str = "unknown"
    entities: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    legal_actions: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    source: str = "offline"
    turn: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {
            "entities": [dict(entity) for entity in self.entities],
            "legal_actions": [dict(action) for action in self.legal_actions],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    @property
    def snapshot_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode()).hexdigest()

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "GameSnapshot":
        return cls(
            version=int(data.get("version", SNAPSHOT_VERSION)),
            scene=str(data.get("scene", "unknown")),
            entities=tuple(dict(x) for x in data.get("entities", ())),
            legal_actions=tuple(dict(x) for x in data.get("legal_actions", ())),
            source=str(data.get("source", "offline")),
            turn=data.get("turn"),
        )
