from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class LegalAction:
    index: int
    kind: str = "option"
    entity: int | None = None
    target: int | None = None
    position: int | None = None
    payload: tuple[tuple[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {"payload": dict(self.payload)}


def _get(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, obj.get(name, default) if isinstance(obj, dict) else default)


def extract_legal_actions(packets: Iterable[Any]) -> tuple[LegalAction, ...]:
    actions: list[LegalAction] = []
    for packet in packets:
        name = type(packet).__name__.lower()
        if name not in {"options", "option", "sendoption", "choices", "sendchoices"}:
            continue
        options = _get(packet, "options", ()) or _get(packet, "choices", ()) or ()
        if not options:
            options = (packet,)
        for item in options:
            index = _get(item, "index", _get(item, "id", len(actions)))
            actions.append(LegalAction(
                index=int(index), kind=type(item).__name__.lower(),
                entity=_get(item, "entity"), target=_get(item, "target"),
                position=_get(item, "position"),
            ))
    return tuple(actions)
