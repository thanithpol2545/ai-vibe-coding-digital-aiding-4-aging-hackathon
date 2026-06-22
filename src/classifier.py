import numpy as np
from typing import Optional, Tuple
import config


class DominanceClassifier:
    def __init__(self, asymmetry_threshold=0.3, non_use_threshold=0.45):
        self.asymmetry_threshold = asymmetry_threshold
        self.non_use_threshold = non_use_threshold

    def _normalize(self, left_val: float, right_val: float) -> Tuple[float, float]:
        denom = max(abs(left_val), abs(right_val), 1e-10)
        return left_val / denom, right_val / denom

    def _dominance_score(self, left: config.HandFeatures, right: config.HandFeatures) -> float:
        score = 0.0
        l_speed, r_speed = self._normalize(left.tapping_speed, right.tapping_speed)
        score += r_speed - l_speed
        l_reg, r_reg = self._normalize(left.tap_regularity, right.tap_regularity)
        score += r_reg - l_reg
        l_eff, r_eff = self._normalize(left.path_efficiency, right.path_efficiency)
        score += r_eff - l_eff
        score -= (right.tremor_index - left.tremor_index) * 0.5
        return score

    def _hand_was_tested(self, feats: config.HandFeatures) -> bool:
        return feats.tap_count >= 2 or feats.tapping_speed > 0.01 or feats.range_of_motion > 0.05

    def classify(self, left: config.HandFeatures, right: config.HandFeatures) -> config.ClassificationResult:
        result = config.ClassificationResult(left_features=left, right_features=right)
        diff = self._dominance_score(left, right)

        asymmetry_scores = {}
        keys = {
            "tapping_speed": (left.tapping_speed, right.tapping_speed, True),
            "tap_regularity": (left.tap_regularity, right.tap_regularity, True),
            "movement_smoothness": (left.movement_smoothness, right.movement_smoothness, True),
            "range_of_motion": (left.range_of_motion, right.range_of_motion, True),
            "tremor_index": (left.tremor_index, right.tremor_index, False),
        }

        for k, (lv, rv, higher_better) in keys.items():
            denom = max(abs(lv), abs(rv), 1e-10)
            asymmetry = abs(lv - rv) / denom
            asymmetry_scores[k] = asymmetry

        mean_asymmetry = np.mean(list(asymmetry_scores.values()))

        result.dominant_hand = "Left" if diff < 0 else "Right"
        result.confidence = float(min(abs(diff) * 2, 0.99))

        weaker_hand = "Left" if diff > 0 else "Right"
        stronger_hand = "Right" if diff > 0 else "Left"
        weaker_feats = left if weaker_hand == "Left" else right
        stronger_feats = right if weaker_hand == "Left" else left

        weaker_tested = self._hand_was_tested(weaker_feats)
        stronger_tested = self._hand_was_tested(stronger_feats)

        if not stronger_tested:
            result.details = (
                f"ตรวจไม่พบมือเพียงพอ ตรวจสอบให้แน่ใจว่ามือทั้งสองข้างอยู่ในเฟรมและมีการเคลื่อนไหว"
            )
            result.learned_non_use_risk = 0.0
            return result

        if not weaker_tested:
            result.learned_non_use_risk = float(min(mean_asymmetry * 0.3, 0.2))
            result.details = (
                f"ข้อมูลมือ{weaker_hand}มีจำกัด ({weaker_feats.tap_count} ครั้ง). "
                f"ควรทดสอบมือทั้งสองข้างเท่าๆ กันเพื่อความแม่นยำ. "
                f"มือที่ถนัด: {result.dominant_hand}."
            )
            return result

        weaker_pct = self._performance_ratio(left, right, weaker_hand)

        if weaker_pct < (1.0 - self.non_use_threshold):
            result.is_learned_non_use = True
            result.learned_non_use_risk = float(min(1.0 - weaker_pct, 0.95))
            result.details = (
                f"พบช่องว่างประสิทธิภาพที่มีนัยสำคัญ. "
                f"มือ{weaker_hand} ทำได้ {weaker_pct*100:.0f}% ของมือ{stronger_hand}. "
                f"อาจมีภาวะ Learned Non-Use — แนะนำให้พบแพทย์."
            )
        elif mean_asymmetry > self.asymmetry_threshold:
            result.learned_non_use_risk = float(min(mean_asymmetry * 0.8, 0.5))
            result.details = (
                f"ความไม่สมมาตรปานกลาง (ดัชนี={mean_asymmetry:.2f}). "
                f"มือที่ถนัด: {result.dominant_hand}. "
                f"ควรติดตามรูปแบบการไม่ใช้นี้."
            )
        else:
            result.learned_non_use_risk = float(min(mean_asymmetry * 0.5, 0.3))
            result.details = (
                f"รูปแบบความไม่สมมาตรปกติ. "
                f"มือที่ถนัด: {result.dominant_hand}. "
                f"ความแตกต่างอยู่ในช่วงที่คาดหวัง."
            )

        return result

    def _performance_ratio(self, left: config.HandFeatures, right: config.HandFeatures, weaker: str) -> float:
        stronger_feats = right if weaker == "Left" else left
        weaker_feats = left if weaker == "Left" else right
        ratios = []
        for k in ["tapping_speed", "tap_regularity", "path_efficiency", "range_of_motion"]:
            sv = getattr(stronger_feats, k, 0.0)
            wv = getattr(weaker_feats, k, 0.0)
            denom = max(sv, 1e-10)
            ratios.append(min(wv / denom, 1.0))
        return float(np.mean(ratios))
