from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, Integer, JSON, String, Text, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

def now(): return datetime.now(timezone.utc)
class Device(Base):
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    device_type: Mapped[str] = mapped_column(String(30))
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    status: Mapped[str] = mapped_column(String(20), default="online")
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
class DetectionEvent(Base):
    __tablename__ = "detection_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)
    detected: Mapped[bool] = mapped_column(Boolean, default=False)
    detection_class: Mapped[str | None] = mapped_column(String(80), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    image_path: Mapped[str | None] = mapped_column(String(300), nullable=True)
    sensor_readings: Mapped[dict] = mapped_column(JSON, default=dict)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.device_id"), index=True)
    capture_status: Mapped[str] = mapped_column(String(30), default="awaiting_image")
    repellent_events = relationship("RepellentEvent", back_populates="detection")
    @property
    def repellent_id(self):
        return self.repellent_events[0].id if self.repellent_events else None
class RepellentEvent(Base):
    __tablename__ = "repellent_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    detection_id: Mapped[int | None] = mapped_column(ForeignKey("detection_events.id"), nullable=True)
    activation_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    duration_s: Mapped[int] = mapped_column(Integer, default=0)
    frequencies: Mapped[list] = mapped_column(JSON, default=list)
    outcome: Mapped[str] = mapped_column(String(40), default="started")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    command_claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    detection = relationship("DetectionEvent", back_populates="repellent_events")
class SystemConfiguration(Base):
    __tablename__ = "system_configuration"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(80), unique=True)
    value: Mapped[str] = mapped_column(Text)

Index("ix_detection_timestamp_device", DetectionEvent.timestamp, DetectionEvent.device_id)
