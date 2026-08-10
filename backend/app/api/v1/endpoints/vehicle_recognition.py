import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.vehicle_recognition_service import vehicle_recognition_service
from app.schemas.vehicle import VehicleRecognitionResponse, VehicleRecognitionPaginatedResponse
from app.schemas.vehicle_detection import VehicleDetectionResponse, VehicleDetectionPaginatedResponse
from app.crud.crud_vehicle_detection import crud_vehicle_detection

router = APIRouter(prefix="/vehicle-recognition", tags=["Vehicle Recognition"])


from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, status, Body

@router.post("/upload", status_code=status.HTTP_200_OK)
def upload_and_recognize(
    file: UploadFile = File(...),
    gate_id: Optional[str] = Form(None),
    driver_id: Optional[str] = Form(None),
    driver_name: Optional[str] = Form(None),
    transporter_id: Optional[str] = Form(None),
    direction: Optional[str] = Form(None),
    purpose: Optional[str] = Form(None),
    destination: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Upload a vehicle image or video for AI-based license plate recognition with auto-sync to Gate & Trip management."""
    return vehicle_recognition_service.process_upload(
        db,
        file,
        gate_id=gate_id,
        driver_id=driver_id,
        driver_name=driver_name,
        transporter_id=transporter_id,
        direction=direction,
        purpose=purpose,
        destination=destination,
    )


@router.post("/detections/{detection_id}/sync", status_code=status.HTTP_200_OK)
def sync_dataset_detection(
    detection_id: uuid.UUID,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    """Re-sync or manually update a recognition dataset entry across Master Catalog, Gate Management & Trip Engine."""
    return vehicle_recognition_service.sync_detection_record(
        db,
        detection_id=detection_id,
        plate_text=payload.get("plate_text"),
        driver_name=payload.get("driver_name"),
        gate_id=uuid.UUID(payload.get("gate_id")) if payload.get("gate_id") else None,
        direction=payload.get("direction"),
        purpose=payload.get("purpose"),
        destination=payload.get("destination"),
    )



@router.get("/vehicles", response_model=VehicleRecognitionPaginatedResponse)
def list_recognized_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by vehicle number"),
    db: Session = Depends(get_db),
):
    """List all vehicles that have been detected/recognized by the AI system."""
    items, total = vehicle_recognition_service.get_vehicles_with_detections(
        db, skip=skip, limit=limit, search=search
    )
    return VehicleRecognitionPaginatedResponse(total=total, items=items)


@router.get("/vehicles/{vehicle_id}", response_model=VehicleRecognitionResponse)
def get_recognized_vehicle(
    vehicle_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Get detailed vehicle information including detection history."""
    vehicle = vehicle_recognition_service.get_vehicle_detail(db, vehicle_id=vehicle_id)
    return vehicle


@router.get("/vehicles/{vehicle_id}/detections", response_model=VehicleDetectionPaginatedResponse)
def get_detection_history(
    vehicle_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get detection history for a specific vehicle."""
    items, total = vehicle_recognition_service.get_detection_history(
        db, vehicle_id=vehicle_id, skip=skip, limit=limit
    )
    return VehicleDetectionPaginatedResponse(total=total, items=items)


@router.get("/detections", response_model=VehicleDetectionPaginatedResponse)
def list_all_detections(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by plate text or filename"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by detection status"),
    db: Session = Depends(get_db),
):
    """List all detection events across all vehicles."""
    items, total = crud_vehicle_detection.get_multi(
        db, skip=skip, limit=limit, search=search, status=status_filter
    )
    return VehicleDetectionPaginatedResponse(total=total, items=items)


@router.get("/detections/{detection_id}", response_model=VehicleDetectionResponse)
def get_detection_detail(
    detection_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Get a specific detection event details."""
    detection = crud_vehicle_detection.get(db, detection_id=detection_id)
    if not detection:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Detection not found")
    return detection


@router.get("/search")
def search_by_plate(
    plate: str = Query(..., min_length=3, description="Plate number to search"),
    db: Session = Depends(get_db),
):
    """Search for a vehicle by its number plate."""
    from app.crud.crud_vehicle import crud_vehicle
    from app.crud.crud_vehicle_plate import crud_vehicle_plate

    plate_rec = crud_vehicle_plate.get_by_plate_number(db, plate_number=plate.upper())
    if plate_rec:
        vehicle = plate_rec.vehicle
    else:
        vehicle = crud_vehicle.get_by_number(db, vehicle_number=plate.upper())

    if not vehicle:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"No vehicle found with plate: {plate}")

    return vehicle


@router.get("/media/{file_type}/{filename}")
def serve_media(file_type: str, filename: str):
    """Serve uploaded or processed media files."""
    from app.ai import config
    project_root = config.PROJECT_ROOT
    backend_dir = os.path.join(project_root, "backend")
    uploads_dir = os.path.join(backend_dir, "uploads")
    debug_dir = os.path.join(project_root, "debug")

    possible_paths = []
    if file_type == "processed":
        possible_paths = [
            os.path.join(uploads_dir, "processed", filename),
            os.path.join(debug_dir, "vehicles", filename),
            os.path.join(debug_dir, "plates", filename),
            os.path.join(debug_dir, "rectified", filename),
            os.path.join(debug_dir, "enhanced", filename),
            os.path.join(debug_dir, "visualizations", filename),
            os.path.join(debug_dir, "original", filename),
            os.path.join(debug_dir, filename),
            os.path.join(backend_dir, "debug", "vehicles", filename),
            os.path.join(backend_dir, "debug", "plates", filename),
        ]
    elif file_type == "images":
        possible_paths = [
            os.path.join(uploads_dir, "images", filename),
            os.path.join(debug_dir, "original", filename),
        ]
    elif file_type == "videos":
        possible_paths = [
            os.path.join(uploads_dir, "videos", filename),
        ]
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid file type")

    for fp in possible_paths:
        if os.path.exists(fp):
            return FileResponse(fp)

    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail=f"File '{filename}' not found")
