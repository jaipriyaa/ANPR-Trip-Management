import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text, inspect
from app.database.session import engine, SessionLocal
from app.models import Base
from app.crud.crud_gate import crud_gate
from app.crud.crud_camera import crud_camera
from app.crud.crud_gate_rule import crud_gate_rule
from app.schemas.gate import GateCreate
from app.schemas.camera import CameraCreate
from app.schemas.gate_rule import GateRuleCreate


def migrate_and_seed():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("ALL TABLES BEFORE MIGRATION:", tables)

    with engine.connect() as conn:
        # 1. Update gates table
        if "gates" in tables:
            g_cols = [c["name"] for c in inspector.get_columns("gates")]
            if "code" in g_cols and "gate_code" not in g_cols:
                conn.execute(text("ALTER TABLE gates RENAME COLUMN code TO gate_code;"))
            if "name" in g_cols and "gate_name" not in g_cols:
                conn.execute(text("ALTER TABLE gates RENAME COLUMN name TO gate_name;"))
            if "description" not in g_cols:
                conn.execute(text("ALTER TABLE gates ADD COLUMN description TEXT;"))
            conn.commit()

        # 2. Update/Rename cameras table to gate_cameras
        if "cameras" in tables and "gate_cameras" not in tables:
            conn.execute(text("ALTER TABLE cameras RENAME TO gate_cameras;"))
            conn.commit()

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if "gate_cameras" in tables:
            c_cols = [c["name"] for c in inspector.get_columns("gate_cameras")]
            if "name" in c_cols and "camera_name" not in c_cols:
                conn.execute(text("ALTER TABLE gate_cameras RENAME COLUMN name TO camera_name;"))
            if "camera_position" not in c_cols:
                conn.execute(text("ALTER TABLE gate_cameras ADD COLUMN camera_position VARCHAR(50) DEFAULT 'Entry Camera';"))
            if "ip_address" not in c_cols:
                conn.execute(text("ALTER TABLE gate_cameras ADD COLUMN ip_address VARCHAR(50);"))
            if "camera_status" not in c_cols:
                if "stream_status" in c_cols:
                    conn.execute(text("ALTER TABLE gate_cameras RENAME COLUMN stream_status TO camera_status;"))
                else:
                    conn.execute(text("ALTER TABLE gate_cameras ADD COLUMN camera_status VARCHAR(20) DEFAULT 'Online';"))
            if "resolution" not in c_cols:
                conn.execute(text("ALTER TABLE gate_cameras ADD COLUMN resolution VARCHAR(30) DEFAULT '1080p';"))
            if "fps" not in c_cols:
                conn.execute(text("ALTER TABLE gate_cameras ADD COLUMN fps INTEGER DEFAULT 30;"))
            conn.commit()

    # 3. Create any missing tables (gates, gate_cameras, gate_rules)
    Base.metadata.create_all(bind=engine)
    print("POSTGRESQL SCHEMA MIGRATION PASSED!")

    # 4. Seed initial records if empty
    db = SessionLocal()
    items, total = crud_gate.get_multi(db)
    if total == 0:
        g1 = crud_gate.create(db, obj_in=GateCreate(
            gate_code="GATE-NORTH-01",
            gate_name="Main Factory North Gate",
            gate_type="Entry & Exit",
            location="North Perimeter - Highway Access",
            description="Primary heavy vehicle entry/exit gate for raw material transport trucks.",
            status="ACTIVE",
            is_active=True
        ))
        g2 = crud_gate.create(db, obj_in=GateCreate(
            gate_code="GATE-SOUTH-02",
            gate_name="Logistics & Dispatch Gate 2",
            gate_type="Exit",
            location="South Perimeter - Warehouse Bay 4",
            description="Dedicated outbound gate for finished goods dispatch.",
            status="ACTIVE",
            is_active=True
        ))

        crud_camera.create(db, obj_in=CameraCreate(
            gate_id=g1.id,
            camera_name="ANPR Cam North Front",
            camera_position="Entry Camera",
            rtsp_url="rtsp://192.168.1.101:554/stream1",
            ip_address="192.168.1.101",
            camera_status="Online",
            resolution="1080p",
            fps=30,
            is_active=True
        ))
        crud_camera.create(db, obj_in=CameraCreate(
            gate_id=g1.id,
            camera_name="ANPR Cam North Rear",
            camera_position="Exit Camera",
            rtsp_url="rtsp://192.168.1.102:554/stream1",
            ip_address="192.168.1.102",
            camera_status="Online",
            resolution="1080p",
            fps=30,
            is_active=True
        ))

        crud_gate_rule.create_or_update(db, obj_in=GateRuleCreate(
            gate_id=g1.id,
            allow_entry=True,
            allow_exit=True,
            allow_trucks=True,
            allow_buses=True,
            allow_cars=True,
            allow_two_wheelers=False,
            maximum_vehicle_height=4.8,
            maximum_vehicle_weight=45.0,
            authorized_only=True,
            working_hours_start="06:00",
            working_hours_end="22:00",
            remarks="Heavy truck access requires prior scheduled trip authorization."
        ))

        crud_gate_rule.create_or_update(db, obj_in=GateRuleCreate(
            gate_id=g2.id,
            allow_entry=False,
            allow_exit=True,
            allow_trucks=True,
            allow_buses=False,
            allow_cars=True,
            allow_two_wheelers=False,
            maximum_vehicle_height=4.2,
            maximum_vehicle_weight=30.0,
            authorized_only=True,
            working_hours_start="08:00",
            working_hours_end="20:00",
            remarks="Strict exit-only gate for logistics trailers."
        ))
        print("SEED DATA CREATED: 2 Gates, 2 Cameras, 2 Gate Rule Sets!")
    else:
        print(f"Gates table already contains {total} records.")
    db.close()


if __name__ == "__main__":
    migrate_and_seed()
