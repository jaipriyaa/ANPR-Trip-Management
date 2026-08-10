from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.master_data_service import master_data_service
from app.schemas.transporter import (
    TransporterCreate, TransporterUpdate, TransporterResponse, TransporterPaginatedResponse
)

router = APIRouter(prefix="/transporters", tags=["Transporter Master"])


@router.post("", response_model=TransporterResponse, status_code=status.HTTP_201_CREATED)
def create_transporter(
    payload: TransporterCreate,
    db: Session = Depends(get_db)
):
    """Register a new transporter fleet company."""
    return master_data_service.create_transporter(db, obj_in=payload)


@router.get("", response_model=TransporterPaginatedResponse)
def list_transporters(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search company name, code, or contact person"),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """List transporters with search, filtering, and pagination."""
    items, total = master_data_service.get_transporters(
        db, skip=skip, limit=limit, search=search, is_active=is_active
    )
    return TransporterPaginatedResponse(total=total, items=items)


@router.get("/{transporter_id}", response_model=TransporterResponse)
def get_transporter(
    transporter_id: UUID,
    db: Session = Depends(get_db)
):
    """Retrieve details of a specific transporter."""
    return master_data_service.get_transporter(db, transporter_id=transporter_id)


@router.put("/{transporter_id}", response_model=TransporterResponse)
def update_transporter(
    transporter_id: UUID,
    payload: TransporterUpdate,
    db: Session = Depends(get_db)
):
    """Update existing transporter information."""
    return master_data_service.update_transporter(db, transporter_id=transporter_id, obj_in=payload)


@router.delete("/{transporter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transporter(
    transporter_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove a transporter from the system."""
    master_data_service.delete_transporter(db, transporter_id=transporter_id)
    return None
