import logging
import numpy as np
from collections import defaultdict
from typing import List, Optional
from scipy.optimize import linear_sum_assignment

from app.ai import config

logger = logging.getLogger(__name__)


class KalmanBoxTracker:
    def __init__(self, bbox: list, track_id: int, confidence: float = 1.0):
        self.track_id = track_id
        self.confidence = confidence
        x1, y1, x2, y2 = bbox
        w, h = x2 - x1, y2 - y1
        cx, cy = x1 + w / 2.0, y1 + h / 2.0
        self.x = np.array([cx, cy, w, h, 0, 0], dtype=np.float64)
        self.P = np.eye(6) * 10.0
        self.F = np.eye(6)
        dt = 1.0
        self.F[0, 4] = dt
        self.F[1, 5] = dt
        self.H = np.eye(6)
        self.R = np.eye(6) * 1.0
        self.Q = np.eye(6) * 0.1
        self.hits = 1
        self.no_losses = 0
        self.age = 0

    def update(self, bbox: list, confidence: float = 1.0):
        self.hits += 1
        self.no_losses = 0
        self.confidence = confidence
        x1, y1, x2, y2 = bbox
        w, h = x2 - x1, y2 - y1
        cx, cy = x1 + w / 2.0, y1 + h / 2.0
        z = np.array([cx, cy, w, h, 0, 0], dtype=np.float64)

        y = z - self.H @ self.x
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y
        self.P = (np.eye(6) - K @ self.H) @ self.P

    def predict(self):
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        self.age += 1
        self.no_losses += 1
        return self.get_bbox()

    def get_bbox(self) -> list:
        cx, cy, w, h = self.x[0], self.x[1], self.x[2], self.x[3]
        x1 = int(cx - w / 2)
        y1 = int(cy - h / 2)
        x2 = int(cx + w / 2)
        y2 = int(cy + h / 2)
        return [max(0, x1), max(0, y1), x2, y2]

    def get_state(self) -> dict:
        return {
            "track_id": self.track_id,
            "bbox": self.get_bbox(),
            "confidence": self.confidence,
            "hits": self.hits,
            "age": self.age,
        }


def iou(bbox1: list, bbox2: list) -> float:
    x1 = max(bbox1[0], bbox2[0])
    y1 = max(bbox1[1], bbox2[1])
    x2 = min(bbox1[2], bbox2[2])
    y2 = min(bbox1[3], bbox2[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
    area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
    union = area1 + area2 - inter
    return inter / max(union, 1e-6)


class VehicleTracker:
    def __init__(self):
        self.trackers: List[KalmanBoxTracker] = []
        self.next_id = 0
        self.max_age = config.TRACKING_MAX_AGE
        self.min_hits = config.TRACKING_MIN_HITS
        self.iou_threshold = config.TRACKING_IOU_THRESHOLD

    def update(self, detections: list) -> list:
        for tracker in self.trackers:
            tracker.predict()

        if not detections:
            self.trackers = [t for t in self.trackers if t.no_losses < self.max_age]
            return [t.get_state() for t in self.trackers if t.hits >= self.min_hits]

        det_bboxes = np.array([d["bbox"] for d in detections])
        trk_bboxes = np.array([t.get_bbox() for t in self.trackers])

        if len(self.trackers) == 0:
            for i, det in enumerate(detections):
                self._create_tracker(det)
        else:
            cost_matrix = np.zeros((len(self.trackers), len(detections)), dtype=np.float64)
            for t, trk in enumerate(self.trackers):
                for d, det in enumerate(detections):
                    cost_matrix[t, d] = 1.0 - iou(trk.get_bbox(), det["bbox"])

            trk_indices, det_indices = linear_sum_assignment(cost_matrix)

            matched_dets = set()
            for t_idx, d_idx in zip(trk_indices, det_indices):
                if cost_matrix[t_idx, d_idx] < (1.0 - self.iou_threshold):
                    self.trackers[t_idx].update(
                        detections[d_idx]["bbox"],
                        detections[d_idx].get("confidence", 1.0),
                    )
                    matched_dets.add(d_idx)

            for i, det in enumerate(detections):
                if i not in matched_dets:
                    self._create_tracker(det)

        self.trackers = [t for t in self.trackers if t.no_losses < self.max_age]
        return [t.get_state() for t in self.trackers if t.hits >= self.min_hits]

    def _create_tracker(self, detection: dict):
        self.trackers.append(KalmanBoxTracker(
            detection["bbox"],
            self.next_id,
            detection.get("confidence", 1.0),
        ))
        self.next_id += 1

    def reset(self):
        self.trackers.clear()
        self.next_id = 0
