import logging
import uuid
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from app.crud.crud_vehicle import crud_vehicle
from app.crud.crud_vehicle_plate import crud_vehicle_plate
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.transporter import Transporter
from app.models.trip import Trip
from app.models.authorization import Authorization

logger = logging.getLogger(__name__)


class VehicleVerificationEngine:
    """
    Enterprise Vehicle Verification Engine orchestrating:
    1. Search Vehicle Plate Master
    2. Search Vehicle Master
    3. Search Driver Master
    4. Search Scheduled / Active Trip
    5. Authorization Engine (AUTHORIZED, UNAUTHORIZED, MANUAL REVIEW)
    6. Complete Structured Verification Payload Generation
    """

    def search_plate_master(self, db: Session, plate_number: str) -> Tuple[Optional[Vehicle], Optional[Any]]:
        cleaned_plate = (plate_number or "").strip().upper()
        if not cleaned_plate:
            return None, None

        plate_rec = crud_vehicle_plate.get_by_plate_number(db, plate_number=cleaned_plate)
        if plate_rec:
            return plate_rec.vehicle, plate_rec

        vehicle = crud_vehicle.get_by_number(db, vehicle_number=cleaned_plate)
        return vehicle, None

    def parse_make_model(self, make_model: Optional[str]) -> Tuple[str, str]:
        if not make_model:
            return "Unknown", "Unknown"
        parts = make_model.strip().split(" ", 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return parts[0], parts[0]

    def search_driver_master(self, db: Session, vehicle: Optional[Vehicle]) -> Optional[Driver]:
        if not vehicle:
            return None

        active_trip = db.query(Trip).filter(
            Trip.vehicle_id == vehicle.id,
            Trip.status == "ACTIVE"
        ).first()

        if active_trip and active_trip.driver:
            return active_trip.driver

        if vehicle.transporter_id:
            driver = db.query(Driver).filter(
                Driver.transporter_id == vehicle.transporter_id,
                Driver.is_active == True
            ).first()
            if driver:
                return driver

        return None

    def search_scheduled_trip(self, db: Session, vehicle: Optional[Vehicle], plate_number: str) -> Tuple[Optional[Trip], Optional[Authorization]]:
        cleaned_plate = (plate_number or "").strip().upper()
        if not cleaned_plate or len(cleaned_plate) < 4:
            return None, None

        query = db.query(Trip)
        if vehicle:
            trip = query.filter(Trip.vehicle_id == vehicle.id).order_by(Trip.created_at.desc()).first()
        else:
            trip = query.filter(Trip.plate_number == cleaned_plate).order_by(Trip.created_at.desc()).first()

        auth_query = db.query(Authorization).filter(Authorization.is_active == True)
        if vehicle:
            authorization = auth_query.filter(
                (Authorization.vehicle_id == vehicle.id) | (Authorization.plate_number == cleaned_plate)
            ).first()
        else:
            authorization = auth_query.filter(Authorization.plate_number == cleaned_plate).first()

        return trip, authorization

    def evaluate_authorization(
        self,
        vehicle: Optional[Vehicle],
        driver: Optional[Driver],
        trip: Optional[Trip],
        authorization: Optional[Authorization],
        is_known_plate: bool
    ) -> Tuple[str, str]:

        # Rule 1: Unknown / Unregistered Plate
        if not is_known_plate or not vehicle:
            return "MANUAL REVIEW", "Unregistered or unverified plate - requires manual gate review"

        # Rule 2: Vehicle Blacklisted
        if vehicle.is_blacklisted:
            return "UNAUTHORIZED", f"Vehicle '{vehicle.vehicle_number}' is blacklisted in security master"

        # Rule 3: Vehicle Inactive
        if not vehicle.is_active:
            return "UNAUTHORIZED", f"Vehicle '{vehicle.vehicle_number}' status is inactive"

        # Rule 4: Driver Inactive
        if driver and not driver.is_active:
            return "MANUAL REVIEW", f"Assigned driver '{driver.full_name}' is inactive - requires manual review"

        # Rule 5: Active Authorization or Scheduled Trip
        if authorization and authorization.is_active:
            return "AUTHORIZED", f"Vehicle matched active security authorization ({authorization.auth_type})"

        if trip:
            if trip.status in ["ACTIVE", "SCHEDULED"]:
                return "AUTHORIZED", f"Vehicle matched scheduled trip #{str(trip.id)[:8]} ({trip.purpose or 'Scheduled Visit'})"
            return "MANUAL REVIEW", f"Trip status is '{trip.status}' - requires gate operator review"

        return "MANUAL REVIEW", "Registered active vehicle - no scheduled trip found for gate entry"

    def verify_and_authorize(
        self,
        db: Session,
        plate_number: str,
        ocr_confidence: float = 0.0,
        vehicle_type_detected: Optional[str] = None,
        ai_result: Optional[dict] = None
    ) -> dict:
        cleaned_plate = (plate_number or "").strip().upper()
        vehicle, plate_rec = self.search_plate_master(db, cleaned_plate) if (cleaned_plate and len(cleaned_plate) >= 4) else (None, None)
        is_known_plate = vehicle is not None

        if vehicle:
            mfr, model = self.parse_make_model(vehicle.make_model)
            vehicle_type = vehicle.vehicle_type or vehicle_type_detected or "Unknown"
            color = vehicle.color or "Unknown"
            transporter_name = vehicle.transporter.company_name if vehicle.transporter else "Unknown"
            transporter_code = vehicle.transporter.code if vehicle.transporter else "N/A"
        else:
            mfr, model = "Unknown", "Unknown"
            vehicle_type = vehicle_type_detected or "Unknown"
            color = "Unknown"
            transporter_name = "Unknown"
            transporter_code = "N/A"

        driver = self.search_driver_master(db, vehicle)
        driver_id = str(driver.id) if driver else None
        driver_name = driver.full_name if driver else "Unassigned"
        driver_license = driver.license_number if driver else "N/A"
        driver_phone = driver.phone_number if driver else "N/A"
        driver_status = "Active" if (driver and driver.is_active) else "Unassigned"

        trip, authorization = self.search_scheduled_trip(db, vehicle, cleaned_plate)

        trip_id = str(trip.id) if trip else None
        purpose = (trip.purpose if trip else None) or (authorization.purpose if authorization else None) or "N/A"
        destination = (trip.destination if trip else None) or (authorization.destination if authorization else None) or "N/A"
        expected_entry = trip.entry_time.isoformat() if (trip and trip.entry_time) else None
        expected_exit = trip.expected_exit_time.isoformat() if (trip and trip.expected_exit_time) else None
        trip_status = trip.status if trip else ("AUTHORIZED" if authorization else "No Active Trip")

        auth_decision, auth_reason = self.evaluate_authorization(
            vehicle, driver, trip, authorization, is_known_plate
        )

        return {
            "plate_number": cleaned_plate if (cleaned_plate and len(cleaned_plate) >= 4) else None,
            "authorization": auth_decision,
            "reason": auth_reason,
            "is_known_plate": is_known_plate,
            "vehicle": {
                "id": str(vehicle.id) if vehicle else None,
                "vehicle_number": cleaned_plate if (cleaned_plate and len(cleaned_plate) >= 4) else "N/A",
                "type": vehicle_type,
                "manufacturer": mfr,
                "model": model,
                "color": color,
                "is_active": vehicle.is_active if vehicle else False,
                "is_blacklisted": vehicle.is_blacklisted if vehicle else False,
            },
            "transporter": {
                "id": str(vehicle.transporter_id) if vehicle and vehicle.transporter_id else None,
                "code": transporter_code,
                "company_name": transporter_name,
            },
            "driver": {
                "id": driver_id,
                "name": driver_name,
                "license": driver_license,
                "phone": driver_phone,
                "status": driver_status,
                "is_active": driver.is_active if driver else False,
            },
            "trip": {
                "id": trip_id,
                "purpose": purpose,
                "destination": destination,
                "expected_entry": expected_entry,
                "expected_exit": expected_exit,
                "transporter_name": transporter_name,
                "material": "N/A" if not trip else "General Cargo / Material",
                "status": trip_status,
            },
        }


vehicle_verification_engine = VehicleVerificationEngine()
