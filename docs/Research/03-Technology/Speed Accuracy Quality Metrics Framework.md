# Speed-Accuracy-Quality Metrics Framework — กรอบการวัดผล

> **3 เสาหลักของการประเมินการเคลื่อนไหวของมือ:**
> ความเร็ว (Speed) + ความแม่นยำ (Accuracy) + คุณภาพการเคลื่อนไหว (Quality of Movements)
> เพื่อแยกแยะระหว่างแขนที่ถนัดโดยธรรมชาติ กับ Learned Non-Use

---

## 1. Speed (ความเร็ว)

### 1.1 Metrics

| Metric | สูตร | หน่วย |
|--------|------|-------|
| **Movement velocity** | v = Δd / Δt | pixels/s หรือ mm/s |
| **Peak velocity** | max(v(t)) | pixels/s |
| **Time to peak velocity** | t(peak) - t(start) | ms |
| **Reaction time** | t(move > 5% max) - t(stimulus) | ms |
| **Completion time** | t(end) - t(start) | s |
| **Tapping frequency** | number of taps / trial time | taps/s |
| **Acceleration** | a = Δv / Δt | pixels/s² |

### 1.2 Interpretation
| ค่า Speed | ความหมาย |
|-----------|---------|
| **สูง** | Reflexes ดี, motor control ปกติ |
| **ต่ำ** | Bradykinesia, อ่อนแรง, Learned Non-Use |
| **ลดลงระหว่าง trial** | Fatigue, endurance ต่ำ |
| **Asymmetry L vs R > 15%** | อาจมี pathology ข้างที่ช้ากว่า |

### 1.3 Fitts' Law
```
Movement Time = a + b × log₂(2A/W)
```
- A = amplitude (ระยะทาง)
- W = target width (ขนาดเป้าหมาย)
- **Speed-accuracy trade-off:** ยิ่งเร็ว = ยิ่งพลาดง่าย
- ผู้ป่วย Learned Non-Use มักเลือก speed ต่ำเพื่อ accuracy

---

## 2. Accuracy (ความแม่นยำ)

### 2.1 Metrics

| Metric | สูตร | ความหมาย |
|--------|------|---------|
| **Endpoint error** | √((x_actual-x_target)² + (y_actual-y_target)²) | ความคลาดเคลื่อนจากเป้าหมาย |
| **Path length ratio** | actual path / ideal straight line | เส้นทางอ้อม |
| **Error rate** | number of errors / total attempts | % ความผิดพลาด |
| **Target hit rate** | hits / total attempts | % การเข้าเป้า |
| **Spatial variability** | SD of endpoint positions | ความสม่ำเสมอ |
| **Overshoot/Undershoot** | movement past vs short of target | การควบคุมแรง |

### 2.2 Finger Confusion Pattern (Lachnit & Pieper, 1990)
- **Spatial proximity:** นิ้วที่อยู่ใกล้กัน → มักสับสนกัน
- **Asymmetry:** Error bias ไปทางนิ้วใกล้โคน (thumb side)
- **Little finger:** False alarm rate ต่ำที่สุด, reliability สูงที่สุด
- **ไม่ขึ้นกับ dexterity level** (ข้อน่าสนใจ)

### 2.3 Interpretation
| ค่า Accuracy | ความหมาย |
|-------------|---------|
| **สูง** | Motor control ดี, visual-motor integration ปกติ |
| **ต่ำ** | Dysmetria, ataxia, sensory deficit |
| **Inconsistent** | Attention lapses, fatigue, PMD |
| **Asymmetry L vs R** | Unilateral pathology → Learned Non-Use |

---

## 3. Quality of Movements (คุณภาพการเคลื่อนไหว)

### 3.1 Smoothness (ความลื่นไหล)

| Metric | สูตร | ค่าตีความ |
|--------|------|----------|
| **Jerk** | j = d³x/dt³ | ต่ำ = ลื่นไหล |
| **Normalized Jerk (LJ)** | -ln(Jerk² × duration⁵ / length²) | สูง = ลื่นไหล |
| **SPARC** | Spectral Arc Length | สูง = ลื่นไหล |
| **Number of velocity peaks** | Count peaks in |v(t)| | น้อย = smooth |
| **Movement units** | Number of acceleration-deceleration phases | น้อย = smooth |

### 3.2 Range of Motion (ROM)

| Metric | วิธีวัด |
|--------|---------|
| **MCP flexion** | Angle between landmarks 0-5-6 (Index) |
| **PIP flexion** | Angle between landmarks 5-6-7 |
| **DIP flexion** | Angle between landmarks 6-7-8 |
| **Hand aperture** | Distance landmark 4 to landmark 8,12,16,20 |
| **Wrist deviation** | Angle of wrist trajectory |

