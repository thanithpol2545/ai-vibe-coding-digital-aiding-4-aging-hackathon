import numpy as np
import config
from features import FeatureExtractor


def _make_frame_data(fps=30, hand="Left", n_frames=30):
    frames = []
    for i in range(n_frames):
        t = i / fps
        y = 0.5 + 0.1 * np.sin(2 * np.pi * 2 * t)
        landmarks_norm = np.zeros((21, 3), dtype=float)
        landmarks_norm[config.WRIST] = [0.5, y, 0.0]
        landmarks_norm[config.INDEX_TIP] = [0.55, y - 0.05, 0.0]
        landmarks_norm[config.THUMB_TIP] = [0.48, y - 0.02, 0.0]
        for idx in config.FINGERTIPS:
            landmarks_norm[idx] = [0.5 + (idx - 4) * 0.01, y - 0.03, 0.0]

        frames.append({
            "frame": i,
            "time_sec": t,
            "hands": [{
                "hand": hand,
                "landmarks": landmarks_norm * 640,
                "landmarks_norm": landmarks_norm.copy(),
            }],
        })
    return {"fps": fps, "frames": frames}


def test_empty_data():
    ex = FeatureExtractor({"fps": 30, "frames": []})
    feats = ex.extract_all("Left", "tapping")
    assert feats.tap_count == 0
    assert feats.tapping_speed == 0.0


def test_extract_tapping():
    data = _make_frame_data(hand="Left")
    ex = FeatureExtractor(data)
    feats = ex.extract_all("Left", "tapping")
    assert feats.hand == "Left"
    assert feats.tap_count >= 1
    assert feats.tapping_speed > 0


def test_extract_reach():
    data = _make_frame_data(hand="Right")
    ex = FeatureExtractor(data)
    feats = ex.extract_all("Right", "reach")
    assert feats.hand == "Right"
    assert feats.reach_time >= 0


def test_symmetry_identical():
    raw = _make_frame_data(hand="Left")
    same_data = {"fps": raw["fps"], "frames": raw["frames"]}
    ex = FeatureExtractor(raw)
    same_ex = FeatureExtractor(same_data)
    left = ex.extract_all("Left", "tapping")
    right = same_ex.extract_all("Left", "tapping")
    sym = ex.compute_symmetry_index(left, right)
    assert sym == 0.0


def test_symmetry_asymmetric():
    left_data = _make_frame_data(hand="Left", n_frames=30)
    right_data = _make_frame_data(hand="Right", n_frames=30)
    merged = {
        "fps": 30,
        "frames": left_data["frames"] + right_data["frames"],
    }
    ex = FeatureExtractor(merged)
    left = ex.extract_all("Left", "tapping")
    ex2 = FeatureExtractor(merged)
    right = ex2.extract_all("Right", "tapping")
    sym = ex.compute_symmetry_index(left, right)
    assert sym >= 0


def test_velocity_computation():
    data = _make_frame_data(hand="Left")
    ex = FeatureExtractor(data)
    times, positions = ex._get_hand_trajectory("Left", config.WRIST)
    assert len(times) == len(positions)
    if len(positions) > 1:
        speed = ex._compute_velocity(times, positions)
        assert len(speed) > 0
        assert np.all(speed >= 0)
