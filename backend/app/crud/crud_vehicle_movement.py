from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_

from app.models.vehicle_movement import VehicleMovement
from app.models.gate import Gate
from app.models.driver import Driver
from app.models.transporter import Transporter
from app.models.vehicle import Vehicle
from app.schemas.vehicle_movement import VehicleMovementCreate, VehicleMovementUpdate, VehicleMovementResponse


class CRUDVehicleMovement:
    def get(self, db: Session, movement_id: UUID) -> Optional[VehicleMovement]:
        return db.query(VehicleMovement).filter(VehicleMovement.id == movement_id).first()

    def get_active_movement_by_plate(self, db: Session, recognized_plate: str) -> Optional[VehicleMovement]:
        """Find open movement record (movement_status == 'INSIDE') for plate."""
        return (
            db.query(VehicleMovement)
            .filter(
                VehicleMovement.recognized_plate == recognized_plate.upper().strip(),
                VehicleMovement.movement_status == "INSIDE"
            )
            .order_by(VehicleMovement.entry_time.desc())
            .first()
        )

    def get_latest_movement_by_plate(self, db: Session, recognized_plate: str) -> Optional[VehicleMovement]:
        """Get latest movement record for plate regardless of status."""
        return (
            db.query(VehicleMovement)
            .filter(VehicleMovement.recognized_plate == recognized_plate.upper().strip())
            .order_by(VehicleMovement.entry_time.desc())
            .first()
        )

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        movement_status: Optional[str] = None,
        vehicle_status: Optional[str] = None,
        gate_id: Optional[UUID] = None,
    ) -> Tuple[List[VehicleMovementResponse], int]:
        query = db.query(VehicleMovement)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    VehicleMovement.recognized_plate.ilike(search_pattern),
                    VehicleMovement.vehicle_type.ilike(search_pattern),
                    VehicleMovement.purpose.ilike(search_pattern),
                )
            )

        if movement_status:
            query = query.filter(VehicleMovement.movement_status == movement_status)

        if vehicle_status:
            query = query.filter(VehicleMovement.vehicle_status == vehicle_status)

        if gate_id:
            query = query.filter(
                or_(
                    VehicleMovement.entry_gate_id == gate_id,
                    VehicleMovement.exit_gate_id == gate_id,
                )
            )

        total = query.count()
        movements = query.order_by(VehicleMovement.entry_time.desc()).offset(skip).limit(limit).all()

        responses = [self._to_response(db, m) for m in movements]
        return responses, total

    def get_current_inside(self, db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[VehicleMovementResponse], int]:
        """Get all vehicles currently INSIDE."""
        query = db.query(VehicleMovement).filter(VehicleMovement.movement_status == "INSIDE")
        total = query.count()
        movements = query.order_by(VehicleMovement.entry_time.desc()).offset(skip).limit(limit).all()
        return [self._to_response(db, m) for m in movements], total

    def get_history(self, db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[VehicleMovementResponse], int]:
        """Get completed entry/exit history (movement_status == 'OUTSIDE')."""
        query = db.query(VehicleMovement).filter(VehicleMovement.movement_status == "OUTSIDE")
        total = query.count()
        movements = query.order_by(VehicleMovement.exit_time.desc()).offset(skip).limit(limit).all()
        return [self._to_response(db, m) for m in movements], total

    def get_by_plate_history(self, db: Session, recognized_plate: str, skip: int = 0, limit: int = 100) -> Tuple[List[VehicleMovementResponse], int]:
        """Get movement history for specific vehicle plate."""
        clean_plate = recognized_plate.upper().strip()
        query = db.query(VehicleMovement).filter(VehicleMovement.recognized_plate == clean_plate)
        total = query.count()
        movements = query.order_by(VehicleMovement.entry_time.desc()).offset(skip).limit(limit).all()
        return [self._to_response(db, m) for m in movements], total

    def create(self, db: Session, *, obj_in: VehicleMovementCreate) -> VehicleMovement:
        db_obj = VehicleMovement(
            recognized_plate=obj_in.recognized_plate.upper().strip(),
            vehicle_id=obj_in.vehicle_id,
            vehicle_plate_id=obj_in.vehicle_plate_id,
            entry_gate_id=obj_in.entry_gate_id,
            exit_gate_id=obj_in.exit_gate_id,
            entry_camera_id=obj_in.entry_camera_id,
            exit_camera_id=obj_in.exit_camera_id,
            entry_time=obj_in.entry_time,
            exit_time=obj_in.exit_time,
            stay_duration_minutes=obj_in.stay_duration_minutes,
            stay_duration_formatted=obj_in.stay_duration_formatted,
            movement_status=obj_in.movement_status,
            vehicle_status=obj_in.vehicle_status,
            recognition_confidence=obj_in.recognition_confidence,
            vehicle_type=obj_in.vehicle_type,
            driver_id=obj_in.driver_id,
            transporter_id=obj_in.transporter_id,
            purpose=obj_in.purpose,
            destination=obj_in.destination,
            cropped_vehicle_path=obj_in.cropped_vehicle_path,
            cropped_plate_path=obj_in.cropped_plate_path,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: VehicleMovement, obj_in: VehicleMovementUpdate) -> VehicleMovement:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def _to_response(self, db: Session, m: VehicleMovement) -> VehicleMovementResponse:
        entry_gate = db.get(Gate, m.entry_gate_id) if m.entry_gate_id else None
        exit_gate = db.get(Gate, m.exit_gate_id) if m.exit_gate_id else None
        driver = db.get(Driver, m.driver_id) if m.driver_id else None
        transporter = db.get(Transporter, m.transporter_id) if m.transporter_id else None
        vehicle = db.get(Vehicle, m.vehicle_id) if m.vehicle_id else None

        resp = VehicleMovementResponse.model_validate(m)
        resp.entry_gate_code = entry_gate.gate_code if entry_gate else None
        resp.entry_gate_name = entry_gate.gate_name if entry_gate else None
        resp.exit_gate_code = exit_gate.gate_code if exit_gate else None
        resp.exit_gate_name = exit_gate.gate_name if exit_gate else None
        resp.driver_name = driver.full_name if driver else None
        resp.transporter_name = transporter.company_name if transporter else None
        resp.make_model = vehicle.make_model if vehicle else None
        resp.color = vehicle.color if vehicle else None
        return resp


crud_vehicle_movement = CRUDVehicleMovement()
