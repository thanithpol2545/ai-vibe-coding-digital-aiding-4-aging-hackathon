import sys, os, cv2, numpy as np, logging
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from hand_tracker import HandTracker

logger = logging.getLogger("extract_detections")

base = "D:/Project/Hackathon/2026/June/ai-vibe-coding-digital-aiding-4-aging-hackathon/assets"
out_dir = os.path.join(config.BASE_DIR, "docs", "Research", "04-Analysis", "detection_samples")

for name, max_save in [("60-L-cut.mp4", 20), ("67-R-cut.mp4", 20)]:
    path = os.path.join(base, name)
    if not os.path.exists(path):
        logger.warning("NOT FOUND: %s", path)
        continue

    tracker = HandTracker()
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    video_out = os.path.join(out_dir, name.replace(".mp4", ""))
    os.makedirs(video_out, exist_ok=True)
    
    frame_idx = 0
    saved = 0
    connections = [
        (0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),
        (0,9),(9,10),(10,11),(11,12),(0,13),(13,14),(14,15),(15,16),
        (0,17),(17,18),(18,19),(19,20),(5,9),(9,13),(13,17)
    ]

    while saved < max_save:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_idx % 5 == 0:
            out = tracker.process_frame(frame)
            hands = out.get("hands", [])
            if hands:
                display = frame.copy()
                for h in hands:
                    for i, lm in enumerate(h["landmarks"]):
                        cx, cy = int(lm[0]), int(lm[1])
                        cv2.circle(display, (cx, cy), 5, (0, 255, 0), -1)
                    for a, b in connections:
                        if a < len(h["landmarks"]) and b < len(h["landmarks"]):
                            pt1 = tuple(h["landmarks"][a][:2].astype(int))
                            pt2 = tuple(h["landmarks"][b][:2].astype(int))
                            cv2.line(display, pt1, pt2, (0, 255, 0), 2)
                    
                    wrist = h["landmarks"][config.WRIST]
                    cv2.putText(display, f"{h['hand']} HAND", (int(wrist[0])-20, int(wrist[1])-15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                
                time_sec = frame_idx / fps
                cv2.putText(display, f"{name} t={time_sec:.1f}s", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(display, f"Hands detected: {len(hands)}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                out_path = os.path.join(video_out, f"detect_{saved+1}_frame{frame_idx}_t{time_sec:.0f}s.jpg")
                cv2.imwrite(out_path, display)
                saved += 1
                logger.info("  %s: saved #%d - frame %d (t=%.1fs) %s", name, saved, frame_idx, time_sec, [h['hand'] for h in hands])
        
        frame_idx += 1
    
    cap.release()
    tracker.close()
    logger.info("%s: %d detection samples from %d frames (%d checked)", name, saved, total, frame_idx)

logger.info("All detection samples saved to: %s", out_dir)
