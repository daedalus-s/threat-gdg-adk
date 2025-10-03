"""Real video processing pipeline for threat detection."""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any

from google.genai import types

# Set up authentication
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError(
        "GOOGLE_API_KEY not found! Please set it:\n"
        "PowerShell: $env:GOOGLE_API_KEY=\"your-key-here\""
    )

from app.agents.orchestrator_agent import create_orchestrator_agent
from app.agents.sensor_agent import create_sensor_agent
from app.sensors.simulator import SensorSimulator
from app.video.real_video_processor import RealVideoProcessor
from app.video.vision_analyzer import analyze_frame
from app.complete_pipeline import analyze_sensors, make_decision

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RealVideoPipeline:
    """Threat detection pipeline using real video files."""
    
    def __init__(self, video_directory: str = "videos"):
        """
        Initialize pipeline with video directory.
        
        Args:
            video_directory: Directory containing video files
        """
        self.video_dir = Path(video_directory)
        if not self.video_dir.exists():
            logger.warning(f"Video directory not found: {video_directory}")
            self.video_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created video directory: {video_directory}")
    
    async def analyze_video_cameras(
        self,
        video_files: dict[int, str],
        scenario: str
    ) -> list[dict[str, Any]]:
        """
        Analyze frames from real video files.
        
        Args:
            video_files: Dict mapping camera_id to video file path
            scenario: Scenario context for analysis
            
        Returns:
            List of camera analysis results
        """
        camera_analyses = []
        
        for camera_id, video_path in video_files.items():
            try:
                logger.info(f"Processing Camera {camera_id}: {video_path}")
                
                with RealVideoProcessor(video_path, camera_id) as processor:
                    # Extract first frame for analysis
                    frame = processor.extract_single_frame(frame_number=0)
                    
                    # Analyze frame with vision agent
                    logger.info(f"Analyzing frame from Camera {camera_id}...")
                    analysis = await analyze_frame(
                        camera_id=camera_id,
                        image_base64=frame.image_base64,
                        scenario=scenario
                    )
                    camera_analyses.append(analysis)
                    
            except FileNotFoundError as e:
                logger.error(f"Camera {camera_id} video not found: {e}")
                camera_analyses.append({
                    "camera_id": camera_id,
                    "error": f"Video file not found: {video_path}",
                    "status": "offline"
                })
            except Exception as e:
                logger.error(f"Camera {camera_id} error: {e}")
                camera_analyses.append({
                    "camera_id": camera_id,
                    "error": str(e),
                    "status": "error"
                })
        
        return camera_analyses
    
    async def process_scenario(
        self,
        scenario: str,
        video_files: dict[int, str]
    ) -> dict[str, Any]:
        """
        Process complete threat detection scenario with real videos.
        
        Args:
            scenario: Scenario name (for sensor simulation)
            video_files: Dict mapping camera_id to video file path
            
        Returns:
            Complete analysis results
        """
        logger.info(f"Starting {scenario} scenario with real videos...")
        
        # Generate sensor data (still simulated)
        sim = SensorSimulator(scenario)
        sensor_data = sim.generate_batch()
        
        # Analyze sensors
        logger.info("Analyzing sensors...")
        sensor_analysis = await analyze_sensors(sensor_data)
        
        # Analyze real video cameras
        logger.info("Analyzing real camera feeds...")
        camera_analyses = await self.analyze_video_cameras(video_files, scenario)
        
        # Make final decision
        logger.info("Making final threat decision...")
        decision = await make_decision(sensor_analysis, camera_analyses, scenario)
        
        return {
            "scenario": scenario,
            "sensor_data": sensor_data,
            "sensor_analysis": sensor_analysis,
            "camera_analyses": camera_analyses,
            "decision": decision
        }


def print_results(result: dict):
    """Pretty print analysis results."""
    scenario = result["scenario"]
    sensor_data = result["sensor_data"]
    sensor_analysis = result["sensor_analysis"]
    camera_analyses = result["camera_analyses"]
    decision = result["decision"]
    
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
    print("\n📹 CAMERA ANALYSIS (Real Videos):")
    for cam in camera_analyses:
        if cam.get("error"):
            print(f"  Camera {cam['camera_id']}: ❌ {cam.get('status', 'ERROR').upper()}")
            print(f"    Error: {cam['error']}")
        else:
            threats = ", ".join(cam.get('threats_detected', [])) or "None"
            print(f"  Camera {cam['camera_id']}: {cam.get('threat_level', 'unknown').upper()}")
            print(f"    • Weapon: {cam.get('weapon_type', 'none')}")
            print(f"    • Unknown Person: {'YES' if cam.get('unfamiliar_face') else 'NO'}")
            print(f"    • People Count: {cam.get('people_count', 0)}")
            print(f"    • Threats: {threats}")
            print(f"    • Description: {cam.get('description', 'N/A')}")
    
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


async def run_real_video_demo():
    """Run demonstration with real videos."""
    
    # Define your video files here
    # Replace these paths with your actual video files
    video_configs = {
        "normal": {
            1: "videos/normal_camera1.mp4",
            2: "videos/normal_camera2.mp4",
            # Add more cameras as needed
        },
        "intrusion": {
            1: "videos/intrusion_camera1.mp4",
            2: "videos/intrusion_camera2.mp4",
        },
        "fall": {
            1: "videos/fall_camera1.mp4",
        },
        "fire": {
            1: "videos/fire_camera1.mp4",
        }
    }
    
    pipeline = RealVideoPipeline(video_directory="videos")
    
    print("\n🎥 REAL VIDEO THREAT DETECTION DEMO")
    print("="*80)
    print("📁 Video Directory: videos/")
    print("📝 Place your video files in the 'videos' directory")
    print("="*80 + "\n")
    
    # Process each scenario
    for scenario, video_files in video_configs.items():
        print(f"\n⏳ Processing {scenario.upper()} scenario...")
        
        result = await pipeline.process_scenario(scenario, video_files)
        print_results(result)
        
        # Pause between scenarios
        await asyncio.sleep(2)


if __name__ == "__main__":
    print("\n🚀 Starting Real Video Threat Detection System\n")
    asyncio.run(run_real_video_demo())