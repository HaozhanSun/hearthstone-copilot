# Hearthstone Copilot

This repository contains a log-first Hearthstone advisory core and an explicitly user-triggered Windows opening-flow debugger. The debugger uses Windows UI Automation for Battle.net controls and local OCR only when Hearthstone renders a control without an accessibility node; it does not inject into the game client.

## Architecture

`Power.log` is tailed or replayed through `hslog` into an immutable, versioned `GameSnapshot`. `LoadingScreen.log` drives a small scene FSM. Server-provided `Options`/`Choices` packets become `LegalAction[]`; advisors may select an index only. Card definitions come from `hearthstone_data`/CardDefs rather than a hand-maintained card JSON.

The package layout follows the redesign brief:

```
src/hscopilot/
  perception/  logconfig.py tailer.py power.py scene.py snapshot.py
  knowledge/   cards.py meta.py (future)
  legality/    options.py validate.py
  advisor/     base.py heuristic.py llm.py search.py ensemble.py (future)
  render/      prompt.py explain.py
  server/      app.py
  replay/      corpus.py (future) evaluate.py
```

## Commands

```powershell
uv sync
uv run hscopilot snapshot path\to\Power.log
uv run hscopilot replay-evaluate fixtures\
uv run hscopilot write-log-config path\to\log.config
uv run hscopilot debug-ui
```

The heuristic advisor is a zero-cost baseline. The localhost debug UI includes screenshot paste, discrepancy reporting, and an explicit Launch Hearthstone action. The opening flow re-observes before every action, closes only the approved Battle.net “What’s New?” modal, clicks a named Play control, recognizes the rendered `点击开始` control through local OCR, and verifies four home-screen mode labels.
The debug UI also exposes explicit Close Hearthstone and Close Battle.net actions for returning to a clean Windows desktop before a fresh launch.

On Windows, the native desktop app can be built with `powershell -ExecutionPolicy Bypass -File packaging/windows/build_debug_ui_app.ps1` and installed with `powershell -ExecutionPolicy Bypass -File packaging/windows/install_desktop_shortcut.ps1`. Double-click `Hearthstone Copilot Debug UI` on the Desktop; the Launch and Close buttons then run through the same local debug-UI worker.