### 3.3 Coordination (การประสานงาน)

| Metric | วิธีวัด |
|--------|---------|
| **Inter-joint correlation** | Cross-correlation between joint angles |
| **Finger individuation** | Movement of one finger without moving others |
| **Bilateral coupling** | Cross-correlation L vs R hand |
| **Movement synergy** | PCA of multi-joint movement |

### 3.4 Symmetry Index (SI)

```
SI = (X_R - X_L) / (0.5 × (X_R + X_L)) × 100
```
- **SI ≈ 0:** สมมาตร (ปกติ)
- **SI > 10%:** Asymmetry (อาจเป็น Learned Non-Use)
- **SI > 20%:** Significant asymmetry (pathology)

---

## 4. Decision Framework

### 4.1 Feature Vector
```
X = [Speed_L, Speed_R, Speed_SI,
     Accuracy_L, Accuracy_R, Accuracy_SI,
     Quality_L, Quality_R, Quality_SI,
     Age, Gender, Handedness]
```

### 4.2 Classification Logic
```
Input: Feature Vector X

Step 1: Calculate individual scores
  Speed_Score = f(Speed_L, Speed_R)       [0-100]
  Accuracy_Score = f(Accuracy_L, Accuracy_R) [0-100]
  Quality_Score = f(Quality_L, Quality_R)   [0-100]

Step 2: Calculate asymmetry scores
  Speed_Asymmetry = |SI_speed|
  Accuracy_Asymmetry = |SI_accuracy|
  Quality_Asymmetry = |SI_quality|

Step 3: Rule-based classification
  IF (all SI < 10%) AND (dominant hand faster by 5-10%)
    → Natural Dominance (Normal)
  
  IF (SI_speed > 15%) AND (SI_quality > 15%)
    AND (non-dominant hand shows higher jerk, lower ROM)
    → Possible Learned Non-Use
  
  IF (SI > 25%) AND (fatigue present)
    AND (quality significantly worse on one side)
    → High Risk Learned Non-Use

Step 4: ML Classification (optional)
  Model: Random Forest / XGBoost
  Train on features + ground truth labels
  Output: Learned Non-Use probability
```

### 4.3 Composite Score

```
Overall Dominance Score = w1 × Speed + w2 × Accuracy + w3 × Quality

Learned Non-Use Risk Score = 
  w4 × Speed_Asymmetry + 
  w5 × Accuracy_Asymmetry + 
  w6 × Quality_Asymmetry

Default weights: w1=0.3, w2=0.3, w3=0.4, w4=0.25, w5=0.35, w6=0.40
```

---

## 5. Implementation Roadmap

### Phase 1: Basic (MVP)
- [ ] Extract 21 landmarks with MediaPipe
- [ ] Calculate basic speed (fingertip velocity)
- [ ] Simple L vs R comparison
- [ ] Score visualization

### Phase 2: Intermediate
- [ ] Accuracy calculation (target deviation)
- [ ] Smoothness metrics (Jerk, velocity peaks)
- [ ] Joint angle estimation (MCP, PIP, DIP)
- [ ] Asymmetry indices

### Phase 3: Advanced
- [ ] ML classification (Random Forest / XGBoost)
- [ ] Fatigue analysis over time
- [ ] Real-time feedback
- [ ] Report generation

---

## 6. References

1. **Fitts, P.M.** (1954). The information capacity of the human motor system in controlling the amplitude of movement. *Journal of Experimental Psychology*, 47(6), 381-391.

2. **Lachnit, H. & Pieper, W.** (1990). Speed and accuracy effects of fingers and dexterity in 5-choice reaction tasks. *Ergonomics*, 33(12), 1443-1454. https://doi.org/10.1080/00140139008925345

3. **Amprimo, G., et al.** (2023). Hand tracking for clinical applications. arXiv:2308.01088.

4. **Balasubramanian, S., et al.** (2015). A robust method for movement smoothness measurement. *Journal of NeuroEngineering and Rehabilitation*, 12, 104. https://doi.org/10.1186/s12984-015-0093-6

5. **Alt Murphy, M., et al.** (2011). Kinematic variables quantifying upper-extremity performance after stroke during reaching and drinking from a glass. *Neurorehabilitation and Neural Repair*, 25(1), 71-80.

6. **Hogan, N. & Sternad, D.** (2009). Sensitivity of smoothness measures to movement duration, amplitude, and arrests. *Journal of Motor Behavior*, 41(6), 529-534.
