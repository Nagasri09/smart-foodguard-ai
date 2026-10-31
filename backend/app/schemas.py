from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Optional
from datetime import datetime

class AuthIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
class AnalyzeIn(BaseModel):
    sample_id: str = Field(min_length=1, max_length=80)
    food: str
    mode: str
    measurements: Dict[str, float]
class DeviceIn(BaseModel):
    device_id: str = Field(min_length=3, max_length=80)
    name: str = "ESP32 device"
    device_key: str = Field(min_length=8)
class SessionIn(BaseModel):
    device_id: str
    sample_id: str
    food: str
class IngestIn(BaseModel):
    message_id: str = Field(min_length=1, max_length=120)
    session_id: str
    food: str
    measured_at: datetime
    measurements: Dict[str, float]
