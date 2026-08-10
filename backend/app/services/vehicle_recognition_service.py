import logging
import os
import time
import uuid
from typing import Optional, Tuple
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.vehicle import Vehicle
from app.models.vehicle_detection import VehicleDetection
from app.crud.crud_vehicle import crud_vehicle
from app.crud.crud_vehicle_plate import crud_vehicle_plate
from app.crud.crud_vehicle_detection import crud_vehicle_detection
from app.schemas.vehicle_detection import VehicleDetectionCreate, VehicleDetectionUpdate
from app.schemas.vehicle import VehicleCreate
from app.ai.pipeline import ANPRPipeline

pipeline = ANPRPipeline()

logger = logging.getLogger(__name__)

UPLOAD_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
MAX_FILE_SIZE = 200 * 1024 * 1024


def _safe_uuid(val) -> Optional[uuid.UUID]:
    if not val:
        return None
    if isinstance(val, uuid.UUID):
        return val
    try:
        return uuid.UUID(str(val))
    except (ValueError, AttributeError, TypeError):
        return None


class VehicleRecognitionService:
    def __init__(self):
        os.makedirs(os.path.join(UPLOAD_BASE, "images"), exist_ok=True)
        os.makedirs(os.path.join(UPLOAD_BASE, "videos"), exist_ok=True)
        os.makedirs(os.path.join(UPLOAD_BASE, "processed"), exist_ok=True)

    def _validate_file(self, file: UploadFile) -> str:
        ext = os.path.splitext(file.filename)[1].lower()
        if not ext:
            raise HTTPException(status_code=400, detail="File has no extension.")

        if ext in ALLOWED_IMAGE_EXTENSIONS:
            return "image"
        elif ext in ALLOWED_VIDEO_EXTENSIONS:
            return "video"
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{ext}'. Allowed: images {ALLOWED_IMAGE_EXTENSIONS}, videos {ALLOWED_VIDEO_EXTENSIONS}",
            )

    def _save_file(self, file: UploadFile, upload_type: str) -> str:
        file_id = str(uuid.uuid4())[:8]
        subdir = "images" if upload_type == "image" else "videos"
        dest_dir = os.path.join(UPLOAD_BASE, subdir)
        os.makedirs(dest_dir, exist_ok=True)

        safe_name = f"{file_id}_{file.filename}"
        dest_path = os.path.join(dest_dir, safe_name)

        content = file.file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File exceeds max size of {MAX_FILE_SIZE // (1024*1024)}MB")

        with open(dest_path, "wb") as f:
            f.write(content)

        return dest_path

    def _find_vehicle_by_plate(self, db: Session, plate_text: str) -> Optional[Vehicle]:
        safe_plate = (plate_text or "").upper().strip()[:20]
        if not safe_plate or len(safe_plate) < 4:
            return None
        try:
            plate = crud_vehicle_plate.get_by_plate_number(db, plate_number=safe_plate)
            if plate:
                return plate.vehicle
            vehicle = crud_vehicle.get_by_number(db, vehicle_number=safe_plate)
            return vehicle
        except Exception as e:
            logger.error(f"Error looking up vehicle by plate '{safe_plate}': {e}")
            db.rollback()
            return None

    def _create_vehicle_from_detection(self, db: Session, plate_text: str, ai_result: dict) -> Optional[Vehicle]:
        safe_plate = (plate_text or "").upper().strip()[:20]
        if not safe_plate or len(safe_plate) < 4:
            return None
        v_type = ai_result.get("vehicle_type")
        if not v_type or v_type in ["Unknown", "Vehicle"]:
            v_type = "Unknown"

        vehicle_in = VehicleCreate(
            vehicle_number=safe_plate,
            vehicle_type=v_type,
            is_active=True,
            is_blacklisted=False,
        )
        try:
            vehicle = crud_vehicle.create(db, obj_in=vehicle_in)
            plate_in_data = {
                "vehicle_id": vehicle.id,
                "plate_number": safe_plate,
                "plate_type": "Standard",
                "is_primary": True,
                "is_active": True,
            }
            from app.schemas.vehicle_plate import VehiclePlateCreate
            plate_in = VehiclePlateCreate(**plate_in_data)
            crud_vehicle_plate.create(db, obj_in=plate_in)
            db.refresh(vehicle)
            return vehicle
        except Exception as e:
            logger.error(f"Error creating vehicle for plate '{safe_plate}': {e}")
            db.rollback()
            return None


    def _update_existing_vehicle(self, db: Session, vehicle: Vehicle, ai_result: dict) -> Vehicle:
        now = datetime.now(timezone.utc)
        update_data = {
            "last_seen_at": now,
            "visit_count": (vehicle.visit_count or 0) + 1,
            "detection_count": (vehicle.detection_count or 0) + 1,
            "last_ocr_confidence": ai_result.get("confidence", 0.0),
        }
        if vehicle.first_seen_at is None:
            update_data["first_seen_at"] = now
        if ai_result.get("cropped_vehicle_path"):
            update_data["cropped_vehicle_image_path"] = ai_result["cropped_vehicle_path"]
        if ai_result.get("cropped_plate_path"):
            update_data["cropped_plate_image_path"] = ai_result["cropped_plate_path"]

        for field, value in update_data.items():
            setattr(vehicle, field, value)
        db.commit()
        db.refresh(vehicle)
        return vehicle

    def _bbox_to_dict(self, bbox):
        if bbox and isinstance(bbox, (list, tuple)) and len(bbox) == 4:
            return {"x1": int(bbox[0]), "y1": int(bbox[1]), "x2": int(bbox[2]), "y2": int(bbox[3])}
        return bbox

    def _create_detection_record(self, db: Session, vehicle: Optional[Vehicle], plate_text: str, ai_result: dict, file_path: str, upload_type: str, filename: str) -> VehicleDetection:
        safe_plate = (plate_text or "")[:20]
        raw_conf = ai_result.get("confidence", 0.0)
        try:
            safe_conf = max(0.0, min(1.0, float(raw_conf)))
        except (ValueError, TypeError):
            safe_conf = 0.0

        detection_in = VehicleDetectionCreate(
            vehicle_id=vehicle.id if vehicle else None,
            plate_text=safe_plate,
            confidence=safe_conf,
            is_valid_plate=bool(ai_result.get("is_valid_plate", False)),
            upload_type=upload_type,
            uploaded_file_path=file_path,
            cropped_vehicle_path=ai_result.get("cropped_vehicle_path"),
            cropped_plate_path=ai_result.get("cropped_plate_path"),
            source_filename=filename,
            detection_status="completed",
            ai_model_version=str(ai_result.get("ai_model_version") or "anpr-pipeline-v2.0"),
            processing_time_ms=ai_result.get("processing_time_ms", 0),
            ocr_raw_text=(ai_result.get("raw_text") or "")[:45],
            detection_bbox=self._bbox_to_dict(ai_result.get("plate_bbox")),
            vehicle_bbox=self._bbox_to_dict(ai_result.get("vehicle_bbox")),
            frame_count=ai_result.get("frame_count"),
            corrected_plate=(ai_result.get("corrected_plate") or "")[:20],
            vehicle_type_detected=ai_result.get("vehicle_type"),


            validation_details=ai_result.get("corrections_applied"),
            pipeline_metrics=ai_result.get("metrics"),
            fusion_method=ai_result.get("fusion_method"),
            character_consistency=ai_result.get("character_consistency"),
        )
        return crud_vehicle_detection.create(db, obj_in=detection_in)

    def process_upload(
        self,
        db: Session,
        file: UploadFile,
        gate_id: Optional[uuid.UUID] = None,
        driver_id: Optional[uuid.UUID] = None,
        driver_name: Optional[str] = None,
        transporter_id: Optional[uuid.UUID] = None,
        direction: Optional[str] = None,
        purpose: Optional[str] = None,
        destination: Optional[str] = None,
    ) -> dict:
        gate_id = _safe_uuid(gate_id)
        driver_id = _safe_uuid(driver_id)
        transporter_id = _safe_uuid(transporter_id)

        req_id = f"ANPR-REQ-{uuid.uuid4().hex[:6].upper()}"
        req_start = time.perf_counter()
        logger.info(f"[{req_id}] REQUEST START — Processing upload: {file.filename} (gate_id: {gate_id}, direction: {direction})")

        file_type = self._validate_file(file)
        upload_type = file_type
        filename = file.filename or "uploaded_file"

        try:
            file_path = self._save_file(file, file_type)
            logger.info(f"[{req_id}] File saved +{time.perf_counter() - req_start:.2f}s -> {file_path}")
        except Exception as e:
            logger.error(f"[{req_id}] Failed to save file {filename}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File save error: {str(e)}",
            )

        processed_dir = os.path.join(UPLOAD_BASE, "processed")
        os.makedirs(processed_dir, exist_ok=True)

        try:
            if file_type == "image":
                logger.info(f"[{req_id}] Starting image pipeline +{time.perf_counter() - req_start:.2f}s")
                ai_result = pipeline.process_image(file_path, processed_dir)
                logger.info(f"[{req_id}] Image pipeline end +{time.perf_counter() - req_start:.2f}s")
            else:
                logger.info(f"[{req_id}] Starting video pipeline +{time.perf_counter() - req_start:.2f}s")
                ai_result = pipeline.process_video(file_path, processed_dir, max_frames=15)
                logger.info(f"[{req_id}] Video pipeline end +{time.perf_counter() - req_start:.2f}s")
            
            if isinstance(ai_result, dict):
                ai_result["request_id"] = req_id

        except Exception as e:
            logger.error(f"[{req_id}] AI pipeline failed for {filename}: {e}", exc_info=True)

            detection_in = VehicleDetectionCreate(
                vehicle_id=None,
                plate_text="",
                confidence=0.0,
                is_valid_plate=False,
                upload_type=upload_type,
                uploaded_file_path=file_path if 'file_path' in locals() else "",
                source_filename=filename,
                detection_status="failed",
                error_message=str(e),
            )
            crud_vehicle_detection.create(db, obj_in=detection_in)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI processing failed: {str(e)}",
            )


        plate_text = ai_result.get("plate_text", "")
        is_new = False

        if plate_text and len(plate_text) >= 4:
            existing_vehicle = self._find_vehicle_by_plate(db, plate_text)
            if existing_vehicle:
                vehicle = self._update_existing_vehicle(db, existing_vehicle, ai_result)
                logger.info(f"Existing vehicle {plate_text} - visit #{vehicle.visit_count}")
            else:
                vehicle = self._create_vehicle_from_detection(db, plate_text, ai_result)
                vehicle.first_seen_at = datetime.now(timezone.utc)
                vehicle.last_seen_at = datetime.now(timezone.utc)
                vehicle.visit_count = 1
                vehicle.detection_count = 1
                db.commit()
                db.refresh(vehicle)
                is_new = True
                logger.info(f"New vehicle created: {plate_text} (ID: {vehicle.id})")
        else:
            vehicle = None

        # Resolve or auto-create Driver record if driver information is supplied
        resolved_driver = None
        if driver_id:
            from app.crud.crud_driver import crud_driver
            resolved_driver = crud_driver.get(db, driver_id=driver_id)
        elif driver_name and driver_name.strip():
            from app.models.driver import Driver
            from app.crud.crud_driver import crud_driver
            from app.schemas.driver import DriverCreate
            clean_name = driver_name.strip()
            existing_driver = db.query(Driver).filter(Driver.full_name.ilike(clean_name)).first()
            if existing_driver:
                resolved_driver = existing_driver
            else:
                import random
                lic_no = f"DL-{random.randint(10000, 99999)}"
                phone_no = f"+91-{random.randint(70000, 99999)}-{random.randint(10000, 99999)}"
                driver_in = DriverCreate(
                    full_name=clean_name,
                    license_number=lic_no,
                    phone_number=phone_no,
                    transporter_id=transporter_id or (vehicle.transporter_id if vehicle else None),
                    is_active=True,
                )
                resolved_driver = crud_driver.create(db, obj_in=driver_in)
                logger.info(f"Auto-created new driver '{clean_name}' (License: {lic_no})")

        # Associate vehicle with transporter if provided
        if vehicle and transporter_id and not vehicle.transporter_id:
            vehicle.transporter_id = transporter_id
            db.commit()
            db.refresh(vehicle)

        filename = file.filename
        upload_type = file_type
        detection = self._create_detection_record(
            db, vehicle, plate_text, ai_result, file_path, upload_type, filename
        )


        from app.services.vehicle_verification_service import vehicle_verification_engine
        
        # Populate verification results for each vehicle tracklet
        vehicles_payload = ai_result.get("vehicles", [])
        for v in vehicles_payload:
            v_plates = v.get("plates", [])
            v_plate_text = v_plates[0].get("plate_text", "") if v_plates else ""
            v_ocr_conf = v_plates[0].get("ocr_confidence", 0.0) if v_plates else 0.0
            
            v_verif = vehicle_verification_engine.verify_and_authorize(
                db,
                plate_number=v_plate_text,
                ocr_confidence=v_ocr_conf,
                vehicle_type_detected=v.get("vehicle_type"),
                ai_result=v,
            )
            v["verification_result"] = v_verif
            v["authorization"] = v_verif.get("authorization")
            v["reason"] = v_verif.get("reason")
            v["cropped_vehicle_path"] = v.get("crop_path")
            v["cropped_plate_path"] = v_plates[0].get("crop_path") if v_plates else ""

        verification_result = vehicle_verification_engine.verify_and_authorize(
            db,
            plate_number=plate_text,
            ocr_confidence=ai_result.get("confidence", 0.0),
            vehicle_type_detected=ai_result.get("vehicle_type"),
            ai_result=ai_result,
        )

        if resolved_driver:
            verification_result["driver"] = {
                "id": str(resolved_driver.id),
                "name": resolved_driver.full_name,
                "license": resolved_driver.license_number,
                "phone": resolved_driver.phone_number,
                "is_active": resolved_driver.is_active,
                "status": "Active" if resolved_driver.is_active else "Inactive",
            }

        # Trigger Entry / Exit Engine for automatic vehicle movement tracking
        from app.services.entry_exit_service import entry_exit_service
        movement_record = None
        if plate_text and len(plate_text) >= 4:
            try:
                movement_record = entry_exit_service.process_recognition_event(
                    db=db,
                    plate_number=plate_text,
                    ocr_confidence=ai_result.get("confidence", 0.0),
                    vehicle_type=ai_result.get("vehicle_type"),
                    gate_id=gate_id,
                    ai_result=ai_result,
                )
                if movement_record and resolved_driver and not movement_record.driver_id:
                    movement_record.driver_id = resolved_driver.id
                    db.commit()
                    db.refresh(movement_record)
            except Exception as ev_err:
                logger.error(f"EntryExitEngine processing failed for {plate_text}: {ev_err}", exc_info=True)

        # Trigger Trip Engine for automated trip approval & status update
        from app.services.trip_service import trip_service
        trip_record = None
        if plate_text and len(plate_text) >= 4:
            try:
                trip_record = trip_service.process_ai_recognition_event(
                    db=db,
                    plate_number=plate_text,
                    ocr_confidence=ai_result.get("confidence", 0.0),
                    gate_id=gate_id,
                    direction=direction or ai_result.get("direction"),
                )
                if trip_record and resolved_driver and not trip_record.driver_id:
                    trip_record.driver_id = resolved_driver.id
                    db.commit()
                    db.refresh(trip_record)
            except Exception as trip_err:
                logger.error(f"TripEngine processing failed for {plate_text}: {trip_err}", exc_info=True)

        # Trigger Phase 9 Authorization Engine for 5-level security & gate decision
        from app.services.authorization_service import authorization_service
        auth_decision = None
        if plate_text and len(plate_text) >= 4:
            try:
                auth_decision = authorization_service.evaluate_gate_access(
                    db=db,
                    plate_text=plate_text,
                    confidence=ai_result.get("confidence", 0.95),
                    tracking_id=ai_result.get("tracking_id", "TRACK-1"),
                )
            except Exception as auth_err:
                logger.error(f"AuthorizationEngine processing failed for {plate_text}: {auth_err}", exc_info=True)

        # Trigger Phase 10 Manual Review Engine for low-confidence or unknown detections
        from app.services.manual_review_service import manual_review_service
        manual_review_record = None
        ocr_conf = float(ai_result.get("confidence", 0.0))
        is_valid = bool(ai_result.get("is_valid_plate", False))
        auth_status = auth_decision.get("decision") if auth_decision else "UNKNOWN_VEHICLE"

        if ocr_conf < 0.75 or not is_valid or auth_status in ["UNKNOWN_VEHICLE", "MANUAL_REVIEW"]:
            try:
                manual_review_record = manual_review_service.create_manual_review_record(
                    db=db,
                    ai_result=ai_result,
                    auth_result=auth_decision,
                )
            except Exception as rev_err:
                logger.error(f"ManualReviewEngine failed for {plate_text}: {rev_err}", exc_info=True)

        total_time = (time.perf_counter() - req_start) * 1000
        logger.info(f"[{req_id}] RETURNING HTTP RESPONSE +{total_time/1000.0:.2f}s")


        top_v = vehicles_payload[0] if vehicles_payload else {}
        top_p = top_v.get("plates", [{}])[0] if top_v.get("plates") else {}
        top_v_type = ai_result.get("vehicle_type") or (top_v.get("vehicle_type") if top_v and top_v.get("vehicle_type") != "Vehicle" else "Unknown")

        class_name_map = {"car": 0, "motorcycle": 1, "bus": 2, "truck": 3}
        v_class_name = (top_v_type or "").lower()
        raw_class_id = top_v.get("class_id") if top_v else None
        if raw_class_id is not None:
            v_class_id = int(raw_class_id)
        elif v_class_name in class_name_map:
            v_class_id = class_name_map[v_class_name]
        else:
            v_class_id = None

        raw_v_bbox = ai_result.get("vehicle_bbox") or top_v.get("vehicle_bbox")
        v_bbox_clean = [int(x) for x in raw_v_bbox] if (raw_v_bbox and isinstance(raw_v_bbox, (list, tuple)) and len(raw_v_bbox) == 4) else None

        raw_p_bbox = ai_result.get("plate_bbox") or top_p.get("plate_bbox")
        p_bbox_clean = [int(x) for x in raw_p_bbox] if (raw_p_bbox and isinstance(raw_p_bbox, (list, tuple)) and len(raw_p_bbox) == 4) else None

        v_conf_raw = ai_result.get("vehicle_confidence", top_v.get("vehicle_confidence", 0.0))
        try:
            v_conf_clean = round(float(v_conf_raw), 4)
        except (ValueError, TypeError):
            v_conf_clean = 0.0

        p_conf_raw = ai_result.get("confidence", top_p.get("confidence", 0.0))
        try:
            p_conf_clean = round(float(p_conf_raw), 4)
        except (ValueError, TypeError):
            p_conf_clean = 0.0

        is_valid_p = bool(ai_result.get("is_valid_plate", False))

        vehicle_info = {
            "class_id": v_class_id,
            "class_name": top_v_type if (top_v_type and top_v_type != "Unknown") else None,
            "confidence": v_conf_clean,
            "bbox": v_bbox_clean,
        }

        plate_info = {
            "text": plate_text if is_valid_p else None,
            "confidence": p_conf_clean,
            "verified": is_valid_p,
            "display_plate": plate_text if is_valid_p else "REQUIRES MANUAL REVIEW",
        }

        return {
            "success": True,
            "request_id": req_id,
            "processing_time": round(total_time / 1000.0, 3),

            "vehicle": vehicle_info,
            "plate": plate_info,

            "vehicles": vehicles_payload,
            "is_new_vehicle": is_new,
            "plate_text": plate_text if ai_result.get("is_valid_plate") else None,
            "display_plate": plate_text if ai_result.get("is_valid_plate") else "REQUIRES MANUAL REVIEW",
            "plate_number": plate_text if ai_result.get("is_valid_plate") else None,
            "raw_ocr": ai_result.get("raw_ocr") or ai_result.get("raw_text") or plate_text,
            "ocr_raw_text": ai_result.get("raw_text") or plate_text,
            "confidence": ai_result.get("confidence", 0.0),
            "vehicle_confidence": ai_result.get("vehicle_confidence", 0.90),
            "ocr_confidence": ai_result.get("ocr_confidence", ai_result.get("confidence", 0.0)),
            "is_valid_plate": ai_result.get("is_valid_plate", False),
            "plate_complete": ai_result.get("is_valid_plate", False),
            "plate_verified": ai_result.get("is_valid_plate", False),

            "vehicle_id": str(vehicle.id) if vehicle else None,
            "detection_id": str(detection.id),
            "visit_count": vehicle.visit_count if vehicle else 0,
            "first_seen_at": vehicle.first_seen_at.isoformat() if vehicle and vehicle.first_seen_at else None,
            "last_seen_at": vehicle.last_seen_at.isoformat() if vehicle and vehicle.last_seen_at else None,
            "upload_type": upload_type,
            "source_filename": filename,
            "cropped_vehicle_path": ai_result.get("cropped_vehicle_path") or (vehicles_payload[0].get("crop_path") if vehicles_payload else None),
            "cropped_plate_path": ai_result.get("cropped_plate_path") or (vehicles_payload[0].get("plates", [{}])[0].get("crop_path") if vehicles_payload and vehicles_payload[0].get("plates") else None),
            "vehicle_bbox": ai_result.get("vehicle_bbox"),
            "plate_bbox": ai_result.get("plate_bbox"),
            "processing_time_ms": total_time,
            "ai_model_version": ai_result.get("ai_model_version"),
            "frame_count": ai_result.get("frame_count"),
            "frames_used": ai_result.get("frames_used") or ai_result.get("processed_frame_count") or 1,
            "corrected_plate": ai_result.get("corrected_plate"),
            "vehicle_type": top_v_type,
            "corrections_applied": ai_result.get("corrections_applied"),

            "pipeline_metrics": ai_result.get("metrics"),
            "fusion_method": ai_result.get("fusion_method") or "Weighted Character-Level Majority Voting & Format Rules",

            "tracking_id": ai_result.get("tracking_id") or (vehicles_payload[0].get("tracking_id") if vehicles_payload else "TRACK-1"),
            "direction": direction or ai_result.get("direction") or (vehicles_payload[0].get("direction") if vehicles_payload else "Entering"),
            "duplicates_eliminated_count": ai_result.get("duplicates_eliminated_count") or (vehicles_payload[0].get("duplicates_eliminated_count") if vehicles_payload else 0),
            "per_frame_history": ai_result.get("per_frame_history") or (vehicles_payload[0].get("per_frame_history") if vehicles_payload else []),
            "video_fps": ai_result.get("video_fps"),
            "total_video_frames": ai_result.get("total_video_frames"),
            "processed_frame_count": ai_result.get("processed_frame_count"),
            "duration_seconds": ai_result.get("duration_seconds"),
            "tracked_vehicle_count": len(vehicles_payload),
            "manual_review_id": str(manual_review_record.id) if manual_review_record else None,
            "verification_result": verification_result,
            "authorization_decision": auth_decision,
            "authorization": verification_result.get("authorization"),
            "reason": verification_result.get("reason"),
            "vehicle_details": verification_result.get("vehicle"),
            "driver_details": verification_result.get("driver"),
            "transporter_details": verification_result.get("transporter"),
            "trip_details": {
                "trip_id": str(trip_record.id) if trip_record else None,
                "trip_number": trip_record.trip_number if trip_record else None,
                "trip_status": trip_record.trip_status if trip_record else None,
                "approval_status": trip_record.approval_status if trip_record else None,
                "purpose": trip_record.purpose if trip_record else None,
            } if trip_record else verification_result.get("trip"),
            "movement_details": {
                "movement_id": str(movement_record.id) if movement_record else None,
                "movement_status": movement_record.movement_status if movement_record else "UNKNOWN",
                "vehicle_status": movement_record.vehicle_status if movement_record else "UNKNOWN",
                "entry_time": movement_record.entry_time.isoformat() if movement_record and movement_record.entry_time else None,
                "exit_time": movement_record.exit_time.isoformat() if movement_record and movement_record.exit_time else None,
                "stay_duration_formatted": movement_record.stay_duration_formatted if movement_record else None,
            } if movement_record else None,
        }

    def sync_detection_record(
        self,
        db: Session,
        detection_id: uuid.UUID,
        plate_text: Optional[str] = None,
        driver_name: Optional[str] = None,
        gate_id: Optional[uuid.UUID] = None,
        direction: Optional[str] = None,
        purpose: Optional[str] = None,
        destination: Optional[str] = None,
    ) -> dict:
        """Re-sync or manually update a recognition dataset entry across Master Catalog, Gate Management & Trip Engine."""
        detection = crud_vehicle_detection.get(db, detection_id=detection_id)
        if not detection:
            raise HTTPException(status_code=404, detail="Detection record not found")

        clean_plate = plate_text.upper().strip() if plate_text else detection.plate_text

        # Update detection record
        if plate_text:
            detection.plate_text = clean_plate
            detection.corrected_plate = clean_plate

        # Find or create vehicle
        vehicle = None
        if clean_plate:
            vehicle = self._find_vehicle_by_plate(db, clean_plate)
            if not vehicle:
                ai_dummy = {"confidence": detection.confidence, "cropped_vehicle_path": detection.cropped_vehicle_path, "cropped_plate_path": detection.cropped_plate_path}
                vehicle = self._create_vehicle_from_detection(db, clean_plate, ai_dummy)

            detection.vehicle_id = vehicle.id

        db.add(detection)
        db.commit()

        # Handle driver auto-resolution
        resolved_driver = None
        if driver_name and driver_name.strip():
            from app.models.driver import Driver
            from app.crud.crud_driver import crud_driver
            from app.schemas.driver import DriverCreate
            clean_dname = driver_name.strip()
            existing_driver = db.query(Driver).filter(Driver.full_name.ilike(clean_dname)).first()
            if existing_driver:
                resolved_driver = existing_driver
            else:
                import random
                lic_no = f"DL-{random.randint(10000, 99999)}"
                phone_no = f"+91-{random.randint(70000, 99999)}-{random.randint(10000, 99999)}"
                driver_in = DriverCreate(
                    full_name=clean_dname,
                    license_number=lic_no,
                    phone_number=phone_no,
                    is_active=True,
                )
                resolved_driver = crud_driver.create(db, obj_in=driver_in)

        # Trigger Gate Movement sync
        from app.services.entry_exit_service import entry_exit_service
        movement_record = None
        if clean_plate:
            try:
                movement_record = entry_exit_service.process_recognition_event(
                    db=db,
                    plate_number=clean_plate,
                    ocr_confidence=detection.confidence,
                    vehicle_type=detection.vehicle_type_detected,
                    gate_id=gate_id,
                    ai_result={"cropped_vehicle_path": detection.cropped_vehicle_path, "cropped_plate_path": detection.cropped_plate_path},
                )
                if movement_record and resolved_driver:
                    movement_record.driver_id = resolved_driver.id
                    db.commit()
                    db.refresh(movement_record)
            except Exception as ev_err:
                logger.error(f"Sync Gate Movement failed: {ev_err}", exc_info=True)

        # Trigger Trip Engine sync
        from app.services.trip_service import trip_service
        trip_record = None
        if clean_plate:
            try:
                trip_record = trip_service.process_ai_recognition_event(
                    db=db,
                    plate_number=clean_plate,
                    ocr_confidence=detection.confidence,
                    gate_id=gate_id,
                )
                if trip_record and resolved_driver:
                    trip_record.driver_id = resolved_driver.id
                    db.commit()
                    db.refresh(trip_record)
            except Exception as trip_err:
                logger.error(f"Sync Trip Engine failed: {trip_err}", exc_info=True)

        return {
            "success": True,
            "message": "Dataset entry re-synced successfully across all modules",
            "detection_id": str(detection.id),
            "plate_text": clean_plate,
            "vehicle_id": str(vehicle.id) if vehicle else None,
            "driver_name": resolved_driver.full_name if resolved_driver else driver_name,
            "trip_id": str(trip_record.id) if trip_record else None,
            "movement_id": str(movement_record.id) if movement_record else None,
        }

    def get_vehicles_with_detections(
        self, db: Session, skip: int = 0, limit: int = 50, search: Optional[str] = None
    ) -> Tuple[list, int]:
        query = db.query(Vehicle).filter(Vehicle.detection_count > 0)

        if search:
            from sqlalchemy import or_
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    Vehicle.vehicle_number.ilike(search_filter),
                    Vehicle.make_model.ilike(search_filter),
                )
            )

        total = query.count()
        items = query.order_by(Vehicle.last_seen_at.desc().nullslast()).offset(skip).limit(limit).all()
        return items, total

    def get_vehicle_detail(self, db: Session, vehicle_id: uuid.UUID) -> Vehicle:
        vehicle = crud_vehicle.get(db, vehicle_id=vehicle_id)
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return vehicle

    def get_detection_history(self, db: Session, vehicle_id: uuid.UUID, skip: int = 0, limit: int = 50) -> Tuple[list, int]:
        return crud_vehicle_detection.get_by_vehicle(db, vehicle_id=vehicle_id, skip=skip, limit=limit)


vehicle_recognition_service = VehicleRecognitionService()
