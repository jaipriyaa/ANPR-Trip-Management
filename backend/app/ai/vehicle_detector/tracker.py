import logging
import numpy as np
from typing import List, Dict
from app.ai.utils.bbox_utils import compute_iou
from app.ai import config

logger = logging.getLogger(__name__)


class TrackedVehicle:
    """Represents a single tracked vehicle state across video frames."""

    def __init__(self, track_id: int, bbox: List[int], vehicle_type: str, confidence: float):
        self.track_id = track_id
        self.tracking_code = f"TEMP-{track_id:03d}"
        self.bbox = bbox
        self.vehicle_type = vehicle_type
        self.confidence = confidence
        self.hits = 1
        self.time_since_update = 0

    def update(self, bbox: List[int], confidence: float, vehicle_type: str):
        self.bbox = bbox
        self.confidence = max(self.confidence, confidence)
        if vehicle_type and vehicle_type != "Vehicle":
            self.vehicle_type = vehicle_type
        self.hits += 1
        self.time_since_update = 0


class VehicleTracker:
    """IoU Multi-Vehicle Tracker assigning unique tracking_id to detected vehicles."""

    def __init__(self, max_age: int = config.TRACKING_MAX_AGE, iou_threshold: float = config.TRACKING_IOU_THRESHOLD):
        self.max_age = max_age
        self.iou_threshold = iou_threshold
        self.next_id = 1
        self.tracks: List[TrackedVehicle] = []

    def reset(self):
        self.next_id = 1
        self.tracks = []

    def update(self, detections: List[dict]) -> List[dict]:
        """
        Updates tracker state with new frame vehicle detections.
        Assigns 'tracking_id' to each detection dict.
        """
        # Increment missing age for existing tracks
        for t in self.tracks:
            t.time_since_update += 1

        updated_detections = []
        if not detections:
            # Clean up dead tracks
            self.tracks = [t for t in self.tracks if t.time_since_update <= self.max_age]
            return []

        matched_track_indices = set()
        matched_det_indices = set()

        # Match detections to existing active tracks via IoU
        for i, det in enumerate(detections):
            det_box = det["vehicle_bbox"]
            best_iou = 0.0
            best_track_idx = -1

            for j, trk in enumerate(self.tracks):
                if j in matched_track_indices:
                    continue
                iou = compute_iou(det_box, trk.bbox)
                if iou > best_iou and iou >= self.iou_threshold:
                    best_iou = iou
                    best_track_idx = j

            if best_track_idx != -1:
                trk = self.tracks[best_track_idx]
                trk.update(det_box, det["vehicle_confidence"], det["vehicle_type"])
                det_copy = dict(det)
                det_copy["tracking_id"] = trk.tracking_code
                updated_detections.append(det_copy)
                matched_track_indices.add(best_track_idx)
                matched_det_indices.add(i)

        # Create new tracks for unmatched detections
        for i, det in enumerate(detections):
            if i not in matched_det_indices:
                new_trk = TrackedVehicle(
                    track_id=self.next_id,
                    bbox=det["vehicle_bbox"],
                    vehicle_type=det["vehicle_type"],
                    confidence=det["vehicle_confidence"],
                )
                self.next_id += 1
                self.tracks.append(new_trk)

                det_copy = dict(det)
                det_copy["tracking_id"] = new_trk.tracking_code
                updated_detections.append(det_copy)

        # Purge stale tracks
        self.tracks = [t for t in self.tracks if t.time_since_update <= self.max_age]
        return updated_detections
