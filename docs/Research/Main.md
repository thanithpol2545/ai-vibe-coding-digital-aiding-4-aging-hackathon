# AI Vibe Coding: Digital Aiding 4 Aging Hackathon 2026

> **Research Vault — หน่วยบ่มเพาะนวัตกรปัญญาประดิษฐ์**
> **หลักสูตรวิทยาการคอมพิวเตอร์ มหาวิทยาลัยเทคโนโลยีราชมงคลล้านนา น่าน**
> 20-27 มิถุนายน 2569

---

## 📂 โครงสร้าง Vault

```
Research/
├── Main.md                                  ← หน้านี้
├── 00-PRD/
│   └── PRD.md                               ← PRD ฉบับสมบูรณ์
├── 00-Planning/
│   ├── Development Plan.md                  ← แผน 6 เฟส (White Code)
│   └── Bug Tracker.md                       ← บั๊กที่เจอและแก้แล้ว
├── 01-Problem/
│   ├── Problem Analysis.md                  ← วิเคราะห์โจทย์จาก PDF
│   ├── Resource Video Notes.md              ← วิดีโอ resource ในโจทย์
│   └── Video Content Analysis.md            ← วิเคราะห์เนื้อหาวิดีโอ
├── 02-Medical-Background/
│   ├── Learned Non-Use Syndrome.md          ← ภาวะ Learned Non-Use
│   ├── Hand Dexterity Assessment Methods.md ← วิธีประเมินความคล่องมือ
│   ├── Constraint-Induced Movement Therapy.md ← การบำบัด CIMT
│   └── Finger Tapping Test.md              ← Finger Tapping Test
├── 03-Technology/
│   ├── MediaPipe Hand Tracking for Rehabilitation.md ← MediaPipe + YOLO
│   ├── Speed Accuracy Quality Metrics Framework.md   ← กรอบวัด + implementation
│   ├── System Architecture.md                          ← สถาปัตยกรรมระบบ
│   └── Streamlit UI.md                                 ← โครงสร้าง UI
└── 04-Analysis/
    ├── Video Analysis Results.md            ← ผล MediaPipe จริง
    └── hand_analysis.json                   ← Raw detection data
```

---

## 🎯 ภาพรวมโปรเจกต์

**Hand Assessment AI** — ระบบวิเคราะห์การเคลื่อนไหวมือจากวิดีโอ เพื่อตรวจสอบความถนัด (Hand Dominance) และภาวะ Learned Non-Use ในผู้สูงอายุ

### Tech Stack

| Component | Technology |
|-----------|-----------|
| Core Language | Python 3.10+ |
| Hand Tracking | Google MediaPipe Hand Landmarker (21 landmarks) |
| Person Validation | YOLOv8 (ultralytics) |
| Signal Processing | NumPy, SciPy |
| Classification | Rule-based heuristic |
| Frontend | Streamlit |
| Persistence | Local filesystem (JSON + fpdf2) |

### Core Pipeline

```
Input (video / webcam)
  → OpenCV frame capture (every 2–3 frames)
  → MediaPipe 21-point landmarks (L + R hands)
  → YOLO person validation (spatial gatekeeper)
  → Feature Extraction:
      Speed:     tapping speed, peak velocity, reach time
      Accuracy:  path efficiency, tap regularity, endpoint error
      Quality:   smoothness (SPARC), ROM, tremor index
  → Symmetry Index (L vs R comparison)
  → Classification:
      Dominance score → Left or Right dominant
      Performance ratio → Learned Non-Use risk (0–95%)
  → Output: result cards + JSON + PDF report
```

### 3 แบบทดสอบ

| Test | ท่า | วัด |
|------|-----|-----|
| 👆 Finger Tapping | แตะนิ้วชี้-นิ้วโป้ง | Speed, Regularity |
| 🏃 Reach-to-Target | เอื้อมแขนไปข้างหน้า | ROM, Smoothness, Path Efficiency |
| 🔄 Combined | สลับแตะนิ้ว + เอื้อมแขน | Task Switching |

---

## 🎯 โจทย์หลัก

> **ตรวจสอบความคล่องของมือผ่านวิดีโอ:** วิเคราะห์ว่าผู้ใช้มือได้ **รวดเร็ว** **แม่นยำ** และ **ลื่นไหล** แค่ไหน
> 
> **เป้าหมาย:** แยกแยะระหว่างแขนที่ถนัดโดยธรรมชาติ กับแขนที่ถูกเลือกใช้เพราะอีกข้างมีภาวะ **Learned Non-Use** ("ลืม" วิธีการใช้แขนข้างที่อ่อนแรง)
>
> **เกณฑ์:** ความเร็ว (Speed) + ความแม่นยำ (Accuracy) + คุณภาพการเคลื่อนไหว (Quality of Movements)

### สิ่งที่ต้องส่ง
1. 📹 วิดีโอนำเสนอ ≤ 10 นาที
2. 💻 Source code ผ่าน GitHub
3. 📥 ส่งที่ https://forms.gle/sAzY9AK7Lj1wXHkq6 ภายใน **24 มิ.ย. 69 เวลา 09:00 น.**

---

## 📊 เกณฑ์การตัดสิน

| หมวด | คะแนน |
|------|-------|
| Problem Solving & Impact | 30 |
| Creativity & Innovation | 25 |
| Prototype & Technical Execution | 30 |
| Pitching & Team Collaboration | 15 |
| **รวม** | **100** |

---

## 🔗 Quick Links

| หัวข้อ | ไปที่ |
|-------|------|
| PRD (Product Requirement Document) | [[00-PRD/PRD]] |
| แผนพัฒนา (White Code 6 เฟส) | [[00-Planning/Development Plan]] |
| Bug Tracker | [[00-Planning/Bug Tracker]] |
| วิเคราะห์โจทย์เต็ม | [[01-Problem/Problem Analysis]] |
| วิดีโอ resource | [[01-Problem/Resource Video Notes]] |
| Learned Non-Use คืออะไร | [[02-Medical-Background/Learned Non-Use Syndrome]] |
| วิธีประเมินความคล่องมือ | [[02-Medical-Background/Hand Dexterity Assessment Methods]] |
| การบำบัด CIMT | [[02-Medical-Background/Constraint-Induced Movement Therapy]] |
| Finger Tapping Test | [[02-Medical-Background/Finger Tapping Test]] |
| MediaPipe + YOLO Hand Tracking | [[03-Technology/MediaPipe Hand Tracking for Rehabilitation]] |
| Speed/Accuracy/Quality Framework + Implementation | [[03-Technology/Speed Accuracy Quality Metrics Framework]] |
| System Architecture | [[03-Technology/System Architecture]] |
| Streamlit UI Structure | [[03-Technology/Streamlit UI]] |
| ผลวิเคราะห์วิดีโอ | [[04-Analysis/Video Analysis Results]] |
| Raw data JSON | [[04-Analysis/hand_analysis.json]] |

---

## 🏆 รางวัล

| รางวัล | จำนวน |
|--------|-------|
| ชนะเลิศ | 3,000 บาท |
| รองชนะเลิศ 1 | 2,000 บาท |
| รองชนะเลิศ 2 | 1,000 บาท |
| ชมเชย (2 รางวัล) | 500 บาท |

## 📞 ติดต่อ

- Line: https://line.me/R/ti/g/LAHXy5AhZ3
- Facebook: หลักสูตรวิทยาการคอมพิวเตอร์ มทร.ล้านนา น่าน
- ผศ.วรวิทย์ ฝนคำอ้าย โทร. 0817832485
- ผศ.ขนิษฐา หอมจันทร์ โทร. 0946041881
