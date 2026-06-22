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
