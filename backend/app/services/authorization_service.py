import logging
from typing import Dict, List, Any, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.vehicle_plate import VehiclePlate
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.transporter import Transporter
from app.models.scheduled_trip import ScheduledTrip
from app.models.whitelist_entry import WhitelistEntry
from app.models.watchlist_entry import WatchlistEntry
from app.models.gate_decision import GateDecision
from app.models.gate import Gate

logger = logging.getLogger(__name__)


class AuthorizationEngine:
    def evaluate_gate_access(
        self,
        db: Session,
        plate_text: str,
        gate_id: Optional[UUID] = None,
        camera_id: Optional[UUID] = None,
        tracking_id: Optional[str] = None,
        confidence: float = 0.95,
    ) -> Dict[str, Any]:
        """
        Core Industrial Authorization Engine. Evaluates recognized plate against
        5 security decision levels and logs to gate_decisions table.
        """
        clean_plate = plate_text.strip().upper() if plate_text else ""
        decision_time = datetime.now(timezone.utc)

        # 1. Level 1: Watchlist Security Check
        watchlist_hit = (
            db.query(WatchlistEntry)
            .filter(
                WatchlistEntry.plate_number.ilike(clean_plate),
                WatchlistEntry.status == "ACTIVE"
            )
            .first()
        )
        if watchlist_hit:
            res_payload = {
                "decision": "DENY",
                "authorization_status": "DENIED",
                "reason": f"SECURITY WATCHLIST HIT: {watchlist_hit.reason} (Severity: {watchlist_hit.severity})",
                "watchlist_hit": True,
                "severity": watchlist_hit.severity,
            }
            self._log_decision(db, clean_plate, "DENY", res_payload["reason"], confidence, gate_id, camera_id, tracking_id)
            return res_payload

        # 2. Level 2: Active Whitelist Verification
        whitelist_hit = (
            db.query(WhitelistEntry)
            .filter(
                WhitelistEntry.recognized_plate.ilike(clean_plate),
                WhitelistEntry.status == "ACTIVE"
            )
            .first()
        )
        if whitelist_hit:
            res_payload = {
                "decision": "ALLOW",
                "authorization_status": "AUTHORIZED",
                "reason": "Vehicle Authorized in Active Industrial Whitelist",
                "whitelist_hit": True,
                "watchlist_hit": False,
            }
            self._log_decision(db, clean_plate, "ALLOW", res_payload["reason"], confidence, gate_id, camera_id, tracking_id)
            return res_payload

        # 3. Level 3: Master Catalog Verification
        plate_rec = db.query(VehiclePlate).filter(VehiclePlate.plate_number.ilike(clean_plate)).first()
        vehicle = None
        driver = None
        transporter = None

        if plate_rec and plate_rec.vehicle_id:
            vehicle = db.get(Vehicle, plate_rec.vehicle_id)
        if not vehicle:
            vehicle = db.query(Vehicle).filter(Vehicle.vehicle_number.ilike(clean_plate)).first()

        if not vehicle:
            res_payload = {
                "decision": "UNKNOWN_VEHICLE",
                "authorization_status": "MANUAL REVIEW REQUIRED",
                "reason": "Vehicle plate not registered in Master Catalog",
                "watchlist_hit": False,
            }
            self._log_decision(db, clean_plate, "UNKNOWN_VEHICLE", res_payload["reason"], confidence, gate_id, camera_id, tracking_id)
            return res_payload

        # 4. Level 4: Master Entity Active Status Verification
        if not vehicle.is_active:
            res_payload = {
                "decision": "DENY",
                "authorization_status": "DENIED",
                "reason": "Vehicle registration status is INACTIVE / SUSPENDED",
                "watchlist_hit": False,
            }
            self._log_decision(db, clean_plate, "DENY", res_payload["reason"], confidence, gate_id, camera_id, tracking_id, vehicle_id=vehicle.id)
            return res_payload

        if vehicle.transporter_id:
            transporter = db.get(Transporter, vehicle.transporter_id)
            if transporter and not transporter.is_active:
                res_payload = {
                    "decision": "DENY",
                    "authorization_status": "DENIED",
                    "reason": f"Transporter '{transporter.company_name}' is INACTIVE / SUSPENDED",
                    "watchlist_hit": False,
                }
                self._log_decision(db, clean_plate, "DENY", res_payload["reason"], confidence, gate_id, camera_id, tracking_id, vehicle_id=vehicle.id)
                return res_payload

        # 5. Level 5: Active Scheduled Trip Verification
        scheduled_trip = (
            db.query(ScheduledTrip)
            .filter(
                ScheduledTrip.vehicle_id == vehicle.id,
                ScheduledTrip.trip_status.in_(["SCHEDULED", "WAITING", "INSIDE"])
            )
            .first()
        )

        if scheduled_trip and scheduled_trip.approval_status == "APPROVED":
            res_payload = {
                "decision": "ALLOW",
                "authorization_status": "AUTHORIZED",
                "reason": f"Approved Industrial Trip Verified ({scheduled_trip.trip_number})",
                "trip_id": str(scheduled_trip.id),
                "trip_number": scheduled_trip.trip_number,
                "watchlist_hit": False,
            }
            self._log_decision(db, clean_plate, "ALLOW", res_payload["reason"], confidence, gate_id, camera_id, tracking_id, vehicle_id=vehicle.id, trip_id=scheduled_trip.id)
            return res_payload

        # Fallback Default: Pending Manual Review
        res_payload = {
            "decision": "MANUAL_REVIEW",
            "authorization_status": "MANUAL REVIEW REQUIRED",
            "reason": "Unscheduled Vehicle Visit — Security Officer Verification Required",
            "watchlist_hit": False,
        }
        self._log_decision(db, clean_plate, "MANUAL_REVIEW", res_payload["reason"], confidence, gate_id, camera_id, tracking_id, vehicle_id=vehicle.id)
        return res_payload

    def _log_decision(
        self,
        db: Session,
        plate: str,
        decision: str,
        reason: str,
        confidence: float,
        gate_id: Any,
        camera_id: Any,
        tracking_id: Optional[str],
        vehicle_id: Optional[UUID] = None,
        trip_id: Optional[UUID] = None,
    ) -> GateDecision:
        def _to_uuid(val):
            if not val:
                return None
            if isinstance(val, UUID):
                return val
            try:
                return UUID(str(val))
            except (ValueError, TypeError):
                return None

        log_entry = GateDecision(
            vehicle_id=vehicle_id,
            tracking_id=tracking_id or "TRACK-1",
            trip_id=trip_id,
            gate_id=_to_uuid(gate_id),
            camera_id=_to_uuid(camera_id),
            decision=decision,
            reason=reason,
            recognized_plate=plate,
            confidence=confidence,
            decision_by="Automated AI Gate Decision Engine",
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)

        if decision == "DENY":
            from app.services.alert_service import alert_engine
            alert_engine.create_alert(
                db=db,
                alert_type="UNAUTHORIZED_VEHICLE",
                message=f"Unauthorized vehicle access attempt at gate: '{plate or 'UNKNOWN'}'. Reason: {reason}",
                reason=reason,
                severity="CRITICAL",
                trip_id=trip_id,
                movement_id=None,
                gate_id=_to_uuid(gate_id),
                camera_id=_to_uuid(camera_id),
                plate_number=plate,
                vehicle_type="Truck"
            )

        return log_entry

    def process_manual_override(
        self,
        db: Session,
        decision_id: UUID,
        action: str,
        officer_name: str = "Security Officer",
        remarks: Optional[str] = "Manual Security Override"
    ) -> GateDecision:
        """Processes Security Officer manual override ('MANUAL_APPROVAL' or 'MANUAL_REJECTION')."""
        dec = db.get(GateDecision, decision_id)
        if not dec:
            raise ValueError(f"Gate Decision #{decision_id} not found.")

        dec.decision = action
        dec.reason = f"Manual Override: {remarks} (by {officer_name})"
        dec.decision_by = officer_name
        db.commit()
        db.refresh(dec)
        return dec

    def get_dashboard_summary(self, db: Session) -> Dict[str, Any]:
        """Aggregates KPI metrics for Authorization Control Room."""
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        authorized_today = db.query(GateDecision).filter(GateDecision.decision == "ALLOW", GateDecision.decision_time >= today_start).count()
        denied_today = db.query(GateDecision).filter(GateDecision.decision == "DENY", GateDecision.decision_time >= today_start).count()
        manual_approvals = db.query(GateDecision).filter(GateDecision.decision == "MANUAL_APPROVAL", GateDecision.decision_time >= today_start).count()
        unknown_vehicles = db.query(GateDecision).filter(GateDecision.decision == "UNKNOWN_VEHICLE", GateDecision.decision_time >= today_start).count()
        watchlist_hits = db.query(WatchlistEntry).filter(WatchlistEntry.status == "ACTIVE").count()
        whitelist_count = db.query(WhitelistEntry).filter(WhitelistEntry.status == "ACTIVE").count()

        pending_queue = db.query(GateDecision).filter(GateDecision.decision.in_(["UNKNOWN_VEHICLE", "MANUAL_REVIEW"])).order_by(GateDecision.decision_time.desc()).limit(20).all()

        return {
            "authorized_today": authorized_today,
            "denied_today": denied_today,
            "manual_approvals": manual_approvals,
            "unknown_vehicles": unknown_vehicles,
            "watchlist_hits": watchlist_hits,
            "whitelist_count": whitelist_count,
            "pending_manual_queue": [{
                "id": str(d.id),
                "plate_number": d.recognized_plate,
                "reason": d.reason,
                "confidence": d.confidence,
                "time": d.decision_time.isoformat() if d.decision_time else None,
                "decision": d.decision,
            } for d in pending_queue]
        }


authorization_service = AuthorizationEngine()
