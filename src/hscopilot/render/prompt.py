from hscopilot.perception.snapshot import GameSnapshot


def snapshot_prompt(snapshot: GameSnapshot) -> str:
    return snapshot.to_json()
