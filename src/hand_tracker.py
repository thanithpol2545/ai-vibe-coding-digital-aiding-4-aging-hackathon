import cv2, numpy as np, urllib.request, os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import config


class HandTracker:
    def __init__(self, model_path=None, use_yolo=True):
        model_path = model_path or config.MODEL_PATH
        if not os.path.exists(model_path):
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            print(f"Downloading hand landmarker model to {model_path}...")
            urllib.request.urlretrieve(config.MODEL_URL, model_path)
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=config.NUM_HANDS,
            running_mode=vision.RunningMode.IMAGE,
            min_hand_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.yolo = None
        if use_yolo:
            try:
                from yolo_detector import YOLODetector
                self.yolo = YOLODetector(
                    model_path=config.YOLO_MODEL_PATH,
                    conf_threshold=config.YOLO_CONFIDENCE,
                )
                print("YOLO hand validation enabled")
            except Exception as e:
                print(f"YOLO not available — skipping hand validation ({e})")

    def process_frame(self, frame: np.ndarray):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.detector.detect(mp_image)
        hands = self._parse_result(result, frame.shape[:2])
        if hands and self.yolo:
            hands = self.yolo.validate_hands(hands, frame)
        return hands

    def _parse_result(self, result, frame_shape):
        hands_data = []
        h, w = frame_shape
        if result.hand_landmarks:
            for idx, landmarks in enumerate(result.hand_landmarks):
                handedness = "Unknown"
                if result.handedness and idx < len(result.handedness):
                    handedness = result.handedness[idx][0].category_name
                pts = np.array([[lm.x * w, lm.y * h, lm.z * w] for lm in landmarks])
                hands_data.append({
                    "hand": handedness,
                    "landmarks": pts,
                    "landmarks_norm": np.array([[lm.x, lm.y, lm.z] for lm in landmarks]),
                })
        return hands_data

    def process_video(self, video_path: str, max_frames=None, step=1):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_data = []
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % step == 0:
                hands = self.process_frame(frame)
                if hands:
                    frame_data.append({
                        "frame": frame_idx,
                        "time_sec": frame_idx / fps,
                        "hands": hands,
                    })
            frame_idx += 1
            if max_frames and frame_idx >= max_frames:
                break

        cap.release()
        return {"fps": fps, "total_frames": total, "frames": frame_data}

    def close(self):
        self.detector.close()
