from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.admin_service import admin_service
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.system_setting import SystemSetting

router = APIRouter(prefix="/admin", tags=["Enterprise Administration & System Health"])


@router.get("/dashboard", summary="Get Analytics Dashboard KPIs & Interactive Chart Data")
def get_analytics_dashboard(
    db: Session = Depends(get_db),
):
    return admin_service.get_analytics_dashboard(db)


@router.get("/reports", summary="Generate Industrial Reports & Data Exports (JSON or CSV)")
def get_reports(
    db: Session = Depends(get_db),
    report_type: str = Query("Daily Vehicle Report", description="Type of report"),
    export_format: str = Query("JSON", description="JSON or CSV"),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
):
    data = admin_service.generate_report(
        db,
        report_type=report_type,
        export_format=export_format,
        date_from=date_from,
        date_to=date_to,
    )
    if export_format.upper() == "CSV":
        return Response(
            content=data["csv_data"],
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=report_{report_type.replace(' ', '_')}.csv"}
        )
    return data


@router.get("/users", summary="Get all registered platform users")
def get_users(
    db: Session = Depends(get_db),
):
    users = db.query(User).all()
    return [{
        "id": str(u.id),
        "username": u.username,
        "email": u.email,
        "full_name": u.full_name,
        "role": u.role,
        "is_active": u.is_active,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    } for u in users]


@router.post("/users", status_code=status.HTTP_201_CREATED, summary="Create a new platform user")
def create_user(
    user_in: dict,
    db: Session = Depends(get_db),
):
    username = user_in.get("username", "").strip()
    email = user_in.get("email", "").strip()
    if not username or not email:
        raise HTTPException(status_code=400, detail="Username and email are required.")

    existing = db.query(User).filter(or_(User.username == username, User.email == email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with username or email already exists.")

    u = User(
        username=username,
        email=email,
        full_name=user_in.get("full_name", username),
        role=user_in.get("role", "VIEWER"),
        hashed_password="hashed_placeholder_secret",
        is_active=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)

    admin_service.record_audit(db, user_id=u.id, action="CREATE_USER", entity_type="USER", entity_id=str(u.id), details={"username": username, "role": u.role})

    return {"id": str(u.id), "username": u.username, "email": u.email, "role": u.role}


@router.get("/roles", summary="Get configurable RBAC Roles & Module Permissions Matrix")
def get_roles_matrix():
    return [
        {
            "role": "Administrator",
            "description": "Full access to all platform modules, configuration, and security controls.",
            "permissions": ["Vehicle Master", "Trips", "Gate Management", "Reports", "Dashboard", "Alerts", "Camera Settings", "Users", "System Settings"],
        },
        {
            "role": "Security Officer",
            "description": "Gate monitoring, trip approval, vehicle inspection, and live security alerts.",
            "permissions": ["Vehicle Master", "Trips", "Gate Management", "Dashboard", "Alerts"],
        },
        {
            "role": "Gate Operator",
            "description": "Live gate monitoring, vehicle recognition, and entry/exit verification.",
            "permissions": ["Vehicle Master", "Gate Management", "Dashboard", "Alerts"],
        },
        {
            "role": "Supervisor",
            "description": "Operational analytics, reports generation, trip scheduling, and auditing.",
            "permissions": ["Trips", "Reports", "Dashboard", "Alerts"],
        },
        {
            "role": "Viewer",
            "description": "Read-only access to live gate dashboard and public statistics.",
            "permissions": ["Dashboard"],
        },
    ]


@router.get("/audit", summary="Get Security Audit Logs trail")
def get_audit_logs(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    total = db.query(AuditLog).count()
    return {
        "total": total,
        "items": [{
            "id": str(l.id),
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "details": l.details,
            "ip_address": l.ip_address or "127.0.0.1",
            "created_at": l.created_at.isoformat() if l.created_at else None,
        } for l in logs]
    }


@router.get("/camera-health", summary="Get Camera Streams Health & Latency Monitoring")
def get_camera_health(
    db: Session = Depends(get_db),
):
    return admin_service.get_camera_health_summary(db)


@router.get("/model-health", summary="Get AI Model Health & GPU/CPU Performance Metrics")
def get_model_health(
    db: Session = Depends(get_db),
):
    return admin_service.get_model_health_summary(db)


@router.get("/settings", summary="Get Key-Value System Settings")
def get_settings(
    db: Session = Depends(get_db),
):
    return admin_service.get_system_settings(db)


@router.put("/settings", summary="Update System Settings")
def update_settings(
    settings_in: dict,
    db: Session = Depends(get_db),
):
    for k, v in settings_in.items():
        s = db.query(SystemSetting).filter(SystemSetting.key == k).first()
        if s:
            s.value = str(v)
        else:
            s = SystemSetting(key=k, value=str(v), description=f"Updated setting {k}")
            db.add(s)
    db.commit()
    admin_service.record_audit(db, user_id=None, action="UPDATE_SETTINGS", entity_type="SYSTEM", details=settings_in)
    return {"message": "System settings updated successfully.", "settings": settings_in}


@router.get("/retention/status", summary="Get Data Retention & Archival Engine Status")
def get_retention_status(
    db: Session = Depends(get_db),
):
    from app.core.config import settings
    from app.models.archive_job import ArchiveJob

    last_job = db.query(ArchiveJob).order_by(ArchiveJob.started_at.desc()).first()
    return {
        "retention_policy": {
            "detection_retention_days": settings.DETECTION_RETENTION_DAYS,
            "plate_prediction_retention_days": settings.PLATE_PREDICTION_RETENTION_DAYS,
            "alert_retention_days": settings.ALERT_RETENTION_DAYS,
            "audit_log_retention_days": settings.AUDIT_LOG_RETENTION_DAYS,
            "camera_health_retention_days": settings.CAMERA_HEALTH_RETENTION_DAYS,
            "dry_run_default": settings.RETENTION_DRY_RUN
        },
        "last_execution": {
            "job_id": str(last_job.id) if last_job else None,
            "job_name": last_job.job_name if last_job else None,
            "status": last_job.status if last_job else "NO_JOBS_RUN",
            "records_archived": last_job.records_archived if last_job else 0,
            "started_at": last_job.started_at.isoformat() if last_job and last_job.started_at else None,
            "completed_at": last_job.completed_at.isoformat() if last_job and last_job.completed_at else None,
            "error_message": last_job.error_message if last_job else None,
        }
    }


@router.post("/retention/run", summary="Trigger Data Retention & Archival Job")
def run_retention_job(
    dry_run: Optional[bool] = Query(None, description="Force dry_run mode (True = no records deleted)"),
    db: Session = Depends(get_db),
):
    from app.services.retention_service import retention_service
    return retention_service.run_retention_job(db, dry_run=dry_run)
