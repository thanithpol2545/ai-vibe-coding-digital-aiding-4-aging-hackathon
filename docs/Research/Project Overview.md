# Hand Assessment AI — Project Overview

**Target**: E-Health Hackathon 2026 — AI system for elderly hand movement analysis  
**Goal**: Differentiate natural handedness from Learned Non-Use (LNU) after stroke  
**Stack**: Python + Streamlit + MediaPipe + YOLOv8 + OpenCV + scikit-learn

## Core Pipeline

1. **Hand Detection** — MediaPipe HandLandmarker (21 landmarks per hand), validated by YOLO person detection
2. **Feature Extraction** — From 2D landmark trajectories: tapping speed, regularity, amplitude, velocity, reach time, path efficiency, smoothness, tremor, ROM, symmetry
3. **Classification** — Rule-based heuristic classifier that compares left/right feature asymmetry to determine dominance and LNU risk

## Project Structure

```
src/
  app.py                  # Streamlit main app (upload + webcam modes)
  hand_tracker.py         # MediaPipe + YOLO hand detection wrapper
  yolo_detector.py        # YOLO hand validation module
  features.py             # FeatureExtractor class (tapping + reach features)
  classifier.py           # DominanceClassifier (rule-based)
  config.py               # Paths, constants, dataclasses
  guidance.py             # Drawing utilities (setup overlay, countdown, recording overlay)
  live_analysis.py        # Standalone analysis script
  demo_record.py          # Demo recording script
  run_analysis.py         # Analysis runner
  analyze_hands.py        # Hand analysis utility
  check_frames.py         # Frame checking utility
  extract_detections.py   # Detection extraction utility
  ocr_video.py            # OCR video utility
```

## Key Design Decisions

- **Streamlit over Flask/FastAPI**: Rapid prototyping for hackathon
- **MediaPipe over OpenCV Haar**: Better landmark accuracy, 21 points per hand
- **YOLO validation added later**: Reduces false positives from non-hand MediaPipe detections
- **Rule-based classifier over ML**: Interpretability for clinical validation
- **Two input modes**: Upload (offline analysis) + Webcam (real-time screening)
