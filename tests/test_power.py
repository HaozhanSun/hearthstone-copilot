from __future__ import annotations

from pathlib import Path

import pytest

from hscopilot.perception.power import parse_power_log


FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_power_log_populates_decision_points() -> None:
    games = parse_power_log(FIXTURES / "13619.log")
    assert len(games) == 1
    assert len(games[0].decision_points) == 24
    assert all(point.legal_actions for point in games[0].decision_points)
    assert any(
        point.actual is not None and point.actual.option_id in {action.option_id for action in point.legal_actions}
        for point in games[0].decision_points
    )
