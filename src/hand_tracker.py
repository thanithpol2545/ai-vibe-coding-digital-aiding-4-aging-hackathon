import cv2, numpy as np, urllib.request, os, logging
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import config
from logger import setup_logger

logger = setup_logger("hand_tracker")


class HandTracker:
    def __init__(self, model_path=None, use_yolo=True, use_pose=True):
        model_path = model_path or config.MODEL_PATH
        if not os.path.exists(model_path):
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            logger.info("Downloading hand landmarker model to %s", model_path)
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
                logger.info("YOLO hand validation enabled")
            except Exception as e:
                logger.warning("YOLO not available — skipping hand validation: %s", e)
        self.pose_detector = None
        self.use_pose = use_pose and config.USE_POSE
        if self.use_pose:
            try:
                model_path_pose = os.path.join(
                    config.ASSETS_DIR, f"{config.POSE_MODEL_NAME}.task"
                )
                if not os.path.exists(model_path_pose):
                    os.makedirs(config.ASSETS_DIR, exist_ok=True)
                    pose_url = (
                        "https://storage.googleapis.com/mediapipe-models/"
                        "pose_landmarker/pose_landmarker_lite/float16/1/"
                        "pose_landmarker_lite.task"
                    )
                    logger.info("Downloading pose model to %s", model_path_pose)
                    urllib.request.urlretrieve(pose_url, model_path_pose)
                pose_base = python.BaseOptions(model_asset_path=model_path_pose)
                pose_options = vision.PoseLandmarkerOptions(
                    base_options=pose_base,
                    running_mode=vision.RunningMode.IMAGE,
                    min_pose_detection_confidence=config.POSE_MIN_DETECTION_CONFIDENCE,
                    min_tracking_confidence=config.POSE_MIN_TRACKING_CONFIDENCE,
                )
                self.pose_detector = vision.PoseLandmarker.create_from_options(pose_options)
                logger.info("MediaPipe Pose Landmarker enabled")
            except Exception as e:
                logger.warning("Pose Landmarker not available: %s", e)
                self.use_pose = False

    def process_frame(self, frame: np.ndarray):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.detector.detect(mp_image)
        hands = self._parse_result(result, frame.shape[:2])
        if hands and self.yolo:
            hands = self.yolo.validate_hands(hands, frame)

        pose = None
        if self.use_pose and self.pose_detector:
            try:
                pose_result = self.pose_detector.detect(mp_image)
                pose = self._parse_pose(pose_result, frame.shape[:2])
            except Exception as e:
                logger.debug("Pose detection error: %s", e)

        return {"hands": hands, "pose": pose}

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

    def _parse_pose(self, result, frame_shape):
        h, w = frame_shape
        if not result.pose_landmarks:
            return None
        landmarks = result.pose_landmarks[0]
        pts = {}
        for idx in config.ARM_LANDMARKS:
            lm = landmarks[idx]
            pts[idx] = {
                "x": lm.x * w,
                "y": lm.y * h,
                "z": lm.z * w,
                "visibility": lm.visibility,
            }
        return pts

    def _compute_arm_angles(self, pose: dict) -> dict:
        if not pose:
            return {}
        angles = {}
        for side, (sh_idx, el_idx, wr_idx) in {
            "Left": (config.LEFT_SHOULDER, config.LEFT_ELBOW, config.LEFT_WRIST),
            "Right": (config.RIGHT_SHOULDER, config.RIGHT_ELBOW, config.RIGHT_WRIST),
        }.items():
            if sh_idx not in pose or el_idx not in pose or wr_idx not in pose:
                continue
            sh = np.array([pose[sh_idx]["x"], pose[sh_idx]["y"]])
            el = np.array([pose[el_idx]["x"], pose[el_idx]["y"]])
            wr = np.array([pose[wr_idx]["x"], pose[wr_idx]["y"]])
            v1 = el - sh
            v2 = wr - el
            dot = np.dot(v1, v2)
            norm = np.linalg.norm(v1) * np.linalg.norm(v2)
            angle = np.degrees(np.arccos(np.clip(dot / (norm + 1e-10), -1.0, 1.0)))
            angles[f"{side.lower()}_elbow_angle"] = float(angle)
            dist = np.linalg.norm(wr - sh)
            angles[f"{side.lower()}_reach_distance"] = float(dist)
        return angles

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
                out = self.process_frame(frame)
                hands = out.get("hands", [])
                pose = out.get("pose")
                entry = {
                    "frame": frame_idx,
                    "time_sec": frame_idx / fps,
                    "hands": hands,
                }
                if pose:
                    entry["pose"] = pose
                    entry["arm_angles"] = self._compute_arm_angles(pose)
                if hands or pose:
                    frame_data.append(entry)
            frame_idx += 1
            if max_frames and frame_idx >= max_frames:
                break

        cap.release()
        return {"fps": fps, "total_frames": total, "frames": frame_data}

    def close(self):
        self.detector.close()
