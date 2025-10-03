"""Sensor data analysis agent."""

from google.adk.agents import Agent
from pydantic import BaseModel, Field


class SensorAnalysis(BaseModel):
    """Structured output for sensor analysis."""
    threat_level: str = Field(description="none, low, medium, high, or critical")
    fall_detected: bool = Field(description="Whether a fall was detected")
    vital_anomaly: bool = Field(description="Whether vital signs are abnormal")
    audio_threat: bool = Field(description="Whether dangerous audio detected")
    fire_detected: bool = Field(description="Whether fire/smoke detected")
    recommendations: list[str] = Field(description="List of recommended actions")
    confidence: float = Field(description="Confidence score 0.0-1.0")


def create_sensor_agent() -> Agent:
    """Create sensor analysis agent for non-video data."""
    
    instruction = """
    You are a health and safety sensor analysis agent.
    
    **CRITICAL THRESHOLDS:**
    - Heart Rate: <50 or >120 bpm = ALERT
    - Oxygen: <90% = CRITICAL
    - Accelerometer: Magnitude >20 m/s² = FALL
    - Audio: Scream/Glass Breaking = ALERT
    - Smoke: >100 ppm = FIRE
    
    Analyze the sensor data and return a JSON response with:
    - threat_level: "none", "low", "medium", "high", or "critical"
    - fall_detected: true/false
    - vital_anomaly: true/false
    - audio_threat: true/false
    - fire_detected: true/false
    - recommendations: list of actions to take
    - confidence: 0.0 to 1.0
    """
    
    return Agent(
        name="sensor_analysis_agent",
        model="gemini-2.5-flash",
        instruction=instruction,
        description="Analyzes sensor data for threats",
        output_schema=SensorAnalysis,
        output_key="sensor_analysis"
    )