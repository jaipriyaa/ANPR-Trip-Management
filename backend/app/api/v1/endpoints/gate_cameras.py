from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.crud.crud_gate import crud_gate
from app.crud.crud_camera import crud_camera
from app.schemas.camera import CameraCreate, CameraUpdate, CameraResponse, CameraPaginatedResponse

router = APIRouter(prefix="/gate-cameras", tags=["Gate Cameras"])


@router.get("", response_model=CameraPaginatedResponse, summary="Get assigned cameras with search & filtering")
def get_cameras(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    gate_id: Optional[UUID] = Query(None, description="Filter cameras by gate_id"),
    search: Optional[str] = Query(None, description="Search by camera name, RTSP URL, or IP address"),
    camera_status: Optional[str] = Query(None, description="Filter by Online, Offline, Maintenance"),
):
    items, total = crud_camera.get_multi(
        db,
        skip=skip,
        limit=limit,
        gate_id=gate_id,
        search=search,
        camera_status=camera_status,
    )
    return {"total": total, "items": items}


@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED, summary="Assign a new camera to a gate")
def assign_camera(
    *,
    db: Session = Depends(get_db),
    camera_in: CameraCreate,
):
    gate = crud_gate.get(db, gate_id=camera_in.gate_id)
    if not gate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gate with ID {camera_in.gate_id} not found.",
        )
    return crud_camera.create(db, obj_in=camera_in)


@router.get("/{camera_id}", response_model=CameraResponse, summary="Get camera by ID")
def get_camera(
    *,
    db: Session = Depends(get_db),
    camera_id: UUID,
):
    camera = crud_camera.get(db, camera_id=camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with ID {camera_id} not found.",
        )
    return camera


@router.put("/{camera_id}", response_model=CameraResponse, summary="Update assigned camera details")
def update_camera(
    *,
    db: Session = Depends(get_db),
    camera_id: UUID,
    camera_in: CameraUpdate,
):
    camera = crud_camera.get(db, camera_id=camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with ID {camera_id} not found.",
        )
    return crud_camera.update(db, db_obj=camera, obj_in=camera_in)


@router.delete("/{camera_id}", status_code=status.HTTP_200_OK, summary="Remove assigned camera from gate")
def delete_camera(
    *,
    db: Session = Depends(get_db),
    camera_id: UUID,
):
    camera = crud_camera.get(db, camera_id=camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with ID {camera_id} not found.",
        )
    crud_camera.remove(db, camera_id=camera_id)
    return {"success": True, "message": f"Camera '{camera.camera_name}' removed successfully."}
