# MediaPipe Hand Tracking for Rehabilitation — การใช้ AI ตรวจจับมือเพื่อการฟื้นฟู

> **Google MediaPipe Hand Landmarker — real-time hand tracking 21 landmarks**
> ใช้ ML เพื่อ infer 3D hand keypoints จาก single RGB frame

---

## 1. ภาพรวม MediaPipe Hands

| หัวข้อ | รายละเอียด |
|-------|-----------|
| **พัฒนาโดย** | Google |
| **เทคโนโลยี** | Convolutional Neural Network (CNN) |
| **Output** | 21 3D landmarks ต่อ 1 มือ |
| **Performance** | Real-time บน mobile device |
| **Multi-hand** | รองรับหลายมือ |
| **Input** | Single RGB frame |

---

## 2. 21 Hand Landmarks

```
   4 (Thumb Tip)
   3 (Thumb IP)
   2 (Thumb MCP)
   1 (Thumb CMC)

   8 (Index Tip)
   7 (Index DIP)
   6 (Index PIP)
   5 (Index MCP)

   12 (Middle Tip)
   11 (Middle DIP)
   10 (Middle PIP)
    9 (Middle MCP)

   16 (Ring Tip)
   15 (Ring DIP)
   14 (Ring PIP)
   13 (Ring MCP)

   20 (Little Tip)
   19 (Little DIP)
   18 (Little PIP)
   17 (Little MCP)

    0 (Wrist)
```

**โครงสร้าง:**
```
0: Wrist (ข้อมือ)
1-4: Thumb (นิ้วโป้ง) — CMC, MCP, IP, Tip
5-8: Index (นิ้วชี้) — MCP, PIP, DIP, Tip
9-12: Middle (นิ้วกลาง) — MCP, PIP, DIP, Tip
13-16: Ring (นิ้วนาง) — MCP, PIP, DIP, Tip
17-20: Little (นิ้วก้อย) — MCP, PIP, DIP, Tip
```

---

## 3. ML Pipeline

```
Stage 1: Palm Detection
  └── Input: Full image
  └── Output: Oriented hand bounding box
  └── Model size: 1.76M parameters

Stage 2: Hand Landmark Model
  └── Input: Cropped hand region
  └── Output: 21 3D keypoints
  └── Model size: 2.01M parameters
```

---

## 4. Clinical Validation

### 4.1 Amprimo et al. (2023) — arXiv:2308.01088
**Hand tracking for clinical applications: validation of GMH and GMH-D**

| ข้อค้นพบ | รายละเอียด |
|---------|-----------|
| **Tasks tested** | Hand Opening-Closing, Single Finger Tapping, Multiple Finger Tapping |
| **Gold standard** | Marker-based motion capture |
| **GMH accuracy** | High temporal & spectral consistency |
| **GMH-D (depth-enhanced)** | Superior spatial accuracy |
| **Conclusion** | GMH-D = reliable framework for clinical 3D hand assessment |

### 4.2 MDPI Sensors (2025) — Markerless vs Marker-Based
| ข้อค้นพบ | รายละเอียด |
|---------|-----------|
| **Setup** | 4 Logitech C920 cameras, 30Hz |
| **MediaPipe version** | 0.10.15 |
| **Valid for** | Clinical hand movement analysis |
| **Limitation** | 2D-only, depth inference indirect |

### 4.3 Validation Metrics ที่เกี่ยวข้อง
| Metric | GMH | GMH-D | Gold Standard |
|--------|-----|-------|---------------|
| Temporal consistency | ✅ High | ✅ High | — |
| Spectral consistency | ✅ High | ✅ High | — |
| Spatial accuracy (x,y) | ✅ Good | ✅ Better | Excellent |
| Spatial accuracy (z-depth) | ⚠️ Limited | ✅ Good | Excellent |
| Slow movements | ✅ Good | ✅ Good | Excellent |
| Fast movements | ⚠️ Reduced | ✅ Good | Excellent |

---

## 5. Metrics ที่ Extract ได้จาก MediaPipe

| Metric | Method |
|--------|--------|
| **Finger angles** | Angle between vectors (MCP-PIP-DIP landmarks) |
| **Fingertip velocity** | Δposition / Δtime for landmarks 4,8,12,16,20 |
| **Range of Motion (ROM)** | Min/max joint angle across frames |
| **Movement smoothness** | Jerk = 3rd derivative of position |
| **Hand aperture** | Distance from thumb tip (4) to each finger tip |
| **Hand symmetry** | Cross-correlation of L vs R landmark trajectories |
| **Tremor** | FFT of fingertip position signal |
| **Reaction time** | Time from start to movement initiation |

---

## 6. การประยุกต์ใช้กับ Hackathon

### 6.1 Pipeline
```python
# Pseudocode
cap = cv2.VideoCapture("video.mp4")
detector = HandLandmarker.create_from_options(options)

while cap.isOpened():
    ret, frame = cap.read()
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = detector.detect(mp_image)
    
    for hand_landmarks in result.hand_landmarks:
        # 21 landmarks per hand → extract features
        fingertip_8 = hand_landmarks[8]  # Index finger tip
        wrist = hand_landmarks[0]        # Wrist
        # Calculate speed, accuracy, quality
```

### 6.2 Features ที่ควร Implement
- [ ] Real-time landmark tracking
- [ ] Fingertip trajectory smoothing (Savitzky-Golay filter)
- [ ] Velocity and acceleration profiles
- [ ] Joint angle calculation
- [ ] Hand aperture over time
- [ ] Smoothness (SPARC / Log Dim Jerk)
- [ ] Bilateral comparison
- [ ] Dominance prediction

