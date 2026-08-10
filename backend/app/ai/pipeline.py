import logging
import time
import os
import cv2
import numpy as np
from typing import Optional, Tuple

from app.ai.inference.pipeline import pipeline as new_pipeline, DetectionPipeline
from app.ai import config

logger = logging.getLogger(__name__)


class ANPRPipeline:
    """
    Backwards-compatible ANPR Pipeline wrapper routing through the production
    Vehicle Detection and Number Plate Detection module.
    """

    def __init__(self):
        self.engine = new_pipeline
        self.model_version = config.AI_MODEL_VERSION

    def _find_best_plate(self, res: dict) -> Tuple[dict, dict]:
        best_veh = {}
        best_plt = {}
        max_score = -1.0

        for veh in res.get("vehicles", []):
            for plt in veh.get("plates", []):
                text = plt.get("plate_text", "")
                conf = plt.get("confidence", 0.0)
                is_valid = plt.get("is_valid_plate", False)
                # Score higher if valid plate, then by text length and OCR confidence
                score = (len(text) * 3.0 + conf * 2.0 + (10.0 if is_valid else 0.0)) if text else (conf * 0.1)
                if score > max_score:
                    max_score = score
                    best_veh = veh
                    best_plt = plt

        if not best_veh and res.get("vehicles"):
            best_veh = res["vehicles"][0]
            if best_veh.get("plates"):
                best_plt = best_veh["plates"][0]

        return best_veh, best_plt

    def process_image(self, image_path: str, output_dir: str) -> dict:
        start_time = time.time()
        res = self.engine.process_image(image_path, output_dir)

        primary_vehicle, primary_plate = self._find_best_plate(res)

        crop_veh_path = primary_vehicle.get("crop_path")
        crop_plt_path = primary_plate.get("crop_path")

        v_bbox = primary_vehicle.get("vehicle_bbox")
        p_bbox = primary_plate.get("plate_bbox")

        plate_text = primary_plate.get("plate_text", "")
        raw_text = primary_plate.get("raw_text", "")
        corrected_plate = primary_plate.get("corrected_plate")
        corrections = primary_plate.get("corrections_applied", [])
        is_valid = primary_plate.get("is_valid_plate", False)

        plate_complete = bool(plate_text and len(plate_text) >= 4 and is_valid)
        display_plate = plate_text if plate_complete else "REQUIRES MANUAL REVIEW"
        plate_verified = bool(is_valid and plate_complete)

        v_type = primary_vehicle.get("vehicle_type")
        if not v_type or v_type == "Vehicle":
            v_type = "Unknown"

        result_payload = {
            "processing_time": res.get("processing_time", 0.0),
            "vehicles": res.get("vehicles", []),
            "plate_text": plate_text if plate_complete else "",
            "display_plate": display_plate,
            "plate_number": plate_text if plate_complete else None,
            "raw_ocr": raw_text or plate_text,
            "raw_text": raw_text,
            "confidence": primary_plate.get("confidence", primary_vehicle.get("vehicle_confidence", 0.0)),
            "vehicle_confidence": primary_vehicle.get("vehicle_confidence", 0.90),
            "ocr_confidence": primary_plate.get("confidence", 0.0),
            "corrected_plate": corrected_plate if plate_complete else "",
            "corrections_applied": corrections,
            "is_valid_plate": is_valid,
            "plate_complete": plate_complete,
            "plate_verified": plate_verified,
            "vehicle_count": len(res.get("vehicles", [])),
            "vehicle_bbox": v_bbox,
            "plate_bbox": p_bbox,
            "cropped_vehicle_path": crop_veh_path,
            "cropped_plate_path": crop_plt_path,
            "ai_model_version": self.model_version,
            "processing_time_ms": res.get("processing_time", 0.0) * 1000,
            "vehicle_type": v_type,
            "frames_used": res.get("processed_frame_count", 1),
        }

        return result_payload

    def process_video(self, video_path: str, output_dir: str, max_frames: int = config.MAX_VIDEO_FRAMES) -> dict:
        res = self.engine.process_video(video_path, output_dir, max_frames=max_frames)

        primary_vehicle, primary_plate = self._find_best_plate(res)

        plate_text = primary_plate.get("plate_text", "")
        raw_text = primary_plate.get("raw_text", "")
        is_valid = primary_plate.get("is_valid_plate", False)

        plate_complete = bool(plate_text and len(plate_text) >= 4 and is_valid)
        display_plate = plate_text if plate_complete else "REQUIRES MANUAL REVIEW"
        plate_verified = bool(is_valid and plate_complete)

        v_type = primary_vehicle.get("vehicle_type")
        if not v_type or v_type == "Vehicle":
            v_type = "Unknown"

        return {
            "processing_time": res.get("processing_time", 0.0),
            "video_fps": res.get("video_fps", 25.0),
            "total_video_frames": res.get("total_video_frames", 1),
            "processed_frame_count": res.get("processed_frame_count", 0),
            "frames_used": res.get("processed_frame_count", 0),
            "duration_seconds": res.get("duration_seconds", 0.0),
            "tracked_vehicle_count": res.get("tracked_vehicle_count", len(res.get("vehicles", []))),
            "vehicles": res.get("vehicles", []),
            "plate_text": plate_text,
            "display_plate": display_plate,
            "plate_number": plate_text if plate_complete else None,
            "raw_ocr": raw_text or plate_text,
            "raw_text": raw_text,
            "corrected_plate": primary_plate.get("corrected_plate"),
            "corrections_applied": primary_plate.get("corrections_applied", []),
            "confidence": primary_plate.get("confidence", primary_vehicle.get("vehicle_confidence", 0.0)),
            "vehicle_confidence": primary_vehicle.get("vehicle_confidence", 0.90),
            "ocr_confidence": primary_plate.get("confidence", 0.0),
            "is_valid_plate": is_valid,
            "plate_complete": plate_complete,
            "plate_verified": plate_verified,
            "vehicle_count": len(res.get("vehicles", [])),
            "vehicle_bbox": primary_vehicle.get("vehicle_bbox"),
            "plate_bbox": primary_plate.get("plate_bbox"),
            "cropped_vehicle_path": primary_vehicle.get("crop_path"),
            "cropped_plate_path": primary_plate.get("crop_path"),
            "ai_model_version": self.model_version,
            "processing_time_ms": res.get("processing_time", 0.0) * 1000,
            "vehicle_type": v_type,
        }



pipeline = ANPRPipeline()
process_image = pipeline.process_image
process_video = pipeline.process_video
