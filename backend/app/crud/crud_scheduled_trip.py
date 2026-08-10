import random
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_

from app.models.scheduled_trip import ScheduledTrip
from app.models.trip_status_history import TripStatusHistory
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.transporter import Transporter
from app.models.gate import Gate
from app.schemas.scheduled_trip import ScheduledTripCreate, ScheduledTripUpdate, ScheduledTripResponse, TripStatusHistoryResponse


class CRUDScheduledTrip:
    def get(self, db: Session, trip_id: UUID) -> Optional[ScheduledTrip]:
        return db.get(ScheduledTrip, trip_id)

    def get_by_trip_number(self, db: Session, trip_number: str) -> Optional[ScheduledTrip]:
        return db.query(ScheduledTrip).filter(ScheduledTrip.trip_number == trip_number.upper().strip()).first()

    def get_active_trip_by_vehicle(self, db: Session, vehicle_id: UUID) -> Optional[ScheduledTrip]:
        """Find active trip (SCHEDULED, WAITING, ARRIVED, ENTRY_APPROVED, INSIDE, INSIDE_PLANT, AT_DESTINATION, EXIT_DETECTED) for vehicle."""
        return (
            db.query(ScheduledTrip)
            .filter(
                ScheduledTrip.vehicle_id == vehicle_id,
                ScheduledTrip.trip_status.in_(["SCHEDULED", "WAITING", "ARRIVED", "ENTRY_APPROVED", "INSIDE", "INSIDE_PLANT", "AT_DESTINATION", "EXIT_DETECTED"])
            )
            .first()
        )

    def get_active_trip_by_plate(self, db: Session, plate_number: str) -> Optional[ScheduledTrip]:
        """Find active trip for plate number."""
        clean_plate = plate_number.upper().strip()
        vehicle = db.query(Vehicle).filter(Vehicle.vehicle_number == clean_plate).first()
        if not vehicle:
            return None
        return self.get_active_trip_by_vehicle(db, vehicle.id)

    def get_active_trip_by_driver(self, db: Session, driver_id: UUID) -> Optional[ScheduledTrip]:
        """Find active trip for driver."""
        return (
            db.query(ScheduledTrip)
            .filter(
                ScheduledTrip.driver_id == driver_id,
                ScheduledTrip.trip_status.in_(["SCHEDULED", "WAITING", "ARRIVED", "ENTRY_APPROVED", "INSIDE", "INSIDE_PLANT", "AT_DESTINATION", "EXIT_DETECTED"])
            )
            .first()
        )

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        trip_status: Optional[str] = None,
        approval_status: Optional[str] = None,
    ) -> Tuple[List[ScheduledTripResponse], int]:
        query = db.query(ScheduledTrip)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    ScheduledTrip.trip_number.ilike(search_pattern),
                    ScheduledTrip.purpose.ilike(search_pattern),
                    ScheduledTrip.material_name.ilike(search_pattern),
                    ScheduledTrip.destination_location.ilike(search_pattern),
                )
            )

        if trip_status:
            query = query.filter(ScheduledTrip.trip_status == trip_status)

        if approval_status:
            query = query.filter(ScheduledTrip.approval_status == approval_status)

        total = query.count()
        trips = query.order_by(ScheduledTrip.expected_entry_time.desc()).offset(skip).limit(limit).all()

        responses = [self._to_response(db, t) for t in trips]
        return responses, total

    def get_active(self, db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[ScheduledTripResponse], int]:
        query = db.query(ScheduledTrip).filter(ScheduledTrip.trip_status.in_(["SCHEDULED", "WAITING", "ARRIVED", "ENTRY_APPROVED", "INSIDE", "INSIDE_PLANT", "AT_DESTINATION", "EXIT_DETECTED"]))
        total = query.count()
        trips = query.order_by(ScheduledTrip.expected_entry_time.desc()).offset(skip).limit(limit).all()
        return [self._to_response(db, t) for t in trips], total

    def get_completed(self, db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[ScheduledTripResponse], int]:
        query = db.query(ScheduledTrip).filter(ScheduledTrip.trip_status == "COMPLETED")
        total = query.count()
        trips = query.order_by(ScheduledTrip.actual_exit_time.desc()).offset(skip).limit(limit).all()
        return [self._to_response(db, t) for t in trips], total

    def get_pending(self, db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[ScheduledTripResponse], int]:
        query = db.query(ScheduledTrip).filter(ScheduledTrip.approval_status == "PENDING")
        total = query.count()
        trips = query.order_by(ScheduledTrip.created_at.desc()).offset(skip).limit(limit).all()
        return [self._to_response(db, t) for t in trips], total

    def generate_trip_number(self, db: Session) -> str:
        """Generate unique trip number e.g. TRIP-2026-001."""
        prefix = f"TRIP-2026-"
        count = db.query(ScheduledTrip).count() + 1
        num_str = f"{prefix}{count:03d}"
        while self.get_by_trip_number(db, num_str):
            count += 1
            num_str = f"{prefix}{count:03d}"
        return num_str

    def create(self, db: Session, *, obj_in: ScheduledTripCreate) -> ScheduledTrip:
        trip_num = obj_in.trip_number or self.generate_trip_number(db)

        db_obj = ScheduledTrip(
            trip_number=trip_num,
            vehicle_id=obj_in.vehicle_id,
            vehicle_plate_id=obj_in.vehicle_plate_id,
            driver_id=obj_in.driver_id,
            transporter_id=obj_in.transporter_id,
            entry_gate_id=obj_in.entry_gate_id,
            exit_gate_id=obj_in.exit_gate_id,
            expected_entry_time=obj_in.expected_entry_time,
            expected_exit_time=obj_in.expected_exit_time,
            actual_entry_time=obj_in.actual_entry_time,
            actual_exit_time=obj_in.actual_exit_time,
            purpose=obj_in.purpose,
            material_name=obj_in.material_name,
            material_quantity=obj_in.material_quantity,
            source_location=obj_in.source_location,
            destination_location=obj_in.destination_location,
            priority=obj_in.priority,
            trip_status=obj_in.trip_status,
            approval_status=obj_in.approval_status,
            remarks=obj_in.remarks,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Record initial status in history
        self.record_status_change(
            db,
            trip_id=db_obj.id,
            previous_status=None,
            current_status=db_obj.trip_status,
            changed_by="USER_DISPATCHER",
            remarks="Trip Scheduled & Dispatched",
        )

        return db_obj

    def update(self, db: Session, *, db_obj: ScheduledTrip, obj_in: ScheduledTripUpdate) -> ScheduledTrip:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def record_status_change(
        self,
        db: Session,
        *,
        trip_id: UUID,
        previous_status: Optional[str],
        current_status: str,
        changed_by: str = "SYSTEM_AI_ENGINE",
        remarks: Optional[str] = None
    ) -> TripStatusHistory:
        history = TripStatusHistory(
            trip_id=trip_id,
            previous_status=previous_status,
            current_status=current_status,
            changed_by=changed_by,
            remarks=remarks,
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        return history

    def _to_response(self, db: Session, t: ScheduledTrip) -> ScheduledTripResponse:
        vehicle = db.get(Vehicle, t.vehicle_id) if t.vehicle_id else None
        driver = db.get(Driver, t.driver_id) if t.driver_id else None
        transporter = db.get(Transporter, t.transporter_id) if t.transporter_id else None
        entry_gate = db.get(Gate, t.entry_gate_id) if t.entry_gate_id else None
        exit_gate = db.get(Gate, t.exit_gate_id) if t.exit_gate_id else None

        resp = ScheduledTripResponse.model_validate(t)
        resp.vehicle_number = vehicle.vehicle_number if vehicle else None
        resp.vehicle_type = vehicle.vehicle_type if vehicle else "SUV"
        resp.driver_name = driver.full_name if driver else None
        resp.transporter_name = transporter.company_name if transporter else None
        resp.entry_gate_code = entry_gate.gate_code if entry_gate else None
        resp.entry_gate_name = entry_gate.gate_name if entry_gate else None
        resp.exit_gate_code = exit_gate.gate_code if exit_gate else None
        resp.exit_gate_name = exit_gate.gate_name if exit_gate else None
        
        # Load status history
        histories = (
            db.query(TripStatusHistory)
            .filter(TripStatusHistory.trip_id == t.id)
            .order_by(TripStatusHistory.changed_at.desc())
            .all()
        )
        resp.status_history = [TripStatusHistoryResponse.model_validate(h) for h in histories]

        return resp


crud_scheduled_trip = CRUDScheduledTrip()
