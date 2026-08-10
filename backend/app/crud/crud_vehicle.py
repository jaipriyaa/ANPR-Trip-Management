from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


class CRUDVehicle:
    def get(self, db: Session, vehicle_id: UUID) -> Optional[Vehicle]:
        return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    def get_by_number(self, db: Session, vehicle_number: str) -> Optional[Vehicle]:
        return db.query(Vehicle).filter(Vehicle.vehicle_number == vehicle_number).first()

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        transporter_id: Optional[UUID] = None,
        vehicle_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_blacklisted: Optional[bool] = None
    ) -> Tuple[List[Vehicle], int]:
        query = db.query(Vehicle)

        if transporter_id is not None:
            query = query.filter(Vehicle.transporter_id == transporter_id)

        if vehicle_type:
            query = query.filter(Vehicle.vehicle_type == vehicle_type)

        if is_active is not None:
            query = query.filter(Vehicle.is_active == is_active)

        if is_blacklisted is not None:
            query = query.filter(Vehicle.is_blacklisted == is_blacklisted)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    Vehicle.vehicle_number.ilike(search_filter),
                    Vehicle.make_model.ilike(search_filter)
                )
            )

        total = query.count()
        items = query.order_by(Vehicle.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def create(self, db: Session, obj_in: VehicleCreate) -> Vehicle:
        data = obj_in.model_dump()
        if data.get("vehicle_number"):
            data["vehicle_number"] = str(data["vehicle_number"])[:20]
        db_obj = Vehicle(**data)
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            raise e

    def update(self, db: Session, db_obj: Vehicle, obj_in: VehicleUpdate) -> Vehicle:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, vehicle_id: UUID) -> bool:
        db_obj = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not db_obj:
            return False
        db.delete(db_obj)
        db.commit()
        return True


crud_vehicle = CRUDVehicle()
