import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Gate(Base):
    __tablename__ = "gates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gate_code = Column(String(50), nullable=False, unique=True, index=True)
    gate_name = Column(String(100), nullable=False)
    gate_type = Column(String(30), nullable=False, default="Entry & Exit")  # Entry, Exit, Entry & Exit
    location = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="ACTIVE")
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    cameras = relationship("Camera", back_populates="gate", cascade="all, delete-orphan")
    rule = relationship("GateRule", back_populates="gate", uselist=False, cascade="all, delete-orphan")
