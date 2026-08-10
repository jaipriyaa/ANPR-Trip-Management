import logging
import json
from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from fastapi import HTTPException, status

from app.models.alert import Alert
from app.models.alert_delivery import AlertDelivery
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class AlertEngine:
    # Default severity mapping per alert type
    SEVERITY_MAP = {
        "LATE_ARRIVAL": "WARNING",
        "OVERSTAY": "WARNING",
        "UNAUTHORIZED_VEHICLE": "CRITICAL",
        "MANUAL_REVIEW_REQUIRED": "WARNING",
        "CAMERA_OFFLINE": "CRITICAL",
        "CAMERA_DEGRADED": "WARNING",
        "INFERENCE_FAILURE": "CRITICAL",
    }

    # Allowed alert lifecycle transitions
    VALID_LIFECYCLE = {
        "OPEN": {"ACKNOWLEDGED", "RESOLVED", "DISMISSED"},
        "ACKNOWLEDGED": {"RESOLVED", "DISMISSED"},
        "RESOLVED": set(),  # Terminal state
        "DISMISSED": set(),  # Terminal state
    }

    def generate_alert_key(
        self,
        alert_type: str,
        trip_id: Optional[UUID] = None,
        movement_id: Optional[UUID] = None,
        gate_id: Optional[UUID] = None,
        camera_id: Optional[UUID] = None,
        plate_number: Optional[str] = None
    ) -> str:
        """Generates a deterministic deduplication key for alert conditions."""
        if trip_id:
            return f"{alert_type}:TRIP:{trip_id}"
        elif movement_id:
            return f"{alert_type}:MOV:{movement_id}"
        elif camera_id:
            return f"{alert_type}:CAM:{camera_id}"
        elif gate_id and plate_number:
            return f"{alert_type}:GATE:{gate_id}:PLATE:{plate_number.upper().strip()}"
        elif plate_number:
            return f"{alert_type}:PLATE:{plate_number.upper().strip()}"
        else:
            return f"{alert_type}:GENERIC:{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    def create_alert(
        self,
        db: Session,
        alert_type: str,
        message: str,
        reason: Optional[str] = None,
        severity: Optional[str] = None,
        trip_id: Optional[UUID] = None,
        movement_id: Optional[UUID] = None,
        gate_id: Optional[UUID] = None,
        camera_id: Optional[UUID] = None,
        plate_number: Optional[str] = None,
        vehicle_type: Optional[str] = None,
        metadata_dict: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Alert, bool]:
        """Idempotently creates or retrieves an active alert using deterministic deduplication key.
        
        Returns: (Alert, created_new_bool)
        """
        sev = severity or self.SEVERITY_MAP.get(alert_type, "WARNING")
        key = self.generate_alert_key(
            alert_type=alert_type,
            trip_id=trip_id,
            movement_id=movement_id,
            gate_id=gate_id,
            camera_id=camera_id,
            plate_number=plate_number
        )

        # 1. Check if an active (OPEN or ACKNOWLEDGED) alert with the exact key exists
        existing = (
            db.query(Alert)
            .filter(
                Alert.alert_key == key,
                Alert.status.in_(["OPEN", "ACKNOWLEDGED"])
            )
            .first()
        )
        if existing:
            logger.info(f"AlertEngine: Suppressed duplicate alert creation for key '{key}'. (ID: {existing.id})")
            return existing, False

        # 2. Create new Alert
        meta_str = json.dumps(metadata_dict) if metadata_dict else None
        new_alert = Alert(
            alert_key=key,
            alert_type=alert_type,
            severity=sev,
            status="OPEN",
            trip_id=trip_id,
            movement_id=movement_id,
            gate_id=gate_id,
            camera_id=camera_id,
            plate_number=plate_number.upper().strip() if plate_number else None,
            vehicle_type=vehicle_type,
            message=message,
            reason=reason,
            metadata_json=meta_str,
        )
        db.add(new_alert)
        db.commit()
        db.refresh(new_alert)

        # 3. Create AlertDelivery records for delivery channels
        for channel in ["DASHBOARD", "EMAIL", "WEBHOOK"]:
            delivery = AlertDelivery(
                alert_id=new_alert.id,
                channel=channel,
                status="DELIVERED" if channel == "DASHBOARD" else "PENDING",
                attempt_count=1,
                sent_at=datetime.now(timezone.utc) if channel == "DASHBOARD" else None,
                delivered_at=datetime.now(timezone.utc) if channel == "DASHBOARD" else None
            )
            db.add(delivery)

        # 4. Log Audit Log
        audit = AuditLog(
            user_id=None,
            action=f"ALERT_CREATED_{alert_type}",
            entity_type="Alert",
            entity_id=str(new_alert.id),
            details={"message": message, "key": key},
            ip_address="SYSTEM_ENGINE"
        )
        db.add(audit)
        db.commit()

        logger.info(f"AlertEngine: Created new alert '{alert_type}' (ID: {new_alert.id}, Key: '{key}').")
        return new_alert, True

    def transition_alert_status(
        self,
        db: Session,
        alert_id: UUID,
        new_status: str,
        changed_by: str = "USER_OPERATOR",
        reason: Optional[str] = None
    ) -> Alert:
        """Transitions alert status along strict lifecycle rules."""
        alert = db.get(Alert, alert_id)
        if not alert:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")

        current_status = alert.status or "OPEN"
        if new_status == current_status:
            return alert

        allowed = self.VALID_LIFECYCLE.get(current_status, set())
        if new_status not in allowed:
            err_msg = f"Invalid alert status transition from {current_status} to {new_status}."
            logger.error(f"AlertEngine: {err_msg}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

        alert.status = new_status
        now = datetime.now(timezone.utc)
        if new_status in ["RESOLVED", "DISMISSED"]:
            alert.resolved_at = now
            if reason:
                alert.resolution_reason = reason

        db.add(alert)

        # Audit trail
        audit = AuditLog(
            user_id=None,
            action=f"ALERT_STATUS_{new_status}",
            entity_type="Alert",
            entity_id=str(alert.id),
            details={"previous_status": current_status, "new_status": new_status, "reason": reason or "N/A"},
            ip_address=changed_by
        )
        db.add(audit)
        db.commit()
        db.refresh(alert)
        return alert

    def resolve_overstay_by_trip(self, db: Session, trip_id: UUID, reason: str = "Vehicle exited plant") -> Optional[Alert]:
        """Auto-resolves open OVERSTAY alert when trip completes on vehicle exit."""
        alert = (
            db.query(Alert)
            .filter(
                Alert.trip_id == trip_id,
                Alert.alert_type == "OVERSTAY",
                Alert.status.in_(["OPEN", "ACKNOWLEDGED"])
            )
            .first()
        )
        if alert:
            return self.transition_alert_status(db, alert.id, "RESOLVED", changed_by="SYSTEM_AI_ENGINE", reason=reason)
        return None

    def resolve_camera_alert(self, db: Session, camera_id: UUID, reason: str = "Camera recovered to ONLINE") -> Optional[Alert]:
        """Auto-resolves open CAMERA_OFFLINE / CAMERA_DEGRADED alert when camera recovers."""
        alert = (
            db.query(Alert)
            .filter(
                Alert.camera_id == camera_id,
                Alert.alert_type.in_(["CAMERA_OFFLINE", "CAMERA_DEGRADED"]),
                Alert.status.in_(["OPEN", "ACKNOWLEDGED"])
            )
            .first()
        )
        if alert:
            return self.transition_alert_status(db, alert.id, "RESOLVED", changed_by="SYSTEM_CAMERA_HEALTH", reason=reason)
        return None

    def get_alerts_summary(self, db: Session) -> Dict[str, int]:
        """Returns dashboard summary counts for active alerts."""
        open_alerts = db.query(Alert).filter(Alert.status.in_(["OPEN", "ACKNOWLEDGED"])).all()

        summary = {
            "total_open": len(open_alerts),
            "critical": sum(1 for a in open_alerts if a.severity == "CRITICAL"),
            "warning": sum(1 for a in open_alerts if a.severity == "WARNING"),
            "info": sum(1 for a in open_alerts if a.severity == "INFO"),
            "late_arrival": sum(1 for a in open_alerts if a.alert_type == "LATE_ARRIVAL"),
            "overstay": sum(1 for a in open_alerts if a.alert_type == "OVERSTAY"),
            "unauthorized": sum(1 for a in open_alerts if a.alert_type == "UNAUTHORIZED_VEHICLE"),
            "manual_review": sum(1 for a in open_alerts if a.alert_type == "MANUAL_REVIEW_REQUIRED"),
            "camera_offline": sum(1 for a in open_alerts if a.alert_type == "CAMERA_OFFLINE"),
            "inference_failure": sum(1 for a in open_alerts if a.alert_type == "INFERENCE_FAILURE"),
        }
        return summary


alert_engine = AlertEngine()
