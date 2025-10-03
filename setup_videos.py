"""Helper script to set up video directory and check video files."""

from pathlib import Path
import cv2


def setup_video_directory():
    """Create video directory structure."""
    video_dir = Path("videos")
    video_dir.mkdir(exist_ok=True)
    
    print("📁 Video Directory Setup")
    print("=" * 60)
    print(f"Directory: {video_dir.absolute()}\n")
    
    # Expected video files
    expected_videos = {
        "Normal Scenario": [
            "normal_camera1.mp4",
            "normal_camera2.mp4",
        ],
        "Intrusion Scenario": [
            "intrusion_camera1.mp4",
            "intrusion_camera2.mp4",
        ],
        "Fall Scenario": [
            "fall_camera1.mp4",
        ],
        "Fire Scenario": [
            "fire_camera1.mp4",
        ]
    }
    
    print("📋 Expected Video Files:")
    print("-" * 60)
    
    for scenario, files in expected_videos.items():
        print(f"\n{scenario}:")
        for filename in files:
            filepath = video_dir / filename
            if filepath.exists():
                # Check if video can be opened
                cap = cv2.VideoCapture(str(filepath))
                if cap.isOpened():
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    duration = frames / fps if fps > 0 else 0
                    cap.release()
                    print(f"  ✅ {filename}")
                    print(f"     Duration: {duration:.1f}s, FPS: {fps:.1f}, Frames: {frames}")
                else:
                    print(f"  ⚠️  {filename} (exists but cannot be opened)")
            else:
                print(f"  ❌ {filename} (not found)")
    
    print("\n" + "=" * 60)
    print("\n💡 Instructions:")
    print("1. Place your video files in the 'videos' directory")
    print("2. Name them according to the expected filenames above")
    print("3. Or edit 'app/real_video_pipeline.py' to match your filenames")
    print("\n📹 Supported formats: .mp4, .avi, .mov, .mkv")
    print("\n⚠️  Note: You can use any videos - the AI will analyze what it sees")
    print("   Scenario names (normal/intrusion/fall/fire) are just for context\n")


def check_single_video(video_path: str):
    """Check if a single video file is valid."""
    path = Path(video_path)
    
    print(f"\n🔍 Checking: {path}")
    print("=" * 60)
    
    if not path.exists():
        print("❌ File not found!")
        return False
    
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        print("❌ Cannot open video file!")
        return False
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frames / fps if fps > 0 else 0
    
    cap.release()
    
    print(f"✅ Video is valid!")
    print(f"   Resolution: {width}x{height}")
    print(f"   FPS: {fps:.2f}")
    print(f"   Total Frames: {frames}")
    print(f"   Duration: {duration:.2f} seconds")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    setup_video_directory()
    
    # Example: Check a specific video
    # check_single_video("videos/test.mp4")