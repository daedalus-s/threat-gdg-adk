"""Sensor data models for home threat detection."""

from typing import Literal
from pydantic import BaseModel, Field


class AccelerometerData(BaseModel):
    """Accelerometer/IMU data from wearables."""
    device_id: str
    timestamp: float
    x_axis: float
    y_axis: float
    z_axis: float
    magnitude: float
    event_type: Literal["normal", "fall", "impact", "violent_shake"] = "normal"


class HeartRateData(BaseModel):
    """Heart rate data from smartwatch."""
    device_id: str
    timestamp: float
    heart_rate: int = Field(ge=0, le=220)
    oxygen_saturation: float = Field(ge=0, le=100)
    blood_pressure_systolic: int = Field(ge=0)
    blood_pressure_diastolic: int = Field(ge=0)
    anomaly: bool = False


class AudioData(BaseModel):
    """Audio event data from microphone."""
    device_id: str
    timestamp: float
    sound_level_db: float
    frequency_hz: float
    event_classification: Literal[
        "silence", "normal_speech", "loud_noise", "scream",
        "glass_breaking", "door_slam", "alarm"
    ]
    confidence: float = Field(ge=0, le=1)


class SmokeDetectorData(BaseModel):
    """Smoke detector sensor data."""
    device_id: str
    timestamp: float
    smoke_level_ppm: float
    temperature_celsius: float
    co_level_ppm: float
    alarm_triggered: bool


class CameraFrame(BaseModel):
    """Camera frame data."""
    camera_id: int
    timestamp: float
    frame_number: int
    image_base64: str
    mime_type: str = "image/jpeg"