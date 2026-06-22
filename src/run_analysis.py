import sys, os, logging
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from hand_tracker import HandTracker
from features import FeatureExtractor
from classifier import DominanceClassifier
import json
from logger import setup_logger

logger = setup_logger("run_analysis")

def analyze_video(video_path, label=""):
    logger.info("=" * 60)
    logger.info("ANALYZING: %s", label or video_path)
    logger.info("=" * 60)
    
    tracker = HandTracker()
    data = tracker.process_video(video_path, step=1)
    tracker.close()
    
    n = len(data["frames"])
    logger.info("Frames with hands detected: %d", n)
    
    if n < 3:
        logger.warning("Too few hand detections to analyze")
        return None
    
    hand_counts = {"Left": 0, "Right": 0}
    for f in data["frames"]:
        for h in f["hands"]:
            if h["hand"] in hand_counts:
                hand_counts[h["hand"]] += 1
    logger.info("Hand distribution: %s", hand_counts)
    
    extractor = FeatureExtractor(data)
    
    for hand_name in ["Left", "Right"]:
        feats = extractor.extract_all(hand_name, "tapping")
        logger.info("  %s Hand:", hand_name)
        logger.info("    Tapping Speed:   %.3f taps/s", feats.tapping_speed)
        logger.info("    Tap Count:       %d", feats.tap_count)
        logger.info("    Tap Regularity:  %.3f", feats.tap_regularity)
        logger.info("    Avg Amplitude:   %.4f", feats.avg_amplitude)
        logger.info("    Peak Velocity:   %.4f", feats.avg_peak_velocity)
        logger.info("    Path Efficiency: %.3f", feats.path_efficiency)
        logger.info("    Smoothness:      %.3f", feats.movement_smoothness)
        logger.info("    Range of Motion: %.4f", feats.range_of_motion)
        logger.info("    Tremor Index:    %.3f", feats.tremor_index)
        logger.info("    Endpoint Error:  %.4f", feats.endpoint_error)
    
    left_feats = extractor.extract_all("Left", "tapping")
    right_feats = extractor.extract_all("Right", "tapping")
    sym_index = extractor.compute_symmetry_index(left_feats, right_feats)
    left_feats.symmetry_index = sym_index
    right_feats.symmetry_index = sym_index
    
    cls = DominanceClassifier()
    result = cls.classify(left_feats, right_feats)
    
    # For front-facing camera videos, MediaPipe's "Right" = person's Left hand
    # Map to physical handedness for clarity
    if "60-L-cut" in label or "67-R-cut" in label:
        # These are front-facing recordings
        actual_dominant = {"Left": "Right (person's Left)", "Right": "Left (person's Right)"}
        actual_detected = actual_dominant.get(result.dominant_hand, result.dominant_hand)
    else:
        actual_detected = result.dominant_hand
    
    logger.info("  CLASSIFICATION RESULT:")
    logger.info("    Dominant (camera): %s", result.dominant_hand)
    logger.info("    Dominant (person): %s", actual_detected)
    logger.info("    Confidence:        %.2f%%", result.confidence * 100)
    logger.info("    LNU Risk:          %.2f%%", result.learned_non_use_risk * 100)
    logger.info("    Is LNU:            %s", result.is_learned_non_use)
    logger.info("    Details:           %s", result.details)
    
    return result


base = "D:/Project/Hackathon/2026/June/ai-vibe-coding-digital-aiding-4-aging-hackathon/assets"
results = {}

for name, label in [("60-L-cut.mp4", "60-L-cut (expected: Left hand)"), ("67-R-cut.mp4", "67-R-cut (expected: Right hand)")]:
    path = os.path.join(base, name)
    if os.path.exists(path):
        result = analyze_video(path, label)
        results[name] = result
    else:
        print(f"\nFile not found: {path}")

# Save results
out_path = os.path.join(config.BASE_DIR, "docs", "Research", "04-Analysis", "real_analysis_results.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({
        k: {
            "dominant_hand": v.dominant_hand,
            "confidence": v.confidence,
            "learned_non_use_risk": v.learned_non_use_risk,
            "is_learned_non_use": v.is_learned_non_use,
            "details": v.details,
        } if v else None
        for k, v in results.items()
    }, f, indent=2, ensure_ascii=False)

logger.info("Results saved to: %s", out_path)
