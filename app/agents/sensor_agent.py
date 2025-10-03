"""Sensor data analysis agent."""

from google.adk.agents import Agent


def create_sensor_agent() -> Agent:
    """Create sensor analysis agent for non-video data."""
    
    instruction = """
    You are a health and safety sensor analysis agent.
    
    **CRITICAL THRESHOLDS:**
    - Heart Rate: <50 or >120 bpm = ALERT
    - Oxygen: <90% = CRITICAL
    - Accelerometer: Magnitude >20 m/sÂ² = FALL
    - Audio: Scream/Glass Breaking = ALERT
    - Smoke: >100 ppm = FIRE
    
    **OUTPUT (JSON format):**
    {
        "threat_level": "none|low|medium|high|critical",
        "alerts": {
            "fall_detected": false,
            "vital_anomaly": false,
            "audio_threat": false,
            "fire_detected": false
        },
        "recommendations": ["Check on person"],
        "confidence": 0.90
    }
    """
    
    return Agent(
        name="sensor_analysis_agent",
        model="gemini-2.5-flash",
        instruction=instruction,
        description="Analyzes sensor data for threats",
        output_key="sensor_analysis"
    )
