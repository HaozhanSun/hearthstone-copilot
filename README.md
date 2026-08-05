# Hearthstone Copilot

This repository is now a read-only Hearthstone advisory and replay-analysis core. It deliberately does not inject into the client, click the game, or use screen OCR as primary perception.

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
```

The heuristic advisor is a zero-cost baseline. Live advisory and a localhost WebSocket UI can be added on the same pipeline; automation/input control is intentionally out of scope.
