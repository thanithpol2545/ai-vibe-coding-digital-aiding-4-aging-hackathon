"""
Demo: Record hand via webcam -> Run analysis pipeline -> Show results.
Run: python src/demo_record.py
     (press SPACE to start/stop recording, ESC to quit)
"""
import sys, os, cv2, time, json, logging
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from hand_tracker import HandTracker
from features import FeatureExtractor
from classifier import DominanceClassifier
from logger import setup_logger

logger = setup_logger("demo_record")

os.makedirs(os.path.join(config.ASSETS_DIR, "recordings"), exist_ok=True)
sys.stdout.reconfigure(encoding='utf-8')

logger.info("=" * 60)
logger.info("HAND ASSESSMENT DEMO - Webcam Recording + Analysis")
logger.info("=" * 60)
logger.info("Controls:  SPACE = Start/Stop   ESC = Quit")
logger.info("=" * 60)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    logger.error("Cannot open webcam")
    exit(1)

fps = 30
recording = False
frame_idx = 0
all_frames = []
tracker = HandTracker()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    display = frame.copy()
    h, w = frame.shape[:2]
    hands = tracker.process_frame(frame)

    if hands:
        for hand_data in hands:
            for lm in hand_data["landmarks"]:
                cx, cy = int(lm[0]), int(lm[1])
                cv2.circle(display, (cx, cy), 4, (0, 255, 0), -1)
            wrist = hand_data["landmarks"][config.WRIST]
            cv2.putText(display, hand_data["hand"], (10, int(wrist[1])-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    if recording:
        cv2.circle(display, (40, 40), 15, (0, 0, 255), -1)
        cv2.putText(display, f"REC {frame_idx//fps}s", (60, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        all_frames.append({"frame": frame_idx, "time": frame_idx / fps, "hands": hands})
        frame_idx += 1
    else:
        cv2.putText(display, "[SPACE] Record  [ESC] Quit", (10, h-20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    cv2.imshow("Hand Assessment Demo", display)
    key = cv2.waitKey(1) & 0xFF

    if key == 27:
        break
    elif key == 32:
        if not recording:
            recording = True; frame_idx = 0; all_frames = []
            logger.info("[REC] Started...")
        else:
            recording = False
            logger.info("[STOP] Stopped (%d frames)", len(all_frames))
            if len([f for f in all_frames if f["hands"]]) > 3:
                data = {"fps": fps, "total_frames": len(all_frames), "frames": all_frames}
                extractor = FeatureExtractor(data)
                logger.info("=== ANALYSIS RESULTS ===")
                for hand_name in ["Left", "Right"]:
                    feats = extractor.extract_all(hand_name, "tapping")
                    logger.info("  %s: Speed=%.2f/s  Taps=%d  Smooth=%.2f  ROM=%.3f", hand_name, feats.tapping_speed, feats.tap_count, feats.movement_smoothness, feats.range_of_motion)

                left_feats = extractor.extract_all("Left", "tapping")
                right_feats = extractor.extract_all("Right", "tapping")
                sym = extractor.compute_symmetry_index(left_feats, right_feats)
                left_feats.symmetry_index = sym
                right_feats.symmetry_index = sym
                result = DominanceClassifier().classify(left_feats, right_feats)

                logger.info("  Result: Dominant=%s (%d%%)  LNU Risk=%d%%  %s", result.dominant_hand, int(result.confidence * 100), int(result.learned_non_use_risk * 100), result.details[:80])
                logger.info("=" * 60)
            else:
                logger.warning("  Too few hand detections. Try again.")

cap.release()
cv2.destroyAllWindows()
tracker.close()
logger.info("Done.")
