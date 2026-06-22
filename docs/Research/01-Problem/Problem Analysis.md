# Problem Analysis — วิเคราะห์โจทย์การแข่งขัน

> **ที่มา:** ไฟล์ PDF `docs/แข่งขัน E-Health Hackathon 2026 Elderly AI Innovation.pdf`

---

## 1. ข้อมูลทั่วไปของงาน

| หัวข้อ | รายละเอียด |
|-------|-----------|
| **ชื่องาน** | AI Vibe Coding: Digital Aiding 4 Aging Hackathon 2026 |
| **หัวข้อ** | Innovation for the Elderly Care: Hack the Future with AI Vibe Coding |
| **ผู้จัด** | หน่วยบ่มเพาะนวัตกรปัญญาประดิษฐ์ หลักสูตรวิทยาการคอมพิวเตอร์ มทร.ล้านนา น่าน |
| **รูปแบบ** | Online — ชี้แจงโจทย์, Offline/Online — พัฒนา, Zoom — Pitching |

---

## 2. ปัญหาพื้นฐาน (Problem Statement)

### 2.1 ภาวะมวลกล้ามเนื้อน้อยในผู้สูงอายุ (Sarcopenia)
เมื่ออายุมากขึ้น กล้ามเนื้อมัดเล็กและมัดใหญ่จะสูญเสียมวลและความแข็งแรง ส่งผลให้:
- มือและแขนอ่อนแรง
- การทรงตัวแย่ลง
- ความสามารถในการทำกิจวัตรประจำวัน (ADL) ลดลง

### 2.2 วงจรอุบาทว์ของ Learned Non-Use
```
ความอ่อนแรง → พยายามใช้แล้วล้มเหลว → ใช้แขนข้างดีแทน
→ ไม่ใช้แขนข้างอ่อนแรง → สมองปรับโครงสร้าง (cortical reorganization)
→ กล้ามเนื้อลีบ ข้อติด → ยิ่งใช้แขนข้างอ่อนแรงไม่ได้
→ เรียนรู้ที่จะไม่ใช้ (Learned Non-Use)
```

**ผลกระทบ:**
- ความไม่สมดุลของกล้ามเนื้อมือ (มัดเล็ก vs มัดใหญ่)
- ข้อยึดติด (Contracture)
- สูญเสียความสามารถในการใช้อวัยวะข้างที่อ่อนแรงอย่างถาวร
- แม้กล้ามเนื้อจะฟื้นฟูได้ แต่พฤติกรรมที่เรียนรู้แล้วยังคงอยู่

### 2.3 เป้าหมาย
- **Task-Specific:** การนำแขนไปใช้ในกิจวัตรประจำวัน (ADL Integration)
- คืนความสมดุลระหว่างกล้ามเนื้อมัดเล็กและมัดใหญ่
- ป้องกันข้อยึดติด
- ตัดวงจร Learned Non-Use

---

## 3. โจทย์การแข่งขัน: AI Vibe Coding

### 3.1 ภารกิจ
> **"ตรวจสอบความคล่องของมือผ่านวิดีโอ: มาดูกันว่าคุณถนัดมือข้างไหนจริงๆ?"**

ระบบจะวิเคราะห์ว่าผู้ใช้มือได้:
1. **รวดเร็ว** แค่ไหน → Speed
2. **แม่นยำ** แค่ไหน → Accuracy
3. **ลื่นไหล** แค่ไหน → Quality of Movements

### 3.2 วัตถุประสงค์หลัก
แยกแยะระหว่าง:
| ประเภท | คำอธิบาย |
|--------|----------|
| **แขนที่ถนัดโดยธรรมชาติ (Natural Dominance)** | มือที่ถนัดมาตั้งแต่เกิด ใช้งานได้คล่องกว่าตามปกติ |
| **แขนที่ถูกเลือกใช้เพราะอีกข้างมีภาวะ Learned Non-Use** | ผู้ใช้ "ลืม" วิธีการใช้แขนข้างที่อ่อนแรง เลือกใช้แขนอีกข้างแทน แม้แขนที่อ่อนแรงจะฟื้นฟูได้บ้างแล้ว |

### 3.3 เกณฑ์การประเมิน (3 Pillars)

| Pillar | คำไทย | Metrics ที่เป็นไปได้ |
|--------|-------|-------------------|
| **Speed** | ความเร็ว | Movement velocity, Reaction time, Completion time, Tapping frequency |
| **Accuracy** | ความแม่นยำ | Endpoint error, Target deviation, Error rate, Path efficiency |
| **Quality of Movements** | คุณภาพการเคลื่อนไหว | Smoothness (Jerk/SPARC), ROM, Symmetry index, Coordination |

### 3.4 แนวทางการสร้างระบบทำนาย (Prediction System)
1. **Input:** วิดีโอการเคลื่อนไหวของมือ (จาก resource หรือที่ผู้ใช้ Upload)
2. **Processing:** 
   - Extract frames → MediaPipe Hand Landmarker → 21 landmarks/motion
   - Feature extraction: velocity, acceleration, jerk, angles, symmetry
3. **Analysis:**
   - เปรียบเทียบ Left vs Right hand kinematics
   - คำนวณ Asymmetry Score
   - เปรียบเทียบกับ normative data
