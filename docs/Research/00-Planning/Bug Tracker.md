# Bug Tracker & Known Issues

---

## Fixed Bugs

### B1: `draw_recording_overlay()` missing `duration`
- **File**: `app.py:318`
- **Cause**: Stale `__pycache__` from before `duration` parameter was added
- **Fix**: Delete `__pycache__` directory
- **Status**: ✅ Fixed

### B2: `hands_ready` counted hands outside zone
- **File**: `app.py:253-269`
- **Cause**: Counter incremented for ANY hand detection, not just in-zone hands
- **Fix**: Moved `hands_ready += 1` inside the `if in_zone:` check
- **Status**: ✅ Fixed

### B3: `process_video_progressive` used global `test_type`
- **File**: `app.py:126`
- **Cause**: Function referenced module-level `test_type` instead of parameter
- **Fix**: Added `test_type` parameter; updated caller to pass it
- **Status**: ✅ Fixed

### B4: Webcam mode always used tapping features
- **File**: `app.py:326-327`
- **Cause**: `extract_all("Left", "tapping")` hardcoded regardless of `test_type`
- **Fix**: Choose feature type based on `test_type`; add reach features for reach/combined tests
- **Status**: ✅ Fixed

### B5: `cam_state` not in session state initialization
- **File**: `app.py:49-55`
- **Cause**: Initialized `"step"` (unused) instead of `"cam_state"`
- **Fix**: Replaced `"step"` with `"cam_state"` in session state keys
- **Status**: ✅ Fixed

### B6: Colors swapped in upload mode (BGR→RGB)
- **File**: `app.py:88-90, 104-106`
- **Cause**: BGR colors drawn on frame, then `cv2.cvtColor(BGR→RGB)` swapped R/B channels
- **Fix**: Convert to RGB first, draw on RGB copy, display with `channels="RGB"`
- **Status**: ✅ Fixed

### B7: No webcam `isOpened()` check
- **File**: `app.py:231`
- **Cause**: `cv2.VideoCapture(0)` without checking if camera opened
- **Fix**: Added `if not cap.isOpened(): st.error() + st.stop()`
- **Status**: ✅ Fixed

### B8: Countdown `break` only exits inner loop
- **File**: `app.py:277-285`
- **Cause**: `break` in inner `while` loop doesn't stop outer `for` loop
- **Fix**: Added `cam_fail` flag to break outer loop on camera failure
- **Status**: ✅ Fixed

---

## Remaining Issues

### I1: Hardcoded 30 FPS in webcam mode
- **File**: `app.py:245`
- **Impact**: Timing slightly off if camera delivers different FPS
- **Workaround**: Near enough for screening purposes

### I2: `endpoint_error` measures distance from origin
- **File**: `features.py:108-111`
- **Impact**: Metric has no clinical meaning — always reports large values
- **Note**: Not used in classification, only displayed

### I3: Reach features overwrite tapping features in upload mode
- **File**: `app.py:126-131`
- **Impact**: `path_efficiency` and `movement_smoothness` from reach replace tapping values
- **Note**: Affects Combined test type only
