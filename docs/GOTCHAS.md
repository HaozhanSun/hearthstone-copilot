# Gotchas

- Hidden cards are normal: in `13619.log`, 37 of 72 card entities have no `card_id`. Render those as `??`; do not infer an identity.
- `PacketTree.export()` returns an exporter. The reconstructed `Game` is on `.game` after export.
