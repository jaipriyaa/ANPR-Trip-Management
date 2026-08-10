import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timezone, timedelta
from sqlalchemy import text, inspect
from app.database.session import engine, SessionLocal
from app.models import Base, ScheduledTrip, TripStatusHistory
from app.crud.crud_gate import crud_gate
from app.crud.crud_vehicle import crud_vehicle
from app.crud.crud_driver import crud_driver
from app.crud.crud_transporter import crud_transporter
from app.crud.crud_scheduled_trip import crud_scheduled_trip
from app.schemas.scheduled_trip import ScheduledTripCreate


def migrate_and_seed_trips():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("ALL TABLES BEFORE TRIPS MIGRATION:", tables)

    # Create scheduled_trips & trip_status_history tables if missing
    Base.metadata.create_all(bind=engine)
    print("POSTGRESQL SCHEDULED_TRIPS & TRIP_STATUS_HISTORY TABLES CREATED SUCCESSFULLY!")

    db = SessionLocal()

    # Seed initial sample trips if table is empty
    items, total = crud_scheduled_trip.get_multi(db)
    if total == 0:
        gates, _ = crud_gate.get_multi(db)
        entry_gate_id = gates[0].id if gates else None
        exit_gate_id = gates[1].id if len(gates) > 1 else entry_gate_id

        v_volks = crud_vehicle.get_by_number(db, "MH14TCF200F")
        v_ka = crud_vehicle.get_by_number(db, "KA01AB1234")
        v_mh12 = crud_vehicle.get_by_number(db, "MH12PQ9999")

        drivers, _ = crud_driver.get_multi(db)
        d1 = drivers[0].id if drivers else None
        d2 = drivers[1].id if len(drivers) > 1 else d1

        transporters, _ = crud_transporter.get_multi(db)
        t1 = transporters[0].id if transporters else None

        now = datetime.now(timezone.utc)

        # 1. Trip Currently INSIDE (MH14TCF200F)
        crud_scheduled_trip.create(db, obj_in=ScheduledTripCreate(
            trip_number="TRIP-2026-001",
            vehicle_id=v_volks.id if v_volks else None,
            driver_id=d1,
            transporter_id=t1,
            entry_gate_id=entry_gate_id,
            exit_gate_id=exit_gate_id,
            expected_entry_time=now - timedelta(hours=2),
            expected_exit_time=now + timedelta(hours=2),
            actual_entry_time=now - timedelta(hours=1, minutes=45),
            purpose="Raw Material Supply",
            material_name="Steel Coils",
            material_quantity="25 Tons",
            source_location="Pune Warehousing Hub",
            destination_location="Plant Bay 4",
            priority="HIGH",
            trip_status="INSIDE",
            approval_status="APPROVED",
            remarks="Scheduled priority delivery for plant assembly.",
        ))

        # 2. Trip SCHEDULED (KA01AB1234) - Waiting for arrival
        crud_scheduled_trip.create(db, obj_in=ScheduledTripCreate(
            trip_number="TRIP-2026-002",
            vehicle_id=v_ka.id if v_ka else None,
            driver_id=d2,
            transporter_id=t1,
            entry_gate_id=entry_gate_id,
            exit_gate_id=exit_gate_id,
            expected_entry_time=now + timedelta(hours=1),
            expected_exit_time=now + timedelta(hours=5),
            purpose="Finished Goods Dispatch",
            material_name="Industrial Motors",
            material_quantity="150 Units",
            source_location="Main Factory Depot",
            destination_location="Bengaluru Logistics Terminal",
            priority="URGENT",
            trip_status="SCHEDULED",
            approval_status="APPROVED",
            remarks="High priority customer order shipment.",
        ))

        # 3. Trip COMPLETED (MH12PQ9999) - Completed 3 hours ago
        crud_scheduled_trip.create(db, obj_in=ScheduledTripCreate(
            trip_number="TRIP-2026-003",
            vehicle_id=v_mh12.id if v_mh12 else None,
            entry_gate_id=entry_gate_id,
            exit_gate_id=exit_gate_id,
            expected_entry_time=now - timedelta(hours=6),
            expected_exit_time=now - timedelta(hours=2),
            actual_entry_time=now - timedelta(hours=6),
            actual_exit_time=now - timedelta(hours=3),
            purpose="Chemical Solvent Delivery",
            material_name="Solvent X",
            material_quantity="12,000 Liters",
            source_location="Chemical Plant 2",
            destination_location="Tank Farm 1",
            priority="MEDIUM",
            trip_status="COMPLETED",
            approval_status="APPROVED",
            remarks="Trip completed cleanly within schedule.",
        ))

        print("SAMPLE INDUSTRIAL TRIPS SEEDED: 1 INSIDE, 1 SCHEDULED, 1 COMPLETED!")
    else:
        print(f"scheduled_trips table already contains {total} records.")

    db.close()


if __name__ == "__main__":
    migrate_and_seed_trips()
