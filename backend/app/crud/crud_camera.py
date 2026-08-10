from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate


class CRUDCamera:
    def get(self, db: Session, camera_id: UUID) -> Optional[Camera]:
        return db.query(Camera).filter(Camera.id == camera_id).first()

    def get_by_gate(self, db: Session, gate_id: UUID) -> List[Camera]:
        return db.query(Camera).filter(Camera.gate_id == gate_id).order_by(Camera.created_at.desc()).all()

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        gate_id: Optional[UUID] = None,
        search: Optional[str] = None,
        camera_status: Optional[str] = None,
    ) -> Tuple[List[Camera], int]:
        query = db.query(Camera)

        if gate_id:
            query = query.filter(Camera.gate_id == gate_id)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Camera.camera_name.ilike(search_pattern),
                    Camera.rtsp_url.ilike(search_pattern),
                    Camera.ip_address.ilike(search_pattern),
                )
            )

        if camera_status:
            query = query.filter(Camera.camera_status == camera_status)

        total = query.count()
        items = query.order_by(Camera.created_at.desc()).offset(skip).limit(limit).all()

        return items, total

    def create(self, db: Session, *, obj_in: CameraCreate) -> Camera:
        db_obj = Camera(
            gate_id=obj_in.gate_id,
            camera_name=obj_in.camera_name.strip(),
            camera_position=obj_in.camera_position,
            rtsp_url=obj_in.rtsp_url.strip(),
            ip_address=obj_in.ip_address.strip() if obj_in.ip_address else None,
            camera_status=obj_in.camera_status,
            resolution=obj_in.resolution,
            fps=obj_in.fps,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Camera, obj_in: CameraUpdate) -> Camera:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if isinstance(value, str):
                value = value.strip()
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, camera_id: UUID) -> Optional[Camera]:
        obj = db.query(Camera).get(camera_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


crud_camera = CRUDCamera()
