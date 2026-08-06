# Decisions

- Decision points are captured during exporter dispatch so each frozen snapshot reflects the game state immediately before its `Options` packet.
- `Option.id` is the action identity; list position is not stable and must not be used for matching `SendOption.option`.
