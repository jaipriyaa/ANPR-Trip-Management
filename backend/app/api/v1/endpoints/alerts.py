from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.dependencies import get_db
from app.services.alert_service import alert_engine
from app.models.alert import Alert
from app.models.alert_delivery import AlertDelivery

router = APIRouter(prefix="/alerts", tags=["Alert Engine & Operational Notifications"])


@router.get("/summary")
def get_alerts_summary(db: Session = Depends(get_db)):
    """Returns dashboard summary counts for active alerts."""
    return alert_engine.get_alerts_summary(db)


@router.get("", response_model=List[Dict[str, Any]])
def list_alerts(
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = Query(None),
    alert_type: Optional[str] = Query(None),
    gate_id: Optional[UUID] = Query(None),
    camera_id: Optional[UUID] = Query(None),
    plate_number: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Lists alerts with rich filtering options."""
    query = db.query(Alert)

    if status_filter:
        query = query.filter(Alert.status == status_filter.upper().strip())

    if severity:
        query = query.filter(Alert.severity == severity.upper().strip())

    if alert_type:
        query = query.filter(Alert.alert_type == alert_type.upper().strip())

    if gate_id:
        query = query.filter(Alert.gate_id == gate_id)

    if camera_id:
        query = query.filter(Alert.camera_id == camera_id)

    if plate_number:
        query = query.filter(Alert.plate_number.ilike(f"%{plate_number.strip()}%"))

    if start_date:
        s_dt = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, tzinfo=timezone.utc)
        query = query.filter(Alert.created_at >= s_dt)

    if end_date:
        e_dt = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59, tzinfo=timezone.utc)
        query = query.filter(Alert.created_at <= e_dt)

    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for a in alerts:
        # Load delivery records
        deliveries = db.query(AlertDelivery).filter(AlertDelivery.alert_id == a.id).all()
        delivery_list = [
            {
                "id": str(d.id),
                "channel": d.channel,
                "status": d.status,
                "attempt_count": d.attempt_count,
                "sent_at": d.sent_at.isoformat() if d.sent_at else None,
                "delivered_at": d.delivered_at.isoformat() if d.delivered_at else None,
                "failure_reason": d.failure_reason
            }
            for d in deliveries
        ]

        result.append({
            "id": str(a.id),
            "alert_key": a.alert_key,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "status": a.status,
            "trip_id": str(a.trip_id) if a.trip_id else None,
            "movement_id": str(a.movement_id) if a.movement_id else None,
            "gate_id": str(a.gate_id) if a.gate_id else None,
            "camera_id": str(a.camera_id) if a.camera_id else None,
            "plate_number": a.plate_number,
            "vehicle_type": a.vehicle_type,
            "message": a.message,
            "reason": a.reason,
            "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None,
            "resolution_reason": a.resolution_reason,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "deliveries": delivery_list
        })

    return result


@router.get("/{alert_id}")
def get_alert_by_id(alert_id: UUID, db: Session = Depends(get_db)):
    """Gets detailed record for a specific alert."""
    alert = db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")

    deliveries = db.query(AlertDelivery).filter(AlertDelivery.alert_id == alert.id).all()
    delivery_list = [
        {
            "id": str(d.id),
            "channel": d.channel,
            "status": d.status,
            "attempt_count": d.attempt_count,
            "sent_at": d.sent_at.isoformat() if d.sent_at else None,
            "delivered_at": d.delivered_at.isoformat() if d.delivered_at else None,
            "failure_reason": d.failure_reason
        }
        for d in deliveries
    ]

    return {
        "id": str(alert.id),
        "alert_key": alert.alert_key,
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "status": alert.status,
        "trip_id": str(alert.trip_id) if alert.trip_id else None,
        "movement_id": str(alert.movement_id) if alert.movement_id else None,
        "gate_id": str(alert.gate_id) if alert.gate_id else None,
        "camera_id": str(alert.camera_id) if alert.camera_id else None,
        "plate_number": alert.plate_number,
        "vehicle_type": alert.vehicle_type,
        "message": alert.message,
        "reason": alert.reason,
        "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
        "resolution_reason": alert.resolution_reason,
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
        "deliveries": delivery_list
    }


@router.post("/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: UUID, reason: Optional[str] = None, db: Session = Depends(get_db)):
    """Acknowledges an open alert (OPEN -> ACKNOWLEDGED)."""
    res = alert_engine.transition_alert_status(db, alert_id=alert_id, new_status="ACKNOWLEDGED", changed_by="SECURITY_OPERATOR", reason=reason or "Operator Acknowledged Alert")
    return {"status": "success", "alert_id": str(res.id), "new_status": res.status}


@router.post("/{alert_id}/resolve")
def resolve_alert(alert_id: UUID, reason: Optional[str] = None, db: Session = Depends(get_db)):
    """Resolves an alert (OPEN/ACKNOWLEDGED -> RESOLVED)."""
    res = alert_engine.transition_alert_status(db, alert_id=alert_id, new_status="RESOLVED", changed_by="SECURITY_OPERATOR", reason=reason or "Manual Resolution")
    return {"status": "success", "alert_id": str(res.id), "new_status": res.status}


@router.post("/{alert_id}/dismiss")
def dismiss_alert(alert_id: UUID, reason: Optional[str] = None, db: Session = Depends(get_db)):
    """Dismisses an alert (OPEN/ACKNOWLEDGED -> DISMISSED)."""
    res = alert_engine.transition_alert_status(db, alert_id=alert_id, new_status="DISMISSED", changed_by="SECURITY_OPERATOR", reason=reason or "Alert Dismissed")
    return {"status": "success", "alert_id": str(res.id), "new_status": res.status}
