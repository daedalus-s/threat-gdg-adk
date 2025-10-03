"""Complete threat detection pipeline with video and sensor analysis."""

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
from app.video.enhanced_frame_extractor import EnhancedCameraFrameExtractor
from app.video.vision_analyzer import analyze_frame

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
    
    async for event in runner.run_async(
        user_id="system",
        session_id="sensor_analysis",
        new_message=content
    ):
        pass
    
    session = await session_service.get_session(
        user_id="system",
        session_id="sensor_analysis",
        app_name="threat_detection"
    )
    
    return session.state.get("sensor_analysis", {})


async def analyze_cameras(scenario: str, num_cameras: int = 5) -> list[dict[str, Any]]:
    """Analyze frames from multiple cameras."""
    camera_analyses = []
    
    for camera_id in range(1, num_cameras + 1):
        try:
            with EnhancedCameraFrameExtractor(camera_id, scenario) as extractor:
                # Get first frame
                frame = next(extractor.extract_frames(num_frames=1))
                
                # Analyze frame
                logger.info(f"Analyzing Camera {camera_id}...")
                analysis = await analyze_frame(
                    camera_id=camera_id,
                    image_base64=frame.image_base64,
                    scenario=scenario
                )
                camera_analyses.append(analysis)
                
        except Exception as e:
            logger.error(f"Camera {camera_id} error: {e}")
            camera_analyses.append({
                "camera_id": camera_id,
                "error": str(e),
                "status": "offline"
            })
    
    return camera_analyses


async def make_decision(
    sensor_analysis: dict,
    camera_analyses: list[dict],
    scenario: str
) -> dict[str, Any]:
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
    
    # Format comprehensive analysis
    analysis_text = f"""
**Scenario**: {scenario.upper()}

**SENSOR ANALYSIS**:
- Threat Level: {sensor_analysis.get('threat_level', 'unknown')}
- Fall Detected: {sensor_analysis.get('fall_detected', False)}
- Vital Anomaly: {sensor_analysis.get('vital_anomaly', False)}
- Audio Threat: {sensor_analysis.get('audio_threat', False)}
- Fire Detected: {sensor_analysis.get('fire_detected', False)}

**CAMERA ANALYSIS**:
"""
    
    for cam_analysis in camera_analyses:
        if cam_analysis.get("error"):
            analysis_text += f"\n- Camera {cam_analysis['camera_id']}: OFFLINE"
        else:
            analysis_text += f"""
- Camera {cam_analysis['camera_id']}:
  * Threat Level: {cam_analysis.get('threat_level', 'unknown')}
  * Weapon: {cam_analysis.get('weapon_type', 'none')}
  * Unfamiliar Face: {cam_analysis.get('unfamiliar_face', False)}
  * People Count: {cam_analysis.get('people_count', 0)}
  * Threats: {', '.join(cam_analysis.get('threats_detected', []))}
"""
    
    analysis_text += "\n\nMake your final threat assessment based on ALL data."
    
    content = types.Content(
        role="user",
        parts=[types.Part(text=analysis_text)]
    )
    
    async for event in runner.run_async(
        user_id="system",
        session_id="orchestrator",
        new_message=content
    ):
        pass
    
    session = await session_service.get_session(
        user_id="system",
        session_id="orchestrator",
        app_name="threat_detection"
    )
    
    return session.state.get("threat_decision", {})


