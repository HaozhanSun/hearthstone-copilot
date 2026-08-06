# Decisions

- Decision points are captured during exporter dispatch so each frozen snapshot reflects the game state immediately before its `Options` packet.
- `Option.id` is the action identity; list position is not stable and must not be used for matching `SendOption.option`.
- `log.config` updates are additive and backed up before writing; `hscopilot write-log-config --dry-run` never writes.
- Live parsing uses hslog's line-oriented `read_line` and exports only at `GameState.SendOption()` boundaries, avoiding repeated full-tree exports for every tag line.
- Scene detection trusts `LoadingScreen.OnSceneLoaded()` `currMode` values; arbitrary substrings such as “arena” are not scene evidence.
- The debug UI is localhost-only by default and discrepancy reports are written only when a fixture directory is explicitly supplied.
- Actuation defaults to `DryRunActuator`; native clicks require explicit construction/enabling and the launcher requires `--execute` plus Play coordinates.
- The launcher verifies Battle.net process, window title, Hearthstone process, and `PLAY` scene from `LoadingScreen.log`; it does not sleep-and-assume success.
- The debug UI serves a supplied screenshot through a local-only route and never captures or uploads images itself.
