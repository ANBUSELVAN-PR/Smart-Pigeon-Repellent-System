from datetime import datetime
from pydantic import BaseModel, Field
class SensorEventIn(BaseModel):
    device_id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,80}$")
    motion: bool
    distance_cm: float | None = Field(default=None, ge=0, le=10000)
    camera_id: str | None = None
    readings: dict = {}
class DetectionOut(BaseModel):
    id: int; timestamp: datetime; detected: bool; detection_class: str | None; confidence: float | None; image_path: str | None; capture_status: str; repellent_id: int | None = None
    class Config: from_attributes = True
class ConfigOut(BaseModel):
    detection_distance_cm: float; confidence_threshold: float; buzzer_min_hz: int; buzzer_max_hz: int; cooldown_s: int
class RepellentStatusIn(BaseModel):
    device_id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,80}$")
    repellent_id: int
    status: str = Field(pattern=r"^(started|frequency_changed|completed|stopped|timeout|communication_failed)$")
    duration_s: int = Field(default=0, ge=0)
    frequency_hz: int | None = Field(default=None, ge=1)
