from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.gate_rule import GateRule
from app.schemas.gate_rule import GateRuleCreate, GateRuleUpdate


class CRUDGateRule:
    def get_by_gate(self, db: Session, gate_id: UUID) -> Optional[GateRule]:
        return db.query(GateRule).filter(GateRule.gate_id == gate_id).first()

    def create_or_update(self, db: Session, *, obj_in: GateRuleCreate) -> GateRule:
        existing = self.get_by_gate(db, obj_in.gate_id)
        if existing:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(existing, field, value)
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing

        db_obj = GateRule(
            gate_id=obj_in.gate_id,
            allow_entry=obj_in.allow_entry,
            allow_exit=obj_in.allow_exit,
            allow_trucks=obj_in.allow_trucks,
            allow_buses=obj_in.allow_buses,
            allow_cars=obj_in.allow_cars,
            allow_two_wheelers=obj_in.allow_two_wheelers,
            maximum_vehicle_height=obj_in.maximum_vehicle_height,
            maximum_vehicle_weight=obj_in.maximum_vehicle_weight,
            authorized_only=obj_in.authorized_only,
            working_hours_start=obj_in.working_hours_start,
            working_hours_end=obj_in.working_hours_end,
            remarks=obj_in.remarks,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: GateRule, obj_in: GateRuleUpdate) -> GateRule:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


crud_gate_rule = CRUDGateRule()
