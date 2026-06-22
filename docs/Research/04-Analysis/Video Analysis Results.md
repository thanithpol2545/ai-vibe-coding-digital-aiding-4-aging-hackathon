# Video Analysis Results — ผลการวิเคราะห์วิดีโอด้วย MediaPipe

> **ผลการรัน MediaPipe Hand Landmarker บนวิดีโอ resource**
> Script: `src/analyze_hands.py`

---

## 1. วิธีการวิเคราะห์

| หัวข้อ | รายละเอียด |
|-------|-----------|
| **Tool** | Google MediaPipe Hand Landmarker (Task Vision API) |
| **Version** | mediapipe 0.10.35 |
| **Model** | hand_landmarker (float16) |
| **Running mode** | VIDEO (monotonically increasing timestamps) |
| **Max hands** | 2 |
| **Confidence** | Detection=0.5, Tracking=0.5 |
| **Sample interval** | ทุก 30 frames (1 ครั้ง/วินาที ที่ 30fps) |
| **Features extracted** | Hand landmarks (21 points), handedness (Left/Right), wrist position |

---

## 2. วิดีโอที่ 1: 60-L-cut.mp4

### 2.1 Metadata
| Property | Value |
|----------|-------|
| ชื่อไฟล์ | 60-L-cut.mp4 |
| Resolution | 1920×1080 (Full HD) |
| FPS | 30 |
| Total frames | 3,802 |
| Duration | ~126.7 วินาที (~2 นาที 7 วินาที) |
| Mean brightness | 133.2 (กลางๆ ไม่มืดไม่สว่างเกิน) |

### 2.2 MediaPipe Detection Results
| เวลา (วินาที) | เฟรม | มือที่ตรวจพบ | จำนวน |
|--------------|-------|-------------|-------|
| 6.0 | 180 | Left | 1 |
| 8.0 | 240 | Right | 1 |
| 10.0 | 300 | Left | 1 |
| 25.0 | 750 | Right | 1 |
| 39.0 | 1170 | Left | 1 |
| 49.0 | 1470 | Left | 1 |
| 59.0 | 1770 | Left | 1 |
| 61.0 | 1830 | Right | 1 |
| 114.0 | 3420 | Left | 1 |

### 2.3 สรุป
| มือ | จำนวนครั้งที่ตรวจพบ | Wrist Movement (avg) |
|-----|-------------------|---------------------|
| **Left** | **6** ครั้ง (66.7%) | **0.2646** |
| Right | 3 ครั้ง (33.3%) | 0.0432 |

**Key finding:** Left wrist เคลื่อนไหวมากกว่า Right **5 เท่า** (0.2646 vs 0.0432)

---

## 3. วิดีโอที่ 2: 67-R-cut.mp4

### 3.1 Metadata
| Property | Value |
|----------|-------|
| ชื่อไฟล์ | 67-R-cut.mp4 |
| Resolution | 1920×1080 (Full HD) |
| FPS | 30 |
| Total frames | 3,969 |
| Duration | ~132.3 วินาที (~2 นาที 12 วินาที) |
| Mean brightness | 122.9 (ค่อนข้างมืดกว่า 60-L-cut เล็กน้อย) |

### 3.2 MediaPipe Detection Results
| เวลา (วินาที) | เฟรม | มือที่ตรวจพบ | จำนวน |
|--------------|-------|-------------|-------|
| 36.0 | 1080 | Right | 1 |
| 37.0 | 1110 | Left | 1 |
| 53.0 | 1590 | Left | 1 |
| 74.0 | 2220 | Right | 1 |
| 125.0 | 3750 | Right | 1 |

### 3.3 สรุป
| มือ | จำนวนครั้งที่ตรวจพบ | Wrist Movement (avg) |
|-----|-------------------|---------------------|
| **Right** | **3** ครั้ง (60%) | 0.2806 |
| Left | 2 ครั้ง (40%) | 0.3872 |

