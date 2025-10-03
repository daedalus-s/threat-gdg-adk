"""Sensor data analysis agent."""

from google.adk.agents import Agent
from typing import Any


def create_sensor_agent() -> Agent:
    """Create sensor analysis agent for non-video data."""
    
    instruction = """
    You are a health and safety sensor analysis agent. Analyze sensor data for threats.
    
    **SENSOR TYPES:**
    1. **Accelerometer**: Detect falls, violent movements, impacts
    2. **Heart Rate Monitor**: Detect vital sign anomalies
    3. **Audio**: Detect screams, glass breaking, alarms
    4. **Smoke Detector**: Detect fire hazards
    
    **CRITICAL THRESHOLDS:**
    - Heart Rate: <50 or >120 bpm = ALERT
    - Oxygen: <90% = CRITICAL
    - Blood Pressure: Systolic <90 or >160 = ALERT
    - Accelerometer: Magnitude >20 m/s² = FALL/IMPACT
    - Audio: Scream/Glass Breaking = ALERT
    - Smoke: >100 ppm = FIRE ALERT
    
    **OUTPUT FORMAT (JSON):**
    {
        "threat_level": "none|low|medium|high|critical",
        "alerts": {
            "fall_detected": false,
            "vital_anomaly": false,
            "audio_threat": false,
            "fire_detected": false
        },
        "vital_signs": {
            "heart_rate": 75,
            "oxygen_saturation": 98,
            "blood_pressure": "120/80"
        },
        "recommendations": ["Check on person", "Call emergency"],
        "confidence": 0.90
    }
    """
    
    return Agent(
        name="sensor_analysis_agent",
        model="gemini-2.5-flash",
        instruction=instruction,
        description="Analyzes sensor data for health and safety threats",
        output_key="sensor_analysis"
    )


def analyze_sensors(agent: Agent, sensor_data: dict[str, Any]) -> dict:
    """Analyze sensor data batch."""
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    import asyncio
    import json
    
    async def run_analysis():
        session_service = InMemorySessionService()
        await session_service.create_session(
            app_name="sensor_app",
            user_id="system",
            session_id="sensor_analysis"
        )
        
        runner = Runner(
            agent=agent,
            app_name="sensor_app",
            session_service=session_service
        )
        
        content = types.Content(
            role="user",
            parts=[types.Part(text=f"Analyze this sensor data:\n{json.dumps(sensor_data, indent=2)}")]
        )
        
        events = []
        async for event in runner.run_async(
            user_id="system",
            session_id="sensor_analysis",
            new_message=content
        ):
            events.append(event)
        
        for event in reversed(events):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        return {"analysis": part.text, "sensor_data": sensor_data}
        
        return {"analysis": "No analysis generated", "sensor_data": sensor_data}
    
    return asyncio.run(run_analysis())