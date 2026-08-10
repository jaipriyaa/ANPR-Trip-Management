import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


class CameraHealthLog(Base):
    __tablename__ = "camera_health"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id = Column(
        UUID(as_uuid=True),
        ForeignKey("gate_cameras.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    fps = Column(Float, nullable=False, default=30.0)
    latency_ms = Column(Float, nullable=False, default=15.0)
    status = Column(String(20), nullable=False, default="Online")  # Online, Offline, Maintenance
    rtsp_connected = Column(Boolean, default=True, nullable=False)
    last_frame_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    camera = relationship("Camera")
