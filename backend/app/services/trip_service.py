import logging
from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from fastapi import HTTPException, status

from app.crud.crud_scheduled_trip import crud_scheduled_trip
from app.crud.crud_vehicle import crud_vehicle
from app.crud.crud_driver import crud_driver
from app.crud.crud_transporter import crud_transporter
from app.crud.crud_gate import crud_gate
from app.models.scheduled_trip import ScheduledTrip
from app.models.vehicle import Vehicle
from app.models.vehicle_movement import VehicleMovement
from app.schemas.scheduled_trip import ScheduledTripCreate, ScheduledTripUpdate, TripDashboardSummaryResponse
from app.services.entry_exit_service import format_stay_duration

logger = logging.getLogger(__name__)


class TripEngine:
    def validate_trip_creation(self, db: Session, obj_in: ScheduledTripCreate) -> None:
        """Validates trip constraints prior to creation."""
        # 1. Expected exit must be after expected entry
        if obj_in.expected_exit_time <= obj_in.expected_entry_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Expected exit time must be strictly after expected entry time.",
            )

        # 2. Resolve vehicle_id from recognized_plate if not provided
        vehicle_id = obj_in.vehicle_id
        if not vehicle_id and obj_in.recognized_plate:
            v = crud_vehicle.get_by_number(db, obj_in.recognized_plate)
            if v:
                vehicle_id = v.id
                obj_in.vehicle_id = v.id

        # 3. Check single active trip constraint per vehicle
        if vehicle_id:
            existing_v_trip = crud_scheduled_trip.get_active_trip_by_vehicle(db, vehicle_id)
            if existing_v_trip:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Vehicle already has an active trip '{existing_v_trip.trip_number}' in state '{existing_v_trip.trip_status}'. Cannot schedule overlapping trips.",
                )

        # 4. Check single active trip constraint per driver
        if obj_in.driver_id:
            existing_d_trip = crud_scheduled_trip.get_active_trip_by_driver(db, obj_in.driver_id)
            if existing_d_trip:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Driver already has an active trip '{existing_d_trip.trip_number}'. Driver cannot be assigned to overlapping trips.",
                )

    # Allowed State Machine Transitions
    VALID_TRANSITIONS = {
        "SCHEDULED": {"ARRIVED", "ENTRY_APPROVED", "INSIDE_PLANT", "CANCELLED", "EXCEPTION"},
        "ARRIVED": {"ENTRY_APPROVED", "INSIDE_PLANT", "CANCELLED", "EXCEPTION"},
        "ENTRY_APPROVED": {"INSIDE_PLANT", "CANCELLED", "EXCEPTION"},
        "INSIDE_PLANT": {"AT_DESTINATION", "EXIT_DETECTED", "COMPLETED", "EXCEPTION"},
        "AT_DESTINATION": {"EXIT_DETECTED", "COMPLETED", "EXCEPTION"},
        "EXIT_DETECTED": {"COMPLETED", "EXCEPTION"},
        "COMPLETED": set(),  # Terminal state
        "CANCELLED": set(),  # Terminal state
        "EXCEPTION": {"INSIDE_PLANT", "COMPLETED", "CANCELLED"},
    }

    def transition_state(
        self,
        db: Session,
        trip: ScheduledTrip,
        new_status: str,
        changed_by: str = "SYSTEM_AI_RECOGNITION",
        remarks: Optional[str] = None
    ) -> ScheduledTrip:
        """Executes a strict trip state machine transition and records history."""
        current_status = trip.trip_status or "SCHEDULED"
        if new_status != current_status:
            allowed = self.VALID_TRANSITIONS.get(current_status, set())
            if new_status not in allowed:
                err_msg = f"Invalid state transition from {current_status} to {new_status}."
                logger.error(f"TripEngine: {err_msg}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

            prev_status = current_status
            trip.trip_status = new_status
            db.add(trip)
            db.commit()
            db.refresh(trip)

            crud_scheduled_trip.record_status_change(
                db,
                trip_id=trip.id,
                previous_status=prev_status,
                current_status=new_status,
                changed_by=changed_by,
                remarks=remarks,
            )
        return trip

    def calculate_late_arrival(self, expected_entry: Optional[datetime], actual_entry: datetime) -> Tuple[str, int]:
        """Calculates late arrival status and delay seconds."""
        if not expected_entry:
            return "ON_TIME", 0

        # Ensure tz awareness consistency
        if expected_entry.tzinfo is None:
            expected_entry = expected_entry.replace(tzinfo=timezone.utc)
        if actual_entry.tzinfo is None:
            actual_entry = actual_entry.replace(tzinfo=timezone.utc)

        delay_sec = int((actual_entry - expected_entry).total_seconds())
        # 15 minutes grace threshold
        if delay_sec > 900:
            return "LATE", delay_sec
        return "ON_TIME", max(0, delay_sec)

    def calculate_dwell_time(self, entry_time: Optional[datetime], exit_time: datetime) -> Tuple[float, float, str]:
        """Calculates non-negative dwell time in seconds, minutes, and formatted string."""
        if not entry_time:
            return 0.0, 0.0, "0 Minutes"

        if entry_time.tzinfo is None:
            entry_time = entry_time.replace(tzinfo=timezone.utc)
        if exit_time.tzinfo is None:
            exit_time = exit_time.replace(tzinfo=timezone.utc)

        dwell_sec = max(0.0, (exit_time - entry_time).total_seconds())
        dwell_min = round(dwell_sec / 60.0, 2)
        dwell_fmt = format_stay_duration(dwell_sec)
        return dwell_sec, dwell_min, dwell_fmt

    def check_overstay(self, dwell_seconds: float, expected_entry: Optional[datetime], expected_exit: Optional[datetime]) -> Tuple[bool, float]:
        """Checks if vehicle stayed inside plant longer than expected/allowed duration."""
        if expected_entry and expected_exit:
            if expected_entry.tzinfo is None:
                expected_entry = expected_entry.replace(tzinfo=timezone.utc)
            if expected_exit.tzinfo is None:
                expected_exit = expected_exit.replace(tzinfo=timezone.utc)
            allowed_sec = max(3600.0, (expected_exit - expected_entry).total_seconds())
        else:
            allowed_sec = 14400.0  # 4 hours default

        is_overstay = dwell_seconds > allowed_sec
        excess_sec = max(0.0, dwell_seconds - allowed_sec)
        return is_overstay, excess_sec

    def process_ai_recognition_event(
        self,
        db: Session,
        plate_number: str,
        ocr_confidence: float = 0.0,
        gate_id: Optional[UUID] = None,
        camera_id: Optional[UUID] = None,
        direction: Optional[str] = None,
    ) -> Optional[ScheduledTrip]:
        """Automatically matches vehicle recognition events to scheduled trips & drives state transitions."""
        clean_plate = plate_number.upper().strip() if plate_number else ""
        if not clean_plate:
            return None

        vehicle = crud_vehicle.get_by_number(db, clean_plate)
        if not vehicle:
            logger.info(f"TripEngine: Vehicle plate '{clean_plate}' not in master catalog.")
            return None

        trip = crud_scheduled_trip.get_active_trip_by_vehicle(db, vehicle.id)
        now = datetime.now(timezone.utc)

        # Check for duplicate frame recognitions for recently completed trips within 120s
        if not trip:
            recent_completed = (
                db.query(ScheduledTrip)
                .filter(
                    ScheduledTrip.vehicle_id == vehicle.id,
                    ScheduledTrip.trip_status == "COMPLETED",
                    ScheduledTrip.actual_exit_time >= now - timedelta(seconds=120)
                )
                .order_by(ScheduledTrip.actual_exit_time.desc())
                .first()
            )
            if recent_completed:
                logger.info(f"TripEngine: Suppressing duplicate recognition for recently completed trip '{recent_completed.trip_number}'.")
                return recent_completed

        # Auto-create ad-hoc trip if no active scheduled trip exists
        if not trip:
            logger.info(f"TripEngine: Creating ad-hoc trip for master vehicle '{clean_plate}'.")
            trip_create = ScheduledTripCreate(
                vehicle_id=vehicle.id,
                driver_id=None,
                transporter_id=vehicle.transporter_id,
                entry_gate_id=gate_id,
                expected_entry_time=now,
                expected_exit_time=now + timedelta(hours=4),
                purpose="Ad-hoc Industrial Visit",
                trip_status="SCHEDULED",
                approval_status="PENDING",
            )
            trip = crud_scheduled_trip.create(db, obj_in=trip_create)

        curr_status = trip.trip_status or "SCHEDULED"

        # Determine Entry vs Exit based on state or explicit direction
        is_exit = (direction == "Exiting") or (curr_status in ["INSIDE", "INSIDE_PLANT", "AT_DESTINATION", "EXIT_DETECTED"])

        if not is_exit:
            # 1. Gate Arrival & Entry Approval Workflow: SCHEDULED -> ARRIVED -> ENTRY_APPROVED -> INSIDE_PLANT
            arr_status, arr_delay = self.calculate_late_arrival(trip.expected_entry_time, now)
            trip.actual_entry_time = now
            trip.approval_status = "APPROVED"
            if gate_id and not trip.entry_gate_id:
                trip.entry_gate_id = gate_id

            # Transition to ARRIVED first if in SCHEDULED
            if curr_status == "SCHEDULED":
                self.transition_state(db, trip, "ARRIVED", remarks=f"Vehicle Arrived at Gate ({arr_status}). Delay: {arr_delay}s")
                if arr_status == "LATE":
                    from app.services.alert_service import alert_engine
                    alert_engine.create_alert(
                        db=db,
                        alert_type="LATE_ARRIVAL",
                        message=f"Vehicle '{clean_plate}' arrived late by {round(arr_delay/60.0, 1)} minutes.",
                        reason=f"Arrival delay: {arr_delay}s",
                        trip_id=trip.id,
                        gate_id=gate_id,
                        plate_number=clean_plate,
                        vehicle_type=vehicle.vehicle_type if vehicle else "Truck"
                    )

            # Transition ARRIVED -> ENTRY_APPROVED
            if trip.trip_status == "ARRIVED":
                self.transition_state(db, trip, "ENTRY_APPROVED", remarks=f"Gate Authorization Approved ({int(ocr_confidence*100)}% OCR conf)")

            # Transition ENTRY_APPROVED -> INSIDE_PLANT
            if trip.trip_status == "ENTRY_APPROVED":
                self.transition_state(db, trip, "INSIDE_PLANT", remarks=f"Vehicle Passed Entry Gate. Trip State: INSIDE_PLANT")

            logger.info(f"TripEngine: Trip '{trip.trip_number}' (Vehicle: {clean_plate}) State: {trip.trip_status}")
            return trip

        else:
            # 2. Gate Exit Workflow: INSIDE_PLANT -> AT_DESTINATION / EXIT_DETECTED -> COMPLETED
            entry_t = trip.actual_entry_time or trip.expected_entry_time or now
            dwell_sec, dwell_min, dwell_fmt = self.calculate_dwell_time(entry_t, now)
            is_overstay, excess_sec = self.check_overstay(dwell_sec, trip.expected_entry_time, trip.expected_exit_time)

            from app.services.alert_service import alert_engine
            if is_overstay:
                alert_engine.create_alert(
                    db=db,
                    alert_type="OVERSTAY",
                    message=f"Vehicle '{clean_plate}' stayed inside plant for {dwell_fmt} ({round(excess_sec/60.0, 1)} minutes over limit).",
                    reason=f"Dwell excess: {excess_sec}s",
                    trip_id=trip.id,
                    gate_id=gate_id,
                    plate_number=clean_plate,
                    vehicle_type=vehicle.vehicle_type if vehicle else "Truck"
                )

            trip.actual_exit_time = now
            if gate_id and not trip.exit_gate_id:
                trip.exit_gate_id = gate_id

            if trip.trip_status in ["INSIDE", "INSIDE_PLANT"]:
                self.transition_state(db, trip, "EXIT_DETECTED", remarks=f"Vehicle Exit Motion Detected at Gate.")

            if trip.trip_status in ["AT_DESTINATION", "EXIT_DETECTED"]:
                rem_msg = f"Trip Completed. Dwell: {dwell_fmt}."
                if is_overstay:
                    rem_msg += f" [OVERSTAY ALERT: {round(excess_sec/60.0, 1)}m over limit]"
                self.transition_state(db, trip, "COMPLETED", remarks=rem_msg)
                alert_engine.resolve_overstay_by_trip(db, trip.id, reason=f"Vehicle exited plant after {dwell_fmt}")

            logger.info(f"TripEngine: Trip '{trip.trip_number}' (Vehicle: {clean_plate}) COMPLETED. Dwell: {dwell_fmt}")
            return trip

    def approve_trip(self, db: Session, trip_id: UUID, remarks: Optional[str] = None) -> ScheduledTrip:
        trip = crud_scheduled_trip.get(db, trip_id)
        if not trip:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        trip.approval_status = "APPROVED"
        if remarks:
            trip.remarks = remarks

        db.add(trip)
        db.commit()
        db.refresh(trip)

        crud_scheduled_trip.record_status_change(
            db,
            trip_id=trip.id,
            previous_status=trip.trip_status,
            current_status=trip.trip_status,
            changed_by="SECURITY_OFFICER",
            remarks=f"Manual Approval Granted. {remarks or ''}",
        )
        return trip

    def reject_trip(self, db: Session, trip_id: UUID, remarks: Optional[str] = None) -> ScheduledTrip:
        trip = crud_scheduled_trip.get(db, trip_id)
        if not trip:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        prev_status = trip.trip_status
        trip.approval_status = "REJECTED"
        trip.trip_status = "CANCELLED"
        if remarks:
            trip.remarks = remarks

        db.add(trip)
        db.commit()
        db.refresh(trip)

        crud_scheduled_trip.record_status_change(
            db,
            trip_id=trip.id,
            previous_status=prev_status,
            current_status="CANCELLED",
            changed_by="SECURITY_OFFICER",
            remarks=f"Trip Rejected & Cancelled. {remarks or ''}",
        )
        return trip

    def get_dashboard_summary(self, db: Session) -> TripDashboardSummaryResponse:
        """Returns trip metrics dashboard summary."""
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        active_statuses = ["SCHEDULED", "WAITING", "ARRIVED", "ENTRY_APPROVED", "INSIDE", "INSIDE_PLANT", "AT_DESTINATION", "EXIT_DETECTED"]
        inside_statuses = ["INSIDE", "INSIDE_PLANT", "AT_DESTINATION"]

        active = db.query(ScheduledTrip).filter(ScheduledTrip.trip_status.in_(active_statuses)).count()
        completed = db.query(ScheduledTrip).filter(ScheduledTrip.trip_status == "COMPLETED").count()
        waiting = db.query(ScheduledTrip).filter(ScheduledTrip.trip_status.in_(["WAITING", "ARRIVED"])).count()
        rejected = db.query(ScheduledTrip).filter(ScheduledTrip.approval_status == "REJECTED").count()
        inside = db.query(ScheduledTrip).filter(ScheduledTrip.trip_status.in_(inside_statuses)).count()
        todays = db.query(ScheduledTrip).filter(ScheduledTrip.created_at >= today_start).count()

        # Avg Trip Duration calculation
        completed_trips = (
            db.query(ScheduledTrip)
            .filter(
                ScheduledTrip.trip_status == "COMPLETED",
                ScheduledTrip.actual_entry_time != None,
                ScheduledTrip.actual_exit_time != None,
            )
            .all()
        )

        total_sec = 0.0
        for t in completed_trips:
            dur = (t.actual_exit_time - t.actual_entry_time).total_seconds()
            if dur > 0:
                total_sec += dur

        avg_sec = (total_sec / len(completed_trips)) if completed_trips else 7200.0
        avg_fmt = format_stay_duration(avg_sec)

        return TripDashboardSummaryResponse(
            active_trips=active,
            completed_trips=completed,
            waiting_vehicles=waiting,
            rejected_trips=rejected,
            vehicles_inside=inside,
            todays_trips=todays,
            avg_trip_duration_formatted=avg_fmt,
        )


trip_service = TripEngine()
