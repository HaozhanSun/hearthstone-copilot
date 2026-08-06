from __future__ import annotations

from pathlib import Path

import pytest

from hscopilot.perception.power import parse_power_log


FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize(
    "filename",
    (
        "10357.log",
        "13619.log",
        "2016-02-04_TagChangeEntityBug.Power.log",
    ),
)
@pytest.mark.xfail(
    strict=True,
    reason="power.py still returns per-game flattened snapshots; rewired to DecisionPoint in Step 3",
)
def test_parse_power_log_populates_snapshots(filename: str) -> None:
    snapshots = parse_power_log(FIXTURES / filename)

    assert len(snapshots) >= 1
    assert len(snapshots[0].entities) > 0
    for action in snapshots[0].legal_actions:
        assert action.get("error") is None
