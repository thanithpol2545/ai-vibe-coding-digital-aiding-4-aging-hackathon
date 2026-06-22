import sys, os, cv2, numpy as np, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from hand_tracker import HandTracker
from features import FeatureExtractor
from classifier import DominanceClassifier


def analyze_video_realtime(video_path):
    tracker = HandTracker()
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_data = []
    frame_idx = 0
    step = 3
    process_count = 0

    try:
        cv2.namedWindow("Live Analysis — Press ESC to skip | Q to quit", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Live Analysis", 960, 720)
    except:
        pass

    start_time = time.time()
    result = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        display = frame.copy()
        h_disp, w_disp = display.shape[:2]

        if frame_idx % step == 0:
            hands = tracker.process_frame(frame)
            if hands:
                frame_data.append({
                    "frame": frame_idx,
                    "time_sec": frame_idx / fps,
                    "hands": hands,
                })
                process_count += 1

                for h in hands:
                    for lm in h["landmarks"]:
                        cx, cy = int(lm[0]), int(lm[1])
                        cv2.circle(display, (cx, cy), 5, (0, 255, 0), -1)
                    color = (255, 0, 0) if h["hand"] == "Left" else (0, 0, 255)
                    cv2.putText(display, h["hand"], (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        progress = min(frame_idx / total, 1.0) if total > 0 else 0
        elapsed = time.time() - start_time
        bar_w = int(300 * progress)
        cv2.rectangle(display, (10, h_disp - 40), (10 + 300, h_disp - 20), (50, 50, 50), -1)
        cv2.rectangle(display, (10, h_disp - 40), (10 + bar_w, h_disp - 20), (0, 200, 0), -1)
        cv2.putText(display, f"{progress*100:.0f}%", (320, h_disp - 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.putText(display, f"Frame {frame_idx}/{total} | Detections: {process_count}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

        if len(frame_data) >= 3:
            data = {"fps": fps, "frames": frame_data}
            extractor = FeatureExtractor(data)
            left = extractor.extract_all("Left", "tapping")
            right = extractor.extract_all("Right", "tapping")
            sym = extractor.compute_symmetry_index(left, right)
            left.symmetry_index = sym
            right.symmetry_index = sym

            cls = DominanceClassifier()
            result = cls.classify(left, right)

            cv2.putText(display, f"Dominant: {result.dominant_hand} ({result.confidence:.0%})", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 100), 2)
            risk_color = (0, 0, 255) if result.is_learned_non_use else (0, 200, 0)
            cv2.putText(display, f"LNU Risk: {result.learned_non_use_risk:.1%}", (10, 115),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, risk_color, 2)

            y = 150
            for name, feats, clr in [("L", left, (255, 0, 0)), ("R", right, (0, 0, 255))]:
                cv2.putText(display, f"{name} | taps:{feats.tap_count} speed:{feats.tapping_speed:.2f}/s reg:{feats.tap_regularity:.2f}", (10, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, clr, 1)
                cv2.putText(display, f"         smooth:{feats.movement_smoothness:.1f} rom:{feats.range_of_motion:.3f} tremor:{feats.tremor_index:.2f} eff:{feats.path_efficiency:.2f}", (10, y + 18),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, clr, 1)
                y += 50

        cv2.imshow("Live Analysis — Press ESC to skip | Q to quit", display)
        key = cv2.waitKey(1) & 0xFF
        if key in [27, ord('q')]:
            break

        frame_idx += 1

    cap.release()
    cv2.destroyAllWindows()
    tracker.close()

    total_time = time.time() - start_time
    print(f"\nProcessed {frame_idx} frames in {total_time:.1f}s ({frame_idx/max(total_time,0.1):.1f} fps)")
    print(f"Hand detections: {process_count}")

    if not frame_data:
        print("No hands detected — check video content")
        return None

    data = {"fps": fps, "frames": frame_data}
    extractor = FeatureExtractor(data)
    left = extractor.extract_all("Left", "tapping")
    right = extractor.extract_all("Right", "tapping")
    sym = extractor.compute_symmetry_index(left, right)
    left.symmetry_index = sym
    right.symmetry_index = sym

    cls = DominanceClassifier()
    result = cls.classify(left, right)

    for name, feats in [("Left", left), ("Right", right)]:
        print(f"  {name}: {feats.tap_count} taps, {feats.tapping_speed:.2f}/s, RoM={feats.range_of_motion:.3f}")

    print(f"\n{'='*50}")
    print(f"  Dominant:  {result.dominant_hand} ({result.confidence:.1%})")
    print(f"  LNU Risk:  {result.learned_non_use_risk:.1%}")
    print(f"  Is LNU:    {result.is_learned_non_use}")
    print(f"  Details:   {result.details}")
    print(f"{'='*50}")

    return result


if __name__ == "__main__":
    video = sys.argv[1] if len(sys.argv) > 1 else None
    if not video or not os.path.exists(video):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates = [os.path.join(base, "assets", f) for f in [
            "bilateral_coordination.mp4", "hand_dexterity_3_exercises.mp4",
            "hand_exercises_70plus.mp4", "60-L-cut.mp4", "67-R-cut.mp4"
        ]]
        video = next((c for c in candidates if os.path.exists(c)), None)
        if not video:
            print("Usage: python live_analysis.py <video_path>")
            sys.exit(1)

    print(f"Loading: {video}")
    analyze_video_realtime(video)
