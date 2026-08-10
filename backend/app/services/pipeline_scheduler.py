import logging
import threading
import time
from datetime import datetime, timezone
from app.database.session import SessionLocal
from app.services.data_pipeline_service import data_pipeline_service

logger = logging.getLogger(__name__)


class PipelineBackgroundScheduler:
    """
    Background scheduler executing periodic data pipeline tasks (Hourly & Daily).
    Runs idempotently in a background daemon thread.
    """
    def __init__(self, interval_seconds: int = 3600):
        self.interval_seconds = interval_seconds
        self.running = False
        self.thread = None

    def _run_loop(self):
        logger.info("PipelineBackgroundScheduler started background loop.")
        while self.running:
            try:
                db = SessionLocal()
                try:
                    # 1. Hourly tasks: Late arrival scan, Overstay scan, Entry/Exit matching, Deduplication
                    data_pipeline_service.deduplicate_detections(db)
                    data_pipeline_service.match_entry_exit_pairs(db)
                    data_pipeline_service.scan_late_arrivals(db)
                    data_pipeline_service.scan_overstay_vehicles(db)

                    # 2. Daily Summary generation
                    data_pipeline_service.generate_daily_summaries(db)

                    # 3. Sync OCR Feedback Dataset
                    data_pipeline_service.sync_ocr_feedback_dataset(db)

                    logger.info("PipelineBackgroundScheduler: Idempotent background job execution completed successfully.")
                except Exception as ex:
                    logger.error(f"Error during scheduled background job execution: {ex}", exc_info=True)
                finally:
                    db.close()
            except Exception as outer_ex:
                logger.error(f"Scheduler outer loop exception: {outer_ex}", exc_info=True)

            # Sleep until next interval
            time.sleep(self.interval_seconds)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            logger.info("Started PipelineBackgroundScheduler thread.")

    def stop(self):
        if self.running:
            self.running = False
            logger.info("Stopped PipelineBackgroundScheduler thread.")


pipeline_scheduler = PipelineBackgroundScheduler(interval_seconds=3600)
