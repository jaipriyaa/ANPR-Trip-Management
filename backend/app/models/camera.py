import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Camera(Base):
    __tablename__ = "gate_cameras"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("gates.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    camera_name = Column(String(100), nullable=False)
    camera_position = Column(String(50), nullable=False, default="Entry Camera")  # Entry Camera, Exit Camera, Top View, Side View
    rtsp_url = Column(String(500), nullable=False)
    ip_address = Column(String(50), nullable=True)
    camera_status = Column(String(20), nullable=False, default="Online")  # Online, Offline, Maintenance
    resolution = Column(String(30), nullable=True, default="1080p")
    fps = Column(Integer, nullable=True, default=30)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    gate = relationship("Gate", back_populates="cameras")
