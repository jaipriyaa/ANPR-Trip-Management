import os
import sys

# Ensure backend path is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.session import engine, SessionLocal
from app.database.base import Base
import app.models  # Ensures all models are loaded in Base.metadata

def migrate_and_seed_manual_review():
    print("Creating Phase 10 Manual Review Engine tables (manual_reviews, ocr_correction_history)...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    db = SessionLocal()
    try:
        # Seed initial pending manual review entry if empty
        from app.models.manual_review import ManualReview
        if db.query(ManualReview).count() == 0:
            review_seeds = [
                ManualReview(
                    recognized_plate="MH14TCF20OF",  # 'O' ambiguity
                    corrected_plate="MH14TCF200F",
                    raw_ocr_text="MH14TCF20OF",
                    confidence=0.68,
                    review_status="PENDING",
                    remarks="Low confidence character ambiguity (0 <-> O)",
                    tracking_id="TRACK-101",
                ),
                ManualReview(
                    recognized_plate="KA01AB9999",
                    raw_ocr_text="KA01AB9999",
                    confidence=0.72,
                    review_status="PENDING",
                    remarks="Unregistered Vehicle Visit — Manual Review Required",
                    tracking_id="TRACK-102",
                ),
            ]
            for r in review_seeds:
                db.add(r)
            db.commit()
            print("Seeded initial pending Manual Review items.")

    except Exception as e:
        print(f"Error during migration/seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_and_seed_manual_review()
