# Development Plan — White Code Methodology

> **แนวทาง:** White Code = ใช้ AI ช่วยออกแบบและเขียนโค้ด
> **เป้าหมาย:** แบ่งงานเป็นเฟสเล็ก ๆ เพื่อป้องกัน Context Overflow

---

## Phase 1: Foundation — MediaPipe Integration

### วัตถุประสงค์
ตั้งค่า MediaPipe Hand Landmarker ให้ตรวจจับ 21 landmarks ได้จริงทั้ง 2 มือ

### งาน
| # | งาน | รายละเอียด |
|---|-----|-----------|
| 1.1 | ติดตั้ง dependencies | mediapipe, opencv-python, numpy, scipy, scikit-learn, streamlit |
| 1.2 | ดาวน์โหลด Model | hand_landmarker.task (auto-download) |
| 1.3 | สร้าง HandTracker class | process_frame(), process_video() |
| 1.4 | ทดสอบกับวิดีโอตัวอย่าง | 60-L-cut.mp4, 67-R-cut.mp4 |
| 1.5 | บันทึกผล detection | JSON landmarks |

### ผลลัพธ์
- ✅ HandTracker ตรวจจับ 21 landmarks ได้
- ✅ แยก Left/Right hand ได้
- ✅ Export data เป็น JSON

### ไฟล์
- `src/hand_tracker.py`
- `src/config.py`
- `src/analyze_hands.py` (legacy)

---

## Phase 2: Core Logic — Feature Extraction

### วัตถุประสงค์
คำนวณ Speed / Accuracy / Quality metrics จาก landmark trajectories

### งาน
| # | งาน | รายละเอียด |
|---|-----|-----------|
| 2.1 | Trajectory extraction | ดึงตำแหน่ง fingertip (landmark 8) ต่อเฟรม |
| 2.2 | Speed metrics | tapping speed, peak velocity, reach time |
| 2.3 | Accuracy metrics | endpoint error, path efficiency, tap regularity |
| 2.4 | Quality metrics | smoothness (SPARC), ROM, tremor index |
| 2.5 | Symmetry Index | เปรียบเทียบ L vs R metrics |
| 2.6 | ทดสอบกับวิดีโอ | ตรวจสอบค่า metric ถูกต้อง |

### ผลลัพธ์
- ✅ FeatureExtractor พร้อม tapped/reach features
- ✅ SymmetryIndex สำหรับทุก metric
- ✅ Export feature vectors

### ไฟล์
- `src/features.py`

---

## Phase 3: Classification Engine

### วัตถุประสงค์
แยกแยะ Natural Dominance vs Learned Non-Use จาก feature vectors

### งาน
| # | งาน | รายละเอียด |
|---|-----|-----------|
| 3.1 | Rule-based classification | Asymmetry threshold, dominance score |
| 3.2 | Performance ratio | คำนวณ % performance ของมือที่อ่อนแรงกว่า |
| 3.3 | Risk scoring | Learned Non-Use risk score (0-1) |
| 3.4 | Edge cases | กรณีตรวจจับมือได้แค่ข้างเดียว, threshold tuning |

### ผลลัพธ์
- ✅ DominanceClassifier
- ✅ ClassificationResult dataclass
- ✅ Risk interpretation text

### ไฟล์
- `src/classifier.py`

---

## Phase 4: UI/UX — Streamlit Frontend

### วัตถุประสงค์
สร้าง Web interface สำหรับ Upload วิดีโอ, Webcam live, และแสดงผล

### งาน
| # | งาน | รายละเอียด |
|---|-----|-----------|
| 4.1 | Upload Video mode | File uploader → process → display |
| 4.2 | Webcam (Live) mode | Real-time tracking, record, analyze |
| 4.3 | Results display | Metrics cards, feature comparison, symmetry |
| 4.4 | Settings sidebar | Test type, duration, threshold |
| 4.5 | Styling | CSS cards, risk color coding |

### ผลลัพธ์
- ✅ ระบบ Upload + Webcam ใช้งานได้
- ✅ แสดง metrics, classification, symmetry
- ✅ UI responsive

