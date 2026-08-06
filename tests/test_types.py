from dataclasses import FrozenInstanceError

from hscopilot.legality.options import LegalAction
from hscopilot.perception.decision import ActualChoice, DecisionPoint, GameMeta, ReplayGame
from hscopilot.perception.snapshot import EntitySnapshot, GameSnapshot


def test_snapshot_round_trip_is_exact() -> None:
    original = GameSnapshot(scene="play", turn=4, entities=(EntitySnapshot(7, None, ((2, 9), (1, 4))),))
    assert GameSnapshot.from_dict(original.to_dict()) == original


def test_round_trip_preserves_tuple_types() -> None:
    restored = GameSnapshot.from_dict(GameSnapshot(entities=(EntitySnapshot(1, "CARD", ((3, 8),)),)).to_dict())
    assert isinstance(restored.entities, tuple)
    assert isinstance(restored.entities[0].tags, tuple)


def test_identical_boards_hash_equal() -> None:
    left = GameSnapshot(entities=(EntitySnapshot(1, "CARD", ((1, 2),)),))
    right = GameSnapshot(entities=(EntitySnapshot(1, "CARD", ((1, 2),)),))
    assert left.snapshot_hash == right.snapshot_hash


def test_different_turn_hashes_differ() -> None:
    assert GameSnapshot(turn=1).snapshot_hash != GameSnapshot(turn=2).snapshot_hash


def test_replay_game_round_trip_is_exact() -> None:
    point = DecisionPoint(0, GameSnapshot(), (LegalAction(3, optype="POWER", sub_option_ids=(4,)),), ActualChoice(3, target=8))
    original = ReplayGame(GameMeta("fixture", ("A", "B")), (point,))
    assert ReplayGame.from_dict(original.to_dict()) == original


def test_frozen_blocks_normal_assignment() -> None:
    snapshot = GameSnapshot()
    try:
        snapshot.scene = "play"
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("frozen snapshot accepted assignment")


def test_slots_block_undeclared_attributes() -> None:
    snapshot = GameSnapshot()
    try:
        snapshot.actual_choices = ()
    except (AttributeError, TypeError):
        pass
    else:
        raise AssertionError("slotted snapshot accepted undeclared attribute")


def test_to_dict_keys_match_declared_fields() -> None:
    assert set(GameSnapshot().to_dict()) == {"version", "scene", "turn", "entities"}
    assert set(LegalAction(1).to_dict()) == {"option_id", "entity", "optype", "sub_option_ids"}
