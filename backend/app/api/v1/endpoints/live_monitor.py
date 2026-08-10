from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.live_monitor_service import live_monitor_service
from app.crud.crud_vehicle_movement import crud_vehicle_movement

router = APIRouter(prefix="/live", tags=["Live Gate Control Room Dashboard"])


@router.get("/dashboard", summary="Get aggregated live control room state for real-time polling")
def get_live_dashboard(
    db: Session = Depends(get_db),
):
    return live_monitor_service.get_full_dashboard(db)


@router.get("/events", summary="Get recent live timeline events")
def get_live_events(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
):
    return live_monitor_service.get_live_timeline(db, limit=limit)


@router.get("/vehicles", summary="Get vehicles currently inside the facility")
def get_live_vehicles_inside(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    items, total = crud_vehicle_movement.get_current_inside(db, skip=skip, limit=limit)
    return {"total": total, "items": items}


@router.get("/trips", summary="Get active scheduled trips status")
def get_live_trips(
    db: Session = Depends(get_db),
):
    return live_monitor_service.get_active_trips(db)


@router.get("/alerts", summary="Get active security & operational alerts")
def get_live_alerts(
    db: Session = Depends(get_db),
):
    return live_monitor_service.get_active_alerts(db)
