"""
Sensor data simulators for home threat detection system.
Generates realistic sensor data in the format actual devices would produce.
"""

import random
import time
from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field


class AccelerometerData(BaseModel):
    """Accelerometer/IMU data format from wearables."""
    device_id: str
    timestamp: float
    x_axis: float = Field(description="X-axis acceleration in m/s²")
    y_axis: float = Field(description="Y-axis acceleration in m/s²")
    z_axis: float = Field(description="Z-axis acceleration in m/s²")
    magnitude: float = Field(description="Total acceleration magnitude")
    event_type: Literal["normal", "fall", "impact", "violent_shake"] = "normal"


class HeartRateData(BaseModel):
    """Heart rate data from smartwatch."""
    device_id: str
    timestamp: float
    heart_rate: int = Field(description="Beats per minute", ge=0, le=220)
    oxygen_saturation: float = Field(description="SpO2 percentage", ge=0, le=100)
    blood_pressure_systolic: int = Field(description="Systolic BP in mmHg", ge=0)
    blood_pressure_diastolic: int = Field(description="Diastolic BP in mmHg", ge=0)
    anomaly: bool = False


class AudioData(BaseModel):
    """Audio event data from microphone."""
    device_id: str
    timestamp: float
    sound_level_db: float = Field(description="Sound level in decibels")
    frequency_hz: float = Field(description="Dominant frequency in Hz")
    event_classification: Literal[
        "silence", "normal_speech", "loud_noise", "scream", 
        "glass_breaking", "door_slam", "alarm"
    ]
    confidence: float = Field(ge=0, le=1)


class SmokeDetectorData(BaseModel):
    """Smoke detector sensor data."""
    device_id: str
    timestamp: float
    smoke_level_ppm: float = Field(description="Smoke particles per million")
    temperature_celsius: float
    co_level_ppm: float = Field(description="Carbon monoxide level")
    alarm_triggered: bool


class SensorSimulator:
    """Simulates realistic sensor data for testing."""
    
    def __init__(self, scenario: Literal["normal", "intrusion", "fall", "fire"] = "normal"):
        self.scenario = scenario
        self.base_timestamp = time.time()
    
    def generate_accelerometer_data(
        self, 
        device_id: str = "wearable_001"
    ) -> AccelerometerData:
        """Generate accelerometer data based on scenario."""
        timestamp = time.time()
        
        if self.scenario == "fall":
            # Simulate a fall: high downward acceleration followed by impact
            x = random.uniform(-2, 2)
            y = random.uniform(-2, 2)
            z = random.uniform(-25, -15)  # Strong downward
            event_type = "fall"
        elif self.scenario == "intrusion":
            # Simulate violent shake during struggle
            x = random.uniform(-15, 15)
            y = random.uniform(-15, 15)
            z = random.uniform(-15, 15)
            event_type = "violent_shake"
        else:
            # Normal movement
            x = random.uniform(-1.5, 1.5)
            y = random.uniform(-1.5, 1.5)
            z = random.uniform(9.5, 10.5)  # Gravity + small movement
            event_type = "normal"
        
        magnitude = (x**2 + y**2 + z**2) ** 0.5
        
        return AccelerometerData(
            device_id=device_id,
            timestamp=timestamp,
            x_axis=x,
            y_axis=y,
            z_axis=z,
            magnitude=magnitude,
            event_type=event_type
        )
    
    def generate_heart_rate_data(
        self, 
        device_id: str = "smartwatch_001"
    ) -> HeartRateData:
        """Generate heart rate data based on scenario."""
        timestamp = time.time()
        
        if self.scenario == "fall":
            # After a fall: potential drop in vitals
            heart_rate = random.randint(45, 60)
            oxygen_saturation = random.uniform(85, 92)
            bp_systolic = random.randint(85, 100)
            bp_diastolic = random.randint(50, 65)
            anomaly = True
        elif self.scenario == "intrusion":
            # During threat: elevated stress response
            heart_rate = random.randint(120, 150)
            oxygen_saturation = random.uniform(94, 98)
            bp_systolic = random.randint(140, 170)
            bp_diastolic = random.randint(90, 105)
            anomaly = True
        else:
            # Normal resting vitals
            heart_rate = random.randint(60, 80)
            oxygen_saturation = random.uniform(96, 99)
            bp_systolic = random.randint(110, 130)
            bp_diastolic = random.randint(70, 85)
            anomaly = False
        
        return HeartRateData(
            device_id=device_id,
            timestamp=timestamp,
            heart_rate=heart_rate,
            oxygen_saturation=oxygen_saturation,
            blood_pressure_systolic=bp_systolic,
            blood_pressure_diastolic=bp_diastolic,
            anomaly=anomaly
        )
    
    def generate_audio_data(
        self, 
        device_id: str = "mic_001"
    ) -> AudioData:
        """Generate audio event data based on scenario."""
        timestamp = time.time()
        
        if self.scenario == "intrusion":
            events = [
                ("scream", random.uniform(85, 105), random.uniform(800, 1200)),
                ("glass_breaking", random.uniform(90, 110), random.uniform(2000, 4000)),
                ("door_slam", random.uniform(85, 95), random.uniform(100, 300)),
            ]
            event_choice = random.choice(events)
            event_classification = event_choice[0]
            sound_level = event_choice[1]
            frequency = event_choice[2]
            confidence = random.uniform(0.75, 0.95)
        elif self.scenario == "fire":
            event_classification = "alarm"
            sound_level = random.uniform(95, 110)
            frequency = random.uniform(2000, 3500)
            confidence = random.uniform(0.85, 0.98)
        else:
            # Normal household sounds
            event_classification = random.choice(["silence", "normal_speech"])
            sound_level = random.uniform(30, 55) if event_classification == "normal_speech" else random.uniform(15, 30)
            frequency = random.uniform(200, 500)
            confidence = random.uniform(0.6, 0.85)
        
        return AudioData(
            device_id=device_id,
            timestamp=timestamp,
            sound_level_db=sound_level,
            frequency_hz=frequency,
            event_classification=event_classification,
            confidence=confidence
        )
    
    def generate_smoke_detector_data(
        self, 
        device_id: str = "smoke_001"
    ) -> SmokeDetectorData:
        """Generate smoke detector data based on scenario."""
        timestamp = time.time()
        
        if self.scenario == "fire":
            smoke_level = random.uniform(150, 500)
            temperature = random.uniform(35, 65)
            co_level = random.uniform(50, 200)
            alarm = True
        else:
            smoke_level = random.uniform(0, 10)
            temperature = random.uniform(18, 24)
            co_level = random.uniform(0, 5)
            alarm = False
        
        return SmokeDetectorData(
            device_id=device_id,
            timestamp=timestamp,
            smoke_level_ppm=smoke_level,
            temperature_celsius=temperature,
            co_level_ppm=co_level,
            alarm_triggered=alarm
        )
    
    def generate_batch_sensor_data(self) -> dict[str, Any]:
        """Generate a complete batch of sensor data."""
        return {
            "accelerometer": self.generate_accelerometer_data().model_dump(),
            "heart_rate": self.generate_heart_rate_data().model_dump(),
            "audio": self.generate_audio_data().model_dump(),
            "smoke_detector": self.generate_smoke_detector_data().model_dump(),
        }