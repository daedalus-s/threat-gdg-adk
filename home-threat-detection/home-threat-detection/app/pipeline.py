"""Main processing pipeline for threat detection."""

import asyncio
import logging
from typing import Dict, List, Any
from pathlib import Path

from .video.frame_extractor import CameraFrameExtractor
from .sensors.simulator import SensorSimulator
from .agents.vision_agent import create_vision_agent, analyze_frame
from .agents.sensor_agent import create_sensor_agent, analyze_sensors
from .agents.orchestrator import create_orchestrator_agent, assess_threat

logger = logging.getLogger(__name__)


class ThreatDetectionPipeline:
    """Main pipeline for threat detection system."""
    
    def __init__(
        self,
        video_paths: Dict[int, str],
        scenario: str = "normal"
    ):
        self.video_paths = video_paths
        self.scenario = scenario
        
        # Initialize agents
        self.vision_agent = create_vision_agent()
        self.sensor_agent = create_sensor_agent()
        self.orchestrator_agent = create_orchestrator_agent()
        
        # Initialize sensor simulator
        self.sensor_sim = SensorSimulator(scenario=scenario)
        
        logger.info(f"Pipeline initialized for scenario: {scenario}")
    
    async def process_cycle(self) -> Dict[str, Any]:
        """Process one cycle (5 seconds) of all sensors."""
        
        # 1. Extract frames from all cameras
        camera_analyses = []
        for camera_id, video_path in self.video_paths.items():
            try:
                with CameraFrameExtractor(video_path, camera_id) as extractor:
                    # Get first frame
                    frame = next(extractor.extract_frames())
                    
                    # Analyze frame
                    analysis = analyze_frame(
                        self.vision_agent,
                        frame.image_base64,
                        camera_id
                    )
                    camera_analyses.append(analysis)
                    logger.info(f"Processed Camera {camera_id}")
            except Exception as e:
                logger.error(f"Camera {camera_id} error: {e}")
                camera_analyses.append({
                    "camera_id": camera_id,
                    "error": str(e),
                    "status": "offline"
                })
        
        # 2. Generate and analyze sensor data
        sensor_data = self.sensor_sim.generate_batch()
        sensor_analysis = analyze_sensors(self.sensor_agent, sensor_data)
        logger.info("Processed sensor data")
        
        # 3. Orchestrator makes final decision
        threat_decision = assess_threat(
            self.orchestrator_agent,
            camera_analyses,
            sensor_analysis
        )
        logger.info("Threat assessment complete")
        
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "camera_analyses": camera_analyses,
            "sensor_analysis": sensor_analysis,
            "threat_decision": threat_decision,
            "scenario": self.scenario
        }
    
    async def run_continuous(self, duration_seconds: int = 60):
        """Run pipeline continuously for specified duration."""
        cycles = duration_seconds // 5
        results = []
        
        for i in range(cycles):
            logger.info(f"Cycle {i+1}/{cycles}")
            result = await self.process_cycle()
            results.append(result)
            
            # Wait 5 seconds before next cycle
            if i < cycles - 1:
                await asyncio.sleep(5)
        
        return results


async def run_demo():
    """Run demonstration of the system."""
    
    # Example video paths (replace with actual paths)
    video_paths = {
        1: "videos/camera1.mp4",
        2: "videos/camera2.mp4",
        3: "videos/camera3.mp4",
        4: "videos/camera4.mp4",
        5: "videos/camera5.mp4"
    }
    
    # Test different scenarios
    scenarios = ["normal", "intrusion", "fall", "fire"]
    
    for scenario in scenarios:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing Scenario: {scenario.upper()}")
        logger.info(f"{'='*60}\n")
        
        pipeline = ThreatDetectionPipeline(video_paths, scenario)
        results = await pipeline.run_continuous(duration_seconds=15)
        
        # Log final results
        for i, result in enumerate(results):
            logger.info(f"Cycle {i+1} Decision: {result['threat_decision']}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(run_demo())