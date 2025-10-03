"""Sensor data simulators for threat scenarios."""

import random
import time
from typing import Literal, Any
from .models import (
    AccelerometerData, HeartRateData, AudioData,
    SmokeDetectorData
)


class SensorSimulator:
    """Simulates realistic sensor data for different scenarios."""
    
    def __init__(
        self,
        scenario: Literal["normal", "intrusion", "fall", "fire"] = "normal"
    ):
        self.scenario = scenario
    
    def generate_accelerometer_data(
        self,
        device_id: str = "wearable_001"
    ) -> AccelerometerData:
        """Generate accelerometer data based on scenario."""
        timestamp = time.time()
        
        if self.scenario == "fall":
            x, y = random.uniform(-2, 2), random.uniform(-2, 2)
            z = random.uniform(-25, -15)  # Strong downward
            event_type = "fall"
        elif self.scenario == "intrusion":
            x = random.uniform(-15, 15)
            y = random.uniform(-15, 15)
            z = random.uniform(-15, 15)
            event_type = "violent_shake"
        else:
            x, y = random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5)
            z = random.uniform(9.5, 10.5)
            event_type = "normal"
        
        magnitude = (x**2 + y**2 + z**2) ** 0.5
        
        return AccelerometerData(
            device_id=device_id,
            timestamp=timestamp,
            x_axis=x, y_axis=y, z_axis=z,
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
            heart_rate = random.randint(45, 60)
            oxygen_saturation = random.uniform(85, 92)
            bp_systolic = random.randint(85, 100)
            bp_diastolic = random.randint(50, 65)
            anomaly = True
        elif self.scenario == "intrusion":
            heart_rate = random.randint(120, 150)
            oxygen_saturation = random.uniform(94, 98)
            bp_systolic = random.randint(140, 170)
            bp_diastolic = random.randint(90, 105)
            anomaly = True
        else:
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
            event_classification = random.choice(["silence", "normal_speech"])
            sound_level = (
                random.uniform(30, 55) if event_classification == "normal_speech"
                else random.uniform(15, 30)
            )
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
    
    def generate_batch(self) -> dict[str, Any]:
        """Generate complete sensor batch."""
        return {
            "accelerometer": self.generate_accelerometer_data().model_dump(),
            "heart_rate": self.generate_heart_rate_data().model_dump(),
            "audio": self.generate_audio_data().model_dump(),
            "smoke_detector": self.generate_smoke_detector_data().model_dump(),
        }