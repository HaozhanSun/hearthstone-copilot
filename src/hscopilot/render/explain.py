from hscopilot.advisor.base import Advice


def explain(advice: Advice) -> str:
    return f"Action {advice.action_index} (confidence {advice.confidence:.2f}): {advice.rationale}"
