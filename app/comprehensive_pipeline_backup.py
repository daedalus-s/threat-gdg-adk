"""Comprehensive pipeline analyzing all 5 cameras + sensors together."""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

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


class ComprehensiveThreatDetectionPipeline:
    """Complete threat detection analyzing all cameras and sensors together."""
    
    def __init__(self, video_directory: str = "videos"):
        self.video_dir = Path(video_directory)
        if not self.video_dir.exists():
            self.video_dir.mkdir(parents=True, exist_ok=True)
    
    async def analyze_all_sensors(self, sensor_data: dict) -> dict[str, Any]:
        """Analyze all sensor data with sensor agent."""
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
    
    async def analyze_all_cameras(
        self,
        video_files: Dict[int, str],
        scenario: str
    ) -> list[dict[str, Any]]:
        """Analyze all 5 camera feeds with full video analysis."""
        camera_analyses = []
        
        for camera_id in range(1, 6):  # Cameras 1-5
            video_path = video_files.get(camera_id)
            
            if not video_path:
                logger.warning(f"No video file configured for Camera {camera_id}")
                camera_analyses.append({
                    "camera_id": camera_id,
                    "error": "No video file configured",
                    "status": "not_configured"
                })
                continue
            
            if not Path(video_path).exists():
                logger.warning(f"Video file not found for Camera {camera_id}: {video_path}")
                camera_analyses.append({
                    "camera_id": camera_id,
                    "error": f"File not found: {video_path}",
                    "status": "offline"
                })
                continue
            
            try:
                logger.info(f"Analyzing Camera {camera_id}: {video_path}")
                analysis = await analyze_full_video(
                    video_path=video_path,
                    camera_id=camera_id,
                    scenario=scenario
                )
                camera_analyses.append(analysis)
                
            except Exception as e:
                logger.error(f"Error analyzing Camera {camera_id}: {e}")
                camera_analyses.append({
                    "camera_id": camera_id,
                    "error": str(e),
                    "status": "error"
                })
        
        return camera_analyses
    
    async def orchestrate_final_decision(
        self,
        sensor_analysis: dict,
        camera_analyses: list[dict],
        scenario: str
    ) -> dict[str, Any]:
        """Use orchestrator agent to make final threat decision."""
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
        
        # Build comprehensive analysis text
        analysis_text = f"""
**COMPREHENSIVE THREAT ASSESSMENT**

**Scenario Context**: {scenario.upper()}

**SENSOR ANALYSIS**:
- Threat Level: {sensor_analysis.get('threat_level', 'unknown')}
- Fall Detected: {sensor_analysis.get('fall_detected', False)}
- Vital Anomaly: {sensor_analysis.get('vital_anomaly', False)}
- Audio Threat: {sensor_analysis.get('audio_threat', False)}
- Fire Detected: {sensor_analysis.get('fire_detected', False)}
- Confidence: {sensor_analysis.get('confidence', 0.0):.2f}
- Recommendations: {', '.join(sensor_analysis.get('recommendations', []))}

**CAMERA ANALYSIS (5 Cameras)**:
"""
        
        for cam_analysis in camera_analyses:
            cam_id = cam_analysis.get('camera_id')
            
            if cam_analysis.get("error"):
                analysis_text += f"\n- Camera {cam_id}: {cam_analysis.get('status', 'ERROR').upper()}"
                continue
            
            analysis_text += f"""
- Camera {cam_id}:
  * Status: ONLINE
  * Video Duration: {cam_analysis.get('video_duration', 0):.1f}s
  * Frames Analyzed: {cam_analysis.get('total_frames_analyzed', 0)}
  * Threat Level: {cam_analysis.get('threat_level', 'unknown')}
  * Weapon Detected: {cam_analysis.get('weapon_type', 'none')}
"""
            
            if cam_analysis.get('weapons_detected'):
                wd_list = cam_analysis['weapons_detected']
                analysis_text += f"  * Weapon Detections: {len(wd_list)} frames\n"
                for wd in wd_list[:3]:
                    analysis_text += f"    - {wd['type']} at {wd['timestamp']:.1f}s\n"
            
            analysis_text += f"  * Unfamiliar Face: {cam_analysis.get('unfamiliar_face', False)}\n"
            if cam_analysis.get('unfamiliar_faces_count', 0) > 0:
                analysis_text += f"  * Unknown Person Frames: {cam_analysis['unfamiliar_faces_count']}\n"
            
            analysis_text += f"  * People Count: {cam_analysis.get('people_count', 0)}\n"
            
            threats = cam_analysis.get('all_threats', [])
            if threats:
                analysis_text += f"  * Threats: {', '.join(threats)}\n"
        
        analysis_text += "\n\nBased on ALL sensor and camera data above, make your FINAL threat assessment decision."
        
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
    
    async def run_complete_analysis(
        self,
        scenario: str,
        video_files: Dict[int, str]
    ) -> dict[str, Any]:
        """
        Run complete threat detection analysis.
        
        Args:
            scenario: Scenario name for context
            video_files: Dict mapping camera_id (1-5) to video file paths
            
        Returns:
            Complete analysis results
        """
        logger.info(f"Starting comprehensive analysis for scenario: {scenario}")
        
        # 1. Generate and analyze sensor data
        logger.info("Step 1/3: Analyzing sensor data...")
        sim = SensorSimulator(scenario)
        sensor_data = sim.generate_batch()
        sensor_analysis = await self.analyze_all_sensors(sensor_data)
        logger.info(f"Sensor analysis complete: {sensor_analysis.get('threat_level', 'unknown')}")
        
        # 2. Analyze all 5 camera feeds
        logger.info("Step 2/3: Analyzing all camera feeds...")
        camera_analyses = await self.analyze_all_cameras(video_files, scenario)
        online_cameras = sum(1 for c in camera_analyses if not c.get('error'))
        logger.info(f"Camera analysis complete: {online_cameras}/5 cameras online")
        
        # 3. Orchestrator makes final decision
        logger.info("Step 3/3: Making final threat decision...")
        decision = await self.orchestrate_final_decision(
            sensor_analysis,
            camera_analyses,
            scenario
        )
        logger.info(f"Final decision: {decision.get('threat_level', 'unknown')}")
        
        return {
            "scenario": scenario,
            "sensor_data": sensor_data,
            "sensor_analysis": sensor_analysis,
            "camera_analyses": camera_analyses,
            "decision": decision
        }


