from __future__ import annotations

from pathlib import Path

from hscopilot.perception.live import replay_incrementally
from hscopilot.perception.power import parse_power_log


def test_incremental_fixture_matches_batch() -> None:
    fixture = Path(__file__).parent / "fixtures" / "13619.log"
    incremental = replay_incrementally(fixture, chunk_size=7)
    batch = parse_power_log(fixture)[0].decision_points
    assert len(incremental) == len(batch) == 24
