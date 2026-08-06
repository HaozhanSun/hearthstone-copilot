from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class LegalAction:
    option_id: int
    entity: int | None = None
    optype: str = ""
    sub_option_ids: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "sub_option_ids", tuple(self.sub_option_ids))

    def to_dict(self) -> dict[str, Any]:
        return {
            "option_id": self.option_id,
            "entity": self.entity,
            "optype": self.optype,
            "sub_option_ids": self.sub_option_ids,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "LegalAction":
        return cls(
            option_id=int(data["option_id"]),
            entity=data.get("entity"),
            optype=str(data.get("optype", "")),
            sub_option_ids=tuple(int(value) for value in data.get("sub_option_ids", ())),
        )


def extract_legal_actions(_packets: Any) -> tuple[LegalAction, ...]:
    """Removed in Step 1; decision-point extraction is implemented in Step 2."""
    raise NotImplementedError("extract_legal_actions is deferred to Step 2")
