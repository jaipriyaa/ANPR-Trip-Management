from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.vehicle_detection import VehicleDetection
from app.schemas.vehicle_detection import VehicleDetectionCreate, VehicleDetectionUpdate


class CRUDVehicleDetection:
    def get(self, db: Session, detection_id: UUID) -> Optional[VehicleDetection]:
        return db.query(VehicleDetection).filter(VehicleDetection.id == detection_id).first()

    def get_by_vehicle(
        self, db: Session, vehicle_id: UUID, skip: int = 0, limit: int = 50
    ) -> Tuple[List[VehicleDetection], int]:
        query = db.query(VehicleDetection).filter(VehicleDetection.vehicle_id == vehicle_id)
        total = query.count()
        items = query.order_by(VehicleDetection.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def get_by_plate(
        self, db: Session, plate_text: str, skip: int = 0, limit: int = 50
    ) -> Tuple[List[VehicleDetection], int]:
        query = db.query(VehicleDetection).filter(VehicleDetection.plate_text == plate_text)
        total = query.count()
        items = query.order_by(VehicleDetection.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        status: Optional[str] = None,
        vehicle_id: Optional[UUID] = None,
    ) -> Tuple[List[VehicleDetection], int]:
        query = db.query(VehicleDetection)

        if status:
            query = query.filter(VehicleDetection.detection_status == status)
        if vehicle_id:
            query = query.filter(VehicleDetection.vehicle_id == vehicle_id)
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    VehicleDetection.plate_text.ilike(search_filter),
                    VehicleDetection.source_filename.ilike(search_filter),
                )
            )

        total = query.count()
        items = query.order_by(VehicleDetection.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def create(self, db: Session, obj_in: VehicleDetectionCreate) -> VehicleDetection:
        data = obj_in.model_dump()
        if data.get("plate_text"):
            data["plate_text"] = str(data["plate_text"])[:20]
        if data.get("corrected_plate"):
            data["corrected_plate"] = str(data["corrected_plate"])[:20]
        if data.get("ocr_raw_text"):
            data["ocr_raw_text"] = str(data["ocr_raw_text"])[:40]
        db_obj = VehicleDetection(**data)
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            raise e

    def update(self, db: Session, db_obj: VehicleDetection, obj_in: VehicleDetectionUpdate) -> VehicleDetection:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, detection_id: UUID) -> bool:
        db_obj = db.query(VehicleDetection).filter(VehicleDetection.id == detection_id).first()
        if not db_obj:
            return False
        db.delete(db_obj)
        db.commit()
        return True


crud_vehicle_detection = CRUDVehicleDetection()
