import os
from dataclasses import dataclass, field
from typing import List, Tuple

# ─── Paths ───
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
MODEL_PATH = os.path.join(ASSETS_DIR, "hand_landmarker.task")
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)

# ─── MediaPipe ───
NUM_HANDS = 2
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5

# ─── YOLO ───
YOLO_MODEL_PATH = "yolov8n.pt"
YOLO_CONFIDENCE = 0.5
YOLO_IOU = 0.5
YOLO_MIN_HAND_OVERLAP = 0.15

# ─── Landmark Indices ───
WRIST = 0
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20

FINGERTIPS = [THUMB_TIP, INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP]

# Base of each finger (MCP joint)
THUMB_MCP = 2
INDEX_MCP = 5
MIDDLE_MCP = 9
RING_MCP = 13
PINKY_MCP = 17

FINGER_MCPS = [THUMB_MCP, INDEX_MCP, MIDDLE_MCP, RING_MCP, PINKY_MCP]

# PIP joints (middle knuckle) for finger flexion
INDEX_PIP = 6
MIDDLE_PIP = 10
RING_PIP = 14
PINKY_PIP = 18

# ─── Feature Extraction ───
TAP_ZONE_RADIUS = 0.05
MOVEMENT_FILTER_WINDOW = 5
MIN_TAP_DISTANCE = 0.02
PEAK_VELOCITY_THRESHOLD = 0.001

# ─── Classification Defaults ───
HAND_LABELS = ["Left", "Right"]


@dataclass
class HandFeatures:
    hand: str
    tapping_speed: float = 0.0
    tap_count: int = 0
    tap_regularity: float = 0.0
    avg_amplitude: float = 0.0
    avg_peak_velocity: float = 0.0
    reach_time: float = 0.0
    path_efficiency: float = 0.0
    endpoint_error: float = 0.0
    movement_smoothness: float = 0.0
    range_of_motion: float = 0.0
    tremor_index: float = 0.0
    symmetry_index: float = 0.0


@dataclass
class ClassificationResult:
    dominant_hand: str = ""
    learned_non_use_risk: float = 0.0
    is_learned_non_use: bool = False
    confidence: float = 0.0
    details: str = ""
    left_features: HandFeatures = field(default_factory=lambda: HandFeatures(hand="Left"))
    right_features: HandFeatures = field(default_factory=lambda: HandFeatures(hand="Right"))
