import logging
from typing import Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.crud.crud_vehicle_movement import crud_vehicle_movement
from app.crud.crud_gate import crud_gate
from app.models.vehicle_movement import VehicleMovement
from app.models.gate import Gate
from app.schemas.vehicle_movement import VehicleMovementCreate, VehicleMovementUpdate, LiveMovementsSummaryResponse

logger = logging.getLogger(__name__)

DUPLICATE_TIME_WINDOW_SECONDS = 120  # 2 minutes duplicate suppression window
CONFIDENCE_THRESHOLD = 0.01         # Minimum OCR confidence threshold (inclusive for all recognized plates)


def format_stay_duration(total_seconds: float) -> str:
    """Format total seconds into human readable duration string (e.g. '2 Hours 17 Minutes')."""
    total_seconds = max(0, float(total_seconds))
    total_minutes = int(total_seconds // 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60

    if hours > 0:
        if minutes > 0:
            return f"{hours} Hour{'s' if hours > 1 else ''} {minutes} Minute{'s' if minutes > 1 else ''}"
        return f"{hours} Hour{'s' if hours > 1 else ''}"
    elif minutes > 0:
        return f"{minutes} Minute{'s' if minutes > 1 else ''}"
    else:
        seconds = int(total_seconds)
        return f"{seconds} Second{'s' if seconds > 1 else ''}"


class EntryExitEngine:
    def process_recognition_event(
        self,
        db: Session,
        plate_number: str,
        ocr_confidence: float = 0.0,
        vehicle_type: Optional[str] = None,
        gate_id: Optional[UUID] = None,
        camera_id: Optional[UUID] = None,
        ai_result: Optional[dict] = None,
    ) -> Optional[VehicleMovement]:
        """Core AI Event Processor converting plate detections into vehicle movements."""
        clean_plate = plate_number.upper().strip() if plate_number else ""

        # 1. Confidence & Validation Filter
        if not clean_plate or len(clean_plate) < 4:
            logger.warning(f"EntryExitEngine: Invalid plate '{clean_plate}' ignored.")
            return None

        if ocr_confidence < CONFIDENCE_THRESHOLD:
            logger.warning(f"EntryExitEngine: Plate '{clean_plate}' confidence {ocr_confidence} below threshold {CONFIDENCE_THRESHOLD}.")
            return None

        now = datetime.now(timezone.utc)

        # 2. Duplicate Detection Protection (Same camera/gate within window)
        latest_movement = crud_vehicle_movement.get_latest_movement_by_plate(db, clean_plate)
        if latest_movement:
            ref_time = latest_movement.exit_time if latest_movement.exit_time else latest_movement.entry_time
            if ref_time and (now - ref_time).total_seconds() < DUPLICATE_TIME_WINDOW_SECONDS:
                logger.info(f"EntryExitEngine: Duplicate detection for '{clean_plate}' within {DUPLICATE_TIME_WINDOW_SECONDS}s window ignored.")
                return latest_movement

        # 3. Determine Gate and Gate Direction (Entry vs Exit)
        gate = crud_gate.get(db, gate_id) if gate_id else None
        if not gate:
            # Fallback to default active gate if not specified
            gates, _ = crud_gate.get_multi(db, limit=1, status="ACTIVE")
            gate = gates[0] if gates else None

        active_inside = crud_vehicle_movement.get_active_movement_by_plate(db, clean_plate)

        is_exit_event = False
        if gate:
            if gate.gate_type == "Exit":
                is_exit_event = True
            elif gate.gate_type == "Entry":
                is_exit_event = False
            else:  # Entry & Exit
                # If vehicle is currently INSIDE, next detection is EXIT
                is_exit_event = active_inside is not None
        else:
            is_exit_event = active_inside is not None

        # Extract IDs from ai_result / verification_result
        verif = ai_result.get("verification_result", {}) if ai_result else {}
        vehicle_id = verif.get("vehicle", {}).get("id") or ai_result.get("vehicle_id") if ai_result else None
        driver_id = verif.get("driver", {}).get("id") if verif else None
        transporter_id = verif.get("transporter", {}).get("id") if verif else None
        purpose = verif.get("trip", {}).get("purpose", "Gate Inspection") if verif else "Gate Inspection"
        destination = verif.get("trip", {}).get("destination", "Main Facility") if verif else "Main Facility"
        v_crop_path = ai_result.get("cropped_vehicle_path") if ai_result else None
        p_crop_path = ai_result.get("cropped_plate_path") if ai_result else None

        # 4. Execute Exit Logic
        if is_exit_event and active_inside:
            exit_time = now
            entry_time = active_inside.entry_time
            if exit_time < entry_time:
                exit_time = entry_time + timedelta(seconds=1)

            duration_sec = max(0.0, (exit_time - entry_time).total_seconds())
            duration_min = round(duration_sec / 60.0, 2)
            duration_fmt = format_stay_duration(duration_sec)

            update_data = VehicleMovementUpdate(
                exit_gate_id=gate.id if gate else None,
                exit_camera_id=camera_id,
                exit_time=exit_time,
                stay_duration_minutes=duration_min,
                stay_duration_formatted=duration_fmt,
                movement_status="OUTSIDE",
                vehicle_status="EXITED",
                recognition_confidence=ocr_confidence,
                purpose=purpose,
                destination=destination,
                cropped_vehicle_path=v_crop_path or active_inside.cropped_vehicle_path,
                cropped_plate_path=p_crop_path or active_inside.cropped_plate_path,
            )

            updated = crud_vehicle_movement.update(db, db_obj=active_inside, obj_in=update_data)
            logger.info(f"EntryExitEngine: Vehicle '{clean_plate}' EXITED gate '{gate.gate_code if gate else 'N/A'}' (Stay: {duration_fmt}).")
            return updated

        # 5. Execute Entry Logic
        elif not is_exit_event:
            # If vehicle is already inside and another entry is triggered, update existing entry time
            if active_inside:
                logger.info(f"EntryExitEngine: Vehicle '{clean_plate}' already INSIDE. Refreshing entry record.")
                return active_inside

            create_obj = VehicleMovementCreate(
                recognized_plate=clean_plate,
                vehicle_id=UUID(vehicle_id) if vehicle_id and isinstance(vehicle_id, str) else vehicle_id,
                entry_gate_id=gate.id if gate else None,
                entry_camera_id=camera_id,
                entry_time=now,
                movement_status="INSIDE",
                vehicle_status="ENTERED",
                recognition_confidence=ocr_confidence,
                vehicle_type=vehicle_type or "Vehicle",
                driver_id=UUID(driver_id) if driver_id and isinstance(driver_id, str) else driver_id,
                transporter_id=UUID(transporter_id) if transporter_id and isinstance(transporter_id, str) else transporter_id,
                purpose=purpose,
                destination=destination,
                cropped_vehicle_path=v_crop_path,
                cropped_plate_path=p_crop_path,
            )

            created = crud_vehicle_movement.create(db, obj_in=create_obj)
            logger.info(f"EntryExitEngine: Vehicle '{clean_plate}' ENTERED gate '{gate.gate_code if gate else 'N/A'}'.")
            return created

        # 6. Fallback Exit Without Active Entry (untracked exit)
        else:
            logger.warning(f"EntryExitEngine: Exit triggered for '{clean_plate}' without active entry. Creating standalone exit record.")
            create_obj = VehicleMovementCreate(
                recognized_plate=clean_plate,
                vehicle_id=UUID(vehicle_id) if vehicle_id and isinstance(vehicle_id, str) else vehicle_id,
                exit_gate_id=gate.id if gate else None,
                exit_camera_id=camera_id,
                entry_time=now,
                exit_time=now,
                stay_duration_minutes=0.0,
                stay_duration_formatted="0 Minutes",
                movement_status="OUTSIDE",
                vehicle_status="EXITED",
                recognition_confidence=ocr_confidence,
                vehicle_type=vehicle_type or "Vehicle",
                purpose=purpose,
                destination=destination,
                cropped_vehicle_path=v_crop_path,
                cropped_plate_path=p_crop_path,
            )
            return crud_vehicle_movement.create(db, obj_in=create_obj)

    def get_live_summary(self, db: Session) -> LiveMovementsSummaryResponse:
        """Computes real-time dashboard summary metrics."""
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        inside_count = db.query(VehicleMovement).filter(VehicleMovement.movement_status == "INSIDE").count()

        entered_today = (
            db.query(VehicleMovement)
            .filter(VehicleMovement.entry_time >= today_start)
            .count()
        )

        exited_today = (
            db.query(VehicleMovement)
            .filter(
                VehicleMovement.exit_time >= today_start,
                VehicleMovement.movement_status == "OUTSIDE"
            )
            .count()
        )

        avg_minutes = (
            db.query(func.avg(VehicleMovement.stay_duration_minutes))
            .filter(
                VehicleMovement.movement_status == "OUTSIDE",
                VehicleMovement.exit_time >= today_start
            )
            .scalar()
        )

        avg_str = format_stay_duration((avg_minutes or 0.0) * 60.0) if avg_minutes else "N/A"

        return LiveMovementsSummaryResponse(
            vehicles_currently_inside=inside_count,
            vehicles_entered_today=entered_today,
            vehicles_exited_today=exited_today,
            avg_stay_duration_formatted=avg_str,
        )


entry_exit_service = EntryExitEngine()
