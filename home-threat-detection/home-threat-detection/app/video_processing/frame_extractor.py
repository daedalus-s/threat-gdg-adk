"""
Video frame extraction for camera feed simulation.
Extracts frames every 5 seconds from pre-recorded videos.
"""

import base64
import logging
from pathlib import Path
from typing import Iterator
import cv2
from PIL import Image
import io


logger = logging.getLogger(__name__)


class CameraFrameExtractor:
    """Extracts frames from video files to simulate camera feeds."""
    
    def __init__(self, video_path: str, camera_id: int, fps_extract: float = 0.2):
        """
        Initialize frame extractor.
        
        Args:
            video_path: Path to the video file
            camera_id: Unique identifier for this camera
            fps_extract: Frames per second to extract (0.2 = 1 frame every 5 seconds)
        """
        self.video_path = Path(video_path)
        self.camera_id = camera_id
        self.fps_extract = fps_extract
        
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        self.cap = cv2.VideoCapture(str(self.video_path))
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        # Get video properties
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.frame_count / self.fps if self.fps > 0 else 0
        
        # Calculate frame interval
        self.frame_interval = int(self.fps / self.fps_extract) if self.fps > 0 else 1
        
        logger.info(
            f"Camera {camera_id}: Loaded video {video_path.name} "
            f"(FPS: {self.fps:.2f}, Duration: {self.duration:.2f}s, "
            f"Extracting every {self.frame_interval} frames)"
        )
    
    def extract_frames(self) -> Iterator[tuple[int, bytes, float]]:
        """
        Extract frames at specified interval.
        
        Yields:
            Tuple of (frame_number, image_bytes, timestamp)
        """
        frame_num = 0
        extracted_count = 0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                logger.info(
                    f"Camera {self.camera_id}: Finished extracting "
                    f"{extracted_count} frames"
                )
                break
            
            # Extract frame at specified interval
            if frame_num % self.frame_interval == 0:
                timestamp = frame_num / self.fps if self.fps > 0 else 0
                
                # Convert frame to JPEG bytes
                image_bytes = self._frame_to_bytes(frame)
                
                extracted_count += 1
                yield (frame_num, image_bytes, timestamp)
            
            frame_num += 1
    
    def _frame_to_bytes(self, frame) -> bytes:
        """Convert OpenCV frame to JPEG bytes."""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_frame)
        
        # Save to bytes
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='JPEG', quality=85)
        img_byte_arr.seek(0)
        
        return img_byte_arr.getvalue()
    
    def frame_to_base64(self, frame_bytes: bytes) -> str:
        """Convert frame bytes to base64 string for API calls."""
        return base64.b64encode(frame_bytes).decode('utf-8')
    
    def release(self):
        """Release video capture resources."""
        if self.cap:
            self.cap.release()
            logger.info(f"Camera {self.camera_id}: Released video capture")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


class MultiCameraManager:
    """Manages multiple camera feeds for the threat detection system."""
    
    def __init__(self, video_paths: dict[int, str]):
        """
        Initialize multi-camera manager.
        
        Args:
            video_paths: Dictionary mapping camera_id to video file path
        """
        self.extractors = {}
        
        for camera_id, video_path in video_paths.items():
            try:
                self.extractors[camera_id] = CameraFrameExtractor(