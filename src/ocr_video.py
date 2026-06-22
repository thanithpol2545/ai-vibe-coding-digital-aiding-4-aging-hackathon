import cv2, numpy as np, os, sys
import easyocr

sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\Project\Hackathon\2026\June\ai-vibe-coding-digital-aiding-4-aging-hackathon\assets\YTMP3GG_YouTube_Media_TTA1mb4ZQeI_002_720p.mp4'
out_dir = r'D:\Project\Hackathon\2026\June\ai-vibe-coding-digital-aiding-4-aging-hackathon\docs\Research\slides_ocr'
os.makedirs(out_dir, exist_ok=True)

cap = cv2.VideoCapture(path)
fps = cap.get(cv2.CAP_PROP_FPS)

# Key timestamps from previous analysis
key_times = list(range(0, 14400, 120))  # every 2 min for first 4 hours

reader = easyocr.Reader(['en'], gpu=False, verbose=False)

results_log = []
current_section = "INTRO"

for i, sec in enumerate(key_times):
    if i % 30 == 0:
        print(f"Progress: {i}/{len(key_times)} ({sec//60}m{sec%60:02d}s)", flush=True)
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(sec * fps))
    ret, frame = cap.read()
    if not ret: continue
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean_b = np.mean(gray)
    h, w = frame.shape[:2]
    
    if mean_b < 15:
        continue
    
    # Use EasyOCR only on center 50% for speed
    crop = frame[h//4:3*h//4, w//4:3*w//4]
    
    try:
        result = reader.readtext(crop, detail=0, paragraph=True, min_size=10, low_text=0.3)
        text = ' | '.join([r for r in result if len(r) > 5])
        if text:
            results_log.append((sec, text[:200]))
    except:
        pass

cap.release()

print("\n" + "="*70)
print("OCR RESULTS (every 2 min)")
print("="*70)

for t, txt in results_log:
    ts = f"{t//60:02d}m{t%60:02d}s"
    print(f"\n[{ts}] {txt}")

# Save to file
out_file = os.path.join(out_dir, 'ocr_results.txt')
with open(out_file, 'w', encoding='utf-8') as f:
    for t, txt in results_log:
        f.write(f"t={t//60:02d}m{t%60:02d}s | {txt}\n")

print(f"\n\nSaved to: {out_file}")
print(f"Total OCR entries: {len(results_log)}")
