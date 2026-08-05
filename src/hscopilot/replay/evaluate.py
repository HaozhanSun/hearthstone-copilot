from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hscopilot.advisor.heuristic import HeuristicAdvisor
from hscopilot.legality.options import LegalAction
from hscopilot.perception.power import parse_power_log


def evaluate(corpus_dir: str | Path) -> dict[str, Any]:
    root = Path(corpus_dir)
    advisor = HeuristicAdvisor()
    rows = []
    for log in sorted(root.glob("*.log")):
        snapshot = parse_power_log(log)
        actions = tuple(LegalAction(**a) for a in snapshot.legal_actions)
        advice = advisor.advise(snapshot, actions) if actions else None
        expected_path = log.with_suffix(".json")
        expected = json.loads(expected_path.read_text()) if expected_path.exists() else {}
        rows.append({"file": log.name, "action_index": advice.action_index if advice else None,
                     "expected": expected.get("action_index"),
                     "correct": advice is not None and advice.action_index == expected.get("action_index") if expected else None})
    scored = [r for r in rows if r["correct"] is not None]
    return {"cases": rows, "accuracy": (sum(r["correct"] for r in scored) / len(scored)) if scored else None}
