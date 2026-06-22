import numpy as np
from scipy import signal, ndimage
from typing import List, Dict
import config


class FeatureExtractor:
    def __init__(self, frame_data: Dict):
        self.fps = frame_data.get("fps", 30)
        self.frames = frame_data.get("frames", [])

    def extract_arm_features(self, hand_name: str):
        side = hand_name.lower()
        angle_key = f"{side}_elbow_angle"
        dist_key = f"{side}_reach_distance"
        times, angles, distances = [], [], []
        for f in self.frames:
            arm = f.get("arm_angles")
            if arm and angle_key in arm:
                times.append(f["time_sec"])
                angles.append(arm[angle_key])
                distances.append(arm[dist_key])
        if not angles:
            return None
        feats = config.HandFeatures(hand=hand_name)
        feats.range_of_motion = float(np.ptp(angles))
        max_dist = max(distances) if distances else 0.0
        feats.reach_time = float(times[np.argmax(distances)] - times[0]) if len(times) > 1 else 0.0
        if len(angles) > 2:
            vel = np.diff(angles) / np.diff(times)
            feats.avg_peak_velocity = float(np.max(np.abs(vel))) if len(vel) > 0 else 0.0
            feats.movement_smoothness = float(np.std(vel))
        return feats

    def _get_hand_trajectory(self, hand_name: str, landmark_idx=config.WRIST):
        times, positions = [], []
        for f in self.frames:
            for h in f["hands"]:
                if h["hand"] == hand_name:
                    pts = h["landmarks_norm"]
                    positions.append(pts[landmark_idx][:2])
                    times.append(f["time_sec"])
                    break
        if not positions:
            return np.array([]), np.array([])
        return np.array(times), np.array(positions)

    def _compute_velocity(self, times: np.ndarray, positions: np.ndarray):
        if len(times) < 2:
            return np.array([])
        dt = np.diff(times)
        dt = np.where(dt == 0, 1e-6, dt)
        vel = np.diff(positions, axis=0) / dt[:, None]
        speed = np.linalg.norm(vel, axis=1)
        return speed

    def _compute_jerk(self, positions: np.ndarray, dt: float):
        if len(positions) < 4:
            return 0.0
        vel = np.diff(positions, axis=0) / dt
        acc = np.diff(vel, axis=0) / dt
        jerk = np.diff(acc, axis=0) / dt
        return float(np.sum(np.linalg.norm(jerk, axis=1) ** 2))

    def extract_tapping_features(self, hand_name: str):
        times, positions = self._get_hand_trajectory(hand_name, config.INDEX_TIP)
        if len(times) < 3:
            return config.HandFeatures(hand=hand_name)

        feats = config.HandFeatures(hand=hand_name)
        speed = self._compute_velocity(times, positions)

        # Speed: tapping frequency via peak detection in vertical movement
        y_pos = positions[:, 1]
        if len(y_pos) >= 5:
            kernel = min(5, len(y_pos) // 2 * 2 + 1)
            if kernel >= 3:
                y_pos = signal.medfilt(y_pos, kernel_size=kernel)

        min_dist = max(3, self.fps // 10)
        peaks, props = signal.find_peaks(-y_pos, distance=min_dist, prominence=0.005)
        valleys, _ = signal.find_peaks(y_pos, distance=min_dist, prominence=0.005)

        if len(peaks) > 0:
            feats.tap_count = len(peaks)
            if len(peaks) > 1:
                inter_tap = np.diff(times[peaks])
                mean_it = np.mean(inter_tap)
                feats.tapping_speed = float(1.0 / mean_it) if mean_it > 0 else 0.0
                feats.tap_regularity = float(1.0 - np.std(inter_tap) / mean_it) if mean_it > 0 else 0.0
                if len(valleys) > 0:
                    paired = min(len(peaks), len(valleys))
                    feats.avg_amplitude = float(np.mean(np.abs(y_pos[peaks[:paired]] - y_pos[valleys[:paired]])))
            else:
                feats.tapping_speed = float(len(peaks) / (times[-1] - times[0])) if times[-1] > times[0] else 0.0

        # Speed: peak velocity
        if len(speed) > 0:
            if len(speed) > 5:
                feats.avg_peak_velocity = float(np.mean(speed[speed > np.percentile(speed, 80)]))
            else:
                feats.avg_peak_velocity = float(np.mean(speed))

        # Accuracy: path efficiency (straight-line / actual)
        if len(positions) > 1:
            total_dist = np.sum(np.linalg.norm(np.diff(positions, axis=0), axis=1))
            straight_dist = np.linalg.norm(positions[-1] - positions[0])
            feats.path_efficiency = float(straight_dist / (total_dist + 1e-10))

        # Quality: smoothness (SPARC approximation)
        if len(speed) > 10:
            try:
                freqs = np.fft.rfftfreq(len(speed), d=1.0 / self.fps)
                mag = np.abs(np.fft.rfft(speed))
                mag = mag / (np.max(mag) + 1e-10)
                cutoff = freqs < 5
                freqs, mag = freqs[cutoff], mag[cutoff]
                sparc = -np.trapz(np.log(mag + 1e-10), freqs)
                feats.movement_smoothness = float(sparc)
            except Exception:
                feats.movement_smoothness = 0.0

        # Quality: tremor index (high-freq energy ratio)
        if len(speed) > 20:
            freqs, psd = signal.periodogram(speed, fs=self.fps)
            low = np.trapz(psd[(freqs >= 0.5) & (freqs < 3)])
            high = np.trapz(psd[(freqs >= 3) & (freqs < 12)])
            feats.tremor_index = float(high / (low + 1e-10))

        # Accuracy: spatial variability of tap endpoints
        if len(peaks) > 2:
            tap_x = positions[peaks, 0]
            tap_y = positions[peaks, 1]
            feats.endpoint_error = float(np.mean(np.sqrt(tap_x ** 2 + tap_y ** 2)))

        # Range of Motion
        feats.range_of_motion = float(np.ptp(y_pos))

        return feats

    def extract_reach_features(self, hand_name: str):
        times, positions = self._get_hand_trajectory(hand_name, config.INDEX_TIP)
        if len(times) < 5:
            return config.HandFeatures(hand=hand_name)

        feats = config.HandFeatures(hand=hand_name)
        speed = self._compute_velocity(times, positions)

        # Speed metrics
        if len(speed) > 0:
            feats.avg_peak_velocity = float(np.max(speed))
            ttp_idx = np.argmax(speed)
            feats.reach_time = float(times[ttp_idx] - times[0]) if ttp_idx < len(times) - 1 else float(times[-1] - times[0])

        # Accuracy: path efficiency (straight-line / actual)
        if len(positions) > 1:
            total_dist = np.sum(np.linalg.norm(np.diff(positions, axis=0), axis=1))
            straight_dist = np.linalg.norm(positions[-1] - positions[0])
            feats.path_efficiency = float(straight_dist / (total_dist + 1e-10))

        # Quality: jerk cost
        dt = 1.0 / self.fps
        feats.movement_smoothness = float(self._compute_jerk(positions, dt))

        # Range of Motion
        feats.range_of_motion = float(np.max(np.linalg.norm(positions - positions[0], axis=1)))

        return feats

    def compute_symmetry_index(self, left_feats: config.HandFeatures, right_feats: config.HandFeatures):
        keys = ["tapping_speed", "tap_regularity", "path_efficiency", "movement_smoothness", "range_of_motion"]
        diffs = []
        for k in keys:
            lv = getattr(left_feats, k, 0.0)
            rv = getattr(right_feats, k, 0.0)
            denom = max(abs(lv), abs(rv), 1e-10)
            diffs.append(abs(lv - rv) / denom)
        return float(np.mean(diffs))

    def extract_all(self, hand_name: str, test_type="tapping"):
        if test_type == "tapping":
            return self.extract_tapping_features(hand_name)
        return self.extract_reach_features(hand_name)