4. **Output:**
   - ความน่าจะเป็นของภาวะ Learned Non-Use
   - คำแนะนำ/feedback

---

## 4. เกณฑ์การตัดสินคะแนน (Judging Criteria)

| หมวด | คะแนน | รายละเอียด |
|------|-------|-----------|
| **Problem Solving & Impact** | 30 | ความเข้าใจปัญหา, แนวทางแก้ตรงประเด็น, ผลกระทบเชิงบวก, สอดคล้องโจทย์ |
| **Creativity & Innovation** | 25 | ความแปลกใหม่, การประยุกต์ใช้เทคโนโลยี, ความน่าสนใจ |
| **Prototype & Technical Execution** | 30 | MVP ใช้ได้จริง, Workflow เหมาะสม, ใช้ AI อย่างเหมาะสม, ความสมบูรณ์ |
| **Pitching & Team Collaboration** | 15 | Presentation, Demo, Q&A, การทำงานทีม |

### 4.1 จุดเน้นตามเกณฑ์
- **Problem Solving:** ต้องแสดงให้เห็นว่าเข้าใจ Learned Non-Use จริง → ดู [[02-Medical-Background/Learned Non-Use Syndrome]]
- **Technical:** ใช้ MediaPipe + ML classification → ดู [[03-Technology/MediaPipe Hand Tracking for Rehabilitation]]
- **Creativity:** การออกแบบ Feature engineering และ scoring system → ดู [[03-Technology/Speed Accuracy Quality Metrics Framework]]

---

## 5. Timeline การแข่งขัน

| วันที่ | เวลา | กิจกรรม |
|-------|------|---------|
| **20 มิ.ย. 69** (ศ.) | 16:00-18:00 น. | ชี้แจงโจทย์ออนไลน์ |
| **20 มิ.ย. 69** (ศ.) | 18:00 น. | เริ่มพัฒนา |
| **24 มิ.ย. 69** (พ.) | 09:00 น. | ปิดรับผลงาน |
| **26 มิ.ย. 69** (ศ.) | 10:00 น. | ประกาศ 5 ทีมสุดท้าย |
| **27 มิ.ย. 69** (ส.) | 13:00 น. | Pitching รอบชิง (Zoom) |

---

## 6. สิ่งที่ต้องส่ง

### 6.1 วิดีโอนำเสนอ (≤ 10 นาที)
ควรประกอบด้วย:
- ปัญหาและ Pain Point
- แนวทางการแก้ไข
- Demo การทำงาน
- ผลลัพธ์
- โค้ดและเทคนิคสำคัญ

### 6.2 Source Code (GitHub)
- ส่งผ่าน GitHub
- ควรมี README.md, requirements.txt
- โค้ดที่ clean และมี comment

### 6.3 ฟอร์มส่งงาน
- https://forms.gle/sAzY9AK7Lj1wXHkq6
- **ห้ามส่งหลัง 24 มิ.ย. 69 เวลา 09:00 น.**

---

## 7. Resource ที่ให้

### 7.1 วิดีโอ
- `60-L-cut.mp4` — การใช้มือซ้าย (Left)
- `67-R-cut.mp4` — การใช้มือขวา (Right)
- ดูรายละเอียด: [[01-Problem/Resource Video Notes]]

### 7.2 Google Drive
- https://drive.google.com/drive/folders/18rELdvoDL0EgdYkTnzMosp4QnJ4lXVFc
- มี resource เพิ่มเติม (อาจเป็นคลิปตัวอย่าง, ข้อมูลอ้างอิง, ฯลฯ)

---

## 8. Solution Approach ที่แนะนำ

### 8.1 Tech Stack
| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| CV | OpenCV, MediaPipe Hand Landmarker |
| Data | NumPy, SciPy |
| ML | scikit-learn (Random Forest / XGBoost) |
| Frontend | Streamlit / Gradio |
| Visualization | Matplotlib, Plotly |

### 8.2 Pipeline
```
Input Video (upload or webcam)
  → Frame Extraction (every 5-10 frames)
  → MediaPipe Hand Detection (21 landmarks/hand)
  → Landmark Tracking (across frames)
  → Feature Engineering:
    ├── Speed: velocity, acceleration, tapping rate
    ├── Accuracy: endpoint deviation, path ratio
    └── Quality: jerk, ROM, symmetry, coordination
  → Bilateral Comparison (L vs R)
  → Classification: Natural Dominance vs Learned Non-Use
  → Output: Score + Visualization + Recommendations
```

### 8.3 MVP Features ที่ควรมี
1. ✅ Upload วิดีโอหรือใช้ webcam
2. ✅ MediaPipe hand tracking
3. ✅ Speed/Accuracy/Quality score แยกแต่ละมือ
4. ✅ Bilateral comparison chart
5. ✅ ผลการทำนาย (ถนัดจริง vs Learned Non-Use)
6. ✅ Export report

---

## 9. References

- ไฟล์ PDF ต้นฉบับ: `docs/แข่งขัน E-Health Hackathon 2026 Elderly AI Innovation.pdf`
- ดูเพิ่มเติม: [[02-Medical-Background/Learned Non-Use Syndrome]]
- ดูเพิ่มเติม: [[03-Technology/Speed Accuracy Quality Metrics Framework]]
- ดูเพิ่มเติม: [[02-Medical-Background/Hand Dexterity Assessment Methods]]
