import numpy as np
import config
from features import FeatureExtractor


def _make_frame_data_with_pose(fps=30, n_frames=30):
    frames = []
    for i in range(n_frames):
        t = i / fps
        progress = i / n_frames
        angle = 60 + 100 * progress  # goes from 60 to 160 degrees
        left_elbow = angle + np.random.normal(0, 2)
        right_elbow = angle + np.random.normal(0, 2)
        left_dist = 100 + 200 * progress
        right_dist = 100 + 200 * progress
        frames.append({
            "frame": i,
            "time_sec": t,
            "hands": [],
            "arm_angles": {
                "left_elbow_angle": float(left_elbow),
                "right_elbow_angle": float(right_elbow),
                "left_reach_distance": float(left_dist),
                "right_reach_distance": float(right_dist),
            },
        })
    return {"fps": fps, "frames": frames}


def test_extract_arm_features_left():
    data = _make_frame_data_with_pose()
    ex = FeatureExtractor(data)
    feats = ex.extract_arm_features("Left")
    assert feats is not None
    assert feats.hand == "Left"
    assert feats.range_of_motion > 80
    assert feats.reach_time >= 0


def test_extract_arm_features_right():
    data = _make_frame_data_with_pose()
    ex = FeatureExtractor(data)
    feats = ex.extract_arm_features("Right")
    assert feats is not None
    assert feats.hand == "Right"
    assert feats.range_of_motion > 80


def test_arm_features_no_pose():
    ex = FeatureExtractor({"fps": 30, "frames": [{"frame": 0, "time_sec": 0.0, "hands": []}]})
    feats = ex.extract_arm_features("Left")
    assert feats is None


def test_pose_constants():
    assert config.LEFT_SHOULDER == 11
    assert config.RIGHT_SHOULDER == 12
    assert config.LEFT_ELBOW == 13
    assert config.RIGHT_ELBOW == 14
    assert config.LEFT_WRIST == 15
    assert config.RIGHT_WRIST == 16
    assert len(config.ARM_LANDMARKS) == 6
    assert config.ARM_EXTENSION_ANGLE == 160
