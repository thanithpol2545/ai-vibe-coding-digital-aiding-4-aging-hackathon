# Finger Tapping Test (FTT) — การทดสอบการแตะนิ้ว

> **Finger Tapping Test (Finger Oscillation Test)** เป็นส่วนหนึ่งของ Halstead-Reitan Neuropsychological Battery
> ใช้วัด motor speed, cortical integrity, และ efferent motor pathways

---

## 1. วิธีการทดสอบมาตรฐาน

### 1.1 ขั้นตอน
1. ผู้ถูกทดสอบนั่งสบาย วางมือบนโต๊ะ
2. ใช้นิ้วชี้แตะบนพื้นราบ (หรือปุ่มกด) เร็วที่สุดเท่าที่ทำได้
3. ทดสอบ **30 วินาที** ต่อ trial
4. ทำ 3-6 trials สลับระหว่างมือถนัดและไม่ถนัด
5. บันทึกจำนวนครั้งที่แตะได้
6. อาจมี practice trial ก่อนเริ่มจริง

### 1.2 รูปแบบต่างๆ
| รูปแบบ | ระยะเวลา | จำนวน trials | การนับ |
|--------|---------|--------------|--------|
| Standard FTT | 30 วิ | 3-6 trials | จำนวนครั้ง |
| 10-second FTT | 10 วิ | 3 trials ต่อมือ | จำนวนครั้ง |
| Computerized FTT | แปรผัน | แปรผัน | Inter-tap interval |
| Finger-to-thumb | 10-30 วิ | 2-3 trials | จำนวนครั้งที่แตะ |

---

## 2. Normative Data

### 2.1 จำนวนครั้งที่แตะได้ (30 วินาที)
| กลุ่มอายุ | เพศ | มือถนัด | มือไม่ถนัด |
|-----------|-----|---------|-----------|
| 20-29 | ชาย | 65-75 | 60-70 |
| 20-29 | หญิง | 58-68 | 53-63 |
| 40-49 | ชาย | 55-65 | 50-60 |
| 40-49 | หญิง | 50-60 | 45-55 |
| 60-69 | ชาย | 45-55 | 40-50 |
| 60-69 | หญิง | 40-50 | 35-45 |
| 70+ | ชาย | 35-45 | 30-40 |
| 70+ | หญิง | 30-40 | 25-35 |

**ที่มา:** Ruff & Parker (1993), Criswell et al. (2010)

### 2.2 ปัจจัยที่มีผล
- **อายุ:** ความเร็วลดลง ~5-10% ต่อทศวรรษ หลังจากอายุ 30
- **เพศ:** ชายแตะเร็วกว่าหญิง ~10%
- **มือถนัด:** มือถนัดแตะเร็วกว่า ~5-10%
- **Pathology:** Parkinson's, Stroke, PMD → FTT ลดลง

---

## 3. Clinical Applications

### 3.1 Parkinson's Disease
| การศึกษา | ข้อค้นพบ |
|---------|----------|
| Criswell et al. (2010) | FTT score สัมพันธ์ inverse กับ Hoehn & Yahr stage (p<.001) |
| Criswell et al. (2010) | FTT decay > 10-15% → suspect bradykinesia |
| MDS-UPDRS | Finger tapping เป็น 1 ใน 3 motor tasks หลัก |

### 3.2 Stroke
- **ความเร็วลดลง** ในมือข้างที่อ่อนแรง
- **Asymmetry** ระหว่างมือข้างที่ affected vs unaffected
- **Fatigue:** จำนวนครั้งลดลงระหว่าง trial = abnormal

### 3.3 Psychogenic Movement Disorders (PMD)
| Metric | PMD | Normal | IPD |
|--------|-----|--------|-----|
| Mean FTT (30s) | 41.72 | ~60 | ~55 |
| Variability | สูง | ต่ำ | ปานกลาง |
| Effort | inconsistent | consistent | consistent |

**Cutoff ratio:** ≤ 0.670 → 89.1% specificity, 76.9% sensitivity for PMD

