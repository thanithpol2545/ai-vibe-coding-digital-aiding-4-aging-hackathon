# Product Requirement Document (PRD)

> **โครงการ:** AI Vibe Coding: Digital Aiding 4 Aging Hackathon 2026
> **เวอร์ชัน:** 1.0
> **วันที่:** 21 มิ.ย. 2569

---

## 1. ที่มาและความสำคัญ

### 1.1 ปัญหา
ผู้สูงอายุมีภาวะมวลกล้ามเนื้อน้อย (Sarcopenia) ส่งผลให้มือและแขนอ่อนแรง นำไปสู่วงจร Learned Non-Use — "ลืม" วิธีการใช้แขนข้างที่อ่อนแรง แม้กล้ามเนื้อจะฟื้นฟูได้บ้างแล้ว

### 1.2 โอกาส
ใช้ AI วิเคราะห์วิดีโอการเคลื่อนไหวมือ เพื่อแยกแยะระหว่าง:
- **Natural Dominance:** การถนัดมือข้างใดข้างหนึ่งโดยธรรมชาติ
- **Learned Non-Use:** การ "ลืมใช้" แขนข้างที่อ่อนแรง

### 1.3 เป้าหมาย
สร้างระบบวิเคราะห์วิดีโอที่วัดผล 3 ด้าน (Speed / Accuracy / Quality) และรายงานความเสี่ยง Learned Non-Use

---

## 2. ผู้ใช้งาน (User Persona)

| Persona | รายละเอียด |
|---------|-----------|
| **แพทย์/นักกิจกรรมบำบัด** | ใช้เป็น screening tool ประเมินผู้สูงอายุ |
| **ผู้สูงอายุ/ญาติ** | ตรวจสอบความคล่องมือด้วยตนเองที่บ้าน |
| **ผู้ดูแล (Caregiver)** | ติดตามความเปลี่ยนแปลงรายสัปดาห์ |

---

## 3. ข้อกำหนดหน้าที่ (Functional Requirements)

### 3.1 ระบบวิเคราะห์วิดีโอ (Core Engine)

| ID | ความต้องการ | เกณฑ์สำเร็จ |
|----|------------|------------|
| FR-01 | รับ Input วิดีโอ (upload/webcam) | รองรับ mp4, avi, mov, webm |
| FR-02 | ตรวจจับมือด้วย MediaPipe Hand Landmarker | 21 landmarks ต่อมือ, 2 hands |
| FR-03 | คำนวณ Speed metrics | Tapping speed, peak velocity, reach time |
| FR-04 | คำนวณ Accuracy metrics | Endpoint error, path efficiency, tap regularity |
| FR-05 | คำนวณ Quality metrics | Smoothness (SPARC), ROM, tremor index |
| FR-06 | เปรียบเทียบ Left vs Right (Symmetry Index) | SI score พร้อม visualization |
| FR-07 | แยกแยะ Natural Dominance vs Learned Non-Use | Output พร้อม confidence |
| FR-08 | Export รายงานผล | JSON / PDF |

### 3.2 UI / Frontend

| ID | ความต้องการ | รายละเอียด |
|----|------------|-----------|
| UI-01 | หน้า Upload วิดีโอ | Drag & drop, เลือกไฟล์ |
| UI-02 | Webcam live mode | Real-time tracking + record |
| UI-03 | แสดงผล Feature Comparison | Left vs Right side-by-side |
| UI-04 | กราฟเปรียบเทียบ | Speed, Accuracy, Quality |
| UI-05 | แสดงผลการวินิจฉัย | ความเสี่ยง Learned Non-Use |
| UI-06 | รองรับ responsive | Desktop + tablet |

### 3.3 การแสดงผล

| หน้าจอ | องค์ประกอบ |
|--------|-----------|
| **Upload** | File uploader, Settings (duration, test type) |
| **Analysis** | Spinner, progress bar |
| **Result** | Dominant hand, LNU risk, Feature comparison, Symmetry chart |
| **Webcam** | Live preview, Record button, Countdown, Result |

---

## 4. ข้อกำหนดที่ไม่ใช่หน้าที่ (Non-Functional Requirements)

