from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

def now_utc():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_utc)

class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    sample_id = Column(String, nullable=False)
    food = Column(String, nullable=False)
    mode = Column(String, nullable=False)
    result = Column(String, nullable=False)
    model_output = Column(String, nullable=False)
    measurements_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_utc)

class Device(Base):
    __tablename__ = "devices"
    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, default="ESP32 device")
    key_hash = Column(String, nullable=False)
    connected = Column(Boolean, default=False)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    selected_food = Column(String, nullable=True)

class TestSession(Base):
    __tablename__ = "test_sessions"
    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(String, ForeignKey("devices.id"), nullable=False)
    sample_id = Column(String, nullable=False)
    food = Column(String, nullable=False)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), default=now_utc)

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True)
    device_id = Column(String, ForeignKey("devices.id"), nullable=False)
    session_id = Column(String, ForeignKey("test_sessions.id"), nullable=False)
    message_id = Column(String, nullable=False)
    food = Column(String, nullable=False)
    measured_at = Column(DateTime(timezone=True), nullable=False)
    received_at = Column(DateTime(timezone=True), default=now_utc)
    measurements_json = Column(Text, nullable=False)
    __table_args__ = (UniqueConstraint("device_id", "message_id", name="uq_device_message"),)
