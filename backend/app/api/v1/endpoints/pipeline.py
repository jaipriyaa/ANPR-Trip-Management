from typing import Optional, List, Dict, Any
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.data_pipeline_service import data_pipeline_service
from app.models.daily_summary import DailySummary
from app.models.daily_gate_summary import DailyGateSummary
from app.models.ocr_feedback_dataset import OcrFeedbackDataset
from app.models.archive_job import ArchiveJob, ArchiveLog

router = APIRouter(prefix="", tags=["Enterprise Data Engineering Pipeline"])


@router.get("/pipeline/statistics", summary="Get Central Pipeline Dashboard Operational Metrics")
def get_pipeline_statistics(db: Session = Depends(get_db)):
    return data_pipeline_service.get_pipeline_statistics(db)


@router.get("/daily-summary", summary="Get Daily Factory Summary Aggregates")
def get_daily_summary(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=100),
):
    summaries = db.query(DailySummary).order_by(DailySummary.summary_date.desc()).offset(skip).limit(limit).all()
    total = db.query(DailySummary).count()
    return {
        "total": total,
        "items": [{
            "id": str(s.id),
            "summary_date": s.summary_date.isoformat(),
            "vehicles_entered": s.vehicles_entered,
            "vehicles_exited": s.vehicles_exited,
            "vehicles_still_inside": s.vehicles_still_inside,
            "trips_completed": s.trips_completed,
            "trips_cancelled": s.trips_cancelled,
            "late_arrivals": s.late_arrivals,
            "overstay_cases": s.overstay_cases,
            "unauthorized_attempts": s.unauthorized_attempts,
            "recognition_accuracy": s.recognition_accuracy,
            "avg_stay_duration_mins": s.avg_stay_duration_mins,
            "avg_ocr_confidence": s.avg_ocr_confidence,
        } for s in summaries]
    }


@router.get("/gate-summary", summary="Get Daily Per-Gate Summary Aggregates")
def get_gate_summary(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    gate_sums = db.query(DailyGateSummary).order_by(DailyGateSummary.summary_date.desc()).offset(skip).limit(limit).all()
    total = db.query(DailyGateSummary).count()
    return {
        "total": total,
        "items": [{
            "id": str(gs.id),
            "summary_date": gs.summary_date.isoformat(),
            "gate_name": gs.gate_name,
            "vehicles_entered": gs.vehicles_entered,
            "vehicles_exited": gs.vehicles_exited,
            "avg_processing_time_secs": gs.avg_processing_time_secs,
            "avg_stay_duration_mins": gs.avg_stay_duration_mins,
            "alerts_generated": gs.alerts_generated,
            "recognition_accuracy": gs.recognition_accuracy,
        } for gs in gate_sums]
    }


@router.get("/late-arrivals", summary="Get Late Arrival Scanner Results")
def get_late_arrivals(db: Session = Depends(get_db)):
    late_list = data_pipeline_service.scan_late_arrivals(db)
    return {
        "total": len(late_list),
        "items": late_list,
    }


@router.get("/overstay", summary="Get Overstay Violation Scanner Results")
def get_overstay_vehicles(
    max_allowed_mins: int = Query(120, ge=10, le=1440),
    db: Session = Depends(get_db)
):
    overstay_list = data_pipeline_service.scan_overstay_vehicles(db, max_allowed_mins=max_allowed_mins)
    return {
        "total": len(overstay_list),
        "items": overstay_list,
    }


@router.get("/archive/jobs", summary="Get Retention & Archival Jobs Log")
def get_archive_jobs(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    jobs = db.query(ArchiveJob).order_by(ArchiveJob.started_at.desc()).offset(skip).limit(limit).all()
    total = db.query(ArchiveJob).count()
    return {
        "total": total,
        "items": [{
            "id": str(j.id),
            "job_name": j.job_name,
            "target_table": j.target_table,
            "records_archived": j.records_archived,
            "retention_days": j.retention_days,
            "status": j.status,
            "started_at": j.started_at.isoformat() if j.started_at else None,
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
        } for j in jobs]
    }


@router.post("/archive/run", summary="Trigger Manual Retention & Archival Job")
def trigger_archive_job(
    retention_days: int = Query(180, ge=30, le=730),
    db: Session = Depends(get_db),
):
    result = data_pipeline_service.run_archival_job(db, retention_days=retention_days)
    return result


@router.post("/cleanup", summary="Trigger Duplicate Removal & Temp File Cleanup")
def trigger_pipeline_cleanup(db: Session = Depends(get_db)):
    dup_res = data_pipeline_service.deduplicate_detections(db)
    match_res = data_pipeline_service.match_entry_exit_pairs(db)
    data_pipeline_service.generate_daily_summaries(db)
    data_pipeline_service.sync_ocr_feedback_dataset(db)
    return {
        "success": True,
        "message": "Pipeline cleanup, duplicate removal, and summary aggregation executed successfully.",
        "duplicate_detection": dup_res,
        "entry_exit_matching": match_res,
    }


@router.get("/ocr-feedback", summary="Get OCR Feedback Dataset Records")
def get_ocr_feedback_dataset(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    data_pipeline_service.sync_ocr_feedback_dataset(db)
    records = db.query(OcrFeedbackDataset).order_by(OcrFeedbackDataset.created_at.desc()).offset(skip).limit(limit).all()
    total = db.query(OcrFeedbackDataset).count()
    return {
        "total": total,
        "items": [{
            "id": str(r.id),
            "raw_ocr_text": r.raw_ocr_text,
            "corrected_ocr_text": r.corrected_ocr_text,
            "confidence": r.confidence,
            "vehicle_image_path": r.vehicle_image_path,
            "plate_image_path": r.plate_image_path,
            "reviewer": r.reviewer,
            "correction_source": r.correction_source,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        } for r in records]
    }
