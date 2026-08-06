# Gotchas

- Hidden cards are normal: in `13619.log`, 37 of 72 card entities have no `card_id`. Render those as `??`; do not infer an identity.
- `PacketTree.export()` returns an exporter. The reconstructed `Game` is on `.game` after export.
- Windows installs may be on a non-system drive. Discover Battle.net/Hearthstone through uninstall registry metadata before standard paths; do not hardcode `C:` or another drive.
- Hearthstone rotates `Logs/` into timestamped subdirectories and can truncate/recreate `Power.log`; the tailer must reselect the newest file and reset its offset on replacement.
