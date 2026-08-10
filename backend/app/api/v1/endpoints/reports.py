from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.reporting_service import reporting_service

router = APIRouter(prefix="/reports", tags=["Reporting & Daily Aggregation"])


@router.get("/daily-summary")
def get_daily_summary(
    target_date: Optional[date] = Query(None, description="Target date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Executes or fetches idempotent daily gate aggregation summary."""
    return reporting_service.run_daily_aggregation(db, target_date=target_date)


@router.get("/vehicles-inside")
def get_vehicles_currently_inside(db: Session = Depends(get_db)):
    """Returns reliable calculation of vehicles currently inside plant."""
    return reporting_service.get_vehicles_currently_inside(db)


@router.get("/entry-exit")
def get_entry_exit_register(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    gate_id: Optional[UUID] = Query(None),
    plate_number: Optional[str] = Query(None),
    transporter_id: Optional[UUID] = Query(None),
    vehicle_type: Optional[str] = Query(None),
    direction: Optional[str] = Query(None),
    authorization: Optional[str] = Query(None),
    trip_status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Produces filtered entry/exit register report."""
    return reporting_service.get_entry_exit_register(
        db=db,
        start_date=start_date,
        end_date=end_date,
        gate_id=gate_id,
        plate_number=plate_number,
        transporter_id=transporter_id,
        vehicle_type=vehicle_type,
        direction=direction,
        authorization=authorization,
        trip_status=trip_status
    )


@router.get("/dwell-time")
def get_dwell_time_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    gate_id: Optional[UUID] = Query(None),
    transporter_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db)
):
    """Calculates average dwell time for completed trips."""
    return reporting_service.get_average_dwell_time(
        db=db,
        start_date=start_date,
        end_date=end_date,
        gate_id=gate_id,
        transporter_id=transporter_id
    )


@router.get("/transporters")
def get_vehicles_by_transporter(
    target_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Aggregates vehicle metrics grouped by transporter."""
    return reporting_service.get_vehicles_by_transporter(db, target_date=target_date)


@router.get("/gates")
def get_vehicles_by_gate(
    target_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Aggregates metrics grouped by gate."""
    return reporting_service.get_vehicles_by_gate(db, target_date=target_date)


@router.get("/arrival-status")
def get_arrival_status_report(
    target_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Calculates expected vs actual arrival metrics."""
    return reporting_service.get_arrival_status_report(db, target_date=target_date)


@router.get("/unauthorized")
def get_unauthorized_attempts(
    target_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Aggregates gate decisions for unauthorized attempts."""
    return reporting_service.get_unauthorized_attempts(db, target_date=target_date)


@router.get("/correction-rate")
def get_plate_correction_rate(
    target_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Calculates manual plate correction rate."""
    return reporting_service.get_plate_correction_rate(db, target_date=target_date)


@router.get("/repeat-visitors")
def get_repeat_visitors(
    target_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Identifies plates appearing more than once in the selected period."""
    return reporting_service.get_repeat_visitors(db, target_date=target_date)


@router.get("/overstay")
def get_overstay_report(db: Session = Depends(get_db)):
    """Reports active and historical overstaying vehicles."""
    return reporting_service.get_overstay_report(db)


@router.get("/camera-health")
def get_camera_health(db: Session = Depends(get_db)):
    """Reports camera health, uptime, and status."""
    return reporting_service.get_camera_health(db)


@router.get("/accuracy")
def get_recognition_accuracy():
    """Returns accuracy metrics or INSUFFICIENT_GROUND_TRUTH."""
    return reporting_service.get_recognition_accuracy()
