from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_

from app.models.transporter import Transporter
from app.schemas.transporter import TransporterCreate, TransporterUpdate


class CRUDTransporter:
    def get(self, db: Session, transporter_id: UUID) -> Optional[Transporter]:
        return db.query(Transporter).filter(Transporter.id == transporter_id).first()

    def get_by_code(self, db: Session, code: str) -> Optional[Transporter]:
        return db.query(Transporter).filter(Transporter.code == code).first()

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Transporter], int]:
        query = db.query(Transporter)

        if is_active is not None:
            query = query.filter(Transporter.is_active == is_active)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    Transporter.company_name.ilike(search_filter),
                    Transporter.code.ilike(search_filter),
                    Transporter.contact_person.ilike(search_filter)
                )
            )

        total = query.count()
        items = query.order_by(Transporter.company_name.asc()).offset(skip).limit(limit).all()
        return items, total

    def create(self, db: Session, obj_in: TransporterCreate) -> Transporter:
        db_obj = Transporter(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Transporter, obj_in: TransporterUpdate) -> Transporter:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, transporter_id: UUID) -> bool:
        db_obj = db.query(Transporter).filter(Transporter.id == transporter_id).first()
        if not db_obj:
            return False
        db.delete(db_obj)
        db.commit()
        return True


crud_transporter = CRUDTransporter()
