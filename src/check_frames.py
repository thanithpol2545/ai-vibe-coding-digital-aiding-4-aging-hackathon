import cv2, sys, os
sys.path.insert(0, 'D:/Project/Hackathon/2026/June/ai-vibe-coding-digital-aiding-4-aging-hackathon/src')
import config

out_dir = os.path.join(config.BASE_DIR, 'docs', 'Research', '04-Analysis', 'detection_samples', '60-L-cut')

for fname in sorted(os.listdir(out_dir))[:5]:
    path = os.path.join(out_dir, fname)
    img = cv2.imread(path)
    h, w = img.shape[:2]
    mean_b = img.mean()
    print(f"{fname}: {w}x{h}, mean_brightness={mean_b:.0f}")
    
    # Check for skin-colored regions (indicates hands)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    skin_mask = cv2.inRange(hsv, (0, 20, 70), (20, 255, 255))
    skin_pct = (skin_mask > 0).sum() / (h * w) * 100
    print(f"  Skin-tone pixels: {skin_pct:.1f}%")
    
    # Describe content (simple analysis)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_pct = (edges > 0).sum() / (h * w) * 100
    print(f"  Edge pixels: {edge_pct:.1f}%")

# Check what the original analysis JSON says
data_path = os.path.join(config.BASE_DIR, 'docs', 'Research', '04-Analysis', 'hand_analysis.json')
import json
if os.path.exists(data_path):
    data = json.load(open(data_path))
    for vid_name, info in data.items():
        print(f"\n{vid_name}: {info.get('detection_rate_pct', '?')}% detection rate, {info.get('frames_with_hands', 0)} frames with hands")
        print(f"  Hand distribution: {info.get('hand_distribution', {})}")
