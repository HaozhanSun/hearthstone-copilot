from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .snapshot import GameSnapshot
from hscopilot.legality.options import LegalAction


@dataclass(frozen=True, slots=True)
class ActualChoice:
    option_id: int
    sub_option_id: int | None = None
    target: int | None = None
    position: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"option_id": self.option_id, "sub_option_id": self.sub_option_id, "target": self.target, "position": self.position}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ActualChoice":
        return cls(option_id=int(data["option_id"]), sub_option_id=data.get("sub_option_id"), target=data.get("target"), position=data.get("position"))


@dataclass(frozen=True, slots=True)
class DecisionPoint:
    index: int
    snapshot: GameSnapshot
    legal_actions: tuple[LegalAction, ...] = ()
    actual: ActualChoice | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "legal_actions", tuple(self.legal_actions))

    def to_dict(self) -> dict[str, Any]:
        return {"index": self.index, "snapshot": self.snapshot.to_dict(), "legal_actions": tuple(action.to_dict() for action in self.legal_actions), "actual": self.actual.to_dict() if self.actual is not None else None}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "DecisionPoint":
        return cls(index=int(data["index"]), snapshot=GameSnapshot.from_dict(data["snapshot"]), legal_actions=tuple(LegalAction.from_dict(action) for action in data.get("legal_actions", ())), actual=ActualChoice.from_dict(data["actual"]) if data.get("actual") is not None else None)


@dataclass(frozen=True, slots=True)
class GameMeta:
    source: str = ""
    player_names: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "player_names", tuple(self.player_names))

    def to_dict(self) -> dict[str, Any]:
        return {"source": self.source, "player_names": self.player_names}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "GameMeta":
        return cls(source=str(data.get("source", "")), player_names=tuple(data.get("player_names", ())))


@dataclass(frozen=True, slots=True)
class ReplayGame:
    meta: GameMeta
    decision_points: tuple[DecisionPoint, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "decision_points", tuple(self.decision_points))

    def to_dict(self) -> dict[str, Any]:
        return {"meta": self.meta.to_dict(), "decision_points": tuple(point.to_dict() for point in self.decision_points)}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ReplayGame":
        return cls(meta=GameMeta.from_dict(data["meta"]), decision_points=tuple(DecisionPoint.from_dict(point) for point in data.get("decision_points", ())))
