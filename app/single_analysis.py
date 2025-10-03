"""Single analysis pipeline - analyze current state only."""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("GOOGLE_API_KEY not found!")

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agents.sensor_agent import create_sensor_agent
from app.agents.orchestrator_agent import create_orchestrator_agent
from app.sensors.simulator import SensorSimulator
from app.video.full_video_analyzer import analyze_full_video

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def analyze_sensors(sensor_data: dict) -> dict:
    """Analyze sensor data."""
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


async def analyze_cameras(video_files: Dict[int, str]) -> list:
    """Analyze all 5 camera feeds."""
    camera_analyses = []
    
    # Always check all 5 cameras
    for camera_id in range(1, 6):
        video_path = video_files.get(camera_id)
        
        if not video_path:
            logger.info(f"Camera {camera_id}: No video configured")
            camera_analyses.append({
                "camera_id": camera_id,
                "status": "not_configured",
                "threat_level": "none",
                "weapon_type": "none",
                "unfamiliar_face": False,
                "people_count": 0,
                "threats_detected": []
            })
            continue
        
        if not Path(video_path).exists():
            logger.warning(f"Camera {camera_id}: Video file not found - {video_path}")
            camera_analyses.append({
                "camera_id": camera_id,
                "status": "offline",
                "error": "Video file not found",
                "threat_level": "none",
                "weapon_type": "none",
                "unfamiliar_face": False,
                "people_count": 0,
                "threats_detected": []
            })
            continue
        
        try:
            logger.info(f"Analyzing Camera {camera_id}: {video_path}")
            analysis = await analyze_full_video(
                video_path=video_path,
                camera_id=camera_id,
                scenario=""  # No scenario - pure analysis
            )
            camera_analyses.append(analysis)
        except Exception as e:
            logger.error(f"Camera {camera_id} error: {e}")
            camera_analyses.append({
                "camera_id": camera_id,
                "status": "error",
                "error": str(e),
                "threat_level": "none",
                "weapon_type": "none",
                "unfamiliar_face": False,
                "people_count": 0,
                "threats_detected": []
            })
    
    return camera_analyses


async def make_decision(sensor_analysis: dict, camera_analyses: list) -> dict:
    """Orchestrator makes final decision."""
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
    
    # Build analysis text
    analysis_text = f"""
**THREAT ASSESSMENT**

**SENSOR ANALYSIS**:
- Threat Level: {sensor_analysis.get('threat_level', 'unknown')}
- Fall Detected: {sensor_analysis.get('fall_detected', False)}
- Vital Anomaly: {sensor_analysis.get('vital_anomaly', False)}
- Audio Threat: {sensor_analysis.get('audio_threat', False)}
- Fire Detected: {sensor_analysis.get('fire_detected', False)}

**CAMERA ANALYSIS (All 5 Cameras)**:
"""
    
    for cam in camera_analyses:
        cam_id = cam.get('camera_id')
        status = cam.get('status')
        
        if status == "not_configured":
            analysis_text += f"\n- Camera {cam_id}: NOT CONFIGURED"
        elif cam.get("error"):
            analysis_text += f"\n- Camera {cam_id}: OFFLINE ({status})"
        else:
            analysis_text += f"""
- Camera {cam_id}: ONLINE
  * Video Duration: {cam.get('video_duration', 0):.1f}s
  * Frames Analyzed: {cam.get('total_frames_analyzed', 0)}
  * Threat Level: {cam.get('threat_level', 'unknown')}
  * Weapon: {cam.get('weapon_type', 'none')}
  * Unfamiliar Face: {cam.get('unfamiliar_face', False)}
  * People Count: {cam.get('people_count', 0)}
"""
            if cam.get('weapons_detected'):
                analysis_text += f"  * Weapon detections: {len(cam['weapons_detected'])} frames\n"
                for wd in cam['weapons_detected'][:2]:
                    analysis_text += f"    - {wd['type']} at {wd['timestamp']:.1f}s\n"
            
            threats = cam.get('all_threats', [])
            if threats:
                analysis_text += f"  * Threats: {', '.join(threats)}\n"
    
    analysis_text += "\n\nMake your final threat assessment."
    
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


