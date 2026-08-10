import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timezone, timedelta
from sqlalchemy import text, inspect
from app.database.session import engine, SessionLocal
from app.models import Base, VehicleMovement
from app.crud.crud_gate import crud_gate
from app.crud.crud_vehicle_movement import crud_vehicle_movement
from app.crud.crud_vehicle import crud_vehicle
from app.schemas.vehicle_movement import VehicleMovementCreate, VehicleMovementUpdate
from app.services.entry_exit_service import format_stay_duration


def migrate_and_seed_movements():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("ALL TABLES BEFORE MOVEMENTS MIGRATION:", tables)

    # Create vehicle_movements table if missing
    Base.metadata.create_all(bind=engine)
    print("POSTGRESQL VEHICLE_MOVEMENTS TABLE CREATED SUCCESSFULLY!")

    db = SessionLocal()

    # Seed sample entry/exit data if table empty
    items, total = crud_vehicle_movement.get_multi(db)
    if total == 0:
        gates, _ = crud_gate.get_multi(db)
        entry_gate_id = gates[0].id if gates else None
        exit_gate_id = gates[1].id if len(gates) > 1 else entry_gate_id

        # 1. Currently INSIDE vehicle (MH14TCF200F) - Entered 1 hour 45 minutes ago
        now = datetime.now(timezone.utc)
        entry_1h_ago = now - timedelta(hours=1, minutes=45)

        v_volks = crud_vehicle.get_by_number(db, "MH14TCF200F")

        crud_vehicle_movement.create(db, obj_in=VehicleMovementCreate(
            recognized_plate="MH14TCF200F",
            vehicle_id=v_volks.id if v_volks else None,
            entry_gate_id=entry_gate_id,
            entry_time=entry_1h_ago,
            movement_status="INSIDE",
            vehicle_status="ENTERED",
            recognition_confidence=0.985,
            vehicle_type="SUV",
            purpose="Material Delivery",
            destination="Main Assembly Bay",
        ))

        # 2. Completed Movement (KA01AB1234) - Entered 4 hours ago, Exited 1 hour ago (Stay: 3 Hours)
        entry_4h_ago = now - timedelta(hours=4)
        exit_1h_ago = now - timedelta(hours=1)
        dur_sec = (exit_1h_ago - entry_4h_ago).total_seconds()

        v_ka = crud_vehicle.get_by_number(db, "KA01AB1234")

        crud_vehicle_movement.create(db, obj_in=VehicleMovementCreate(
            recognized_plate="KA01AB1234",
            vehicle_id=v_ka.id if v_ka else None,
            entry_gate_id=entry_gate_id,
            exit_gate_id=exit_gate_id,
            entry_time=entry_4h_ago,
            exit_time=exit_1h_ago,
            stay_duration_minutes=round(dur_sec / 60.0, 2),
            stay_duration_formatted=format_stay_duration(dur_sec),
            movement_status="OUTSIDE",
            vehicle_status="EXITED",
            recognition_confidence=0.962,
            vehicle_type="Truck",
            purpose="Cargo Dispatch",
            destination="South Logistics Yard",
        ))

        # 3. Completed Movement (MH12PQ9999) - Entered 6 hours ago, Exited 3 hours ago (Stay: 3 Hours)
        entry_6h_ago = now - timedelta(hours=6)
        exit_3h_ago = now - timedelta(hours=3)
        dur_sec_3h = (exit_3h_ago - entry_6h_ago).total_seconds()

        crud_vehicle_movement.create(db, obj_in=VehicleMovementCreate(
            recognized_plate="MH12PQ9999",
            entry_gate_id=entry_gate_id,
            exit_gate_id=exit_gate_id,
            entry_time=entry_6h_ago,
            exit_time=exit_3h_ago,
            stay_duration_minutes=round(dur_sec_3h / 60.0, 2),
            stay_duration_formatted=format_stay_duration(dur_sec_3h),
            movement_status="OUTSIDE",
            vehicle_status="EXITED",
            recognition_confidence=0.941,
            vehicle_type="Tanker",
            purpose="Chemical Unloading",
            destination="Plant Tank 2",
        ))

        print("SAMPLE VEHICLE MOVEMENTS SEEDED: 1 INSIDE, 2 COMPLETED EXITS!")
    else:
        print(f"vehicle_movements table already contains {total} records.")

    db.close()


if __name__ == "__main__":
    migrate_and_seed_movements()
