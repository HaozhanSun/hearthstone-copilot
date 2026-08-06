from __future__ import annotations

import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Protocol

from .launcher import process_running
from .perception.doctor import discover
from .perception.scene import Scene, scene_from_line


class AutomationError(RuntimeError):
    """Base class for an automation run that cannot safely continue."""


class SafetyStop(AutomationError):
    """A login, security, permission, or CAPTCHA screen was observed."""


class UnexpectedModal(AutomationError):
    """A modal was observed but is not an explicitly approved modal."""


@dataclass(frozen=True, slots=True)
class UiObservation:
    target: str
    window_found: bool
    labels: tuple[str, ...] = ()
    modal_title: str | None = None
    blocking_text: str | None = None
    close_available: bool = False
    play_available: bool = False
    start_available: bool = False
    mode_labels: tuple[str, ...] = ()
    home_evidence: str | None = None
    _close_control: Any = field(default=None, repr=False, compare=False)
    _play_control: Any = field(default=None, repr=False, compare=False)
    _start_control: Any = field(default=None, repr=False, compare=False)
    _modal_control: Any = field(default=None, repr=False, compare=False)


@dataclass(frozen=True, slots=True)
class AutomationResult:
    battle_net: str
    hearthstone: str
    actions: tuple[str, ...]
    home_evidence: str


@dataclass(frozen=True, slots=True)
class CloseResult:
    target: str
    closed: bool
    actions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class OcrMatch:
    text: str
    box: tuple[tuple[float, float], ...]
    score: float
    window: Any = field(default=None, repr=False, compare=False)

    @property
    def center(self) -> tuple[int, int]:
        return (
            round(sum(point[0] for point in self.box) / len(self.box)),
            round(sum(point[1] for point in self.box) / len(self.box)),
        )


class UiDriver(Protocol):
    def run(self) -> AutomationResult: ...

    def close_hearthstone(self) -> CloseResult: ...

    def close_battle_net(self) -> CloseResult: ...


_BLOCKING_RE = re.compile(
    r"(?:login|log in|sign in|password|security|captcha|permission|authorize|verification|two[- ]factor|"
    r"登录|登入|密码|安全|验证码|验证|权限|授权)",
    re.IGNORECASE,
)
_WHAT_IS_NEW_RE = re.compile(r"what\s*[’']?s\s+new|最新消息|What's New", re.IGNORECASE)
_AUTH_PROGRESS_RE = re.compile(r"^logging\s+in(?:\.\.\.)?$", re.IGNORECASE)
_AUTH_PROGRESS_TITLE_RE = re.compile(r"^battle\.net\s+login$", re.IGNORECASE)
_PLAY_RE = re.compile(r"^play\s*:\s*hearthstone\b", re.IGNORECASE)
_START_RE = re.compile(r"^(?:点击开始|click\s+to\s+start|start)$", re.IGNORECASE)
_MODE_RE = re.compile(
    r"(?:play|arena|battleground|mercenar|duel|solo|对战|竞技场|酒馆战棋|佣兵|冒险|模式)",
    re.IGNORECASE,
)


class _RapidOcrScreenReader:
    """Optional rendered-screen OCR using the Windows extra's local model."""

    def __init__(self) -> None:
        from rapidocr_onnxruntime import RapidOCR

        self._ocr = RapidOCR()

    def read(self, window: Any) -> tuple[OcrMatch, ...]:
        import numpy as np

        image = np.asarray(window.capture_as_image().convert("RGB"))
        results, _ = self._ocr(image)
        if not results:
            return ()
        matches: list[OcrMatch] = []
        for result in results:
            box, text, score = result
            matches.append(
                OcrMatch(
                    str(text).strip(),
                    tuple((float(point[0]), float(point[1])) for point in box),
                    float(score),
                    window,
                )
            )
        return tuple(matches)


def _control_text(control: Any) -> str:
    try:
        return str(control.window_text() or "").strip()
    except Exception:
        return ""


def _control_type(control: Any) -> str:
    try:
        return str(control.element_info.control_type or "")
    except Exception:
        return ""