### 3.4 Cognitive Assessment in Elderly
- **MDPI JPM (2022):** FTT parameters สามารถ classify CHI vs MCI ได้บางส่วน
- **Self-selected pace vs Fast pace:** 4 vs 8 parameters แตกต่างระหว่างกลุ่ม
- **ข้อจำกัด:** Classify ถูกต้อง ~50% → ควรใช้ร่วมกับ cognitive test อื่น

---

## 4. FTT Parameters

| Parameter | คำอธิบาย | ความหมายทางคลินิก |
|-----------|---------|------------------|
| **Mean taps** | จำนวนครั้งเฉลี่ยต่อ trial | Motor speed |
| **Coefficient of Variation (CV)** | SD/Mean | Consistency |
| **Inter-tap interval (ITI)** | ระยะห่างระหว่าง tap | Rhythm |
| **Tap duration** | ระยะเวลาที่นิ้วแตะพื้น | Motor control |
| **Fatigue index** | (max-min)/max first 5-10 วิ | Endurance |
| **Reaction time** | เวลาตั้งแต่ start signal | Processing speed |
| **Asymmetry ratio** | Non-dominant/dominant | Hemispheric difference |

---

## 5. การนำมาใช้กับ AI Vibe Coding

### 5.1 Video-based FTT with MediaPipe
```
Camera → Frame → MediaPipe (21 landmarks)
  → Extract index finger tip (landmark 8)
  → Track Y-position over time
  → Detect taps (local minima in Y)
  → Calculate: frequency, ITI, variability
  → Compare L vs R hand
  → Score!
```

### 5.2 Metrics Mapping
| FTT Parameter | Video Metric | MediaPipe |
|--------------|-------------|-----------|
| Number of taps | Finger tip Y-local minima count | Landmark 8 (Index Tip) |
| Tap speed | Taps/second | Time between Y minima |
| Rhythm consistency | CV of inter-tap interval | ITI standard deviation |
| Fatigue | Change in frequency over time | Rolling window analysis |
| Accuracy | Hit target zone? | Distance from finger to target |

### 5.3 Features ที่ควร Implement
- [ ] Real-time tap detection
- [ ] Left vs Right comparison
- [ ] Normative data overlay
- [ ] Fatigue trend line
- [ ] Asymmetry score
- [ ] Learned Non-Use indicator

---

## 6. References

1. **Ruff, R.M. & Parker, S.B.** (1993). Gender- and age-specific changes in motor speed and eye-hand coordination in adults: normative values for the Finger Tapping and Grooved Pegboard Tests. *Perceptual and Motor Skills*, 76(3 Pt 2), 1219-1230. https://doi.org/10.2466/pms.1993.76.3c.1219

2. **Criswell, S.R., et al.** (2010). Sensitivity and specificity of the finger tapping task for the detection of psychogenic movement disorders. *Parkinsonism & Related Disorders*, 16(3), 197-201. https://doi.org/10.1016/j.parkreldis.2009.11.007

3. **Di Libero, T., et al.** (2024). An Overall Automated Architecture Based on the Tapping Test Measurement Protocol: Hand Dexterity Assessment through an Innovative Objective Method. *Sensors*, 24(12), 3953. https://doi.org/10.3390/s24123953

4. **MDPI JPM** (2022). Finger Tapping as a Biomarker to Classify Cognitive Status in 80+-Year-Olds. *Journal of Personalized Medicine*, 12(2), 286. https://doi.org/10.3390/jpm12020286

5. **Axelrod, B., Meyers, J.E., & Davis, J.J.** (2014). Finger Tapping Test Performance as a Measure of Performance Validity. *Archives of Clinical Neuropsychology*, 29(4), 365-371.

6. **Lachnit, H. & Pieper, W.** (1990). Speed and accuracy effects of fingers and dexterity in 5-choice reaction tasks. *Ergonomics*, 33(12), 1443-1454. https://doi.org/10.1080/00140139008925345