async def analyze_current_state(video_files: Dict[int, str], sensor_data: Optional[dict] = None):
    """
    Analyze current state - single analysis point.
    
    Args:
        video_files: Dict of camera_id -> video_path
        sensor_data: Optional sensor data (will simulate if not provided)
    """
    logger.info("Starting threat analysis...")
    
    # Get or simulate sensor data
    if not sensor_data:
        sim = SensorSimulator("normal")  # Default baseline
        sensor_data = sim.generate_batch()
    
    # Analyze sensors
    logger.info("Analyzing sensors...")
    sensor_analysis = await analyze_sensors(sensor_data)
    
    # Analyze cameras
    logger.info("Analyzing cameras...")
    camera_analyses = await analyze_cameras(video_files)
    
    # Make decision
    logger.info("Making threat decision...")
    decision = await make_decision(sensor_analysis, camera_analyses)
    
    return {
        "sensor_data": sensor_data,
        "sensor_analysis": sensor_analysis,
        "camera_analyses": camera_analyses,
        "decision": decision
    }


def print_results(result: dict):
    """Print analysis results."""
    sensor_analysis = result["sensor_analysis"]
    camera_analyses = result["camera_analyses"]
    decision = result["decision"]
    
    print(f"\n{'='*100}")
    print("HOME THREAT DETECTION - LIVE ANALYSIS")
    print(f"{'='*100}")
    
    print(f"\n[SENSORS] {sensor_analysis.get('threat_level', 'unknown').upper()}")
    print(f"  Fall: {'YES' if sensor_analysis.get('fall_detected') else 'NO'} | "
          f"Vitals: {'ANOMALY' if sensor_analysis.get('vital_anomaly') else 'NORMAL'} | "
          f"Fire: {'YES' if sensor_analysis.get('fire_detected') else 'NO'}")
    
    print(f"\n[CAMERAS - All 5 Camera System]")
    online_count = 0
    for cam in camera_analyses:
        cam_id = cam['camera_id']
        status = cam.get('status')
        
        if status == "not_configured":
            print(f"  Camera {cam_id}: NOT CONFIGURED")
        elif cam.get("error"):
            print(f"  Camera {cam_id}: {status.upper()}")
        else:
            online_count += 1
            threat = cam.get('threat_level', 'unknown').upper()
            weapon = cam.get('weapon_type', 'none')
            people = cam.get('people_count', 0)
            frames = cam.get('total_frames_analyzed', 0)
            duration = cam.get('video_duration', 0)
            
            print(f"  Camera {cam_id}: {threat} | Weapon: {weapon} | People: {people} | "
                  f"{frames} frames ({duration:.1f}s)")
            
            if cam.get('weapons_detected'):
                print(f"    → Weapon detected in {len(cam['weapons_detected'])} frames")
            if cam.get('unfamiliar_face'):
                print(f"    → Unknown person detected")
    
    print(f"\n  Status: {online_count}/5 cameras online")
    
    print(f"\n{'='*100}")
    print(f"[FINAL THREAT ASSESSMENT] {decision.get('threat_level', 'unknown').upper()}")
    print(f"{'='*100}")
    print(f"  Action Required: {decision.get('action_required', 'none').upper()}")
    print(f"  Emergency Response: {'CALL 911 NOW' if decision.get('call_911') else 'Not Required'}")
    print(f"\n  Reasoning: {decision.get('reasoning', 'No reasoning provided')}")
    print(f"\n  Alert: {decision.get('message_to_user', 'N/A')}")
    print(f"\n{'='*100}\n")


async def main():
    """Run single analysis with all 5 cameras."""
    
    # Configure all 5 cameras (add your video paths)
    video_files = {
        1: r"videos\fall.mp4",
        2: r"videos\fire.mp4",  # Add when available
        3: r"videos\weapon.mp4",
        4: r"videos\normal.mp4",
        # 5: r"videos\camera5.mp4",
    }
    
    print("\n" + "="*100)
    print("INITIALIZING HOME THREAT DETECTION SYSTEM")
    print("="*100)
    print("\nConfigured Cameras:")
    for cam_id in range(1, 6):
        if cam_id in video_files:
            print(f"  Camera {cam_id}: {video_files[cam_id]}")
        else:
            print(f"  Camera {cam_id}: Not configured")
    print()
    
    result = await analyze_current_state(video_files)
    print_results(result)


if __name__ == "__main__":
    asyncio.run(main())