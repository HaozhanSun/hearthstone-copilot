from __future__ import annotations

import ctypes
import logging
import os
import subprocess
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol


class ActionKind(StrEnum):
    MOVE = "move"
    CLICK = "click"


@dataclass(frozen=True, slots=True)
class ClickAction:
    x: int
    y: int
    label: str = ""
    confidence: float = 1.0


@dataclass(frozen=True, slots=True)
class ActionEvent:
    kind: ActionKind
    x: int
    y: int
    label: str
    dry_run: bool


class Actuator(Protocol):
    def click(self, action: ClickAction) -> ActionEvent: ...


class DryRunActuator:
    """Record intended actions without moving the cursor or clicking."""

    def __init__(self) -> None:
        self.events: list[ActionEvent] = []

    def click(self, action: ClickAction) -> ActionEvent:
        event = ActionEvent(ActionKind.CLICK, action.x, action.y, action.label, True)
        self.events.append(event)
        logging.getLogger(__name__).info("dry-run click %s (%d,%d)", action.label, action.x, action.y)
        return event


class NativeActuator:
    """Perform native clicks only when explicitly constructed with enabled=True."""

    def __init__(self, *, enabled: bool = False) -> None:
        self.enabled = enabled

    def click(self, action: ClickAction) -> ActionEvent:
        if not self.enabled:
            raise PermissionError("native actuation is disabled; use DryRunActuator or explicitly enable it")
        if os.name == "nt":
            ctypes.windll.user32.SetCursorPos(action.x, action.y)
            ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)
            ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)
        elif sys_platform_is_macos():
            raise NotImplementedError("macOS native actuation requires an Accessibility adapter")
        else:
            raise NotImplementedError("native actuation is only implemented for Windows")
        return ActionEvent(ActionKind.CLICK, action.x, action.y, action.label, False)


def sys_platform_is_macos() -> bool:
    return os.sys.platform == "darwin"


@dataclass(frozen=True, slots=True)
class CoordinateModel:
    """Resolution-relative coordinates for the Hearthstone hand and end-turn control."""

    viewport_width: int
    viewport_height: int
    hand_y_ratio: float = 0.91
    end_turn_x_ratio: float = 0.91
    end_turn_y_ratio: float = 0.52

    def hand_card(self, index: int, count: int) -> tuple[int, int]:
        if count <= 0 or not 0 <= index < count:
            raise ValueError("hand index must be within a non-empty hand")
        spacing = min(110, self.viewport_width / max(count, 1))
        start = self.viewport_width / 2 - spacing * (count - 1) / 2
        return round(start + index * spacing), round(self.viewport_height * self.hand_y_ratio)

    def end_turn(self) -> tuple[int, int]:
        return round(self.viewport_width * self.end_turn_x_ratio), round(self.viewport_height * self.end_turn_y_ratio)


def execute(actions: list[ClickAction], actuator: Actuator | None = None) -> tuple[ActionEvent, ...]:
    runner = actuator or DryRunActuator()
    return tuple(runner.click(action) for action in actions)
