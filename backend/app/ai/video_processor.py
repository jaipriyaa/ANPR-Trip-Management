import logging
import time
import cv2
import numpy as np
import os
from typing import List, Optional

logger = logging.getLogger(__name__)


def extract_frames(
    video_path: str,
    max_frames: int = 30,
    target_fps: Optional[float] = None,
) -> List[np.ndarray]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / max(fps, 1)

    if target_fps:
        frame_interval = max(1, int(fps / target_fps))
    else:
        frame_interval = max(1, int(total_frames / max_frames))

    frames = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % frame_interval == 0 and len(frames) < max_frames:
            frames.append(frame)
        frame_idx += 1

    cap.release()

    if not frames:
        raise ValueError(f"No frames extracted from video: {video_path}")

    logger.info(f"Extracted {len(frames)}/{total_frames} frames from video ({duration:.1f}s @ {fps:.1f}fps)")
    return frames


def iou(box1: list, box2: list) -> float:
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - intersection

    return intersection / max(union, 1e-6)


def track_vehicle_across_frames(
    frame_detections: List[dict],
    iou_threshold: float = 0.3,
) -> dict:
    if not frame_detections:
        return {"tracked_vehicle": None, "track_confidence": 0.0, "frames_count": 0}

    tracks = {}
    next_track_id = 0

    for det in frame_detections:
        frame_idx = det.get("frame_idx", 0)
        for vehicle in det.get("vehicles", []):
            bbox = vehicle["bbox"]
            assigned = False
            for tid, track_info in tracks.items():
                last_bbox = track_info["last_bbox"]
                if iou(bbox, last_bbox) >= iou_threshold:
                    track_info["bboxes"].append(bbox)
                    track_info["confidences"].append(vehicle["confidence"])
                    track_info["frames"].append(frame_idx)
                    track_info["last_bbox"] = bbox
                    track_info["count"] += 1
                    assigned = True
                    break
            if not assigned:
                tracks[next_track_id] = {
                    "bboxes": [bbox],
                    "confidences": [vehicle["confidence"]],
                    "frames": [frame_idx],
                    "last_bbox": bbox,
                    "count": 1,
                }
                next_track_id += 1

    best_track = None
    best_track_id = None
    for tid, track in tracks.items():
        if best_track is None or track["count"] > best_track["count"]:
            best_track = track
            best_track_id = tid

    if best_track is None or best_track["count"] == 0:
        return {"tracked_vehicle": None, "track_confidence": 0.0, "frames_count": 0}

    avg_confidence = sum(best_track["confidences"]) / len(best_track["confidences"])
    median_bbox = best_track["bboxes"][len(best_track["bboxes"]) // 2]

    return {
        "tracked_vehicle": {
            "track_id": best_track_id,
            "bbox": median_bbox,
            "all_bboxes": best_track["bboxes"],
            "frame_indices": best_track["frames"],
        },
        "track_confidence": avg_confidence,
        "frames_count": best_track["count"],
    }
