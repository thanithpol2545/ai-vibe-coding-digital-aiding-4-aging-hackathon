import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from hand_tracker import HandTracker
from features import FeatureExtractor
from classifier import DominanceClassifier
import json

def analyze_video(video_path, label=""):
    print(f"\n{'='*60}")
    print(f"ANALYZING: {label or video_path}")
    print(f"{'='*60}")
    
    tracker = HandTracker()
    data = tracker.process_video(video_path, step=1)
    tracker.close()
    
    n = len(data["frames"])
    print(f"Frames with hands detected: {n}")
    
    if n < 3:
        print("Too few hand detections to analyze")
        return None
    
    # Count hand types
    hand_counts = {"Left": 0, "Right": 0}
    for f in data["frames"]:
        for h in f["hands"]:
            if h["hand"] in hand_counts:
                hand_counts[h["hand"]] += 1
    print(f"Hand distribution: {hand_counts}")
    
    # Note: MediaPipe labels hands from camera perspective.
    # If person faces camera, their actual Left appears on camera Right.
    # We detect both, compare performance, and report relative dominance.
    extractor = FeatureExtractor(data)
    
    for hand_name in ["Left", "Right"]:
        feats = extractor.extract_all(hand_name, "tapping")
        print(f"\n  {hand_name} Hand:")
        print(f"    Tapping Speed:   {feats.tapping_speed:.3f} taps/s")
        print(f"    Tap Count:       {feats.tap_count}")
        print(f"    Tap Regularity:  {feats.tap_regularity:.3f}")
        print(f"    Avg Amplitude:   {feats.avg_amplitude:.4f}")
        print(f"    Peak Velocity:   {feats.avg_peak_velocity:.4f}")
        print(f"    Path Efficiency: {feats.path_efficiency:.3f}")
        print(f"    Smoothness:      {feats.movement_smoothness:.3f}")
        print(f"    Range of Motion: {feats.range_of_motion:.4f}")
        print(f"    Tremor Index:    {feats.tremor_index:.3f}")
        print(f"    Endpoint Error:  {feats.endpoint_error:.4f}")
    
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
    
    print(f"\n  CLASSIFICATION RESULT:")
    print(f"    Dominant (camera): {result.dominant_hand}")
    print(f"    Dominant (person): {actual_detected}")
    print(f"    Confidence:        {result.confidence:.2%}")
    print(f"    LNU Risk:          {result.learned_non_use_risk:.2%}")
    print(f"    Is LNU:            {result.is_learned_non_use}")
    print(f"    Details:           {result.details}")
    
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

print(f"\nResults saved to: {out_path}")
