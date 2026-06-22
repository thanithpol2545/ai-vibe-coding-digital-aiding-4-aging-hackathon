# Classification

Class: `DominanceClassifier` in `classifier.py`

## Algorithm — Rule-Based Threshold Classifier

No ML model. Uses heuristic rules based on feature asymmetry.

### Step 1: Dominance Score

```python
score = (R_tapping_speed - L_tapping_speed)
      + (R_tap_regularity - L_tap_regularity)
      + (R_path_efficiency - L_path_efficiency)
      - (R_tremor - L_tremor) * 0.5
```

- `score < 0` → Left dominant
- `score > 0` → Right dominant
- `confidence = min(abs(score) * 2, 0.99)`

### Step 2: Performance Ratio

Compare weaker hand vs stronger hand across 4 metrics:
- tapping_speed, tap_regularity, path_efficiency, range_of_motion

```python
ratio = mean(weaker_val / max(stronger_val, 1e-10))
```

### Step 3: Risk Classification

| Condition | LNU Risk | Classification |
|-----------|----------|----------------|
| Stronger hand not tested | 0% | Insufficient data |
| Weaker hand not tested | capped at 20% | Limited data warning |
| Weaker ratio < 0.55 | 0.55-0.95 | **Learned Non-Use** |
| Mean asymmetry > 0.30 | 0-50% | Moderate asymmetry |
| Otherwise | 0-30% | Normal variation |

### Thresholds

- `asymmetry_threshold = 0.30`: Above this = moderate asymmetry
- `non_use_threshold = 0.45`: Weaker hand performs < 55% of stronger = LNU flag

## Known Issue

When `diff == 0` (perfectly equal hands):
- `dominant_hand = "Right"` but `stronger_hand = "Left"` — contradictory
- Edge case: extremely rare in practice but a latent logic bug
