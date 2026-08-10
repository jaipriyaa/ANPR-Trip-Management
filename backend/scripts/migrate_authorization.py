import os
import sys

# Ensure backend path is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.session import engine, SessionLocal
from app.database.base import Base
import app.models  # Ensures all models are loaded in Base.metadata

def migrate_and_seed_authorization():
    print("Creating Phase 9 Authorization Engine tables (whitelist_entries, watchlist_entries, gate_decisions)...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    db = SessionLocal()
    try:
        # 1. Seed Whitelist Entries if empty
        from app.models.whitelist_entry import WhitelistEntry
        if db.query(WhitelistEntry).count() == 0:
            whitelist_seeds = [
                WhitelistEntry(recognized_plate="MH14TCF200F", allowed_entry_gates="GATE-NORTH-01,GATE-SOUTH-02", allowed_exit_gates="ALL", status="ACTIVE", remarks="Permanent Factory Delivery Vehicle"),
                WhitelistEntry(recognized_plate="TN38AB1234", allowed_entry_gates="ALL", allowed_exit_gates="ALL", status="ACTIVE", remarks="Executive Transporter Fleet"),
                WhitelistEntry(recognized_plate="KA01AB1234", allowed_entry_gates="GATE-NORTH-01", allowed_exit_gates="GATE-NORTH-01", status="ACTIVE", remarks="Approved Raw Material Truck"),
            ]
            for w in whitelist_seeds:
                db.add(w)
            db.commit()
            print("Seeded default Whitelist entries.")

        # 2. Seed Watchlist Entries if empty
        from app.models.watchlist_entry import WatchlistEntry
        if db.query(WatchlistEntry).count() == 0:
            watchlist_seeds = [
                WatchlistEntry(plate_number="KA01AB9999", reason="Stolen Vehicle Alert", severity="CRITICAL", status="ACTIVE", remarks="Police Flagged Stolen Truck"),
                WatchlistEntry(plate_number="DL8CAF5032", reason="Expired Registration & Insurance", severity="HIGH", status="ACTIVE", remarks="Denied Entry until Renewal"),
                WatchlistEntry(plate_number="MH12CD4321", reason="Suspended Transporter Fleet", severity="MEDIUM", status="ACTIVE", remarks="Safety Violation Pending Investigation"),
            ]
            for w in watchlist_seeds:
                db.add(w)
            db.commit()
            print("Seeded default Watchlist entries.")

        # 3. Seed Initial Gate Decisions if empty
        from app.models.gate_decision import GateDecision
        if db.query(GateDecision).count() == 0:
            db.add(GateDecision(
                recognized_plate="MH14TCF200F",
                decision="ALLOW",
                reason="Approved Industrial Trip Verified (TRIP-2026-001)",
                confidence=0.98,
                decision_by="Automated AI Gate Decision Engine"
            ))
            db.commit()
            print("Seeded initial Gate Decision entry.")

    except Exception as e:
        print(f"Error during migration/seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_and_seed_authorization()
