import os, json
import config
from session import new_session_id, save_session, load_session, list_sessions, SESSION_DIR


def _make_mock_result():
    cls_result = config.ClassificationResult
    hf = config.HandFeatures
    result = cls_result(
        dominant_hand="Right",
        learned_non_use_risk=0.15,
        is_learned_non_use=False,
        confidence=0.85,
        details="Normal asymmetry pattern.",
        left_features=hf(hand="Left", tapping_speed=1.2, tap_count=15, tap_regularity=0.85, movement_smoothness=1.5, range_of_motion=0.4, tremor_index=0.6),
        right_features=hf(hand="Right", tapping_speed=2.1, tap_count=22, tap_regularity=0.92, movement_smoothness=2.0, range_of_motion=0.5, tremor_index=0.4),
    )
    result.left_features.symmetry_index = 0.12
    result.right_features.symmetry_index = 0.12
    return result


def test_new_session_id():
    sid1 = new_session_id()
    sid2 = new_session_id()
    assert sid1 != sid2
    assert len(sid1) == 12


def test_save_and_load():
    result = _make_mock_result()
    sid = save_session("Test Patient", 70, "Testing session persistence", result)
    assert sid is not None
    assert os.path.exists(os.path.join(SESSION_DIR, f"{sid}.json"))

    loaded = load_session(sid)
    assert loaded is not None
    assert loaded["patient"]["name"] == "Test Patient"
    assert loaded["patient"]["age"] == 70
    assert loaded["result"]["dominant_hand"] == "Right"
    assert loaded["result"]["learned_non_use_risk"] == 0.15


def test_list_sessions():
    result = _make_mock_result()
    save_session("List Test", 65, "", result)
    sessions = list_sessions(5)
    assert len(sessions) >= 1
    found = any(s["patient_name"] == "List Test" for s in sessions)
    assert found


def test_load_nonexistent():
    loaded = load_session("nonexistent123")
    assert loaded is None
