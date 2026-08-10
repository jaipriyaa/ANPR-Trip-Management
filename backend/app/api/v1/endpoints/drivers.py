from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.master_data_service import master_data_service
from app.schemas.driver import (
    DriverCreate, DriverUpdate, DriverResponse, DriverPaginatedResponse
)

router = APIRouter(prefix="/drivers", tags=["Driver Master"])


@router.post("", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
def create_driver(
    payload: DriverCreate,
    db: Session = Depends(get_db)
):
    """Register a new driver with license and transporter details."""
    return master_data_service.create_driver(db, obj_in=payload)


@router.get("", response_model=DriverPaginatedResponse)
def list_drivers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search driver name, license, or phone"),
    transporter_id: Optional[UUID] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """List drivers with search and pagination."""
    items, total = master_data_service.get_drivers(
        db, skip=skip, limit=limit, search=search, transporter_id=transporter_id, is_active=is_active
    )
    return DriverPaginatedResponse(total=total, items=items)


@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(
    driver_id: UUID,
    db: Session = Depends(get_db)
):
    """Get driver details by ID."""
    return master_data_service.get_driver(db, driver_id=driver_id)


@router.put("/{driver_id}", response_model=DriverResponse)
def update_driver(
    driver_id: UUID,
    payload: DriverUpdate,
    db: Session = Depends(get_db)
):
    """Update driver contact info or transporter association."""
    return master_data_service.update_driver(db, driver_id=driver_id, obj_in=payload)


@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_driver(
    driver_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a driver record."""
    master_data_service.delete_driver(db, driver_id=driver_id)
    return None
