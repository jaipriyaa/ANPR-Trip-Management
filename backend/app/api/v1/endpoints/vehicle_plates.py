from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.master_data_service import master_data_service
from app.schemas.vehicle_plate import (
    VehiclePlateCreate, VehiclePlateResponse, VehiclePlatePaginatedResponse
)

router = APIRouter(prefix="/vehicle-plates", tags=["Vehicle Plate Master"])


@router.post("", response_model=VehiclePlateResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle_plate(
    payload: VehiclePlateCreate,
    db: Session = Depends(get_db)
):
    """Add a new registration plate mapping to a vehicle (e.g. trailer plate)."""
    return master_data_service.create_plate(db, obj_in=payload)


@router.get("", response_model=VehiclePlatePaginatedResponse)
def list_vehicle_plates(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search plate number"),
    vehicle_id: Optional[UUID] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """List vehicle registration plates with search and filters."""
    items, total = master_data_service.get_plates(
        db, skip=skip, limit=limit, search=search, vehicle_id=vehicle_id, is_active=is_active
    )
    return VehiclePlatePaginatedResponse(total=total, items=items)


@router.delete("/{plate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle_plate(
    plate_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a vehicle plate record."""
    master_data_service.delete_plate(db, plate_id=plate_id)
    return None
