"""
NVDSEventBridge: Processes DeepStream inference payloads & NVDSAnalytics metadata events.
Bridges edge hardware detections directly into FastAPI services and database decisions.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.services.vehicle_recognition_service import vehicle_recognition_service
from app.services.authorization_service import authorization_service

logger = logging.getLogger("deepstream.event_bridge")


class DeepStreamDetectionPayload(BaseModel):
    stream_id: str
    camera_id: str
    gate_id: Optional[str] = "GATE-ENTRY-01"
    license_plate: str
    confidence: float
    vehicle_type: Optional[str] = "Truck"
    tracking_id: int
    roi_zone: Optional[str] = "roi-gate-entry"
    line_crossing_event: Optional[str] = "line-crossing-entry"
    timestamp: Optional[str] = None


class NVDSEventBridge:
    def __init__(self):
        self.processed_events_count = 0

    def process_deepstream_payload(
        self,
        db: Session,
        payload: DeepStreamDetectionPayload,
    ) -> Dict[str, Any]:
        """
        Translates a DeepStream detection payload into local vehicle recognition & gate decision.
        """
        self.processed_events_count += 1
        clean_plate = payload.license_plate.strip().upper().replace(" ", "").replace("-", "")

        logger.info(
            f"[DeepStream Bridge] Event #{self.processed_events_count} received | "
            f"Stream: {payload.stream_id} | Plate: {clean_plate} (Conf: {payload.confidence:.2f}) | "
            f"Tracking ID: {payload.tracking_id}"
        )

        # Evaluate Gate Access using existing authorization engine
        auth_decision = authorization_service.evaluate_gate_access(
            db=db,
            plate_text=clean_plate,
            confidence=payload.confidence,
            gate_id=payload.gate_id,
            camera_id=payload.camera_id,
            tracking_id=payload.tracking_id,
        )

        return {
            "status": "SUCCESS",
            "event_index": self.processed_events_count,
            "license_plate": clean_plate,
            "confidence": payload.confidence,
            "tracking_id": payload.tracking_id,
            "gate_id": payload.gate_id,
            "authorization_decision": auth_decision,
            "timestamp": payload.timestamp or datetime.utcnow().isoformat(),
        }


_event_bridge_instance = NVDSEventBridge()


def get_event_bridge() -> NVDSEventBridge:
    return _event_bridge_instance