### ไฟล์
- `src/app.py`

---

## Phase 5: Testing & Validation

### วัตถุประสงค์
ทดสอบระบบกับวิดีโอจริง แก้บั๊ก และปรับปรุง performance

### งาน
| # | งาน | รายละเอียด |
|---|-----|-----------|
| 5.1 | ทดสอบ 60-L-cut.mp4 | ตรวจสอบว่าตรวจพบ Left dominance |
| 5.2 | ทดสอบ 67-R-cut.mp4 | ตรวจสอบว่าตรวจพบ Right dominance |
| 5.3 | ทดสอบ Webcam mode | ทดสอบ real-time tracking |
| 5.4 | Edge cases | Video ไม่มีมือ, มือไม่ชัด, แสงน้อย |
| 5.5 | Performance tuning | Reduce processing time, step=2-3 frames |
| 5.6 | Save analysis results | JSON report |

### ผลลัพธ์
- ✅ ระบบทำงานบนวิดีโอจริง
- ✅ Performance ใช้ได้
- ✅ Report saved

### ไฟล์
- `src/run_analysis.py`
- `docs/Research/04-Analysis/real_analysis_results.json`

---

## Phase 6: Delivery & Documentation

### วัตถุประสงค์
เตรียมเอกสาร, วิดีโอสาธิต, และส่งผลงาน

### งาน
| # | งาน | รายละเอียด |
|---|-----|-----------|
| 6.1 | README.md | วิธีติดตั้ง, วิธีใช้, pipeline |
| 6.2 | SUMMARY.md | Project summary |
| 6.3 | วิดีโอสาธิต (≤10 นาที) | Demo การทำงาน + อธิบาย |
| 6.4 | GitHub push | Source code พร้อม assets |
| 6.5 | ส่งฟอร์ม | https://forms.gle/sAzY9AK7Lj1wXHkq6 |

### ผลลัพธ์
- ✅ Source code บน GitHub
- ✅ วิดีโอ ≤ 10 นาที
- ✅ ส่งภายใน 24 มิ.ย. 09:00 น.

---

## Data Pipeline Overview

```
Input Video/Webcam
    │
    ▼
OpenCV Frame Capture (every 2-3 frames)
    │
    ▼
MediaPipe Hand Landmarker
    │
    ├── 21 landmarks → Left Hand
    └── 21 landmarks → Right Hand
    │
    ▼
Feature Extraction
    ├── Speed:   tapping_speed, peak_velocity, reach_time
    ├── Accuracy: endpoint_error, path_efficiency, tap_regularity
    └── Quality:  movement_smoothness, range_of_motion, tremor_index
    │
    ▼
Symmetry Index (L vs R comparison)
    │
    ▼
Classification
    ├── Dominance Score (Left vs Right)
    └── Learned Non-Use Risk
    │
    ▼
Output: Result + Visualization
```

---

## การจัดการ Context Overflow

| ปัญหา | วิธีแก้ |
|-------|--------|
| Token limit เกิน | แบ่งโค้ดเป็นไฟล์เล็ก (config, tracker, features, classifier) |
| AI ลืม context ก่อนหน้า | แต่ละเฟสมี prompt แยก, อ้างอิงเฉพาะไฟล์ที่เกี่ยวข้อง |
| Dependency หลายตัว | requirements.txt ชัดเจน, ใช้ virtual environment |
| Testing ซับซ้อน | run_analysis.py สำหรับ batch test โดยเฉพาะ |

---

## ความเสี่ยงและการลดความเสี่ยง

| ความเสี่ยง | ผลกระทบ | การลดความเสี่ยง |
|-----------|---------|---------------|
| MediaPipe ไม่ detect มือ | สูง | ปรับ confidence threshold, แสง, ระยะห่าง |
| Video resolution ต่ำ | ปานกลาง | Resize ก่อน processing |
| Performance ช้า | ปานกลาง | Process ทุก 2-3 frame, limit max frames |
| Classification ผิดพลาด | ต่ำ | ใช้ rule-based สำรอง, confidence threshold |
