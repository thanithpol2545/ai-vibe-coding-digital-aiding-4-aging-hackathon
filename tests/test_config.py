import config


def test_hand_features_defaults():
    hf = config.HandFeatures(hand="Left")
    assert hf.hand == "Left"
    assert hf.tapping_speed == 0.0
    assert hf.tap_count == 0
    assert hf.tap_regularity == 0.0
    assert hf.symmetry_index == 0.0


def test_hand_features_right():
    hf = config.HandFeatures(hand="Right")
    assert hf.hand == "Right"


def test_classification_result_defaults():
    cr = config.ClassificationResult()
    assert cr.dominant_hand == ""
    assert cr.learned_non_use_risk == 0.0
    assert cr.is_learned_non_use is False
    assert cr.confidence == 0.0
    assert cr.left_features.hand == "Left"
    assert cr.right_features.hand == "Right"


def test_constants():
    assert config.NUM_HANDS == 2
    assert config.WRIST == 0
    assert config.THUMB_TIP == 4
    assert config.INDEX_TIP == 8
    assert len(config.FINGERTIPS) == 5
    assert len(config.FINGER_MCPS) == 5
