import os
import json
import uuid
from datetime import datetime
from typing import Optional
import config
from logger import setup_logger

logger = setup_logger("session")

SESSION_DIR = os.path.join(config.ASSETS_DIR, "recordings", "sessions")
os.makedirs(SESSION_DIR, exist_ok=True)


def new_session_id():
    return uuid.uuid4().hex[:12]


def save_session(patient_name: str, patient_age: int, patient_notes: str,
                 result) -> str:
    sid = new_session_id()
    session = {
        "session_id": sid,
        "timestamp": datetime.now().isoformat(),
        "patient": {
            "name": patient_name,
            "age": patient_age,
            "notes": patient_notes,
        },
        "result": {
            "dominant_hand": result.dominant_hand,
            "learned_non_use_risk": result.learned_non_use_risk,
            "is_learned_non_use": result.is_learned_non_use,
            "confidence": result.confidence,
            "details": result.details,
            "symmetry_index": result.left_features.symmetry_index,
            "left": {
                "tapping_speed": result.left_features.tapping_speed,
                "tap_count": result.left_features.tap_count,
                "tap_regularity": result.left_features.tap_regularity,
                "path_efficiency": result.left_features.path_efficiency,
                "movement_smoothness": result.left_features.movement_smoothness,
                "range_of_motion": result.left_features.range_of_motion,
                "tremor_index": result.left_features.tremor_index,
            },
            "right": {
                "tapping_speed": result.right_features.tapping_speed,
                "tap_count": result.right_features.tap_count,
                "tap_regularity": result.right_features.tap_regularity,
                "path_efficiency": result.right_features.path_efficiency,
                "movement_smoothness": result.right_features.movement_smoothness,
                "range_of_motion": result.right_features.range_of_motion,
                "tremor_index": result.right_features.tremor_index,
            },
        },
    }

    path = os.path.join(SESSION_DIR, f"{sid}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(session, f, indent=2, ensure_ascii=False)

    logger.info("Session saved: %s (%s)", sid, patient_name)
    return sid


def load_session(sid: str) -> Optional[dict]:
    path = os.path.join(SESSION_DIR, f"{sid}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_sessions(limit: int = 20) -> list:
    if not os.path.isdir(SESSION_DIR):
        return []
    sessions = []
    for fname in os.listdir(SESSION_DIR):
        if fname.endswith(".json"):
            path = os.path.join(SESSION_DIR, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    sessions.append({
                        "session_id": data.get("session_id", fname[:-5]),
                        "timestamp": data.get("timestamp", ""),
                        "patient_name": data.get("patient", {}).get("name", "?"),
                        "dominant_hand": data.get("result", {}).get("dominant_hand", "?"),
                        "lnu_risk": data.get("result", {}).get("learned_non_use_risk", 0),
                    })
            except Exception:
                pass
    sessions.sort(key=lambda s: s["timestamp"], reverse=True)
    return sessions[:limit]
