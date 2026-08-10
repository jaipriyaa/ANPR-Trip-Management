from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.crud.crud_scheduled_trip import crud_scheduled_trip
from app.services.trip_service import trip_service
from app.schemas.scheduled_trip import (
    ScheduledTripCreate,
    ScheduledTripUpdate,
    TripStatusUpdate,
    TripApprovalUpdate,
    ScheduledTripResponse,
    ScheduledTripPaginatedResponse,
    TripDashboardSummaryResponse,
)

router = APIRouter(prefix="/trips", tags=["Industrial Vehicle Trip Management Engine"])


@router.get("", response_model=ScheduledTripPaginatedResponse, summary="Get all scheduled trips with search & status filters")
def get_trips(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None, description="Search by trip number, purpose, material, or destination"),
    trip_status: Optional[str] = Query(None, description="Filter by SCHEDULED, WAITING, INSIDE, COMPLETED, CANCELLED"),
    approval_status: Optional[str] = Query(None, description="Filter by PENDING, APPROVED, REJECTED"),
):
    items, total = crud_scheduled_trip.get_multi(
        db,
        skip=skip,
        limit=limit,
        search=search,
        trip_status=trip_status,
        approval_status=approval_status,
    )
    return {"total": total, "items": items}


@router.get("/dashboard", response_model=TripDashboardSummaryResponse, summary="Get trip metrics dashboard summary")
def get_trip_dashboard(
    db: Session = Depends(get_db),
):
    return trip_service.get_dashboard_summary(db)


@router.get("/active", response_model=ScheduledTripPaginatedResponse, summary="Get active trips (SCHEDULED, WAITING, INSIDE)")
def get_active_trips(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    items, total = crud_scheduled_trip.get_active(db, skip=skip, limit=limit)
    return {"total": total, "items": items}


@router.get("/completed", response_model=ScheduledTripPaginatedResponse, summary="Get completed trips history")
def get_completed_trips(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    items, total = crud_scheduled_trip.get_completed(db, skip=skip, limit=limit)
    return {"total": total, "items": items}


@router.get("/pending", response_model=ScheduledTripPaginatedResponse, summary="Get pending approval trips")
def get_pending_trips(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    items, total = crud_scheduled_trip.get_pending(db, skip=skip, limit=limit)
    return {"total": total, "items": items}


@router.get("/{trip_id}", response_model=ScheduledTripResponse, summary="Get detailed trip record by ID with status history")
def get_trip(
    trip_id: UUID,
    db: Session = Depends(get_db),
):
    trip = crud_scheduled_trip.get(db, trip_id)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheduled trip not found")
    return crud_scheduled_trip._to_response(db, trip)


@router.post("", response_model=ScheduledTripResponse, status_code=status.HTTP_201_CREATED, summary="Create & schedule a new vehicle trip")
def create_trip(
    *,
    db: Session = Depends(get_db),
    trip_in: ScheduledTripCreate,
):
    trip_service.validate_trip_creation(db, trip_in)
    trip = crud_scheduled_trip.create(db, obj_in=trip_in)
    return crud_scheduled_trip._to_response(db, trip)


@router.put("/{trip_id}", response_model=ScheduledTripResponse, summary="Update an existing scheduled trip")
def update_trip(
    *,
    db: Session = Depends(get_db),
    trip_id: UUID,
    trip_in: ScheduledTripUpdate,
):
    trip = crud_scheduled_trip.get(db, trip_id)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheduled trip not found")
    
    if trip.trip_status in ["COMPLETED", "CANCELLED"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Completed or Cancelled trips cannot be modified.")

    updated = crud_scheduled_trip.update(db, db_obj=trip, obj_in=trip_in)
    return crud_scheduled_trip._to_response(db, updated)


@router.delete("/{trip_id}", status_code=status.HTTP_200_OK, summary="Cancel or delete a scheduled trip")
def cancel_trip(
    trip_id: UUID,
    db: Session = Depends(get_db),
):
    trip = crud_scheduled_trip.get(db, trip_id)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheduled trip not found")
    
    prev_status = trip.trip_status
    trip.trip_status = "CANCELLED"
    trip.approval_status = "REJECTED"
    db.add(trip)
    db.commit()

    crud_scheduled_trip.record_status_change(
        db,
        trip_id=trip.id,
        previous_status=prev_status,
        current_status="CANCELLED",
        changed_by="USER_OPERATOR",
        remarks="Trip Cancelled by User Dispatcher",
    )
    return {"message": f"Trip '{trip.trip_number}' cancelled successfully."}


@router.post("/{trip_id}/approve", response_model=ScheduledTripResponse, summary="Approve trip entry authorization")
def approve_trip(
    trip_id: UUID,
    body: Optional[TripApprovalUpdate] = None,
    db: Session = Depends(get_db),
):
    remarks = body.remarks if body else None
    approved_trip = trip_service.approve_trip(db, trip_id=trip_id, remarks=remarks)
    return crud_scheduled_trip._to_response(db, approved_trip)


@router.post("/{trip_id}/reject", response_model=ScheduledTripResponse, summary="Reject trip entry authorization")
def reject_trip(
    trip_id: UUID,
    body: Optional[TripApprovalUpdate] = None,
    db: Session = Depends(get_db),
):
    remarks = body.remarks if body else None
    rejected_trip = trip_service.reject_trip(db, trip_id=trip_id, remarks=remarks)
    return crud_scheduled_trip._to_response(db, rejected_trip)


@router.put("/{trip_id}/status", response_model=ScheduledTripResponse, summary="Update trip status with status history logging")
def update_trip_status(
    *,
    db: Session = Depends(get_db),
    trip_id: UUID,
    status_in: TripStatusUpdate,
):
    trip = crud_scheduled_trip.get(db, trip_id)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheduled trip not found")

    prev_status = trip.trip_status
    trip.trip_status = status_in.trip_status
    if status_in.remarks:
        trip.remarks = status_in.remarks

    db.add(trip)
    db.commit()
    db.refresh(trip)

    crud_scheduled_trip.record_status_change(
        db,
        trip_id=trip.id,
        previous_status=prev_status,
        current_status=status_in.trip_status,
        changed_by=status_in.changed_by,
        remarks=status_in.remarks,
    )
    return crud_scheduled_trip._to_response(db, trip)
