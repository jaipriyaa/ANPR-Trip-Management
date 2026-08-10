import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base


class ArchiveJob(Base):
    __tablename__ = "archive_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_name = Column(String(100), nullable=False)
    target_table = Column(String(100), nullable=False)
    records_archived = Column(Integer, nullable=False, default=0)
    retention_days = Column(Integer, nullable=False, default=180)
    status = Column(String(30), nullable=False, default="SUCCESS")  # RUNNING, SUCCESS, FAILED
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    logs = relationship("ArchiveLog", back_populates="job", cascade="all, delete-orphan")


class ArchiveLog(Base):
    __tablename__ = "archive_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("archive_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    action = Column(String(50), nullable=False)
    records_affected = Column(Integer, nullable=False, default=0)
    message = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    job = relationship("ArchiveJob", back_populates="logs")