def print_results(
    scenario: str,
    sensor_data: dict,
    sensor_analysis: dict,
    camera_analyses: list[dict],
    decision: dict
):
    """Pretty print comprehensive results."""
    print(f"\n{'='*80}")
    print(f"🏠 HOME THREAT DETECTION - SCENARIO: {scenario.upper()}")
    print(f"{'='*80}")
    
    # Sensor Data
    print("\n📊 SENSOR DATA:")
    print(f"  ❤️  Heart Rate: {sensor_data['heart_rate']['heart_rate']} bpm")
    print(f"  🫁 O2 Saturation: {sensor_data['heart_rate']['oxygen_saturation']:.1f}%")
    print(f"  📱 Accelerometer: {sensor_data['accelerometer']['magnitude']:.2f} m/s²")
    print(f"  🔊 Audio: {sensor_data['audio']['event_classification']}")
    print(f"  💨 Smoke Level: {sensor_data['smoke_detector']['smoke_level_ppm']:.1f} ppm")
    
    # Sensor Analysis
    print("\n🔍 SENSOR ANALYSIS:")
    print(f"  Threat Level: {sensor_analysis.get('threat_level', 'unknown').upper()}")
    print(f"  Fall: {'✓' if sensor_analysis.get('fall_detected') else '✗'}")
    print(f"  Vital Anomaly: {'✓' if sensor_analysis.get('vital_anomaly') else '✗'}")
    print(f"  Audio Threat: {'✓' if sensor_analysis.get('audio_threat') else '✗'}")
    print(f"  Fire: {'✓' if sensor_analysis.get('fire_detected') else '✗'}")
    
    # Camera Analysis
    print("\n📹 CAMERA ANALYSIS:")
    for cam in camera_analyses:
        if cam.get("error"):
            print(f"  Camera {cam['camera_id']}: ❌ OFFLINE")
        else:
            threats = ", ".join(cam.get('threats_detected', [])) or "None"
            print(f"  Camera {cam['camera_id']}: {cam.get('threat_level', 'unknown').upper()}")
            print(f"    • Weapon: {cam.get('weapon_type', 'none')}")
            print(f"    • Unknown Person: {'YES' if cam.get('unfamiliar_face') else 'NO'}")
            print(f"    • Threats: {threats}")
    
    # Final Decision
    print("\n" + "="*80)
    print(f"⚡ FINAL DECISION: {decision.get('threat_level', 'unknown').upper()}")
    print("="*80)
    print(f"  Action: {decision.get('action_required', 'unknown').upper()}")
    print(f"  Call 911: {'☎️  YES - EMERGENCY' if decision.get('call_911') else '✗ NO'}")
    
    print(f"\n💭 REASONING:")
    print(f"  {decision.get('reasoning', 'No reasoning provided')}")
    
    if decision.get('evidence'):
        print(f"\n📋 EVIDENCE:")
        for evidence in decision['evidence']:
            print(f"  • {evidence}")
    
    print(f"\n📢 USER ALERT:")
    print(f"  {decision.get('message_to_user', 'No message')}")
    print("\n" + "="*80 + "\n")


async def process_scenario(scenario: str):
    """Process a complete threat detection cycle."""
    logger.info(f"Starting {scenario} scenario...")
    
    # Generate sensor data
    sim = SensorSimulator(scenario)
    sensor_data = sim.generate_batch()
    
    # Analyze sensors
    logger.info("Analyzing sensors...")
    sensor_analysis = await analyze_sensors(sensor_data)
    
    # Analyze cameras
    logger.info("Analyzing camera feeds...")
    camera_analyses = await analyze_cameras(scenario, num_cameras=5)
    
    # Make final decision
    logger.info("Making final threat decision...")
    decision = await make_decision(sensor_analysis, camera_analyses, scenario)
    
    # Display results
    print_results(scenario, sensor_data, sensor_analysis, camera_analyses, decision)
    
    return {
        "scenario": scenario,
        "sensor_data": sensor_data,
        "sensor_analysis": sensor_analysis,
        "camera_analyses": camera_analyses,
        "decision": decision
    }


async def run_demo():
    """Run demonstration of all scenarios."""
    scenarios = ["normal", "intrusion", "fall", "fire"]
    results = []
    
    for i, scenario in enumerate(scenarios):
        result = await process_scenario(scenario)
        results.append(result)
        
        # Pause between scenarios
        if i < len(scenarios) - 1:
            print("⏳ Waiting 3 seconds before next scenario...\n")
            await asyncio.sleep(3)
    
    # Summary
    print("\n" + "="*80)
    print("📊 DEMO SUMMARY")
    print("="*80)
    for result in results:
        decision = result["decision"]
        print(f"{result['scenario'].upper():12} | {decision.get('threat_level', 'unknown').upper():10} | 911: {'YES' if decision.get('call_911') else 'NO'}")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n🚀 Starting Home Threat Detection System Demo\n")
    asyncio.run(run_demo())