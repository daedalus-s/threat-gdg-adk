"""Simple pipeline without video processing for initial testing."""

import asyncio
import logging
import json
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.sensors.simulator import SensorSimulator
from app.agents.sensor_agent import create_sensor_agent
from app.agents.orchestrator_agent import create_orchestrator_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def analyze_sensors(sensor_data: dict) -> str:
    """Analyze sensor data using ADK agent."""
    sensor_agent = create_sensor_agent()
    
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="threat_detection",
        user_id="system",
        session_id="sensor_analysis"
    )
    
    runner = Runner(
        agent=sensor_agent,
        app_name="threat_detection",
        session_service=session_service
    )
    
    content = types.Content(
        role="user",
        parts=[types.Part(text=f"Analyze this sensor data:\n{json.dumps(sensor_data, indent=2)}")]
    )
    
    response_text = ""
    async for event in runner.run_async(
        user_id="system",
        session_id="sensor_analysis",
        new_message=content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text = part.text
    
    return response_text


async def make_decision(sensor_analysis: str, scenario: str) -> str:
    """Make final threat decision."""
    orchestrator = create_orchestrator_agent()
    
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="threat_detection",
        user_id="system",
        session_id="orchestrator"
    )
    
    runner = Runner(
        agent=orchestrator,
        app_name="threat_detection",
        session_service=session_service
    )
    
    content = types.Content(
        role="user",
        parts=[types.Part(text=f"""
Scenario: {scenario}
Sensor Analysis: {sensor_analysis}

Make final threat assessment.
""")]
    )
    
    decision_text = ""
    async for event in runner.run_async(
        user_id="system",
        session_id="orchestrator",
        new_message=content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    decision_text = part.text
    
    return decision_text


async def run_demo():
    """Run demonstration."""
    scenarios = ["normal", "intrusion", "fall", "fire"]
    
    for scenario in scenarios:
        print(f"\n{'='*60}")
        print(f"SCENARIO: {scenario.upper()}")
        print(f"{'='*60}\n")
        
        # Generate sensor data
        sim = SensorSimulator(scenario)
        sensor_data = sim.generate_batch()
        
        print("Sensor Data Generated:")
        print(json.dumps(sensor_data, indent=2)[:500] + "...")
        
        # Analyze sensors
        print("\nAnalyzing sensors with ADK...")
        sensor_analysis = await analyze_sensors(sensor_data)
        print(f"Sensor Analysis: {sensor_analysis[:200]}...")
        
        # Make final decision
        print("\nMaking final threat decision...")
        decision = await make_decision(sensor_analysis, scenario)
        print(f"\nFINAL DECISION:\n{decision}\n")
        
        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(run_demo())
