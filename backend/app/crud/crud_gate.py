from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.gate import Gate
from app.schemas.gate import GateCreate, GateUpdate


class CRUDGate:
    def get(self, db: Session, gate_id: UUID) -> Optional[Gate]:
        return db.query(Gate).filter(Gate.id == gate_id).first()

    def get_by_code(self, db: Session, gate_code: str) -> Optional[Gate]:
        return db.query(Gate).filter(Gate.gate_code == gate_code.upper().strip()).first()

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        gate_type: Optional[str] = None,
        status: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Gate], int]:
        query = db.query(Gate)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Gate.gate_code.ilike(search_pattern),
                    Gate.gate_name.ilike(search_pattern),
                    Gate.location.ilike(search_pattern),
                )
            )

        if gate_type:
            query = query.filter(Gate.gate_type == gate_type)

        if status:
            query = query.filter(Gate.status == status)

        if is_active is not None:
            query = query.filter(Gate.is_active == is_active)

        total = query.count()
        items = query.order_by(Gate.created_at.desc()).offset(skip).limit(limit).all()

        # Compute camera_count dynamically
        for item in items:
            item.camera_count = len(item.cameras) if item.cameras else 0

        return items, total

    def create(self, db: Session, *, obj_in: GateCreate) -> Gate:
        db_obj = Gate(
            gate_code=obj_in.gate_code.upper().strip(),
            gate_name=obj_in.gate_name.strip(),
            gate_type=obj_in.gate_type,
            location=obj_in.location,
            description=obj_in.description,
            status=obj_in.status,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        db_obj.camera_count = 0
        return db_obj

    def update(self, db: Session, *, db_obj: Gate, obj_in: GateUpdate) -> Gate:
        update_data = obj_in.model_dump(exclude_unset=True)
        if "gate_code" in update_data and update_data["gate_code"]:
            update_data["gate_code"] = update_data["gate_code"].upper().strip()

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        db_obj.camera_count = len(db_obj.cameras) if db_obj.cameras else 0
        return db_obj

    def remove(self, db: Session, *, gate_id: UUID) -> Optional[Gate]:
        obj = db.query(Gate).get(gate_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


crud_gate = CRUDGate()
