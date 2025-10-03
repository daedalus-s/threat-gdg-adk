"""Full video analysis with temporal threat tracking."""

import asyncio
import logging
from typing import Any
from pathlib import Path

from app.video.real_video_processor import RealVideoProcessor
from app.video.vision_analyzer import analyze_frame

logger = logging.getLogger(__name__)


async def analyze_full_video(
    video_path: str,
    camera_id: int,
    scenario: str = "unknown"
) -> dict[str, Any]:
    """
    Analyze all frames from a video at 5-second intervals.
    
    Args:
        video_path: Path to video file
        camera_id: Camera identifier
        scenario: Scenario context
        
    Returns:
        Comprehensive analysis with temporal data
    """
    video_path = str(Path(video_path))
    logger.info(f"Analyzing full video: {video_path}")
    
    frame_analyses = []
    max_threat_level = "none"
    threat_levels = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
    
    with RealVideoProcessor(video_path, camera_id, fps_extract=0.2) as processor:
        # Extract all frames at 5-second intervals
        frames = list(processor.extract_frames())
        logger.info(f"Extracted {len(frames)} frames from video")
        
        # Analyze each frame
        for i, frame in enumerate(frames, 1):
            logger.info(f"Analyzing frame {i}/{len(frames)} at {frame.timestamp:.1f}s")
            
            analysis = await analyze_frame(
                camera_id=camera_id,
                image_base64=frame.image_base64,
                scenario=scenario
            )
            
            # Add temporal info
            analysis["frame_number"] = frame.frame_number
            analysis["timestamp"] = frame.timestamp
            frame_analyses.append(analysis)
            
            # Track max threat
            threat_level = analysis.get('threat_level', 'none')
            if threat_levels.get(threat_level, 0) > threat_levels.get(max_threat_level, 0):
                max_threat_level = threat_level
    
    # Aggregate analysis across all frames
    weapons_detected = [
        {"timestamp": a["timestamp"], "type": a.get("weapon_type")}
        for a in frame_analyses 
        if a.get("weapon_type") != "none"
    ]
    
    unfamiliar_faces_count = sum(
        1 for a in frame_analyses if a.get("unfamiliar_face")
    )
    
    all_threats = set()
    for analysis in frame_analyses:
        all_threats.update(analysis.get("threats_detected", []))
    
    # Build comprehensive result
    result = {
        "camera_id": camera_id,
        "video_path": video_path,
        "scenario": scenario,
        "total_frames_analyzed": len(frames),
        "video_duration": frames[-1].timestamp if frames else 0,
        "max_threat_level": max_threat_level,
        "weapons_detected": weapons_detected,
        "unfamiliar_faces_detected": unfamiliar_faces_count > 0,
        "unfamiliar_faces_count": unfamiliar_faces_count,
        "all_threats": list(all_threats),
        "frame_analyses": frame_analyses,
        # Summary for orchestrator
        "threat_level": max_threat_level,
        "weapon_type": weapons_detected[0]["type"] if weapons_detected else "none",
        "unfamiliar_face": unfamiliar_faces_count > 0,
        "people_count": max(a.get("people_count", 0) for a in frame_analyses) if frame_analyses else 0,
        "threats_detected": list(all_threats),
        "description": f"Video analysis: {len(frames)} frames over {frames[-1].timestamp:.1f}s. Max threat: {max_threat_level}."
    }
    
    logger.info(
        f"Video analysis complete: {max_threat_level.upper()} threat level, "
        f"{len(weapons_detected)} weapon detections"
    )
    
    return result