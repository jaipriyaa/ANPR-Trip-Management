from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.master_data_service import master_data_service
from app.schemas.vehicle import (
    VehicleCreate, VehicleUpdate, VehicleResponse, VehiclePaginatedResponse
)

router = APIRouter(prefix="/vehicles", tags=["Vehicle Master"])


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    payload: VehicleCreate,
    db: Session = Depends(get_db)
):
    """Register a new vehicle with automatic primary plate association."""
    return master_data_service.create_vehicle(db, obj_in=payload)


@router.get("", response_model=VehiclePaginatedResponse)
def list_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search vehicle number or make model"),
    transporter_id: Optional[UUID] = Query(None),
    vehicle_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_blacklisted: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """List fleet vehicles with search, filtering, and pagination."""
    items, total = master_data_service.get_vehicles(
        db, skip=skip, limit=limit, search=search,
        transporter_id=transporter_id, vehicle_type=vehicle_type,
        is_active=is_active, is_blacklisted=is_blacklisted
    )
    return VehiclePaginatedResponse(total=total, items=items)


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: UUID,
    db: Session = Depends(get_db)
):
    """Get vehicle details including registered plates and transporter company."""
    return master_data_service.get_vehicle(db, vehicle_id=vehicle_id)


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: UUID,
    payload: VehicleUpdate,
    db: Session = Depends(get_db)
):
    """Update vehicle specifications or transporter assignment."""
    return master_data_service.update_vehicle(db, vehicle_id=vehicle_id, obj_in=payload)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a vehicle record."""
    master_data_service.delete_vehicle(db, vehicle_id=vehicle_id)
    return None
