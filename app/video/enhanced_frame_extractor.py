"""Enhanced video frame extraction with scenario-based simulation."""

import base64
import logging
from pathlib import Path
from typing import Iterator
import io

from PIL import Image, ImageDraw, ImageFont
from ..sensors.models import CameraFrame

logger = logging.getLogger(__name__)


class EnhancedCameraFrameExtractor:
    """Extracts frames from video files or generates simulated threat scenarios."""
    
    SCENARIOS = {
        "normal": {
            "description": "Person sitting normally on couch",
            "people_count": 1,
            "has_weapon": False,
            "unfamiliar_face": False,
            "suspicious_activity": False
        },
        "intrusion": {
            "description": "Unknown person holding a weapon near entrance",
            "people_count": 1,
            "has_weapon": True,
            "unfamiliar_face": True,
            "suspicious_activity": True
        },
        "fall": {
            "description": "Person lying motionless on floor",
            "people_count": 1,
            "has_weapon": False,
            "unfamiliar_face": False,
            "suspicious_activity": False
        },
        "fire": {
            "description": "Visible smoke and flames in kitchen area",
            "people_count": 0,
            "has_weapon": False,
            "unfamiliar_face": False,
            "suspicious_activity": False
        }
    }
    
    def __init__(
        self,
        camera_id: int,
        scenario: str = "normal",
        video_path: str = None
    ):
        self.camera_id = camera_id
        self.scenario = scenario
        self.video_path = Path(video_path) if video_path else None
        self.frame_count = 0
        
        logger.info(
            f"Camera {camera_id}: Initialized with scenario '{scenario}'"
        )
    
    def generate_simulated_frame(self, timestamp: float) -> CameraFrame:
        """Generate a simulated frame with scenario-specific annotations."""
        
        scenario_data = self.SCENARIOS.get(self.scenario, self.SCENARIOS["normal"])
        
        # Create a blank image (640x480)
        img = Image.new('RGB', (640, 480), color=(30, 30, 40))
        draw = ImageDraw.Draw(img)
        
        # Add scenario information as text overlay
        try:
            font = ImageFont.truetype("arial.ttf", 20)
            font_small = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Header
        draw.rectangle([(0, 0), (640, 50)], fill=(50, 50, 60))
        draw.text((10, 10), f"Camera {self.camera_id}", fill=(255, 255, 255), font=font)
        draw.text((10, 35), f"Scenario: {self.scenario.upper()}", fill=(200, 200, 200), font=font_small)
        
        # Draw scenario-specific elements
        y_offset = 100
        
        if scenario_data["has_weapon"]:
            # Draw a simple weapon representation
            draw.rectangle([(200, 200), (250, 220)], fill=(80, 80, 80))
            draw.ellipse([(240, 195), (260, 225)], fill=(60, 60, 60))
            draw.text((150, 250), "⚠️ WEAPON DETECTED", fill=(255, 0, 0), font=font)
        
        if scenario_data["unfamiliar_face"]:
            # Draw a person silhouette
            draw.ellipse([(280, 150), (360, 230)], fill=(100, 100, 120))
            draw.rectangle([(250, 230), (390, 400)], fill=(100, 100, 120))
            draw.text((220, 420), "❌ UNKNOWN PERSON", fill=(255, 100, 0), font=font)
        
        if self.scenario == "fall":
            # Draw person on ground
            draw.ellipse([(200, 350), (250, 380)], fill=(120, 100, 100))
            draw.rectangle([(250, 360), (450, 390)], fill=(120, 100, 100))
            draw.text((150, 400), "🚨 PERSON DOWN", fill=(255, 0, 0), font=font)
        
        if self.scenario == "fire":
            # Draw fire/smoke
            draw.ellipse([(250, 200), (390, 350)], fill=(255, 100, 0))
            draw.ellipse([(260, 150), (380, 250)], fill=(150, 150, 150))
            draw.text((200, 370), "🔥 FIRE/SMOKE", fill=(255, 0, 0), font=font)
        
        # Add description at bottom
        draw.rectangle([(0, 430), (640, 480)], fill=(40, 40, 50))
        desc_text = scenario_data["description"]
        draw.text((10, 440), desc_text[:60], fill=(200, 200, 200), font=font_small)
        
        # Convert to base64
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=85)
        img_byte_arr.seek(0)
        image_bytes = img_byte_arr.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        self.frame_count += 1
        
        return CameraFrame(
            camera_id=self.camera_id,
            timestamp=timestamp,
            frame_number=self.frame_count,
            image_base64=image_base64
        )
    
    def extract_frames(self, num_frames: int = 1) -> Iterator[CameraFrame]:
        """Extract or generate specified number of frames."""
        import time
        
        for i in range(num_frames):
            timestamp = time.time()
            frame = self.generate_simulated_frame(timestamp)
            yield frame
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass