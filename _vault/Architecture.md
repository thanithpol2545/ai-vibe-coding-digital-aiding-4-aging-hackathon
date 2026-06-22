# System Architecture

## Data Flow

```
Input Source (Upload/Webcam)
  │
  ▼
HandTracker.process_frame()
  │  ├── cv2.cvtColor(BGR→RGB)
  │  ├── MediaPipe HandLandmarker.detect()
  │  ├── _parse_result() → landmarks list
  │  └── [YOLO] yolo.validate_hands() → filter false positives
  │
  ▼
FeatureExtractor
  │  ├── extract_tapping_features() → tapping_speed, regularity, velocity, etc.
  │  └── extract_reach_features() → reach_time, path_efficiency, smoothness
  │
  ▼
DominanceClassifier.classify()
  │  ├── _dominance_score() → scalar diff (left vs right)
  │  ├── _performance_ratio() → weaker/stronger comparison
  │  └── Returns ClassificationResult with risk assessment
  │
  ▼
display_metrics() → Streamlit UI cards + JSON
```

## Streamlit State Machine (Webcam Mode)

```
preview ───→ countdown ───→ recording ───→ done
  ↑                                              │
  └─────────── "ทดสอบใหม่" button ────────────────┘
```

- **preview**: Show setup overlay, detect hands in zone (8 consecutive in-zone detections to proceed)
- **countdown**: 3-2-1 countdown (0.7s per number, ~30 FPS)
- **recording**: Capture frames for `duration` seconds, draw recording overlay
- **done**: Show completion message, display results if available

## Session State Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `cam_state` | str | "preview" | Current webcam state machine state |
| `result` | ClassificationResult | None | Final classification result |
| `rec_start` | float | — | timestamp when recording started |
| `frame_count` | int | 0 | Frame counter during recording |
| `left_feats` | HandFeatures | {} | Left hand features |
| `right_feats` | HandFeatures | {} | Right hand features |

## Config (config.py)

- MediaPipe confidence thresholds: `MIN_DETECTION_CONFIDENCE=0.5`, `MIN_TRACKING_CONFIDENCE=0.5`
- YOLO: `yolov8n.pt`, conf=0.5, min hand overlap=0.15
- Feature extraction parameters: tap zone radius, filter window, min tap distance
