from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.vehicle_plate import VehiclePlate
from app.schemas.vehicle_plate import VehiclePlateCreate, VehiclePlateUpdate


class CRUDVehiclePlate:
    def get(self, db: Session, plate_id: UUID) -> Optional[VehiclePlate]:
        return db.query(VehiclePlate).filter(VehiclePlate.id == plate_id).first()

    def get_by_plate_number(self, db: Session, plate_number: str) -> Optional[VehiclePlate]:
        return db.query(VehiclePlate).filter(VehiclePlate.plate_number == plate_number).first()

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        vehicle_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[VehiclePlate], int]:
        query = db.query(VehiclePlate)

        if vehicle_id is not None:
            query = query.filter(VehiclePlate.vehicle_id == vehicle_id)

        if is_active is not None:
            query = query.filter(VehiclePlate.is_active == is_active)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(VehiclePlate.plate_number.ilike(search_filter))

        total = query.count()
        items = query.order_by(VehiclePlate.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def create(self, db: Session, obj_in: VehiclePlateCreate) -> VehiclePlate:
        db_obj = VehiclePlate(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: VehiclePlate, obj_in: VehiclePlateUpdate) -> VehiclePlate:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, plate_id: UUID) -> bool:
        db_obj = db.query(VehiclePlate).filter(VehiclePlate.id == plate_id).first()
        if not db_obj:
            return False
        db.delete(db_obj)
        db.commit()
        return True


crud_vehicle_plate = CRUDVehiclePlate()