**Key finding:** Right ตรวจพบบ่อยกว่า Left เล็กน้อย แต่ Left wrist movement มากกว่า

---

## 4. การเปรียบเทียบสองวิดีโอ

| เปรียบเทียบ | 60-L-cut | 67-R-cut |
|------------|----------|----------|
| **มือเด่น** | Left (6/9 detections) | Right (3/5 detections) |
| **มือที่เคลื่อนไหวมากกว่า** | Left (5x Right) | Left (เล็กน้อย) |
| **จำนวน detection** | 9 | 5 |
| **ความสม่ำเสมอในการเคลื่อนไหว** | Left เคลื่อนไหวสม่ำเสมอ | ทั้งสองมือใกล้เคียงกัน |
| **Brightness** | 133.2 (สว่างกว่า) | 122.9 (มืดกว่า) |

### 4.1 การตีความ
| ข้อสังเกต | การตีความ |
|-----------|-----------|
| **60-L-cut มี Left detection มากกว่า** | วิดีโอแสดงการใช้มือซ้ายเป็นหลัก |
| **60-L-cut Left wrist movement มากกว่า Right 5x** | โฟกัสที่มือซ้าย มือขวา stationary |
| **67-R-cut Right detection มากกว่าเล็กน้อย** | วิดีโอแสดงการใช้มือขวาเป็นหลัก |
| **67-R-cut Left/Right movement ใกล้เคียง** | อาจสลับหรือเปรียบเทียบสองมือ |
| **Detection rate ต่ำ (~0.1-0.2%)** | Sample interval ถี่เกินไป (30 frames) |

---

## 5. ข้อค้นพบสำคัญ

### 5.1 วิดีโอ 60-L-cut
- **มือซ้าย (Left)** → dominant hand of this video
- Wrist movement asymmetry **มาก** → Left เคลื่อนที่มาก, Right นิ่ง
- น่าจะเป็น **Finger Tapping หรือ Hand Exercise** ที่เน้นซ้าย

### 5.2 วิดีโอ 67-R-cut
- **มือขวา (Right)** → dominant hand of this video
- Wrist movement **ใกล้เคียงกัน** ทั้งสองข้าง
- น่าจะเป็น exercise ที่สลับซ้าย-ขวา

---

## 6. ข้อจำกัดและข้อเสนอแนะ

### 6.1 ข้อจำกัดในการวิเคราะห์ปัจจุบัน
1. **Sampling rate:** ทุก 30 frames อาจพลาด movement detail
2. **Detection rate:** ต่ำมาก (0.1-0.2%) → ต้องลด sample interval
3. **No ground truth:** ไม่ทราบว่าผู้เข้าร่วมเป็น Learned Non-Use หรือไม่
4. **Wrist movement only:** ยังไม่ได้วิเคราะห์ fingertip trajectory
5. **No temporal dynamics:** ยังไม่มี velocity profile, smoothness

### 6.2 ข้อเสนอแนะสำหรับการวิเคราะห์รอบถัดไป
- [ ] Sample ทุก 5-10 frames (ไม่ใช่ 30)
- [ ] วิเคราะห์ fingertip trajectories (landmark 4,8,12,16,20)
- [ ] คำนวณ velocity profile และ acceleration
- [ ] วัด smoothness (Jerk / SPARC)
- [ ] วัด hand aperture (thumb-finger distance)
- [ ] คำนวณ Symmetry Index (SI) สำหรับทุก metric
- [ ] วิเคราะห์ fatigue (performance ลดลงตามเวลา)

---

## 7. References

1. Full analysis script: `src/analyze_hands.py`
2. Raw detection data: `04-Analysis/hand_analysis.json`
3. Google MediaPipe Hand Landmarker documentation
4. ดูเพิ่ม: [[03-Technology/Speed Accuracy Quality Metrics Framework]]
5. ดูเพิ่ม: [[03-Technology/MediaPipe Hand Tracking for Rehabilitation]]
