# Resource Video Notes — ข้อมูลวิดีโอ Resource

> **ที่มา:** ดาวน์โหลดจาก Google Drive (ตามลิงก์ใน PDF โจทย์)
> https://drive.google.com/drive/folders/18rELdvoDL0EgdYkTnzMosp4QnJ4lXVFc

---

## 1. ข้อมูลไฟล์

| ไฟล์ | ขนาด | Resolution | FPS | ระยะเวลา | Mean Brightness |
|------|------|-----------|-----|----------|----------------|
| `60-L-cut.mp4` | 132 MB | 1920×1080 | 30 | ~126.7 วิ (3,802 frames) | 133.2 |
| `67-R-cut.mp4` | 145 MB | 1920×1080 | 30 | ~132.3 วิ (3,969 frames) | 122.9 |

---

## 2. การตีความชื่อไฟล์

| ส่วน | ความหมายที่เป็นไปได้ |
|------|-------------------|
| **60 / 67** | Participant ID, BPM (metronome speed), หรือรหัส exercise |
| **L / R** | Left hand (มือซ้าย) / Right hand (มือขวา) |
| **cut** | ผ่านการตัดต่อ / edited version |

### ความเป็นไปได้ของ "60" และ "67"
- **BPM hypothesis:** 60 BPM = 1 ครั้ง/วินาที, 67 BPM ≈ 1.12 ครั้ง/วินาที
  - อาจเป็นความเร็วของ metronome ที่ใช้กำหนดจังหวะในการทำ exercise
- **Participant hypothesis:** รหัสผู้เข้าร่วม testing คนที่ 60 และ 67

---

## 3. สรุปผล MediaPipe Detection

| รายการ | 60-L-cut | 67-R-cut |
|--------|----------|----------|
| ตรวจพบ Left | 6 ครั้ง | 2 ครั้ง |
| ตรวจพบ Right | 3 ครั้ง | 3 ครั้ง |
| รวม detection | 9 ครั้ง | 5 ครั้ง |
| Left wrist movement avg | 0.2646 | 0.3872 |
| Right wrist movement avg | 0.0432 | 0.2806 |

ดูผลวิเคราะห์เต็ม: [[04-Analysis/Video Analysis Results]]

---

## 4. ข้อสังเกต

### 4.1 การปรากฏของมือในวิดีโอ
- 60-L-cut: มือซ้ายขยับมากกว่ามือขวา **5 เท่า**
  - → วิดีโอน่าจะโฟกัสที่การเคลื่อนไหวของมือซ้าย
  - มือขวาอาจปรากฏเป็นครั้งคราว (พัก พยุง หรือสลับข้าง)
- 67-R-cut: มือขวาและซ้ายเคลื่อนไหวใกล้เคียงกัน
  - → อาจมีการสลับใช้งานทั้งสองข้าง

### 4.2 ข้อจำกัดในการวิเคราะห์
- Sampling เฉลี่ย 1 ครั้ง/วินาที (ทุก 30 frames)
- มืออาจอยู่นอก frame ที่สุ่มตรวจ
- ไม่มี ground truth ว่าเป็น Learned Non-Use หรือไม่
- ต้องวิเคราะห์ kinematic parameters เพิ่มเติม

---

## 5. Task ที่น่าจะเป็น

จากความยาว (~2 นาทีต่อคลิป) และรูปแบบการขยับ น่าจะเป็น:
- **Finger Tapping Task** — แตะนิ้วตามจังหวะ
- **Hand Opening-Closing** — กำ-แบมือ
- **Reaching & Grasping** — เอื้อมหยิบวัตถุ
- **Combination** — หลายท่าผสมกัน

ดูเพิ่มเติม: [[02-Medical-Background/Finger Tapping Test]]

---

## 6. การนำไปใช้

| ไฟล์ | ใช้ประโยชน์ |
|------|-----------|
| 60-L-cut.mp4 | Train model ด้วย Left-dominant movement |
| 67-R-cut.mp4 | Test model ด้วย Right-dominant movement |
| ทั้งคู่ | เปรียบเทียบ kinematic symmetry |

---

## References

1. MediaPipe analysis script: `src/analyze_hands.py`
2. Full results JSON: `04-Analysis/hand_analysis.json`
3. Video files path: `assets/60-L-cut.mp4`, `assets/67-R-cut.mp4`
