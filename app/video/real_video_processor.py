"""Real video processing for threat detection."""

import base64
import logging
from pathlib import Path
from typing import Iterator
import cv2
from PIL import Image
import io

from ..sensors.models import CameraFrame

logger = logging.getLogger(__name__)


class RealVideoProcessor:
    """Processes real video files for threat detection."""
    
    def __init__(
        self,
        video_path: str,
        camera_id: int,
        fps_extract: float = 0.2  # Extract 1 frame every 5 seconds
    ):
        """
        Initialize video processor.
        
        Args:
            video_path: Path to the video file
            camera_id: Camera identifier
            fps_extract: Frames to extract per second (0.2 = 1 frame per 5 seconds)
        """
        self.video_path = Path(video_path)
        self.camera_id = camera_id
        self.fps_extract = fps_extract
        
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        self.cap = cv2.VideoCapture(str(self.video_path))
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        # Get video properties
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.frame_count / self.fps if self.fps > 0 else 0
        self.frame_interval = int(self.fps / self.fps_extract) if self.fps > 0 else 1
        
        logger.info(
            f"Camera {camera_id}: Loaded {self.video_path.name} "
            f"(FPS: {self.fps:.2f}, Duration: {self.duration:.2f}s, "
            f"Total Frames: {self.frame_count})"
        )
    
    def _frame_to_base64(self, frame) -> str:
        """Convert OpenCV frame to base64 encoded JPEG."""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_frame)
        
        # Resize if too large (optional, saves bandwidth)
        max_size = 1024
        if max(pil_image.size) > max_size:
            ratio = max_size / max(pil_image.size)
            new_size = (int(pil_image.size[0] * ratio), int(pil_image.size[1] * ratio))
            pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to JPEG bytes
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='JPEG', quality=85)
        img_byte_arr.seek(0)
        image_bytes = img_byte_arr.getvalue()
        
        # Encode to base64
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def extract_frames(self, max_frames: int = None) -> Iterator[CameraFrame]:
        """
        Extract frames from the video at specified interval.
        
        Args:
            max_frames: Maximum number of frames to extract (None = all)
            
        Yields:
            CameraFrame objects with extracted frames
        """
        frame_num = 0
        extracted = 0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                logger.info(
                    f"Camera {self.camera_id}: Extracted {extracted} frames from video"
                )
                break
            
            # Extract frame at interval
            if frame_num % self.frame_interval == 0:
                timestamp = frame_num / self.fps if self.fps > 0 else 0
                image_base64 = self._frame_to_base64(frame)
                
                extracted += 1
                yield CameraFrame(
                    camera_id=self.camera_id,
                    timestamp=timestamp,
                    frame_number=frame_num,
                    image_base64=image_base64
                )
                
                # Check if we've reached max frames
                if max_frames and extracted >= max_frames:
                    logger.info(
                        f"Camera {self.camera_id}: Reached max frames ({max_frames})"
                    )
                    break
            
            frame_num += 1
    
    def extract_single_frame(self, frame_number: int = 0) -> CameraFrame:
        """
        Extract a specific frame from the video.
        
        Args:
            frame_number: Frame number to extract (0 = first frame)
            
        Returns:
            CameraFrame object
        """
        # Set frame position
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError(f"Cannot read frame {frame_number}")
        
        timestamp = frame_number / self.fps if self.fps > 0 else 0
        image_base64 = self._frame_to_base64(frame)
        
        return CameraFrame(
            camera_id=self.camera_id,
            timestamp=timestamp,
            frame_number=frame_number,
            image_base64=image_base64
        )
    
    def release(self):
        """Release video capture resources."""
        if self.cap:
            self.cap.release()
            logger.info(f"Camera {self.camera_id}: Released video capture")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()