from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.dependencies import get_db
from app.services.manual_review_service import manual_review_service
from app.models.manual_review import ManualReview
from app.models.ocr_correction_history import OcrCorrectionHistory

router = APIRouter(prefix="/manual-review", tags=["Manual Review & OCR Correction System"])


@router.get("", summary="Get Manual Review Queue Items")
def get_manual_reviews(
    db: Session = Depends(get_db),
    status_filter: Optional[str] = Query(None, alias="status", description="PENDING, APPROVED, REJECTED, CORRECTED"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    query = db.query(ManualReview)
    if status_filter and status_filter.upper() != "ALL":
        query = query.filter(ManualReview.review_status == status_filter.upper())

    reviews = query.order_by(ManualReview.created_at.desc()).offset(skip).limit(limit).all()
    total = query.count()

    return {
        "total": total,
        "items": [{
            "id": str(r.id),
            "recognized_plate": r.recognized_plate,
            "corrected_plate": r.corrected_plate,
            "raw_ocr_text": r.raw_ocr_text,
            "confidence": r.confidence,
            "tracking_id": r.tracking_id or "TRACK-1",
            "vehicle_image_path": r.vehicle_image_path,
            "plate_image_path": r.plate_image_path,
            "review_status": r.review_status,
            "reviewed_by": r.reviewed_by,
            "review_time": r.review_time.isoformat() if r.review_time else None,
            "remarks": r.remarks,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        } for r in reviews]
    }


@router.get("/statistics", summary="Get Manual Review Queue KPI Statistics")
def get_manual_review_statistics(
    db: Session = Depends(get_db),
):
    return manual_review_service.get_statistics(db)


@router.get("/{id}", summary="Get Manual Review Details by ID")
def get_manual_review_by_id(
    id: UUID,
    db: Session = Depends(get_db),
):
    review = db.get(ManualReview, id)
    if not review:
        raise HTTPException(status_code=404, detail="Manual review item not found.")

    corrections = db.query(OcrCorrectionHistory).filter(OcrCorrectionHistory.manual_review_id == id).order_by(OcrCorrectionHistory.timestamp.desc()).all()

    return {
        "id": str(review.id),
        "recognized_plate": review.recognized_plate,
        "corrected_plate": review.corrected_plate,
        "raw_ocr_text": review.raw_ocr_text,
        "confidence": review.confidence,
        "tracking_id": review.tracking_id or "TRACK-1",
        "vehicle_image_path": review.vehicle_image_path,
        "plate_image_path": review.plate_image_path,
        "review_status": review.review_status,
        "reviewed_by": review.reviewed_by,
        "review_time": review.review_time.isoformat() if review.review_time else None,
        "remarks": review.remarks,
        "created_at": review.created_at.isoformat() if review.created_at else None,
        "corrections_history": [{
            "id": str(c.id),
            "old_plate": c.old_plate,
            "new_plate": c.new_plate,
            "old_confidence": c.old_confidence,
            "new_confidence": c.new_confidence,
            "correction_reason": c.correction_reason,
            "reviewed_by": c.reviewed_by,
            "timestamp": c.timestamp.isoformat() if c.timestamp else None,
        } for c in corrections]
    }


@router.post("/{id}/approve", summary="Approve Manual Review Recognition")
def approve_manual_review(
    id: UUID,
    payload: Optional[dict] = None,
    db: Session = Depends(get_db),
):
    reviewer = payload.get("reviewer", "Major Rajesh Verma") if payload else "Major Rajesh Verma"
    remarks = payload.get("remarks", "Approved by Security Officer") if payload else "Approved by Security Officer"
    try:
        updated = manual_review_service.approve_review(db, review_id=id, reviewer=reviewer, remarks=remarks)
        return {"success": True, "id": str(updated.id), "review_status": updated.review_status}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{id}/reject", summary="Reject Manual Review Recognition")
def reject_manual_review(
    id: UUID,
    payload: Optional[dict] = None,
    db: Session = Depends(get_db),
):
    reviewer = payload.get("reviewer", "Major Rajesh Verma") if payload else "Major Rajesh Verma"
    remarks = payload.get("remarks", "Denied by Security Officer") if payload else "Denied by Security Officer"
    try:
        updated = manual_review_service.reject_review(db, review_id=id, reviewer=reviewer, remarks=remarks)
        return {"success": True, "id": str(updated.id), "review_status": updated.review_status}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{id}/correct", summary="Correct License Plate & Save AI Feedback Dataset")
def correct_manual_review(
    id: UUID,
    payload: dict,
    db: Session = Depends(get_db),
):
    new_plate = payload.get("corrected_plate") or payload.get("new_plate")
    if not new_plate:
        raise HTTPException(status_code=400, detail="corrected_plate is required.")

    reviewer = payload.get("reviewer", "Major Rajesh Verma")
    remarks = payload.get("remarks", "Corrected OCR Mistake")

    try:
        updated = manual_review_service.correct_review(
            db,
            review_id=id,
            new_plate=new_plate,
            reviewer=reviewer,
            remarks=remarks,
        )
        return {
            "success": True,
            "id": str(updated.id),
            "corrected_plate": updated.corrected_plate,
            "review_status": updated.review_status,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/correct", summary="Standalone Plate Correction Endpoint")
def correct_plate_standalone(
    payload: dict,
    db: Session = Depends(get_db)
):
    event_id = payload.get("event_id") or payload.get("review_id") or payload.get("prediction_id")
    corrected_plate = payload.get("corrected_plate") or payload.get("new_plate")
    original_plate = payload.get("original_plate") or payload.get("raw_ocr_text")
    reason = payload.get("reason") or payload.get("remarks") or "Plate Correction"
    reviewer = payload.get("reviewer") or payload.get("operator_id") or "Security Officer"

    if not corrected_plate:
        raise HTTPException(status_code=400, detail="corrected_plate is required.")

    # Try UUID parse or find latest review
    review = None
    if event_id:
        try:
            review = db.get(ManualReview, UUID(str(event_id)))
        except (ValueError, TypeError):
            review = None

    if not review and original_plate:
        review = db.query(ManualReview).filter(ManualReview.recognized_plate == original_plate).first()

    if not review:
        review = manual_review_service.create_manual_review_record(
            db,
            ai_result={"plate_text": original_plate or "MH12TEMP", "raw_text": original_plate or "MH12TEMP", "confidence": 0.70}
        )

    try:
        updated = manual_review_service.correct_review(
            db,
            review_id=review.id,
            new_plate=corrected_plate,
            reviewer=reviewer,
            remarks=reason
        )
        return {
            "success": True,
            "correction_id": str(updated.id),
            "original_plate": updated.recognized_plate,
            "corrected_plate": updated.corrected_plate,
            "review_status": updated.review_status,
            "reason": reason,
            "reviewed_by": reviewer
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
