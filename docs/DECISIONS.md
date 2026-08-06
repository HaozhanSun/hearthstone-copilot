# Decisions

- Decision points are captured during exporter dispatch so each frozen snapshot reflects the game state immediately before its `Options` packet.
- `Option.id` is the action identity; list position is not stable and must not be used for matching `SendOption.option`.
- `log.config` updates are additive and backed up before writing; `hscopilot write-log-config --dry-run` never writes.
- Live parsing uses hslog's line-oriented `read_line` and exports only at `GameState.SendOption()` boundaries, avoiding repeated full-tree exports for every tag line.
- Scene detection trusts `LoadingScreen.OnSceneLoaded()` `currMode` values; arbitrary substrings such as “arena” are not scene evidence.
