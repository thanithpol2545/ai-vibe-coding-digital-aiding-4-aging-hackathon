# AI Vibe Coding Hackathon 2026 — Project Summary

## Goal
Build an AI system that analyzes hand movement from video to detect **learned non-use syndrome** and **hand dominance** in elderly adults.

## Problem Statement
**Source:** `docs/แข่งขัน E-Health Hackathon 2026 Elderly AI Innovation.pdf`

Differentiate between:
- **Natural hand dominance** (normal asymmetry)
- **Learned Non-Use** (pathological disuse of one hand despite physical capability)

3 assessment pillars: **Speed** | **Accuracy** | **Quality of Movement**

## Tech Stack
| Component | Tech |
|-----------|------|
| Python 3.10+ | Core language |
| OpenCV | Video processing |
| MediaPipe Hand Landmarker | 21-point hand tracking |
| NumPy / SciPy | Signal processing, kinematics |
| scikit-learn | Classification |
| Streamlit | Web UI (webcam + upload) |

## Project Structure
```
ai-vibe-coding-digital-aiding-4-aging-hackathon/
├── assets/
│   └── hand_landmarker.task          ← MediaPipe model (auto-downloaded)
├── docs/
│   ├── Research/                     ← Obsidian vault
│   │   ├── Main.md                   ← Entry point
│   │   ├── 01-Problem/               ← Problem analysis, video notes
│   │   ├── 02-Medical-Background/    ← LNU, CIMT, dexterity, tapping test
│   │   ├── 03-Technology/            ← MediaPipe, speed/accuracy framework
│   │   └── 04-Analysis/             ← Video analysis results
│   ├── SUMMARY.md                    ← This file
│   └── แข่งขัน E-Health Hackathon 2026 Elderly AI Innovation.pdf
├── src/
│   ├── app.py                        ← Streamlit UI entry point
│   ├── config.py                     ← Constants, landmark indices, thresholds
│   ├── hand_tracker.py               ← MediaPipe hand landmark detection
│   ├── features.py                   ← Speed/Accuracy/Quality feature extraction
│   ├── classifier.py                 ← Dominance + Learned Non-Use classifier
│   ├── analyze_hands.py              ← Legacy: batch video analysis
│   └── ocr_video.py                  ← Legacy: video slide OCR
├── video/                            ← Presentation video output
├── requirements.txt
└── .gitignore
```

## Pipeline
```
Input (webcam/video)
  → OpenCV frame capture
    → MediaPipe 21-point landmarks (L+R hands)
      → Feature extraction:
          Speed: tap frequency, peak velocity, reach time
          Accuracy: endpoint error, path efficiency, tap regularity
          Quality: smoothness (SPARC/jerk), ROM, tremor index, symmetry
        → Classification (rule-based + ML)
          → Output: Dominant hand + Learned Non-Use risk score
```

## Key References
- Amprimo et al. (2023) — MediaPipe for neurorehab assessment
- Kwakkel et al. (2015) — Learned Non-Use, Lancet Neurology
- Balasubramanian et al. (2015) — SPARC smoothness metric
- Taub et al. (2006) — Constraint-Induced Movement Therapy

## Deliverables
1. Source code on GitHub
2. Video presentation ≤10 min
3. Submit at https://forms.gle/sAzY9AK7Lj1wXHkq6

## Deadline
**24 มิ.ย. 69 เวลา 09:00 น.** (June 24, 2026, 09:00 AM)

## How to Run
```bash
cd ai-vibe-coding-digital-aiding-4-aging-hackathon
pip install -r requirements.txt
streamlit run src/app.py
```
