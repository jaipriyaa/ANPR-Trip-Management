import logging
import time
import os
import cv2
import numpy as np
from typing import Dict, List, Optional

from app.ai import config
from app.ai.vehicle_detector import VehicleDetector, VehicleTracker, crop_vehicle
from app.ai.plate_detector import PlateDetector, crop_plate, crop_plate_with_preprocessing
from app.ai.preprocessing.perspective import correct_perspective
from app.ai.preprocessing.plate_enhancer import PlateEnhancer
from app.ai.ocr.engine import OCREngine
from app.ai.postprocessing.plate_validator import IndianPlateValidator
from app.ai.visualization import annotate_image
from app.ai.debug.debug_saver import DebugSaver

logger = logging.getLogger(__name__)


class DetectionPipeline:
    """
    Industrial Grade AI Pipeline orchestrating:
    Image / Video -> Vehicle Detection -> Vehicle Tracking -> Number Plate Detection -> Plate Crop & Preprocessing -> Perspective Rectification -> Multi-pass OCR -> Indian Plate Validation -> Debug Export -> JSON Response.
    """

    def __init__(self):
        self.vehicle_detector = VehicleDetector()
        self.plate_detector = PlateDetector()
        self.tracker = VehicleTracker()
        self.enhancer = PlateEnhancer()
        self.ocr_engine = OCREngine()
        self.validator = IndianPlateValidator()
        self.debug_saver = DebugSaver()

    def process_image(self, image_input, output_dir: Optional[str] = None) -> dict:
        """
        Processes a single image file path or numpy image array.
        Returns exact required JSON response.
        """
        start_time = time.time()

        if isinstance(image_input, str):
            image = cv2.imread(image_input)
            if image is None:
                raise ValueError(f"Unable to load image file from path: {image_input}")
        elif isinstance(image_input, np.ndarray):
            image = image_input
        else:
            raise TypeError(f"Invalid image input type: {type(image_input)}")

        orig_h, orig_w = image.shape[:2]

        # 1. Vehicle Detection
        veh_res = self.vehicle_detector.detect(image)
        raw_vehicles = veh_res.get("vehicles", [])

        # 2. Vehicle Tracking & ID Assignment
        tracked_vehicles = self.tracker.update(raw_vehicles)

        if not tracked_vehicles and not raw_vehicles:
            # Full image fallback scan if no vehicles detected
            tracked_vehicles = [{
                "tracking_id": "TEMP-001",
                "vehicle_type": "Unknown",
                "vehicle_confidence": 0.0,
                "vehicle_bbox": [0, 0, orig_w, orig_h],
            }]

        all_vehicle_outputs = []
        all_plates_flat = []

        # 3. Number Plate Detection, Preprocessing, OCR & Validation per detected vehicle
        for veh in tracked_vehicles:
            v_bbox = veh["vehicle_bbox"]
            v_type = veh.get("vehicle_type", "Vehicle")
            v_conf = veh.get("vehicle_confidence", 0.0)
            t_id = veh.get("tracking_id", "TEMP-001")

            # Crop vehicle ROI
            v_crop = crop_vehicle(image, v_bbox)

            # Detect plates in vehicle ROI
            plate_res = self.plate_detector.detect(image, vehicle_bbox=v_bbox)
            detected_plates = plate_res.get("plates", [])

            # candidate_list consists ONLY of actual plate detections (never the entire vehicle crop)
            candidate_list = list(detected_plates)


            plates_output = []
            for pl in candidate_list:
                p_bbox = pl["plate_bbox"]
                p_conf = pl["confidence"]

                # Crop plate ROI
                p_crop = crop_plate(image, p_bbox)
                if p_crop is None or p_crop.size == 0:
                    continue

                # Perspective Rectification & Deskewing
                rectified = correct_perspective(image, p_bbox)
                ocr_input_image = rectified if (rectified is not None and getattr(rectified, "size", 0) > 0) else p_crop

                # Contrast & Noise Enhancement
                enhanced = self.enhancer.enhance(p_crop)

                # Multi-pass OCR Execution
                ocr_res = self.ocr_engine.read_ensemble(ocr_input_image, enhanced)
                raw_text = ocr_res.get("raw_text", "")
                plate_text = ocr_res.get("plate_text", "")
                ocr_conf = ocr_res.get("confidence", 0.0)

                # Indian Plate Regex Validation & Confusion Correction
                val_res = self.validator.correct_with_confidence(plate_text, ocr_conf)
                corrected_plate = val_res.get("plate_text", plate_text)
                is_valid = val_res.get("is_valid", False)
                corrections = val_res.get("corrections", [])

                plate_entry = {
                    "plate_bbox": p_bbox,
                    "confidence": p_conf,
                    "crop_path": "",
                    "plate_crop": p_crop,
                    "plate_crop_arr": p_crop,
                    "rectified_crop": rectified,
                    "enhanced_crop": enhanced,
                    "plate_text": corrected_plate if corrected_plate else plate_text,
                    "raw_text": raw_text,
                    "corrected_plate": corrected_plate,
                    "corrections_applied": corrections,
                    "is_valid_plate": is_valid,
                    "ocr_confidence": ocr_conf,
                }

                plates_output.append(plate_entry)
                all_plates_flat.append(pl)

            all_vehicle_outputs.append({
                "tracking_id": t_id,
                "vehicle_type": v_type,
                "vehicle_confidence": v_conf,
                "vehicle_bbox": v_bbox,
                "vehicle_crop": v_crop,
                "vehicle_crop_arr": v_crop,
                "plates": plates_output,
            })


        # 4. Generate Visualization (Color-coded BBoxes per vehicle class + Plate badges)
        annotated_img = annotate_image(image, tracked_vehicles, all_plates_flat)

        total_processing_sec = round(time.time() - start_time, 3)
        top_vehicle_type = all_vehicle_outputs[0]["vehicle_type"] if (all_vehicle_outputs and all_vehicle_outputs[0].get("vehicle_type") not in ["Vehicle", "Unknown", None]) else "Unknown"

        payload = {
            "processing_time": total_processing_sec,
            "vehicles": all_vehicle_outputs,
            "vehicle_type": top_vehicle_type,
        }



        # 5. Debug Mode Export
        payload = self.debug_saver.save_session(image, annotated_img, tracked_vehicles, payload)

        return payload

    def process_video(self, video_path: str, output_dir: Optional[str] = None, max_frames: int = config.MAX_VIDEO_FRAMES) -> dict:
        """Processes video file frame by frame with vehicle tracking."""
        start_time = time.time()
    def process_video(self, video_path: str, output_dir: Optional[str] = None, max_frames: int = config.MAX_VIDEO_FRAMES) -> dict:
        """Processes video file frame by frame with vehicle tracking & multi-frame OCR fusion."""
        from app.ai.inference.video_pipeline import video_pipeline
        payload = video_pipeline.process_video(video_path, output_dir, max_frames=max_frames)
        
        # Save session debug artifacts for video tracklets
        dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
        payload = self.debug_saver.save_session(dummy_img, dummy_img, [], payload)
        return payload


pipeline = DetectionPipeline()
process_image = pipeline.process_image
process_video = pipeline.process_video