def print_comprehensive_results(result: dict):
    """Print detailed results from comprehensive analysis."""
    scenario = result["scenario"]
    sensor_data = result["sensor_data"]
    sensor_analysis = result["sensor_analysis"]
    camera_analyses = result["camera_analyses"]
    decision = result["decision"]
    
    print(f"\n{'='*100}")
    print(f"COMPREHENSIVE THREAT DETECTION - SCENARIO: {scenario.upper()}")
    print(f"{'='*100}")
    
    # Sensor Data
    print("\n[SENSOR DATA]")
    print(f"  Heart Rate: {sensor_data['heart_rate']['heart_rate']} bpm | "
          f"O2: {sensor_data['heart_rate']['oxygen_saturation']:.1f}% | "
          f"Accelerometer: {sensor_data['accelerometer']['magnitude']:.2f} m/s²")
    print(f"  Audio: {sensor_data['audio']['event_classification']} | "
          f"Smoke: {sensor_data['smoke_detector']['smoke_level_ppm']:.1f} ppm")
    
    # Sensor Analysis
    print(f"\n[SENSOR ANALYSIS] Threat: {sensor_analysis.get('threat_level', 'unknown').upper()}")
    print(f"  Fall: {'YES' if sensor_analysis.get('fall_detected') else 'NO'} | "
          f"Vital Anomaly: {'YES' if sensor_analysis.get('vital_anomaly') else 'NO'} | "
          f"Audio Threat: {'YES' if sensor_analysis.get('audio_threat') else 'NO'} | "
          f"Fire: {'YES' if sensor_analysis.get('fire_detected') else 'NO'}")
    
    # Camera Analyses
    print(f"\n[CAMERA ANALYSIS] 5 Camera System")
    for cam in camera_analyses:
        cam_id = cam['camera_id']
        
        if cam.get("error"):
            print(f"  Camera {cam_id}: OFFLINE - {cam.get('status', 'ERROR')}")
            continue
        
        threat = cam.get('threat_level', 'unknown').upper()
        weapon = cam.get('weapon_type', 'none')
        unfamiliar = 'YES' if cam.get('unfamiliar_face') else 'NO'
        people = cam.get('people_count', 0)
        frames = cam.get('total_frames_analyzed', 0)
        duration = cam.get('video_duration', 0)
        
        print(f"  Camera {cam_id}: {threat} | Weapon: {weapon} | Unknown: {unfamiliar} | "
              f"People: {people} | {frames} frames ({duration:.1f}s)")
        
        if cam.get('weapons_detected'):
            print(f"    Weapon detections in {len(cam['weapons_detected'])} frames:")
            for wd in cam['weapons_detected'][:3]:
                print(f"      - {wd['type']} at {wd['timestamp']:.1f}s")
    
    # Final Decision
    print(f"\n{'='*100}")
    print(f"[FINAL DECISION] {decision.get('threat_level', 'unknown').upper()}")
    print(f"{'='*100}")
    print(f"  Action Required: {decision.get('action_required', 'unknown').upper()}")
    print(f"  Call 911: {'YES - EMERGENCY' if decision.get('call_911') else 'NO'}")
    
    print(f"\n  Reasoning: {decision.get('reasoning', 'No reasoning provided')}")
    
    if decision.get('evidence'):
        print(f"\n  Evidence:")
        for evidence in decision['evidence'][:10]:
            print(f"    - {evidence}")
    
    print(f"\n  Alert Message: {decision.get('message_to_user', 'No message')}")
    print(f"\n{'='*100}\n")


async def main():
    """Run comprehensive threat detection demo."""
    
    # Configure your 5 camera video files
    video_config = {
        1: r"videos\fall.mp4",
        2: r"videos\fire.mp4",  # Add when you have more videos
        3: r"videos\normal.mp4",
        4: r"videos\weapon.mp4",
        # 5: r"videos\camera5.mp4",
    }
    
    pipeline = ComprehensiveThreatDetectionPipeline()
    
    print("\n" + "="*100)
    print("COMPREHENSIVE THREAT DETECTION SYSTEM")
    print("5 Cameras + Multiple Sensors + AI Analysis")
    print("="*100 + "\n")
    
    # You can test different scenarios
    scenarios = ["weapon_threat", "normal", "intrusion"]
    
    for scenario in scenarios:
        print(f"Processing scenario: {scenario.upper()}\n")
        
        result = await pipeline.run_complete_analysis(scenario, video_config)
        print_comprehensive_results(result)
        
        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())