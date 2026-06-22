import cv2
import numpy as np
import logging

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

logger = logging.getLogger("yolo_detector")


class YOLODetector:
    def __init__(self, model_path="yolov8n.pt", conf_threshold=0.5, iou_threshold=0.5):
        if YOLO is None:
            raise ImportError(
                "ultralytics not installed. Run: pip install ultralytics"
            )
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.person_class_id = 0

    def detect_persons(self, frame: np.ndarray):
        results = self.model(
            frame,
            classes=[self.person_class_id],
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            verbose=False,
        )
        boxes = []
        if len(results) > 0 and results[0].boxes is not None:
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                boxes.append({
                    "bbox": (x1, y1, x2, y2),
                    "confidence": conf,
                    "cx": (x1 + x2) / 2,
                    "cy": (y1 + y2) / 2,
                })
        return boxes

    def validate_landmarks(self, landmarks: np.ndarray, person_boxes: list, min_overlap=0.15):
        if not person_boxes:
            return False, 0.0

        hx, hy = landmarks[:, 0], landmarks[:, 1]
        hx1, hy1 = float(np.min(hx)), float(np.min(hy))
        hx2, hy2 = float(np.max(hx)), float(np.max(hy))
        hand_w = hx2 - hx1
        hand_h = hy2 - hy1
        if hand_w <= 0 or hand_h <= 0:
            return False, 0.0
        hand_area = hand_w * hand_h

        best_overlap = 0.0
        for pb in person_boxes:
            px1, py1, px2, py2 = pb["bbox"]
            ox1 = max(hx1, px1)
            oy1 = max(hy1, py1)
            ox2 = min(hx2, px2)
            oy2 = min(hy2, py2)
            if ox1 < ox2 and oy1 < oy2:
                overlap_area = (ox2 - ox1) * (oy2 - oy1)
                overlap_ratio = overlap_area / hand_area
                if overlap_ratio > best_overlap:
                    best_overlap = overlap_ratio

        return best_overlap >= min_overlap, best_overlap

    def validate_hands(self, hands_data: list, frame: np.ndarray):
        if not hands_data:
            return hands_data

        person_boxes = self.detect_persons(frame)
        if not person_boxes:
            return []

        validated = []
        for hand in hands_data:
            landmarks = hand["landmarks"]
            is_valid, overlap = self.validate_landmarks(landmarks, person_boxes)
            hand["yolo_validated"] = is_valid
            hand["yolo_overlap"] = round(overlap, 3)
            if is_valid:
                validated.append(hand)
        return validated

    def close(self):
        pass
