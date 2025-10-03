"""Video frame extraction for camera simulation."""

import base64
import logging
from pathlib import Path
from typing import Iterator
import cv2
from PIL import Image
import io

from ..sensors.models import CameraFrame

logger = logging.getLogger(__name__)


class CameraFrameExtractor:
    """Extracts frames from video files to simulate camera feeds."""
    
    def __init__(
        self,
        video_path: str,
        camera_id: int,
        fps_extract: float = 0.2  # 1 frame every 5 seconds
    ):
        self.video_path = Path(video_path)
        self.camera_id = camera_id
        self.fps_extract = fps_extract
        
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        self.cap = cv2.VideoCapture(str(self.video_path))
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.frame_count / self.fps if self.fps > 0 else 0
        self.frame_interval = int(self.fps / self.fps_extract) if self.fps > 0 else 1
        
        logger.info(
            f"Camera {camera_id}: Loaded {video_path.name} "
            f"(FPS: {self.fps:.2f}, Duration: {self.duration:.2f}s)"
        )
    
    def extract_frames(self) -> Iterator[CameraFrame]:
        """Extract frames at specified interval."""
        frame_num = 0
        extracted = 0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                logger.info(f"Camera {self.camera_id}: Extracted {extracted} frames")
                break
            
            if frame_num % self.frame_interval == 0:
                timestamp = frame_num / self.fps if self.fps > 0 else 0
                image_bytes = self._frame_to_bytes(frame)
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                
                extracted += 1
                yield CameraFrame(
                    camera_id=self.camera_id,
                    timestamp=timestamp,
                    frame_number=frame_num,
                    image_base64=image_base64
                )
            
            frame_num += 1
    
    def _frame_to_bytes(self, frame) -> bytes:
        """Convert OpenCV frame to JPEG bytes."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='JPEG', quality=85)
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()
    
    def release(self):
        """Release video capture resources."""
        if self.cap:
            self.cap.release()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()