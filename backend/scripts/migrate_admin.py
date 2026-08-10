import os
import sys

# Ensure backend path is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.session import engine, SessionLocal
from app.database.base import Base
import app.models  # Ensures all models are loaded in Base.metadata

def migrate_and_seed_admin():
    print("Creating Phase 8 Enterprise Administration tables (system_settings, camera_health, users, audit_logs)...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    db = SessionLocal()
    try:

        # 1. Seed Default Admin & Operator Users if empty
        from app.models.user import User
        if db.query(User).count() == 0:
            users_seed = [
                User(username="admin", email="admin@factory.com", full_name="System Administrator", role="Administrator", hashed_password="hashed_admin_pass", is_active=True),
                User(username="sec_officer", email="security@factory.com", full_name="Major Rajesh Verma", role="Security Officer", hashed_password="hashed_sec_pass", is_active=True),
                User(username="operator1", email="gate1@factory.com", full_name="Suresh Gate Operator", role="Gate Operator", hashed_password="hashed_gate_pass", is_active=True),
            ]
            for u in users_seed:
                db.add(u)
            db.commit()
            print("Seeded default users (admin, sec_officer, operator1).")

        # 2. Seed System Settings if empty
        from app.models.system_setting import SystemSetting
        if db.query(SystemSetting).count() == 0:
            settings_seed = [
                SystemSetting(key="recognition_confidence_threshold", value="0.75", description="Minimum OCR confidence required for auto approval", category="ANPR"),
                SystemSetting(key="duplicate_suppression_window_seconds", value="120", description="Window in seconds to suppress repeated detections", category="ANPR"),
                SystemSetting(key="max_upload_size_mb", value="50", description="Maximum video/image upload file size", category="SYSTEM"),
                SystemSetting(key="data_retention_days", value="180", description="Number of days to preserve recognition media & logs", category="RETENTION"),
                SystemSetting(key="rtsp_timeout_seconds", value="10", description="RTSP stream connection timeout", category="SECURITY"),
            ]
            for s in settings_seed:
                db.add(s)
            db.commit()
            print("Seeded default system settings.")

        # 3. Seed Initial Audit Log if empty
        from app.models.audit_log import AuditLog
        if db.query(AuditLog).count() == 0:
            db.add(AuditLog(action="SYSTEM_INIT", entity_type="SYSTEM", entity_id="INITIALIZATION", details={"message": "Enterprise ANPR Platform initialized with RBAC and Audit Trail"}, ip_address="127.0.0.1"))
            db.commit()
            print("Seeded initial audit log entry.")

    except Exception as e:
        print(f"Error during migration/seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_and_seed_admin()
