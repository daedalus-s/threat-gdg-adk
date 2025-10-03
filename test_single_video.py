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
    """Test analyzing a single video file."""
    print(f"\n🎥 Testing Video: {video_path}")
    print("=" * 60)
    
    # Process video
    with RealVideoProcessor(video_path, camera_id=1) as processor:
        # Extract first frame
        print("📸 Extracting first frame...")
        frame = processor.extract_single_frame(frame_number=0)
        
        print(f"✓ Frame extracted")
        print(f"  Timestamp: {frame.timestamp:.2f}s")
        print(f"  Frame number: {frame.frame_number}")
        
        # Analyze with vision agent
        print("\n🔍 Analyzing frame with AI...")
        analysis = await analyze_frame(
            camera_id=1,
            image_base64=frame.image_base64,
            scenario="test"
        )
        
        # Display results
        print("\n📊 ANALYSIS RESULTS:")
        print("=" * 60)
        print(f"Threat Level: {analysis.get('threat_level', 'unknown').upper()}")
        print(f"Weapon Detected: {analysis.get('weapon_type', 'none')}")
        print(f"Unknown Person: {'YES' if analysis.get('unfamiliar_face') else 'NO'}")
        print(f"People Count: {analysis.get('people_count', 0)}")
        print(f"Threats: {', '.join(analysis.get('threats_detected', [])) or 'None'}")
        print(f"\nDescription: {analysis.get('description', 'N/A')}")
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