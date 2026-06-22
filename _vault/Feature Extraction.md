# Feature Extraction

Class: `FeatureExtractor` in `features.py`

## Tapping Features (`extract_tapping_features`)

For finger tapping tests. Tracks **INDEX_TIP** landmark trajectory.

### Metrics

| Feature | Method | Description |
|---------|--------|-------------|
| `tapping_speed` | 1 / mean(inter-tap interval) | Taps per second |
| `tap_count` | `signal.find_peaks(-y_pos)` | Number of detected tap peaks |
| `tap_regularity` | 1 - std(interval)/mean(interval) | 1.0 = perfect rhythm, 0.0 = irregular |
| `avg_amplitude` | mean(peak - valley) in y-axis | Vertical tap displacement |
| `avg_peak_velocity` | mean(speed > 80th percentile) | High-velocity movement bursts |
| `path_efficiency` | straight_dist / total_dist | 1.0 = straight line, 0.0 = inefficient |
| `movement_smoothness` | SPARC (negative log spectral rolloff) | Higher = smoother movement |
| `tremor_index` | high_freq_energy / low_freq_energy | Higher = more tremor |
| `endpoint_error` | mean distance of tap endpoints from origin | Spatial consistency (note: currently from (0,0), not meaningful) |
| `range_of_motion` | peak-to-peak y displacement | Movement range |

### Peak Detection

- Uses `scipy.signal.find_peaks` on inverted y-position
- Minimum distance: `max(3, fps//10)` frames
- Minimum prominence: 0.005 (in normalized coordinates)

## Reach Features (`extract_reach_features`)

For reach-to-target tests.

| Feature | Method | Description |
|---------|--------|-------------|
| `avg_peak_velocity` | max(speed) | Peak reach velocity |
| `reach_time` | time at max velocity - start time | Time to peak speed |
| `path_efficiency` | straight_dist / total_dist | Reach directness |
| `movement_smoothness` | Jerk cost (sum of squared jerk) | Lower = smoother |
| `range_of_motion` | max distance from start position | Reach extent |

## Symmetry Index (`compute_symmetry_index`)

```
symmetry = mean(|L - R| / max(|L|,|R|, 1e-10)) over keys:
    tapping_speed, tap_regularity, path_efficiency, movement_smoothness, range_of_motion
```

- 0.0 = perfect symmetry  
- Higher = more asymmetric

## Frame Data Structure

```python
{
    "fps": 30,
    "total_frames": 0,
    "frames": [
        {
            "frame": 0,          # frame index
            "time_sec": 0.0,     # elapsed time in seconds
            "hands": [
                {
                    "hand": "Left",
                    "landmarks": np.array([[x, y, z], ...]),  # 21x3 pixel coords
                    "landmarks_norm": np.array([[x, y, z], ...]),  # 21x3 normalized [0,1]
                    "yolo_validated": True,   # added by YOLO validation
                    "yolo_overlap": 0.85,     # overlap ratio with person
                }
            ]
        }
    ]
}
```
