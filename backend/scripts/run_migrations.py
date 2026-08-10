#!/usr/bin/env python3
"""
Enterprise Database Migration & Initialization Script
Industrial ANPR Trip Management System
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add backend directory to sys.path
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("DB_Migration")


def wait_for_database(max_retries: int = 30, retry_interval: int = 2) -> bool:
    """Waits for the database connection to become available."""
    from app.core.config import settings
    from sqlalchemy import create_engine, text

    db_url = settings.DATABASE_URL
    logger.info(f"Connecting to database: {db_url.split('@')[-1] if '@' in db_url else db_url}")

    for attempt in range(1, max_retries + 1):
        try:
            engine = create_engine(db_url, connect_args={"connect_timeout": 5} if "postgresql" in db_url else {})
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✓ Database connection established successfully!")
            return True
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                time.sleep(retry_interval)
    logger.error("✗ Failed to connect to the database within timeout period.")
    return False


def run_alembic_migrations() -> bool:
    """Executes Alembic migrations to upgrade database schema to head."""
    logger.info("--- Running Alembic Schema Migrations ---")
    alembic_ini_path = BACKEND_DIR / "alembic.ini"
    if not alembic_ini_path.exists():
        logger.warning(f"Alembic configuration file not found at: {alembic_ini_path}. Skipping Alembic upgrade.")
        return False

    try:
        from alembic.config import Config
        from alembic import command

        alembic_cfg = Config(str(alembic_ini_path))
        alembic_cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
        
        from app.core.config import settings
        alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

        logger.info("Applying Alembic migrations ('alembic upgrade head')...")
        command.upgrade(alembic_cfg, "head")
        logger.info("✓ Alembic schema migrations completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Error during Alembic migration execution: {e}", exc_info=True)
        return False


def create_all_tables() -> bool:
    """Ensures all SQLAlchemy model tables are created in the database."""
    logger.info("--- Creating Missing ORM Tables ---")
    try:
        from app.database.connection import engine
        from app.database.base import Base
        import app.models  # Ensures all models register with Base.metadata

        Base.metadata.create_all(bind=engine)
        logger.info("✓ All database tables verified / created successfully!")
        return True
    except Exception as e:
        logger.error(f"Error creating ORM tables: {e}", exc_info=True)
        return False


def run_seed_migrations() -> None:
    """Executes modular seeding and data migration scripts."""
    logger.info("--- Executing Modular Seed & Data Migration Scripts ---")

    seed_modules = [
        ("Gates & Cameras", "scripts.migrate_gates", "migrate_and_seed"),
        ("Trips", "scripts.migrate_trips", "migrate_and_seed_trips"),
        ("Movements", "scripts.migrate_movements", "migrate_and_seed_movements"),
        ("Pipeline Data", "scripts.migrate_pipeline", "migrate_and_seed_pipeline"),
        ("Manual Review", "scripts.migrate_manual_review", "migrate_and_seed_manual_review"),
        ("Admin & Security", "scripts.migrate_admin", "migrate_and_seed_admin"),
        ("Authorization Engine", "scripts.migrate_authorization", "migrate_and_seed_authorization"),
    ]

    for label, module_name, func_name in seed_modules:
        try:
            mod = __import__(module_name, fromlist=[func_name])
            func = getattr(mod, func_name)
            logger.info(f"Running migration/seeding for [{label}]...")
            func()
            logger.info(f"✓ [{label}] seeding completed successfully.")
        except Exception as e:
            logger.error(f"✗ Failed seeding for [{label}]: {e}")


def main():
    logger.info("=========================================================")
    logger.info("Starting Enterprise ANPR Database Migration Runner...")
    logger.info("=========================================================")

    # 1. Check DB Connection
    if not wait_for_database():
        sys.exit(1)

    # 2. Run Alembic Schema Migrations
    alembic_success = run_alembic_migrations()

    # 3. Create missing tables via SQLAlchemy Metadata
    table_success = create_all_tables()

    # 4. Run Seed & Data Migration Scripts
    run_seed_migrations()

    logger.info("=========================================================")
    logger.info("DATABASE MIGRATION SUMMARY")
    logger.info("=========================================================")
    logger.info(f"Alembic Schema Upgrade: {'SUCCESS' if alembic_success else 'SKIPPED/WARNING'}")
    logger.info(f"ORM Table Creation:    {'SUCCESS' if table_success else 'FAILED'}")
    logger.info("=========================================================")


if __name__ == "__main__":
    main()
