from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.dependencies import get_db
from app.services.authorization_service import authorization_service
from app.models.whitelist_entry import WhitelistEntry
from app.models.watchlist_entry import WatchlistEntry
from app.models.gate_decision import GateDecision

router = APIRouter(tags=["Authorization Engine & Gate Decisions"])


# ----------------------------------------------------
# 1. Whitelist APIs
# ----------------------------------------------------
@router.get("/whitelist", summary="Get all Whitelist entries")
def get_whitelist(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    entries = db.query(WhitelistEntry).offset(skip).limit(limit).all()
    total = db.query(WhitelistEntry).count()
    return {
        "total": total,
        "items": [{
            "id": str(w.id),
            "recognized_plate": w.recognized_plate,
            "authorized_from": w.authorized_from.isoformat() if w.authorized_from else None,
            "authorized_to": w.authorized_to.isoformat() if w.authorized_to else None,
            "allowed_entry_gates": w.allowed_entry_gates,
            "allowed_exit_gates": w.allowed_exit_gates,
            "status": w.status,
            "remarks": w.remarks,
        } for w in entries]
    }


@router.post("/whitelist", status_code=status.HTTP_201_CREATED, summary="Create Whitelist Entry")
def create_whitelist_entry(
    entry_in: dict,
    db: Session = Depends(get_db),
):
    plate = entry_in.get("recognized_plate", "").strip().upper()
    if not plate:
        raise HTTPException(status_code=400, detail="Plate number is required.")

    w = WhitelistEntry(
        recognized_plate=plate,
        allowed_entry_gates=entry_in.get("allowed_entry_gates", "ALL"),
        allowed_exit_gates=entry_in.get("allowed_exit_gates", "ALL"),
        status=entry_in.get("status", "ACTIVE"),
        remarks=entry_in.get("remarks", "Authorized Vehicle"),
    )
    db.add(w)
    db.commit()
    db.refresh(w)
    return {"id": str(w.id), "recognized_plate": w.recognized_plate, "status": w.status}


@router.delete("/whitelist/{id}", summary="Delete Whitelist Entry")
def delete_whitelist_entry(id: UUID, db: Session = Depends(get_db)):
    w = db.get(WhitelistEntry, id)
    if not w:
        raise HTTPException(status_code=404, detail="Whitelist entry not found.")
    db.delete(w)
    db.commit()
    return {"message": "Whitelist entry deleted successfully."}


# ----------------------------------------------------
# 2. Watchlist APIs
# ----------------------------------------------------
@router.get("/watchlist", summary="Get all Watchlist entries")
def get_watchlist(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    entries = db.query(WatchlistEntry).offset(skip).limit(limit).all()
    total = db.query(WatchlistEntry).count()
    return {
        "total": total,
        "items": [{
            "id": str(w.id),
            "plate_number": w.plate_number,
            "reason": w.reason,
            "severity": w.severity,
            "status": w.status,
            "remarks": w.remarks,
            "created_at": w.created_at.isoformat() if w.created_at else None,
        } for w in entries]
    }


@router.post("/watchlist", status_code=status.HTTP_201_CREATED, summary="Create Watchlist Entry")
def create_watchlist_entry(
    entry_in: dict,
    db: Session = Depends(get_db),
):
    plate = entry_in.get("plate_number", "").strip().upper()
    if not plate:
        raise HTTPException(status_code=400, detail="Plate number is required.")

    w = WatchlistEntry(
        plate_number=plate,
        reason=entry_in.get("reason", "Security Alert"),
        severity=entry_in.get("severity", "HIGH"),
        status=entry_in.get("status", "ACTIVE"),
        remarks=entry_in.get("remarks", "High Priority Attention"),
    )
    db.add(w)
    db.commit()
    db.refresh(w)
    return {"id": str(w.id), "plate_number": w.plate_number, "severity": w.severity}


@router.delete("/watchlist/{id}", summary="Delete Watchlist Entry")
def delete_watchlist_entry(id: UUID, db: Session = Depends(get_db)):
    w = db.get(WatchlistEntry, id)
    if not w:
        raise HTTPException(status_code=404, detail="Watchlist entry not found.")
    db.delete(w)
    db.commit()
    return {"message": "Watchlist entry deleted successfully."}


# ----------------------------------------------------
# 3. Authorization Check & Dashboard APIs
# ----------------------------------------------------
@router.post("/authorization/check", summary="Evaluate Gate Authorization Check for Recognized Vehicle")
def check_authorization(
    check_in: dict,
    db: Session = Depends(get_db),
):
    plate = check_in.get("plate_number") or check_in.get("recognized_plate")
    if not plate:
        raise HTTPException(status_code=400, detail="plate_number is required.")

    return authorization_service.evaluate_gate_access(
        db,
        plate_text=plate,
        gate_id=check_in.get("gate_id"),
        camera_id=check_in.get("camera_id"),
        tracking_id=check_in.get("tracking_id"),
        confidence=check_in.get("confidence", 0.95),
    )


@router.get("/authorization/dashboard", summary="Get Authorization Control Room Dashboard KPIs & Manual Queue")
def get_authorization_dashboard(
    db: Session = Depends(get_db),
):
    return authorization_service.get_dashboard_summary(db)


# ----------------------------------------------------
# 4. Gate Decisions Log APIs
# ----------------------------------------------------
@router.get("/gate-decisions", summary="Get Gate Decision History Log")
def get_gate_decisions(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    decisions = db.query(GateDecision).order_by(GateDecision.decision_time.desc()).offset(skip).limit(limit).all()
    total = db.query(GateDecision).count()
    return {
        "total": total,
        "items": [{
            "id": str(d.id),
            "recognized_plate": d.recognized_plate,
            "decision": d.decision,
            "reason": d.reason,
            "confidence": d.confidence,
            "decision_by": d.decision_by,
            "decision_time": d.decision_time.isoformat() if d.decision_time else None,
        } for d in decisions]
    }


@router.get("/gate-decisions/{id}", summary="Get Gate Decision Details by ID")
def get_gate_decision_by_id(id: UUID, db: Session = Depends(get_db)):
    d = db.get(GateDecision, id)
    if not d:
        raise HTTPException(status_code=404, detail="Gate decision not found.")
    return {
        "id": str(d.id),
        "recognized_plate": d.recognized_plate,
        "decision": d.decision,
        "reason": d.reason,
        "confidence": d.confidence,
        "decision_by": d.decision_by,
        "decision_time": d.decision_time.isoformat() if d.decision_time else None,
    }


# ----------------------------------------------------
# 5. Security Officer Manual Override API
# ----------------------------------------------------
@router.post("/manual-approval", summary="Process Security Officer Manual Override (Approve or Reject)")
def process_manual_approval(
    override_in: dict,
    db: Session = Depends(get_db),
):
    decision_id = override_in.get("decision_id")
    action = override_in.get("action", "MANUAL_APPROVAL")  # MANUAL_APPROVAL or MANUAL_REJECTION
    officer_name = override_in.get("officer_name", "Security Officer")
    remarks = override_in.get("remarks", "Manual Security Verification Approved")

    if not decision_id:
        raise HTTPException(status_code=400, detail="decision_id is required.")

    try:
        updated = authorization_service.process_manual_override(
            db,
            decision_id=UUID(decision_id),
            action=action,
            officer_name=officer_name,
            remarks=remarks,
        )
        return {
            "success": True,
            "id": str(updated.id),
            "decision": updated.decision,
            "reason": updated.reason,
            "decision_by": updated.decision_by,
        }
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))
