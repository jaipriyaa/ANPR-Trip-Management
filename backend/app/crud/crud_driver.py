from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.driver import Driver
from app.schemas.driver import DriverCreate, DriverUpdate


class CRUDDriver:
    def get(self, db: Session, driver_id: UUID) -> Optional[Driver]:
        return db.query(Driver).filter(Driver.id == driver_id).first()

    def get_by_license(self, db: Session, license_number: str) -> Optional[Driver]:
        return db.query(Driver).filter(Driver.license_number == license_number).first()

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        transporter_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Driver], int]:
        query = db.query(Driver)

        if transporter_id is not None:
            query = query.filter(Driver.transporter_id == transporter_id)

        if is_active is not None:
            query = query.filter(Driver.is_active == is_active)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    Driver.full_name.ilike(search_filter),
                    Driver.license_number.ilike(search_filter),
                    Driver.phone_number.ilike(search_filter)
                )
            )

        total = query.count()
        items = query.order_by(Driver.full_name.asc()).offset(skip).limit(limit).all()
        return items, total

    def create(self, db: Session, obj_in: DriverCreate) -> Driver:
        db_obj = Driver(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Driver, obj_in: DriverUpdate) -> Driver:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, driver_id: UUID) -> bool:
        db_obj = db.query(Driver).filter(Driver.id == driver_id).first()
        if not db_obj:
            return False
        db.delete(db_obj)
        db.commit()
        return True


crud_driver = CRUDDriver()
