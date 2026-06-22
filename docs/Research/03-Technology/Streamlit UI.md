# Streamlit UI Structure

**File:** `src/app.py`

---

## 1. Layout

```
Sidebar                                     Main Area
├── Patient Info                            ├── Upload Video mode
│   ├── Name, Age, Notes                    │   └── file_uploader → process → display
├── Settings                                └── Webcam (Live) mode
│   ├── Input mode (Upload / Webcam)            └── state machine loop
│   ├── Test type (Finger Tapping / Reach / Combined)
│   └── Duration (5–30s)
├── Clinical Info
├── Tips
├── References
└── Session History
    └── Load previous results
```

---

## 2. Input Modes

### 2.1 Upload Video

1. `st.file_uploader` — accepts mp4, avi, mov, webm
2. Save to temp file → `process_video_progressive()`
3. Live progress bar + frame preview with hand landmarks
4. Show results via `display_metrics()`
5. Save session / download PDF buttons

### 2.2 Webcam (Live)

1. `cv2.VideoCapture(0)` — 640×480 resolution
2. State machine: preview → countdown → recording → done
3. Each iteration: read frame → process hands → draw overlay → `st.image()`

---

## 3. Drawing Overlays (`src/guidance.py`)

| Function | State | Description |
|----------|-------|-------------|
| `draw_setup_overlay()` | preview | Dimmed frame + green zone rectangle + exercise posture instructions |
| `draw_countdown()` | countdown | Large centered number + "เตรียม..." label |
| `draw_recording_overlay()` | recording | REC indicator, remaining time, zone outline, live cues |

### 3.1 Recording Overlay Elements

```
┌─────────────────────────────────┐
│ 🔴 REC           ⏱ 8s / 10s   │
│                                 │
│   ┌─────────────────────┐      │
│   │  (hand zone)        │      │
│   └─────────────────────┘      │
│                                 │
│       👆 แตะนิ้วให้ใหญ่และเร็ว!  │
└─────────────────────────────────┘
```

### 3.2 Cue Messages (by time remaining)

| Remaining | Color | Message |
|-----------|-------|---------|
| No hand detected | Yellow | "🖐️ หันฝ่ามือเข้าหากล้อง" |
| > 4s | Green | Exercise-specific "go" cue |
| 1–4s | Orange | "อีกนิดเดียว! สุดแรง! 🔥" |
| 0s | Cyan | "เยี่ยมมาก! 🎉" |

---

## 4. Results Display (`display_metrics`)

### 4.1 Three-Column Top Section

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Dominant hand + confidence | LNU risk (color-coded) | Classification details |

### 4.2 Feature Comparison

Two side-by-side JSON panels:
- **Left Hand:** speed, regularity, velocity, efficiency, smoothness, ROM, tremor
- **Right Hand:** same metrics

### 4.3 Symmetry Index

Single metric display: `0.0` = perfect, higher = more asymmetric.

### 4.4 Action Buttons

- **💾 Save Session** — persists to `assets/recordings/sessions/`
- **📄 Download PDF** — generates A4 report via `src/report.py`

---

## 5. CSS Styling (`app.py` lines 14–26)

- Background: `#f0f2f6` (light gray)
- Metric cards: white, rounded, shadow
- Risk colors: red (high), yellow (moderate), green (low)
- Full-width buttons
