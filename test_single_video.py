"""Test script to analyze a single video file."""

import asyncio
import os
from app.video.real_video_processor import RealVideoProcessor
from app.video.vision_analyzer import analyze_frame

# Set up authentication
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("GOOGLE_API_KEY not found!")


async def test_video(video_path: str):
    """Test analyzing multiple frames from a video file."""
    print(f"\n🎥 Testing Video: {video_path}")
    print("=" * 60)
    
    # Process video
    with RealVideoProcessor(video_path, camera_id=1, fps_extract=0.2) as processor:
        # Extract frames at 5-second intervals
        print("📸 Extracting frames (1 frame every 5 seconds)...")
        frames = list(processor.extract_frames())
        
        print(f"✓ Extracted {len(frames)} frames")
        print(f"  Video duration: ~{frames[-1].timestamp:.1f}s" if frames else "")
        
        # Analyze each frame
        print("\n🔍 Analyzing frames with AI...")
        print("=" * 60)
        
        max_threat_level = "none"
        threat_levels = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
        all_analyses = []
        
        for i, frame in enumerate(frames, 1):
            print(f"\nFrame {i}/{len(frames)} (at {frame.timestamp:.1f}s):")
            
            analysis = await analyze_frame(
                camera_id=1,
                image_base64=frame.image_base64,
                scenario="test"
            )
            all_analyses.append(analysis)
            
            threat_level = analysis.get('threat_level', 'unknown')
            print(f"  Threat Level: {threat_level.upper()}")
            print(f"  Weapon: {analysis.get('weapon_type', 'none')}")
            print(f"  People: {analysis.get('people_count', 0)}")
            print(f"  Description: {analysis.get('description', 'N/A')[:60]}...")
            
            # Track highest threat level
            if threat_levels.get(threat_level, 0) > threat_levels.get(max_threat_level, 0):
                max_threat_level = threat_level
        
        # Summary
        print("\n📊 VIDEO ANALYSIS SUMMARY:")
        print("=" * 60)
        print(f"Total Frames Analyzed: {len(frames)}")
        print(f"Maximum Threat Level: {max_threat_level.upper()}")
        
        # Count weapons detected across all frames
        weapons_detected = [a.get('weapon_type', 'none') for a in all_analyses if a.get('weapon_type') != 'none']
        if weapons_detected:
            print(f"Weapons Detected: {len(weapons_detected)} frames")
            print(f"  Types: {', '.join(set(weapons_detected))}")
        
        # Count unfamiliar faces
        unfamiliar_count = sum(1 for a in all_analyses if a.get('unfamiliar_face'))
        if unfamiliar_count > 0:
            print(f"Unknown Persons Detected: {unfamiliar_count} frames")
        
        print("=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("\n📝 Usage: uv run python test_single_video.py <video_path>")
        print("\nExample:")
        print("  uv run python test_single_video.py videos/test.mp4")
        print("  uv run python test_single_video.py C:\\Videos\\my_video.mp4")
    else:
        video_path = sys.argv[1]
        asyncio.run(test_video(video_path))