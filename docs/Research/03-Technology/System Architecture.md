# System Architecture

**File:** `docs/Research/03-Technology/System Architecture.md`

---

## 1. Data Flow

```
Input Source (Upload / Webcam)
  │
  ▼
HandTracker.process_frame()
  │  ├── cv2.cvtColor(BGR → RGB)
  │  ├── MediaPipe HandLandmarker.detect()
  │  ├── _parse_result() → landmarks list
  │  └── [YOLO] yolo.validate_hands() → filter false positives
  │
  ▼
FeatureExtractor
  │  ├── extract_tapping_features() → speed, regularity, velocity, etc.
  │  └── extract_reach_features() → reach_time, path_efficiency, smoothness
  │
  ▼
DominanceClassifier.classify()
  │  ├── _dominance_score() → scalar diff (left vs right)
  │  ├── _performance_ratio() → weaker / stronger comparison
  │  └── Returns ClassificationResult with risk assessment
  │
  ▼
display_metrics() → Streamlit UI cards + comparison
```

---

## 2. Streamlit State Machine (Webcam Mode)

```
preview ──────→ countdown ──────→ recording ──────→ done
  ↑                                                     │
  └───────────────── "ทดสอบใหม่" button ─────────────────┘
```

| State | Description |
|-------|-------------|
| **preview** | Show setup overlay with posture guide; detect hands inside green zone; 8 consecutive in-zone detections to proceed |
| **countdown** | 3-2-1 countdown (0.7s per number at ~30 FPS) |
| **recording** | Capture frames for `duration` seconds; draw REC overlay; process every other frame |
| **done** | Display completion message + classification results |

---

## 3. Upload Mode Flow

```
User selects video file
  → tempfile save
  → process_video_progressive()
      → every 3rd frame: detect → extract → classify
      → live progress bar + frame preview
  → os.unlink(temp)
  → display_metrics()
  → save session / download PDF buttons
```

---

## 4. Session State Keys (`st.session_state`)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `cam_state` | str | `"preview"` | Webcam state machine |
| `result` | ClassificationResult | `None` | Final classification result |
| `rec_start` | float | — | Timestamp when recording started |
| `frame_count` | int | 0 | Frame counter during recording |
| `saved_session_id` | str | `None` | Last saved session ID |

---

## 5. Configuration (`src/config.py`)

| Parameter | Value | Description |
|-----------|-------|-------------|
| `NUM_HANDS` | 2 | Max hands to detect |
| `MIN_DETECTION_CONFIDENCE` | 0.5 | MediaPipe hand detection threshold |
| `MIN_TRACKING_CONFIDENCE` | 0.5 | MediaPipe tracking threshold |
| `YOLO_CONFIDENCE` | 0.5 | YOLO person detection threshold |
| `YOLO_MIN_HAND_OVERLAP` | 0.15 | Minimum hand-person overlap ratio |
| `TAP_ZONE_RADIUS` | 0.05 | Tap detection zone (normalized) |
| `MOVEMENT_FILTER_WINDOW` | 5 | Median filter kernel size |
| `MIN_TAP_DISTANCE` | 0.02 | Min distance between taps |

---

## 6. Dataclasses (`src/config.py`)

### `HandFeatures`
```
hand, tapping_speed, tap_count, tap_regularity, avg_amplitude,
avg_peak_velocity, reach_time, path_efficiency, endpoint_error,
movement_smoothness, range_of_motion, tremor_index, symmetry_index
```

### `ClassificationResult`
```
dominant_hand, learned_non_use_risk, is_learned_non_use,
confidence, details, left_features, right_features
```
