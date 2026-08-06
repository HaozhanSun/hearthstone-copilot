from __future__ import annotations

import ctypes
import os
import subprocess
import time
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Callable, Protocol

from .actuation import ClickAction, DryRunActuator, NativeActuator
from .perception.doctor import discover
from .perception.scene import Scene, SceneFSM
from .perception.tailer import LogTailer, newest_power_log


class LaunchStage(StrEnum):
    DISCOVER = "discover"
    BATTLE_NET = "battle_net"
    WINDOW = "window"
    PLAY_CLICK = "play_click"
    HEARTHSTONE = "hearthstone"
    SCENE = "scene"


@dataclass(frozen=True, slots=True)
class LaunchReport:
    dry_run: bool
    stages: tuple[str, ...]
    battle_net: str | None
    hearthstone: str | None
    hearthstone_running: bool
    scene: str


class WindowAdapter(Protocol):
    def find(self, title: str) -> bool: ...


class WindowsWindowAdapter:
    def find(self, title: str) -> bool:
        if os.name != "nt":
            return False
        found = False
        title = title.casefold()

        @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        def callback(hwnd, _lparam):
            nonlocal found
            buffer = ctypes.create_unicode_buffer(512)
            ctypes.windll.user32.GetWindowTextW(hwnd, buffer, len(buffer))
            if title in buffer.value.casefold():
                found = True
                return False
            return True

        ctypes.windll.user32.EnumWindows(callback, 0)
        return found


def process_running(executable: str) -> bool:
    name = Path(executable).name.casefold()
    if os.name == "nt":
        result = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True, text=True, check=False)
        return any(line.split(",", 1)[0].strip('"').casefold() == name for line in result.stdout.splitlines())
    result = subprocess.run(["ps", "-A", "-o", "comm="], capture_output=True, text=True, check=False)
    return any(line.strip().casefold() == name for line in result.stdout.splitlines())


def wait_until(predicate: Callable[[], bool], *, timeout: float, poll_seconds: float = 0.25, label: str) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(poll_seconds)
    raise TimeoutError(f"timed out waiting for {label} after {timeout:g}s")


def wait_for_scene(logs_dir: str | Path, expected: Scene, *, timeout: float, poll_seconds: float = 0.25) -> Scene:
    log = newest_power_log(logs_dir)
    if log is None:
        raise FileNotFoundError(f"no Power.log found under {logs_dir}")
    loading = log.with_name("LoadingScreen.log")
    tailer = LogTailer(loading)
    fsm = SceneFSM()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for line in tailer.read_new_lines():
            if fsm.observe(line) is expected:
                return expected
        time.sleep(poll_seconds)
    raise TimeoutError(f"timed out waiting for LoadingScreen scene {expected}")


def launch(
    *,
    dry_run: bool = True,
    play_x: int | None = None,
    play_y: int | None = None,
    timeout: float = 30.0,
    window: WindowAdapter | None = None,
) -> LaunchReport:
    """Run the Battle.net → Play → Hearthstone flow with explicit verification.

    Dry-run is the default. Execution requires explicit Play coordinates and
    performs no click until Battle.net's process and window are confirmed.
    """
    report = discover()
    battle_net = report["battle_net"]["executable"]
    hearthstone = report["hearthstone"]["executable"]
    logs_dir = report["logs"]["directory"]
    stages = [LaunchStage.DISCOVER.value]
    if not battle_net or not hearthstone:
        raise FileNotFoundError("Battle.net.exe and Hearthstone.exe must both be discovered")
    running = process_running(battle_net)
    if dry_run:
        stages.extend((LaunchStage.BATTLE_NET.value, LaunchStage.WINDOW.value, LaunchStage.PLAY_CLICK.value, LaunchStage.HEARTHSTONE.value, LaunchStage.SCENE.value))
        return LaunchReport(True, tuple(stages), battle_net, hearthstone, process_running(hearthstone), Scene.UNKNOWN.value)
    if play_x is None or play_y is None:
        raise ValueError("--play-x and --play-y are required with --execute")
    if not running:
        subprocess.Popen([battle_net], close_fds=True)
    wait_until(lambda: process_running(battle_net), timeout=timeout, label="Battle.net process")
    stages.append(LaunchStage.BATTLE_NET.value)
    adapter = window or WindowsWindowAdapter()
    wait_until(lambda: adapter.find("Battle.net"), timeout=timeout, label="Battle.net window")
    stages.append(LaunchStage.WINDOW.value)
    NativeActuator(enabled=True).click(ClickAction(play_x, play_y, "Battle.net Play"))
    stages.append(LaunchStage.PLAY_CLICK.value)
    wait_until(lambda: process_running(hearthstone), timeout=timeout, label="Hearthstone process")
    stages.append(LaunchStage.HEARTHSTONE.value)
    scene = wait_for_scene(logs_dir, Scene.PLAY, timeout=timeout)
    stages.append(LaunchStage.SCENE.value)
    return LaunchReport(False, tuple(stages), battle_net, hearthstone, True, scene.value)
