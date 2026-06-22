import cv2, numpy as np, json, os, urllib.request
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

base = 'D:/Project/Hackathon/2026/June/AI Vibe Coding - Digital Aiding 4 Aging Hackathon/assets/'
output = {}

model_path = os.path.join(base, 'hand_landmarker.task')
if not os.path.exists(model_path):
    url = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
    print(f"Downloading model from {url}...")
    urllib.request.urlretrieve(url, model_path)
    print("Model downloaded")

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,
    running_mode=vision.RunningMode.VIDEO,
    min_hand_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
def create_detector():
    return vision.HandLandmarker.create_from_options(options)

for name in ['60-L-cut.mp4', '67-R-cut.mp4']:
    detector = create_detector()
    path = base + name
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total == 0:
        print(f"{name}: ERROR - cannot read video")
        continue
    
    # Process every 30th frame (1 per sec at 30fps)
    process_every = 30
    frame_results = []
    frame_count = 0
    timestamp_ms = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % process_every == 0:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp_ms = int((frame_count / fps) * 1000)
            result = detector.detect_for_video(mp_image, timestamp_ms)
            
            landmarks_data = []
            if result.hand_landmarks:
                for hand_idx, hand_landmarks in enumerate(result.hand_landmarks):
                    handedness_label = 'Unknown'
                    if result.handedness and hand_idx < len(result.handedness):
                        handedness_label = result.handedness[hand_idx][0].category_name
                    pts = []
                    for lm in hand_landmarks:
                        pts.append({'x': round(lm.x, 4), 'y': round(lm.y, 4), 'z': round(lm.z, 4)})
                    landmarks_data.append({'hand': handedness_label, 'landmarks': pts})
            
            if landmarks_data:
                frame_results.append({
                    'frame': frame_count,
                    'time_sec': round(frame_count/fps, 2),
                    'timestamp_ms': timestamp_ms,
                    'hands': landmarks_data
                })
        
        frame_count += 1
    
    pct = len(frame_results)/total*100
    print(f"\n{name}:")
    print(f"  Processed {frame_count}/{total} frames")
    print(f"  Hands detected in {len(frame_results)} samples ({pct:.1f}% of frames)")
    
    hand_counts = {}
    for f in frame_results:
        for h in f['hands']:
            hand_counts[h['hand']] = hand_counts.get(h['hand'], 0) + 1
    
    print(f"  Hand distribution: {hand_counts}")
    print(f"  Detections over time:")
    for s in frame_results[:10]:
        hands_str = "+".join([h['hand'] for h in s['hands']])
        print(f"    t={s['time_sec']}s frame={s['frame']}: {hands_str}")
    if len(frame_results) > 10:
        print(f"    ... and {len(frame_results) - 10} more")
    
    # Calculate hand position stats
    if frame_results:
        # Track fingertip movement
        fingertip_indices = [4, 8, 12, 16, 20]  # thumb, index, middle, ring, little tips
        hand_positions = {'Left': [], 'Right': []}
        for f in frame_results:
            for h in f['hands']:
                hand_name = h['hand']
                if hand_name in hand_positions:
                    fingertips = [h['landmarks'][i] for i in fingertip_indices]
                    hand_positions[hand_name].append({
                        'time': f['time_sec'],
                        'wrist': h['landmarks'][0],
                        'fingertips': fingertips
                    })
        
        for hand_name, positions in hand_positions.items():
            if len(positions) > 1:
                # Calculate movement speed
                total_dist = 0
                for i in range(1, len(positions)):
                    p1 = positions[i-1]['wrist']
                    p2 = positions[i]['wrist']
                    dist = np.sqrt((p2['x']-p1['x'])**2 + (p2['y']-p1['y'])**2)
                    total_dist += dist
                avg_speed = total_dist / max(len(positions)-1, 1)
                print(f"  {hand_name}: avg wrist movement per step = {avg_speed:.4f}")
    
    output[name] = {
        'fps': fps,
        'total_frames': total,
        'duration_sec': total/fps,
        'frames_with_hands': len(frame_results),
        'detection_rate_pct': round(pct, 1),
        'hand_distribution': hand_counts,
        'sample_interval': process_every
    }

    cap.release()
    detector.close()

out_path = 'D:/Project/Hackathon/2026/June/AI Vibe Coding - Digital Aiding 4 Aging Hackathon/docs/Research/hand_analysis.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"\nResults saved to: {out_path}")
print("DONE")