### 6.3 ที่เก็บไฟล์
- Script: `src/analyze_hands.py`
- Results: `04-Analysis/hand_analysis.json`
- Detail: [[04-Analysis/Video Analysis Results]]

---

## 7. References

1. **Amprimo, G., Masi, G., Pettiti, G., Olmo, G., Priano, L., & Ferraris, C.** (2023). Hand tracking for clinical applications: validation of the Google MediaPipe Hand (GMH) and the depth-enhanced GMH-D frameworks. arXiv:2308.01088. https://arxiv.org/abs/2308.01088

2. **Google MediaPipe.** (2024). Hand Landmarker Task Guide. https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker

3. **MDPI Sensors.** (2025). Optimisation and Comparison of Markerless and Marker-Based Motion Capture Methods for Hand and Finger Movement Analysis. *Sensors*, 25(4), 1079. https://doi.org/10.3390/s25041079

4. **Bazarevsky, V., et al.** (2019). MediaPipe Hands: On-device Real-time Hand Tracking. arXiv:2006.10214. https://arxiv.org/abs/2006.10214

5. **Lugaresi, C., et al.** (2019). MediaPipe: A Framework for Building Perception Pipelines. arXiv:1906.08172.

---

## 8. Implementation: HandTracker Class

### 8.1 File: `src/hand_tracker.py`

```python
class HandTracker:
    def __init__(self, model_path=None, use_yolo=True):
        # Auto-downloads model on first run
        # MediaPipe HandLandmarker (IMAGE mode, 2 hands)
        # YOLO validation (optional, enabled by default)
    
    def process_frame(self, frame: np.ndarray):
        # BGR→RGB → MediaPipe detect → parse → YOLO validate → return
    
    def process_video(self, video_path, max_frames=None, step=1):
        # Iterates frames, calls process_frame, builds frame_data list
    
    def close(self):
        self.detector.close()
```

### 8.2 Key Landmarks Used

| Index | Name | Usage |
|-------|------|-------|
| 0 | WRIST | Trajectory reference, position tracking |
| 4 | THUMB_TIP | Fingertip detection for aperture |
| 8 | INDEX_TIP | **Primary tracking point** for tapping & reach |
| 12 | MIDDLE_TIP | Secondary reference |
| 16 | RING_TIP | Secondary reference |
| 20 | PINKY_TIP | Secondary reference |

### 8.3 Handedness Detection

MediaPipe returns `handedness` (Left/Right) per detected hand via its internal classification. The system uses `result.handedness[idx][0].category_name` to separate left/right feature extraction pipelines.

### 8.4 Frame Data Output Structure

```python
{
    "fps": 30,
    "total_frames": 0,
    "frames": [
        {
            "frame": 0,
            "time_sec": 0.0,
            "hands": [
                {
                    "hand": "Left",
                    "landmarks": np.array([[x, y, z], ...]),       # 21×3 pixel coords
                    "landmarks_norm": np.array([[x, y, z], ...]),  # 21×3 normalized [0,1]
                    "yolo_validated": True,
                    "yolo_overlap": 0.85,
                }
            ]
        }
    ]
}
```

### 8.5 Performance

| Component | GPU Inference | CPU Inference |
|-----------|---------------|---------------|
| MediaPipe HandLandmarker | ~5–15ms/frame | ~15–30ms/frame |
| YOLO person detection | ~10–30ms/frame | ~50–100ms/frame |
| **Total** | **~15–45ms** | **~65–130ms** |

Webcam mode skips every other frame (`webcam_step % 2 == 0`) to maintain usable FPS.

---

## 9. YOLO Person Validation

### 9.1 Motivation

MediaPipe HandLandmarker can produce false positives on textures/patterns that vaguely resemble hands. YOLO (`yolov8n.pt`) person detection acts as a **spatial gatekeeper**: if no person bounding box overlaps with a detected hand's landmark bounding box, that hand is likely a false positive.

### 9.2 File: `src/yolo_detector.py`

```python
class YOLODetector:
    def __init__(self, model_path="yolov8n.pt", conf_threshold=0.5, iou_threshold=0.5)
    def detect_persons(frame) → [{"bbox": (x1,y1,x2,y2), "confidence": float}]
    def validate_landmarks(landmarks, person_boxes, min_overlap=0.15) → (is_valid, overlap_ratio)
    def validate_hands(hands_data, frame) → [validated_hands]
```

### 9.3 Overlap Algorithm

```
hand_bbox = [min(x), min(y), max(x), max(y)] from 21 landmarks
for each person_bbox from YOLO:
    compute intersection area / hand area
keep hand if max_overlap >= MIN_HAND_OVERLAP (default 0.15)
```

### 9.4 Configuration (`config.py`)

```python
YOLO_MODEL_PATH = "yolov8n.pt"       # Auto-downloaded by ultralytics
YOLO_CONFIDENCE = 0.5
YOLO_IOU = 0.5
YOLO_MIN_HAND_OVERLAP = 0.15
```

### 9.5 Integration Flow

```
frame (BGR)
  → MediaPipe → hands_data (list of hand dicts with landmarks)
  → YOLO → person_boxes (COCO class 0)
  → For each hand: compute hand_bbox from landmarks
  → Compute overlap with each person_bbox
  → Keep hands with overlap >= MIN_HAND_OVERLAP
  → Return filtered list
```

### 9.6 Fallback

If `ultralytics` is not installed or the model file is missing:
- YOLO init fails gracefully → `self.yolo = None`
- MediaPipe runs alone without validation
- No crash, only reduced false-positive rejection