class WindowsUiAutomation:
    """Semantic Windows UI Automation driver for the Battle.net opening flow.

    The adapter intentionally uses UI Automation control names and Invoke
    patterns. It never derives or guesses a screen coordinate. Hearthstone's
    rendered home screen is additionally confirmed by LoadingScreen.log when
    the game does not expose its rendered controls to UI Automation.
    """

    def __init__(
        self,
        *,
        timeout: float = 90.0,
        poll_seconds: float = 0.5,
        on_event: Callable[[str], None] | None = None,
        desktop: Any | None = None,
        screen_reader: Any | None = None,
    ) -> None:
        if os.name != "nt":
            raise AutomationError("Windows UI Automation is only available on Windows")
        if desktop is None:
            try:
                from pywinauto import Desktop
            except ImportError as error:  # pragma: no cover - depends on host extras
                raise AutomationError("install the Windows extra: pywinauto") from error
            desktop = Desktop(backend="uia")
        self.desktop = desktop
        self.timeout = timeout
        self.poll_seconds = poll_seconds
        self.on_event = on_event or (lambda _message: None)
        self.actions: list[str] = []
        self.screen_reader = screen_reader

    def _event(self, message: str) -> None:
        self.actions.append(message)
        self.on_event(message)

    def _windows(self) -> list[Any]:
        try:
            return [window for window in self.desktop.windows() if window.is_visible()]
        except Exception as error:
            raise AutomationError(f"could not enumerate visible windows: {error}") from error

    def _find_window(self, pattern: str) -> Any | None:
        regex = re.compile(pattern, re.IGNORECASE)
        for window in self._windows():
            if regex.search(_control_text(window)):
                return window
        return None

    @staticmethod
    def _controls(window: Any) -> list[Any]:
        try:
            return [window, *window.descendants()]
        except Exception:
            return [window]

    @staticmethod
    def _is_visible(control: Any) -> bool:
        try:
            return bool(control.is_visible())
        except Exception:
            return True

    @staticmethod
    def _labels(window: Any) -> tuple[str, ...]:
        labels: list[str] = []
        for control in WindowsUiAutomation._controls(window):
            if not WindowsUiAutomation._is_visible(control):
                continue
            text = _control_text(control)
            if text and text not in labels:
                labels.append(text)
        return tuple(labels)

    @staticmethod
    def _find_control(window: Any, predicate: Callable[[Any, str, str], bool]) -> Any | None:
        for control in WindowsUiAutomation._controls(window):
            if not WindowsUiAutomation._is_visible(control):
                continue
            text = _control_text(control)
            kind = _control_type(control)
            if predicate(control, text, kind):
                return control
        return None

    def _blocking_text(self, labels: tuple[str, ...]) -> str | None:
        auth_in_progress = any(_AUTH_PROGRESS_RE.search(label) for label in labels)
        for label in labels:
            if auth_in_progress and _AUTH_PROGRESS_TITLE_RE.fullmatch(label):
                # Battle.net briefly exposes an off-screen authentication
                # window while an already-authenticated account is restored.
                # It contains no credential or sign-in control; actionable
                # login/security labels still stop below.
                continue
            if _BLOCKING_RE.search(label):
                return label
        return None

    def inspect_battle_net(self) -> UiObservation:
        window = self._find_window(r"battle\.net")
        if window is None:
            return UiObservation("battle_net", False)
        labels = self._labels(window)
        blocking = self._blocking_text(labels)
        modal_control = self._find_control(
            window,
            lambda _control, text, kind: kind in {"Dialog", "Window"} and bool(text),
        )
        modal_title = _control_text(modal_control) if modal_control else None
        if modal_title and not _WHAT_IS_NEW_RE.search(modal_title):
            # A titled dialog is never dismissed speculatively. The caller
            # reports it as unexpected and stops for human inspection.
            return UiObservation("battle_net", True, labels, modal_title, blocking)
        close_control = None
        if modal_control is not None:
            close_control = self._find_control(
                modal_control,
                lambda _control, text, kind: kind == "Button" and text.casefold() in {"close", "关闭", "x"},
            )
        play_control = self._find_control(
            window,
            lambda _control, text, kind: kind == "Button" and bool(_PLAY_RE.search(text)),
        )
        return UiObservation(
            "battle_net",
            True,
            labels,
            modal_title,
            blocking,
            close_control is not None,
            play_control is not None,
            _close_control=close_control,
            _play_control=play_control,
            _modal_control=modal_control,
        )

    def _dismiss_battle_net_modal(self, observation: UiObservation) -> None:
        if observation._close_control is not None:
            self._click(observation._close_control)
            return
        modal = observation._modal_control
        close = getattr(modal, "close", None)
        if not callable(close):
            handle = None
            try:
                handle = getattr(modal, "handle", None)
                if callable(handle):
                    handle = handle()
                if not handle and modal is not None:
                    handle = getattr(getattr(modal, "element_info", None), "handle", None)
            except Exception:
                handle = None
            if handle:
                import ctypes

                if not ctypes.WinDLL("user32", use_last_error=True).PostMessageW(int(handle), 0x0010, 0, 0):
                    raise AutomationError("semantic close of observed Battle.net What鈥檚 New? window failed")
                self._event("Closing observed Battle.net What鈥檚 New? window via its observed window handle")
                return
        if not callable(close):
            raise UnexpectedModal("What鈥檚 New? modal has no observed Close control")
        self._event("Closing observed Battle.net What鈥檚 New? window")
        try:
            close()
        except Exception as error:
            raise AutomationError(f"semantic close of Battle.net What鈥檚 New? failed: {error}") from error

    def inspect_hearthstone(self) -> UiObservation:
        window = self._find_window(r"hearthstone|炉石传说")
        if window is None:
            return UiObservation("hearthstone", False)
        labels = self._labels(window)
        ocr_matches = self._ocr_matches(window)
        labels = tuple(dict.fromkeys([*labels, *(match.text for match in ocr_matches)]))
        blocking = self._blocking_text(labels)
        start_control = self._find_control(
            window,
            lambda _control, text, _kind: bool(_START_RE.fullmatch(text)),
        )
        if start_control is None:
            start_control = next(
                (match for match in ocr_matches if _START_RE.fullmatch(match.text) and match.score >= 0.5),
                None,
            )
        mode_labels = tuple(label for label in labels if _MODE_RE.search(label))
        distinct_modes = tuple(dict.fromkeys(mode_labels))
        home_evidence = "UI Automation mode selector" if len(distinct_modes) >= 4 else None
        return UiObservation(
            "hearthstone",
            True,
            labels,
            None,
            blocking,
            start_available=start_control is not None,
            mode_labels=distinct_modes,
            home_evidence=home_evidence,
            _start_control=start_control,
        )

    def _ocr_matches(self, window: Any) -> tuple[OcrMatch, ...]:
        if self.screen_reader is None:
            try:
                self.screen_reader = _RapidOcrScreenReader()
            except Exception:
                # UI Automation remains useful on systems without the optional
                # OCR extra; it simply cannot click a rendered-only control.
                return ()
        try:
            return tuple(self.screen_reader.read(window))
        except Exception as error:
            self._event(f"Rendered-screen OCR unavailable: {error}")
            return ()

    def _click(self, control: Any) -> None:
        if control is None:
            raise AutomationError("requested UI control was not present in the fresh observation")
        if isinstance(control, OcrMatch):
            try:
                control.window.click_input(coords=control.center)
                return
            except Exception as error:
                raise AutomationError(f"OCR-observed rendered control click failed: {error}") from error
        try:
            invoke = getattr(control, "invoke", None)
            if callable(invoke):
                invoke()
                return
            click = getattr(control, "click", None)
            if callable(click):
                click()
                return
        except Exception as error:
            raise AutomationError(f"semantic UI action failed: {error}") from error
            raise AutomationError("observed UI control has no supported Invoke or click pattern")

    def _wait(self, predicate: Callable[[], bool], label: str, *, timeout: float | None = None) -> None:
        wait_timeout = self.timeout if timeout is None else timeout
        deadline = time.monotonic() + wait_timeout
        while time.monotonic() < deadline:
            if predicate():
                return
            time.sleep(self.poll_seconds)
        raise AutomationError(f"timed out waiting for {label} after {wait_timeout:g}s")

    @staticmethod
    def _process_path(pid: int) -> str | None:
        if os.name != "nt":
            return None
        import ctypes
        from ctypes import wintypes

        query_limited = 0x1000
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.OpenProcess(query_limited, False, pid)
        if not handle:
            return None
        try:
            buffer = ctypes.create_unicode_buffer(32768)
            size = wintypes.DWORD(len(buffer))
            if not kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
                return None
            return buffer.value
        finally:
            kernel32.CloseHandle(handle)

    def _close_window(self, title_pattern: str, executable: str, label: str) -> CloseResult:
        window = self._find_window(title_pattern)
        if window is None and not process_running(executable):
            self._event(f"{label} is already closed")
            return CloseResult(executable, True, tuple(self.actions))
        if window is None:
            raise AutomationError(f"{label} process is running but its window is not observable; stopped")
        observed_pid = None
        process_id = getattr(window, "process_id", None)
        if callable(process_id):
            try:
                observed_pid = int(process_id())
            except Exception:
                observed_pid = None
        self._event(f"Closing observed {label} window")
        close = getattr(window, "close", None)
        if not callable(close):
            raise AutomationError(f"observed {label} window has no supported close action")
        try:
            close()
        except Exception as error:
            raise AutomationError(f"semantic close of {label} failed: {error}") from error
        try:
            self._wait(
                lambda: not process_running(executable) and self._find_window(title_pattern) is None,
                f"{label} to close",
                timeout=min(self.timeout, 10.0),
            )
        except AutomationError as graceful_error:
            if observed_pid is None:
                raise graceful_error
            observed_path = self._process_path(observed_pid)
            if observed_path is None or str(Path(observed_path).resolve()).casefold() != str(Path(executable).resolve()).casefold():
                raise AutomationError(f"refusing to terminate an unverified {label} process") from graceful_error
            self._event(f"Graceful close left {label} running; terminating the verified process")
            result = subprocess.run(
                ["taskkill", "/PID", str(observed_pid), "/T", "/F"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                raise AutomationError(f"could not terminate verified {label} process: {result.stderr.strip()}") from graceful_error
            self._wait(
                lambda: not process_running(executable) and self._find_window(title_pattern) is None,
                f"{label} process termination",
            )
        return CloseResult(executable, True, tuple(self.actions))

    def close_hearthstone(self) -> CloseResult:
        report = discover()
        executable = report["hearthstone"]["executable"]
        if not executable:
            raise AutomationError("doctor could not discover Hearthstone.exe")
        return self._close_window(r"hearthstone|炉石传说", str(executable), "Hearthstone")

    def close_battle_net(self) -> CloseResult:
        report = discover()
        executable = report["battle_net"]["executable"]
        if not executable:
            raise AutomationError("doctor could not discover Battle.net.exe")
        return self._close_window(r"battle\.net", str(executable), "Battle.net")

    def _latest_scene(self, logs_dir: str | Path) -> Scene:
        root = Path(logs_dir)
        candidates = sorted(root.glob("**/LoadingScreen.log"), key=lambda path: path.stat().st_mtime, reverse=True)
        for path in candidates[:3]:
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-200:]
            except OSError:
                continue
            current = Scene.UNKNOWN
            for line in lines:
                parsed = scene_from_line(line)
                if parsed is not None:
                    current = parsed
            if current is not Scene.UNKNOWN:
                return current
        return Scene.UNKNOWN

    def run(self) -> AutomationResult:
        self._event("Discovering Battle.net and Hearthstone")
        report = discover()
        battle_net = report["battle_net"]["executable"]
        hearthstone = report["hearthstone"]["executable"]
        logs_dir = report["logs"]["directory"]
        if not battle_net or not hearthstone:
            raise AutomationError("doctor could not discover Battle.net.exe and Hearthstone.exe")
        if not process_running(battle_net):
            self._event("Launching Battle.net")
            subprocess.Popen([battle_net], close_fds=True)
        self._event("Inspecting Battle.net window")
        self._wait(lambda: self.inspect_battle_net().window_found, "Battle.net window")
        self._event("Battle.net window observed")

        hearthstone_active = process_running(hearthstone)
        while True:
            observation = self.inspect_battle_net()
            if observation.blocking_text:
                raise SafetyStop(f"stopped on Battle.net safety screen: {observation.blocking_text}")
            if observation.modal_title:
                if not observation.close_available:
                    self._event("Rechecking observed Battle.net What鈥檚 New? modal for a visible Close action")
                    try:
                        self._wait(
                            lambda: self.inspect_battle_net().modal_title is None,
                            "approved Battle.net modal to settle",
                            timeout=2.0,
                        )
                    except AutomationError as error:
                        raise UnexpectedModal("What鈥檚 New? modal has no observed Close control") from error
                    continue
                if not observation.close_available:
                    raise UnexpectedModal("What’s New? modal has no observed Close control")
                self._event("Closing observed Battle.net What’s New? modal")
                self._click(observation._close_control)
                time.sleep(self.poll_seconds)
                continue
            if hearthstone_active:
                self._event("Hearthstone is already running; inspecting its current screen")
                break
            if observation.play_available:
                self._event("Clicking observed Hearthstone Play control")
                self._click(observation._play_control)
                break
            time.sleep(self.poll_seconds)

        self._event("Waiting for Hearthstone process")
        self._wait(lambda: process_running(hearthstone), "Hearthstone process")
        self._event("Inspecting Hearthstone rendered screen")
        self._wait(lambda: self.inspect_hearthstone().window_found, "Hearthstone window")
        hub_seen = False
        while True:
            observation = self.inspect_hearthstone()
            if observation.blocking_text:
                raise SafetyStop(f"stopped on Hearthstone safety screen: {observation.blocking_text}")
            if observation.start_available:
                self._event("Clicking observed 点击开始 control")
                self._click(observation._start_control)
                time.sleep(self.poll_seconds)
                continue
            if observation.home_evidence:
                return AutomationResult(str(battle_net), str(hearthstone), tuple(self.actions), observation.home_evidence)
            if logs_dir and self._latest_scene(logs_dir) is Scene.MENU:
                if not hub_seen:
                    self._event("LoadingScreen HUB scene observed; verifying four mode labels")
                    hub_seen = True
            time.sleep(self.poll_seconds)
