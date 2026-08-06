# Gotchas

- Hidden cards are normal: in `13619.log`, 37 of 72 card entities have no `card_id`. Render those as `??`; do not infer an identity.
- `PacketTree.export()` returns an exporter. The reconstructed `Game` is on `.game` after export.
- Windows installs may be on a non-system drive. Discover Battle.net/Hearthstone through uninstall registry metadata before standard paths; do not hardcode `C:` or another drive.
- Hearthstone rotates `Logs/` into timestamped subdirectories and can truncate/recreate `Power.log`; the tailer must reselect the newest file and reset its offset on replacement.
- Launcher execution is intentionally gated: dry-run is the default, and real Battle.net Play clicks require explicit coordinates plus `--execute`.
- A real launcher run needs the current Battle.net Play-button coordinates; the coordinate is deliberately not guessed from a screenshot.
- The debug UI opening flow does not use Play coordinates. On Windows it requires the `windows` extra (`pywinauto` and `rapidocr-onnxruntime`) and invokes only freshly observed UI Automation controls; rendered Hearthstone controls are clicked from a fresh local OCR bounding box.
