from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.crud.crud_vehicle_movement import crud_vehicle_movement
from app.services.entry_exit_service import entry_exit_service
from app.schemas.vehicle_movement import (
    VehicleMovementCreate,
    VehicleMovementUpdate,
    VehicleMovementResponse,
    VehicleMovementPaginatedResponse,
    LiveMovementsSummaryResponse,
)

router = APIRouter(prefix="/movements", tags=["Vehicle Movements & Entry/Exit Engine"])


@router.get("", response_model=VehicleMovementPaginatedResponse, summary="Get all vehicle movement logs with search & filters")
def get_movements(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None, description="Search by plate number, vehicle type, or purpose"),
    movement_status: Optional[str] = Query(None, description="Filter by INSIDE or OUTSIDE"),
    vehicle_status: Optional[str] = Query(None, description="Filter by ENTERED or EXITED"),
    gate_id: Optional[UUID] = Query(None, description="Filter by entry/exit gate ID"),
):
    items, total = crud_vehicle_movement.get_multi(
        db,
        skip=skip,
        limit=limit,
        search=search,
        movement_status=movement_status,
        vehicle_status=vehicle_status,
        gate_id=gate_id,
    )
    return {"total": total, "items": items}


@router.get("/current", response_model=VehicleMovementPaginatedResponse, summary="Get all vehicles currently INSIDE the facility")
def get_current_vehicles_inside(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    items, total = crud_vehicle_movement.get_current_inside(db, skip=skip, limit=limit)
    return {"total": total, "items": items}


@router.get("/history", response_model=VehicleMovementPaginatedResponse, summary="Get completed entry/exit movement history")
def get_movement_history(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    items, total = crud_vehicle_movement.get_history(db, skip=skip, limit=limit)
    return {"total": total, "items": items}


@router.get("/summary", response_model=LiveMovementsSummaryResponse, summary="Get live real-time movements summary cards")
def get_movements_summary(
    db: Session = Depends(get_db),
):
    return entry_exit_service.get_live_summary(db)


@router.get("/{plate}", response_model=VehicleMovementPaginatedResponse, summary="Get movement history for a specific plate number")
def get_movement_history_by_plate(
    plate: str,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    items, total = crud_vehicle_movement.get_by_plate_history(db, recognized_plate=plate, skip=skip, limit=limit)
    return {"total": total, "items": items}


@router.post("", response_model=VehicleMovementResponse, status_code=status.HTTP_201_CREATED, summary="Create a manual vehicle movement entry")
def create_movement(
    *,
    db: Session = Depends(get_db),
    movement_in: VehicleMovementCreate,
):
    movement = crud_vehicle_movement.create(db, obj_in=movement_in)
    return crud_vehicle_movement._to_response(db, movement)


@router.put("/{movement_id}", response_model=VehicleMovementResponse, summary="Update an existing vehicle movement record")
def update_movement(
    *,
    db: Session = Depends(get_db),
    movement_id: UUID,
    movement_in: VehicleMovementUpdate,
):
    movement = crud_vehicle_movement.get(db, movement_id=movement_id)
    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle movement record '{movement_id}' not found.",
        )
    updated = crud_vehicle_movement.update(db, db_obj=movement, obj_in=movement_in)
    return crud_vehicle_movement._to_response(db, updated)
