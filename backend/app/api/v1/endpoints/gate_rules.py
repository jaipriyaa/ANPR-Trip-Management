from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.crud.crud_gate import crud_gate
from app.crud.crud_gate_rule import crud_gate_rule
from app.schemas.gate_rule import GateRuleCreate, GateRuleUpdate, GateRuleResponse

router = APIRouter(prefix="/gate-rules", tags=["Gate Rules"])


@router.get("/{gate_id}", response_model=GateRuleResponse, summary="Get operational rules configured for a gate")
def get_gate_rule(
    *,
    db: Session = Depends(get_db),
    gate_id: UUID,
):
    gate = crud_gate.get(db, gate_id=gate_id)
    if not gate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gate with ID {gate_id} not found.",
        )
    rule = crud_gate_rule.get_by_gate(db, gate_id=gate_id)
    if not rule:
        # Return default initialized rule payload if rule not created yet
        rule = crud_gate_rule.create_or_update(db, obj_in=GateRuleCreate(gate_id=gate_id))
    return rule


@router.post("", response_model=GateRuleResponse, status_code=status.HTTP_201_CREATED, summary="Create or configure operational rules for a gate")
def create_gate_rule(
    *,
    db: Session = Depends(get_db),
    rule_in: GateRuleCreate,
):
    gate = crud_gate.get(db, gate_id=rule_in.gate_id)
    if not gate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gate with ID {rule_in.gate_id} not found.",
        )
    return crud_gate_rule.create_or_update(db, obj_in=rule_in)


@router.put("/{gate_id}", response_model=GateRuleResponse, summary="Update operational rules for a gate")
def update_gate_rule(
    *,
    db: Session = Depends(get_db),
    gate_id: UUID,
    rule_in: GateRuleUpdate,
):
    gate = crud_gate.get(db, gate_id=gate_id)
    if not gate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gate with ID {gate_id} not found.",
        )
    rule = crud_gate_rule.get_by_gate(db, gate_id=gate_id)
    if not rule:
        # Create new rule if it doesn't exist
        create_data = GateRuleCreate(gate_id=gate_id, **rule_in.model_dump(exclude_unset=True))
        return crud_gate_rule.create_or_update(db, obj_in=create_data)

    return crud_gate_rule.update(db, db_obj=rule, obj_in=rule_in)
