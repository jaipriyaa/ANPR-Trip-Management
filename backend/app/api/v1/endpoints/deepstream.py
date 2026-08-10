"""
DeepStream 7.x & Edge Vision API Endpoints
Provides runtime controls for dynamic RTSP stream addition/removal, pipeline metrics, and metadata event ingestion.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.dependencies import get_db
from app.deepstream.stream_manager import get_stream_manager, StreamManager, StreamInfo
from app.deepstream.nvds_event_bridge import get_event_bridge, NVDSEventBridge, DeepStreamDetectionPayload

router = APIRouter()


class AddStreamRequest(BaseModel):
    name: str
    rtsp_url: str
    gate_id: Optional[str] = None
    camera_type: str = "GATE_IN"  # GATE_IN or GATE_OUT


@router.get("/streams", response_model=List[StreamInfo], summary="List all active DeepStream RTSP video feeds")
def get_deepstream_streams(
    manager: StreamManager = Depends(get_stream_manager),
):
    """Retrieves all RTSP streams currently multiplexed in the DeepStream pipeline."""
    return manager.list_streams()


@router.post("/streams", response_model=StreamInfo, status_code=status.HTTP_201_CREATED, summary="Dynamically add an RTSP camera stream")
def add_deepstream_stream(
    payload: AddStreamRequest,
    manager: StreamManager = Depends(get_stream_manager),
):
    """
    Dynamically adds a new camera RTSP stream to the running DeepStream pipeline
    without stopping the hardware video pipeline (runtime_source_add_delete).
    """
    return manager.add_stream(
        name=payload.name,
        rtsp_url=payload.rtsp_url,
        gate_id=payload.gate_id,
        camera_type=payload.camera_type,
    )


@router.delete("/streams/{stream_id}", status_code=status.HTTP_200_OK, summary="Dynamically remove an RTSP camera stream")
def remove_deepstream_stream(
    stream_id: str,
    manager: StreamManager = Depends(get_stream_manager),
):
    """Dynamically removes an active RTSP stream from the DeepStream video pipeline."""
    success = manager.remove_stream(stream_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DeepStream stream with ID '{stream_id}' not found.",
        )
    return {"status": "SUCCESS", "message": f"Stream '{stream_id}' removed from pipeline."}


@router.get("/metrics", summary="Get DeepStream GPU & GStreamer hardware performance metrics")
def get_deepstream_metrics(
    manager: StreamManager = Depends(get_stream_manager),
):
    """Returns GPU usage, FPS throughput, latency, and active stream count."""
    return manager.get_pipeline_metrics()


@router.post("/webhook", summary="DeepStream Metadata & Event Ingestion Webhook")
def deepstream_webhook_event(
    payload: DeepStreamDetectionPayload,
    db: Session = Depends(get_db),
    bridge: NVDSEventBridge = Depends(get_event_bridge),
):
    """
    Ingests live inference metadata events directly from DeepStream's Kafka / HTTP msg-broker.
    Triggers automatic gate decision evaluations and records detections.
    """
    return bridge.process_deepstream_payload(db=db, payload=payload)
