# Streamlit UI Structure

## App Entry (`app.py`)

### Layout
- Sidebar: Settings (input mode, test type, duration), clinical info
- Main: Upload mode OR Webcam mode (mutually exclusive)

### Input Modes

**Upload Video** (`input_mode == "Upload Video"`):
1. `st.file_uploader` → accept mp4/avi/mov/webm
2. Save to temp file → `process_video_progressive()`
3. Display progress bar + real-time frame preview
4. Show results via `display_metrics()`

**Webcam (Live)** (`input_mode != "Upload Video"`):
1. Open `cv2.VideoCapture(0)`
2. State machine loop: preview → countdown → recording → done
3. Each iteration: read frame → process → draw overlay → display

### Drawing Overlays (guidance.py)

| Function | Used In | Description |
|----------|---------|-------------|
| `draw_setup_overlay()` | preview | Dimmed frame + zone rectangle + posture instructions |
| `draw_countdown()` | countdown | Large centered number + "เตรียม..." text |
| `draw_recording_overlay()` | recording | REC indicator, remaining time, zone outline, cues |

### Recording Overlay Colors (guidance.py)

- REC indicator: Red circle + "REC" text (top-left)
- Timer: `⏱ Xs / Ys` (top-right, white on black)
- Zone: Green rectangle (upper-center)
- Cues:
  - No hand: Yellow message
  - >4s remaining: Green "go" cue
  - 0-4s remaining: Yellow "almost" cue
  - 0s remaining: Cyan "done" cue

### Display Metrics (display_metrics)

Three-column layout:
1. Dominant hand with confidence
2. LNU risk (color-coded: red/yellow/green)
3. Classification details

Two-column feature comparison:
- Left hand metrics JSON
- Right hand metrics JSON

Symmetry index display
