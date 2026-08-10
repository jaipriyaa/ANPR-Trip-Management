from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.crud.crud_gate import crud_gate
from app.schemas.gate import GateCreate, GateUpdate, GateResponse, GatePaginatedResponse

router = APIRouter(prefix="/gates", tags=["Gates"])


@router.get("", response_model=GatePaginatedResponse, summary="Get all gates with search & pagination")
def get_gates(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None, description="Search by gate code, name, or location"),
    gate_type: Optional[str] = Query(None, description="Filter by Entry, Exit, or Entry & Exit"),
    status: Optional[str] = Query(None, description="Filter by ACTIVE or INACTIVE"),
    is_active: Optional[bool] = Query(None),
):
    items, total = crud_gate.get_multi(
        db,
        skip=skip,
        limit=limit,
        search=search,
        gate_type=gate_type,
        status=status,
        is_active=is_active,
    )
    return {"total": total, "items": items}


@router.post("", response_model=GateResponse, status_code=status.HTTP_201_CREATED, summary="Create a new gate")
def create_gate(
    *,
    db: Session = Depends(get_db),
    gate_in: GateCreate,
):
    existing = crud_gate.get_by_code(db, gate_code=gate_in.gate_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Gate with code '{gate_in.gate_code}' already exists.",
        )
    return crud_gate.create(db, obj_in=gate_in)


@router.get("/{gate_id}", response_model=GateResponse, summary="Get gate by ID")
def get_gate(
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
    gate.camera_count = len(gate.cameras) if gate.cameras else 0
    return gate


@router.put("/{gate_id}", response_model=GateResponse, summary="Update gate details")
def update_gate(
    *,
    db: Session = Depends(get_db),
    gate_id: UUID,
    gate_in: GateUpdate,
):
    gate = crud_gate.get(db, gate_id=gate_id)
    if not gate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gate with ID {gate_id} not found.",
        )
    if gate_in.gate_code and gate_in.gate_code.upper().strip() != gate.gate_code:
        existing = crud_gate.get_by_code(db, gate_code=gate_in.gate_code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Gate with code '{gate_in.gate_code}' already exists.",
            )
    return crud_gate.update(db, db_obj=gate, obj_in=gate_in)


@router.delete("/{gate_id}", status_code=status.HTTP_200_OK, summary="Delete a gate")
def delete_gate(
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
    crud_gate.remove(db, gate_id=gate_id)
    return {"success": True, "message": f"Gate '{gate.gate_code}' deleted successfully."}
