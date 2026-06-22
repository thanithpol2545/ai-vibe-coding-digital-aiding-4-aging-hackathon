# YOLO Integration

Module: `yolo_detector.py`  
Integrated into: `hand_tracker.py`  

## Purpose

MediaPipe HandLandmarker can produce false positives on textures/patterns that vaguely resemble hands. YOLO person detection acts as a spatial gatekeeper: if no person is detected in the frame region where MediaPipe found a hand, that hand is likely a false positive.

## Implementation

```python
class YOLODetector:
    def __init__(self, model_path="yolov8n.pt", conf_threshold=0.5, iou_threshold=0.5)
    def detect_persons(frame) → [{"bbox": (x1,y1,x2,y2), "confidence": float}]
    def validate_landmarks(landmarks, person_boxes) → (is_valid, overlap_ratio)
    def validate_hands(hands_data, frame) → [validated_hands]
```

### Configuration (config.py)

```python
YOLO_MODEL_PATH = "yolov8n.pt"
YOLO_CONFIDENCE = 0.5
YOLO_IOU = 0.5
YOLO_MIN_HAND_OVERLAP = 0.15
```

### Integration Points

1. **HandTracker.__init__**: YOLO initialized as optional component
2. **HandTracker.process_frame**: After MediaPipe, before returning — YOLO filters hands
3. **yolo_detector.py**: Standalone module, can be used independently

### Data Flow

```
frame (BGR)
  → MediaPipe → hands_data (list of hand dicts with landmarks)
  → YOLO → person_boxes
  → For each hand: compute hand_bbox from landmarks
  → Compute overlap with each person_bbox
  → Keep hands with overlap >= MIN_HAND_OVERLAP
  → Return filtered list
```

### Fallback

If `ultralytics` is not installed or the model file is missing:
- YOLO initialization fails gracefully
- `self.yolo` remains `None`
- MediaPipe runs without validation
- No crash — just reduced false positive rejection

## Dependency

Add `ultralytics>=8.0.0` to `requirements.txt`.  
First run auto-downloads `yolov8n.pt` (~6MB) from Ultralytics.
