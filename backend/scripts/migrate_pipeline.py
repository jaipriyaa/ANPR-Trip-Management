import os
import sys
from datetime import date, timedelta

# Ensure backend path is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.session import engine, SessionLocal
from app.database.base import Base
import app.models  # Ensures all models are loaded in Base.metadata

def migrate_and_seed_pipeline():
    print("Creating Phase 11 Enterprise Data Engineering Pipeline tables (daily_summary, daily_gate_summary, ocr_feedback_dataset, archive_jobs, archive_logs)...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    db = SessionLocal()
    try:
        from app.services.data_pipeline_service import data_pipeline_service

        # 1. Generate Daily Summaries for today and yesterday
        today = date.today()
        yesterday = today - timedelta(days=1)

        data_pipeline_service.generate_daily_summaries(db, target_date=yesterday)
        data_pipeline_service.generate_daily_summaries(db, target_date=today)
        print("Generated Daily Summary & Daily Gate Summary records.")

        # 2. Sync OCR Feedback Dataset if empty
        data_pipeline_service.sync_ocr_feedback_dataset(db)
        print("Synced OCR Feedback Dataset.")

        # 3. Seed initial Archive Job if empty
        from app.models.archive_job import ArchiveJob, ArchiveLog
        if db.query(ArchiveJob).count() == 0:
            data_pipeline_service.run_archival_job(db, retention_days=180)
            print("Executed initial Retention & Archival Job.")

    except Exception as e:
        print(f"Error during migration/seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_and_seed_pipeline()
