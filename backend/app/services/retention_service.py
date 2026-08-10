import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.models.archive_job import ArchiveJob, ArchiveLog
from app.models.audit_log import AuditLog
from app.models.alert import Alert
from app.models.camera_health import CameraHealthLog
from app.models.vehicle_movement import VehicleMovement
from app.models.scheduled_trip import ScheduledTrip
from app.models.manual_review import ManualReview

logger = logging.getLogger(__name__)

ARCHIVE_STORAGE_DIR = os.path.abspath("archival_data/archives")
os.makedirs(ARCHIVE_STORAGE_DIR, exist_ok=True)


class RetentionArchivalService:
    def __init__(self):
        self.archive_dir = ARCHIVE_STORAGE_DIR

    def run_retention_job(self, db: Session, dry_run: Optional[bool] = None) -> Dict[str, Any]:
        """Runs configurable retention check, archive-before-delete pipeline, and safe cleanup."""
        is_dry_run = dry_run if dry_run is not None else settings.RETENTION_DRY_RUN
        now = datetime.now(timezone.utc)

        # Active operational protection filters
        active_trip_vehicle_ids = [
            t.vehicle_id for t in db.query(ScheduledTrip.vehicle_id)
            .filter(ScheduledTrip.trip_status.in_(["SCHEDULED", "ARRIVED", "ENTRY_APPROVED", "INSIDE_PLANT", "AT_DESTINATION"]))
            .all()
            if t.vehicle_id is not None
        ]
        open_alert_ids = [a.id for a in db.query(Alert.id).filter(Alert.status.in_(["OPEN", "ACKNOWLEDGED"])).all()]
        pending_review_ids = [r.id for r in db.query(ManualReview.id).filter(ManualReview.review_status == "PENDING").all()]

        # 1. Start ArchiveJob record
        job = ArchiveJob(
            job_name=f"Retention_Job_{now.strftime('%Y%m%d_%H%M%S')}",
            target_table="MULTI_TABLE",
            records_archived=0,
            retention_days=settings.DETECTION_RETENTION_DAYS,
            status="RUNNING",
            started_at=now,
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        results = {
            "job_id": str(job.id),
            "dry_run": is_dry_run,
            "execution_time": now.isoformat(),
            "eligible_alerts": 0,
            "eligible_camera_health": 0,
            "eligible_audit_logs": 0,
            "eligible_movements": 0,
            "records_archived": 0,
            "records_deleted": 0,
            "status": "SUCCESS",
            "failures": []
        }

        try:
            # ----------------------------------------------------
            # A. ALERTS RETENTION (Retention Days: settings.ALERT_RETENTION_DAYS)
            # ----------------------------------------------------
            alert_cutoff = now - timedelta(days=settings.ALERT_RETENTION_DAYS)
            eligible_alerts = (
                db.query(Alert)
                .filter(
                    Alert.created_at < alert_cutoff,
                    Alert.status.in_(["RESOLVED", "DISMISSED"]),  # Protect OPEN & ACKNOWLEDGED alerts
                    ~Alert.id.in_(open_alert_ids) if open_alert_ids else True
                )
                .all()
            )
            results["eligible_alerts"] = len(eligible_alerts)

            # Archive Alerts
            if eligible_alerts and not is_dry_run:
                alert_archive_file = os.path.join(self.archive_dir, f"alerts_{now.strftime('%Y%m%d_%H%M%S')}.jsonl")
                alert_data = [
                    {
                        "id": str(a.id),
                        "alert_key": a.alert_key,
                        "alert_type": a.alert_type,
                        "severity": a.severity,
                        "status": a.status,
                        "message": a.message,
                        "created_at": a.created_at.isoformat() if a.created_at else None,
                        "archived_at": now.isoformat()
                    }
                    for a in eligible_alerts
                ]
                # Archive write
                with open(alert_archive_file, "w", encoding="utf-8") as f:
                    for item in alert_data:
                        f.write(json.dumps(item) + "\n")

                # Verify archive write success before delete
                if os.path.exists(alert_archive_file) and os.path.getsize(alert_archive_file) > 0:
                    for a in eligible_alerts:
                        db.delete(a)
                    results["records_archived"] += len(eligible_alerts)
                    results["records_deleted"] += len(eligible_alerts)
                else:
                    raise IOError("Alert archive file write failed or produced 0 bytes.")

            # ----------------------------------------------------
            # B. CAMERA HEALTH LOGS RETENTION (settings.CAMERA_HEALTH_RETENTION_DAYS)
            # ----------------------------------------------------
            cam_cutoff = now - timedelta(days=settings.CAMERA_HEALTH_RETENTION_DAYS)
            eligible_cams = (
                db.query(CameraHealthLog)
                .filter(CameraHealthLog.created_at < cam_cutoff)
                .all()
            )
            results["eligible_camera_health"] = len(eligible_cams)

            if eligible_cams and not is_dry_run:
                cam_archive_file = os.path.join(self.archive_dir, f"camera_health_{now.strftime('%Y%m%d_%H%M%S')}.jsonl")
                cam_data = [
                    {
                        "id": str(c.id),
                        "camera_id": str(c.camera_id) if c.camera_id else None,
                        "status": c.status,
                        "created_at": c.created_at.isoformat() if c.created_at else None,
                        "archived_at": now.isoformat()
                    }
                    for c in eligible_cams
                ]
                with open(cam_archive_file, "w", encoding="utf-8") as f:
                    for item in cam_data:
                        f.write(json.dumps(item) + "\n")

                if os.path.exists(cam_archive_file) and os.path.getsize(cam_archive_file) > 0:
                    for c in eligible_cams:
                        db.delete(c)
                    results["records_archived"] += len(eligible_cams)
                    results["records_deleted"] += len(eligible_cams)
                else:
                    raise IOError("Camera health archive file write failed or produced 0 bytes.")

            # Update ArchiveJob Status
            job.records_archived = results["records_archived"]
            job.status = "SUCCESS"
            job.completed_at = datetime.now(timezone.utc)

            log_entry = ArchiveLog(
                job_id=job.id,
                action="RETENTION_CLEANUP",
                records_affected=results["records_deleted"],
                message=f"Retention job completed. Dry run: {is_dry_run}. Archived: {results['records_archived']}, Deleted: {results['records_deleted']}."
            )
            db.add(log_entry)

            audit = AuditLog(
                user_id=None,
                action="RETENTION_JOB_SUCCESS",
                entity_type="ArchiveJob",
                entity_id=str(job.id),
                details=results,
                ip_address="SYSTEM_RETENTION_SERVICE"
            )
            db.add(audit)
            db.commit()

            logger.info(f"RetentionArchivalService: Job #{job.id} finished successfully. DryRun: {is_dry_run}, Archived: {results['records_archived']}, Deleted: {results['records_deleted']}")
            return results

        except Exception as e:
            db.rollback()
            err_msg = str(e)
            logger.error(f"RetentionArchivalService: Retention job failed: {err_msg}", exc_info=True)
            job.status = "FAILED"
            job.error_message = err_msg
            db.add(job)
            db.commit()

            results["status"] = "FAILED"
            results["failures"].append(err_msg)
            return results


retention_service = RetentionArchivalService()