| ID | ความต้องการ | รายละเอียด |
|----|------------|-----------|
| NFR-01 | Performance | Video 2 นาที วิเคราะห์ ≤ 30 วินาที |
| NFR-02 | Accuracy | Hand detection confidence ≥ 0.5 |
| NFR-03 | Usability | ไม่ต้องติดตั้ง dependencies เพิ่ม |
| NFR-04 | Portability | รันบน Windows/Mac/Linux |
| NFR-05 | Privacy | ข้อมูลไม่ถูกส่งออกไป (ประมวลผล Local) |

---

## 5. Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Hand Tracking | Google MediaPipe Hand Landmarker |
| Video Processing | OpenCV |
| Signal Processing | NumPy, SciPy |
| Classification | scikit-learn (rule-based + ML) |
| Frontend | Streamlit |
| Storage | Local filesystem |

---

## 6. User Stories

1. ในฐานะ **แพทย์** ฉันต้องการ **อัปโหลดวิดีโอของผู้ป่วย** เพื่อ **วิเคราะห์ความเสี่ยง Learned Non-Use**
2. ในฐานะ **ผู้สูงอายุ** ฉันต้องการ **ทดสอบด้วยเว็บแคม** เพื่อ **รู้ว่ามือข้างไหนถนัดและมีความเสี่ยงหรือไม่**
3. ในฐานะ **นักกิจกรรมบำบัด** ฉันต้องการ **เปรียบเทียบผลรายสัปดาห์** เพื่อ **ติดตามความคืบหน้าในการฟื้นฟู**
4. ในฐานะ **ผู้ดูแล** ฉันต้องการ **ดูรายงานผลที่เข้าใจง่าย** เพื่อ **วางแผนการดูแลที่เหมาะสม**

---

## 7. Success Metrics

| Metric | Target |
|--------|--------|
| Hand detection success rate | ≥ 80% |
| Classification accuracy (vs expert) | ≥ 75% |
| Processing time (ต่อ 2 นาทีวิดีโอ) | ≤ 30 วินาที |
| User satisfaction (System Usability Scale) | ≥ 70 |

---

## 8. MVP Scope (Minimum Viable Product)

### ใน Scope (Phase 1)
- [x] Upload วิดีโอ
- [x] MediaPipe hand tracking (21 landmarks)
- [x] Speed metrics (tapping speed, peak velocity)
- [x] Accuracy metrics (tap regularity, endpoint error)
- [x] Quality metrics (smoothness, tremor index, ROM)
- [x] Symmetry Index
- [x] Classification (Natural vs Learned Non-Use)
- [x] Streamlit UI

### นอก Scope (Phase 2+)
- [ ] ML model training ด้วยข้อมูลจริง
- [ ] Fatigue analysis
- [ ] Report generation (PDF)
- [ ] Multi-language support
- [ ] Mobile app

---

## 9. Timeline

| เฟส | วันที่ | งาน |
|-----|-------|-----|
| **Planning & PRD** | 20-21 มิ.ย. | วิเคราะห์โจทย์, PRD, Research |
| **Phase 1: Foundation** | 21 มิ.ย. | MediaPipe integration, feature extraction |
| **Phase 2: Core Logic** | 22 มิ.ย. | Classification, Symmetry analysis |
| **Phase 3: UI/UX** | 22-23 มิ.ย. | Streamlit UI, Webcam mode |
| **Phase 4: Testing** | 23 มิ.ย. | Test with real videos, fix bugs |
| **Phase 5: Polish** | 23 มิ.ย. | Performance optimization, edge cases |
| **Submission** | 24 มิ.ย. 09:00 น. | วิดีโอ + Source code |

---

## 10. อ้างอิง

- โจทย์: `docs/แข่งขัน E-Health Hackathon 2026 Elderly AI Innovation.pdf`
- Medical background: [[02-Medical-Background/Learned Non-Use Syndrome]]
- Technology: [[03-Technology/MediaPipe Hand Tracking for Rehabilitation]]
- Metrics: [[03-Technology/Speed Accuracy Quality Metrics Framework]]
