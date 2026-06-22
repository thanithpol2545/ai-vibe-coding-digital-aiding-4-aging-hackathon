import pytest
import config
from classifier import DominanceClassifier


def _make_feats(hand, speed=1.0, reg=1.0, eff=1.0, smooth=1.0, rom=0.5, tremor=0.5, taps=10):
    return config.HandFeatures(
        hand=hand,
        tapping_speed=speed,
        tap_count=taps,
        tap_regularity=reg,
        path_efficiency=eff,
        movement_smoothness=smooth,
        range_of_motion=rom,
        tremor_index=tremor,
    )


def test_right_dominant():
    cls = DominanceClassifier()
    left = _make_feats("Left", speed=1.0)
    right = _make_feats("Right", speed=2.0)
    result = cls.classify(left, right)
    assert result.dominant_hand == "Right"
    assert result.confidence > 0


def test_left_dominant():
    cls = DominanceClassifier()
    left = _make_feats("Left", speed=2.0)
    right = _make_feats("Right", speed=1.0)
    result = cls.classify(left, right)
    assert result.dominant_hand == "Left"


def test_symmetric_hands():
    cls = DominanceClassifier()
    left = _make_feats("Left", speed=1.5, reg=0.9, eff=0.8, smooth=1.2)
    right = _make_feats("Right", speed=1.5, reg=0.9, eff=0.8, smooth=1.2)
    result = cls.classify(left, right)
    assert result.is_learned_non_use is False
    assert result.learned_non_use_risk < 0.5


def test_no_detection_returns_zero_risk():
    cls = DominanceClassifier()
    left = _make_feats("Left", taps=0, speed=0.0)
    right = _make_feats("Right", taps=0, speed=0.0)
    result = cls.classify(left, right)
    assert result.learned_non_use_risk == 0.0


def test_lnu_detection():
    cls = DominanceClassifier()
    left = _make_feats("Left", speed=0.3, reg=0.2, eff=0.2, smooth=0.1, taps=2)
    right = _make_feats("Right", speed=3.0, reg=0.95, eff=0.9, smooth=2.0, taps=20)
    result = cls.classify(left, right)
    assert result.dominant_hand == "Right"
    assert result.learned_non_use_risk > 0


def test_performance_ratio_identical():
    cls = DominanceClassifier()
    left = _make_feats("Left", speed=1.0, reg=1.0)
    right = _make_feats("Right", speed=1.0, reg=1.0)
    ratio = cls._performance_ratio(left, right, "Left")
    assert ratio == pytest.approx(1.0, abs=0.05)

    ratio2 = cls._performance_ratio(left, right, "Right")
    assert ratio2 == pytest.approx(1.0, abs=0.05)


def test_features_stored_in_result():
    cls = DominanceClassifier()
    left = _make_feats("Left", speed=1.0)
    right = _make_feats("Right", speed=2.0)
    result = cls.classify(left, right)
    assert result.left_features.hand == "Left"
    assert result.right_features.hand == "Right"
