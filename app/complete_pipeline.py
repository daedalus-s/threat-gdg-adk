"""Complete threat detection pipeline with proper agent integration."""

import asyncio
import json
import logging
import os
from typing import Any

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Set up authentication
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError(
        "GOOGLE_API_KEY not found! Please set it:\n"
        "PowerShell: $env:GOOGLE_API_KEY=\"your-key-here\"\n"
        "Or get your key from: https://aistudio.google.com/app/apikey"
    )

from app.agents.orchestrator_agent import create_orchestrator_agent
from app.agents.sensor_agent import create_sensor_agent
from app.sensors.simulator import SensorSimulator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def analyze_sensors(sensor_data: dict) -> dict[str, Any]:
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
    
    # Get the structured output from state
    async for event in runner.run_async(
        user_id="system",
        session_id="sensor_analysis",
        new_message=content
    ):
        pass  # Process events
    
    # Retrieve the analysis from session state
    session = await session_service.get_session(
        user_id="system",
        session_id="sensor_analysis",
        app_name="threat_detection"
    )
    
    return session.state.get("sensor_analysis", {})


async def make_decision(sensor_analysis: dict, scenario: str) -> dict[str, Any]:
    """Make final threat decision using orchestrator."""
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
    
    # Format the analysis data
    analysis_text = f"""
**Scenario**: {scenario.upper()}

**Sensor Analysis Results**:
- Threat Level: {sensor_analysis.get('threat_level', 'unknown')}
- Fall Detected: {sensor_analysis.get('fall_detected', False)}
- Vital Anomaly: {sensor_analysis.get('vital_anomaly', False)}
- Audio Threat: {sensor_analysis.get('audio_threat', False)}
- Fire Detected: {sensor_analysis.get('fire_detected', False)}
- Confidence: {sensor_analysis.get('confidence', 0.0):.2f}

**Recommendations**: {', '.join(sensor_analysis.get('recommendations', []))}

Make your final threat assessment.
"""
    
    content = types.Content(
        role="user",
        parts=[types.Part(text=analysis_text)]
    )
    
    async for event in runner.run_async(
        user_id="system",
        session_id="orchestrator",
        new_message=content
    ):
        pass  # Process events
    
    # Retrieve the decision from session state
    session = await session_service.get_session(
        user_id="system",
        session_id="orchestrator",
        app_name="threat_detection"
    )
    
    return session.state.get("threat_decision", {})


def print_results(scenario: str, sensor_data: dict, sensor_analysis: dict, decision: dict):
    """Pretty print the results."""
    print(f"\n{'='*70}")
    print(f"SCENARIO: {scenario.upper()}")
    print(f"{'='*70}")
    
    print("\n📊 SENSOR DATA SUMMARY:")
    print(f"  Heart Rate: {sensor_data['heart_rate']['heart_rate']} bpm")
    print(f"  O2 Saturation: {sensor_data['heart_rate']['oxygen_saturation']:.1f}%")
    print(f"  Accelerometer: {sensor_data['accelerometer']['magnitude']:.2f} m/s²")
    print(f"  Audio: {sensor_data['audio']['event_classification']}")
    print(f"  Smoke: {sensor_data['smoke_detector']['smoke_level_ppm']:.1f} ppm")
    
    print("\n🔍 SENSOR ANALYSIS:")
    print(f"  Threat Level: {sensor_analysis.get('threat_level', 'unknown').upper()}")
    print(f"  Fall Detected: {'YES' if sensor_analysis.get('fall_detected') else 'NO'}")
    print(f"  Vital Anomaly: {'YES' if sensor_analysis.get('vital_anomaly') else 'NO'}")
    print(f"  Audio Threat: {'YES' if sensor_analysis.get('audio_threat') else 'NO'}")
    print(f"  Fire Detected: {'YES' if sensor_analysis.get('fire_detected') else 'NO'}")
    print(f"  Confidence: {sensor_analysis.get('confidence', 0.0):.2%}")
    
    print("\n⚡ FINAL DECISION:")
    print(f"  Threat Level: {decision.get('threat_level', 'unknown').upper()}")
    print(f"  Action Required: {decision.get('action_required', 'unknown').upper()}")
    print(f"  Call 911: {'YES ☎️' if decision.get('call_911') else 'NO'}")
    
    print(f"\n💭 REASONING:")
    print(f"  {decision.get('reasoning', 'No reasoning provided')}")
    
    if decision.get('evidence'):
        print(f"\n📋 EVIDENCE:")
        for evidence in decision['evidence']:
            print(f"  • {evidence}")
    
    print(f"\n📢 ALERT MESSAGE:")
    print(f"  {decision.get('message_to_user', 'No message')}")
    print()


async def run_demo():
    """Run demonstration of all scenarios."""
    scenarios = ["normal", "intrusion", "fall", "fire"]
    
    for scenario in scenarios:
        # Generate sensor data
        sim = SensorSimulator(scenario)
        sensor_data = sim.generate_batch()
        
        # Analyze sensors
        logger.info(f"Analyzing {scenario} scenario...")
        sensor_analysis = await analyze_sensors(sensor_data)
        
        # Make final decision
        logger.info(f"Making threat decision for {scenario}...")
        decision = await make_decision(sensor_analysis, scenario)
        
        # Print results
        print_results(scenario, sensor_data, sensor_analysis, decision)
        
        # Pause between scenarios
        if scenario != scenarios[-1]:
            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(run_demo())