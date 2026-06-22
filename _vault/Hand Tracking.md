# Hand Tracking

## MediaPipe HandLandmarker

- Model: `hand_landmarker.task` (downloaded on first run from Google Storage)
- Detects **21 landmarks per hand** (x, y, z normalized coordinates)
- Supports up to 2 hands (`NUM_HANDS=2`)
- Running mode: IMAGE (single-frame detection, not video streaming)

### Landmark Index (key points)

| Index | Name | Use |
|-------|------|-----|
| 0 | WRIST | Trajectory reference |
| 4 | THUMB_TIP | Fingertip detection |
| 8 | INDEX_TIP | Primary tapping/reach tracking point |
| 12 | MIDDLE_TIP | — |
| 16 | RING_TIP | — |
| 20 | PINKY_TIP | — |

### Handedness Detection

MediaPipe returns handedness (Left/Right) per detected hand. The system uses this to separate left/right feature extraction.

## YOLO Validation (yolo_detector.py)

Added to reduce false positive hand detections from MediaPipe.

### How It Works

1. **YOLO person detection**: Run `yolov8n.pt` on each frame, filter for COCO class 0 (person)
2. **Landmark overlap check**: For each MediaPipe-detected hand, compute its bounding box from landmarks and check overlap with YOLO person boxes
3. **Filter**: Only keep hands with overlap ratio ≥ 0.15 (configurable via `YOLO_MIN_HAND_OVERLAP`)

### Why Person Detection Instead of Hand Detection?

- `yolov8n.pt` (COCO) is widely available, no custom training needed
- Person detection is more robust than hand-specific models
- Hands are always attached to persons in this use case (elderly assessment)
- Falls back gracefully if the YOLO model is missing (MediaPipe runs alone)

### Integration Point

`HandTracker.process_frame()` in `hand_tracker.py:25-32`:
1. MediaPipe detects hands → landmarks
2. If YOLO is available, `yolo.validate_hands()` filters results
3. Returns only validated hands

### Overlap Calculation

```
hand_bbox = [min(x), min(y), max(x), max(y)] from landmarks
for each person_bbox from YOLO:
    compute intersection area / hand area
keep hand if max_overlap >= threshold (0.15)
```

## Performance Notes

- YOLO adds ~10-30ms inference time on GPU, ~50-100ms on CPU
- MediaPipe adds ~5-15ms per frame
- Total: ~15-45ms per frame (GPU) or ~55-115ms (CPU)
- Webcam mode skips every other frame (webcam_step % 2 == 0) to maintain FPS
