"""Vision analysis agent for camera frame processing."""

from google.adk.agents import Agent
from pydantic import BaseModel, Field


class VisionAnalysis(BaseModel):
    """Structured output for vision analysis."""
    threat_level: str = Field(description="none, low, medium, high, or critical")
    threats_detected: list[str] = Field(description="List of threats found")
    weapon_type: str = Field(description="Type of weapon detected, or 'none'")
    people_count: int = Field(description="Number of people visible")
    unfamiliar_face: bool = Field(description="Whether unknown person detected")
    description: str = Field(description="Brief scene description")


def create_vision_agent() -> Agent:
    """Create vision analysis agent for threat detection."""
    
    instruction = """
    You are a security vision analysis agent. Analyze camera frames for threats.
    
    **CRITICAL DETECTION PRIORITIES:**
    1. **WEAPONS**: Gun, knife, any weapon-like object → IMMEDIATE CRITICAL ALERT
    2. **UNFAMILIAR FACES**: Unknown person → HIGH if combined with weapon
    3. **SUSPICIOUS BEHAVIOR**: Camera tampering, forced entry, aggressive movements
    4. **PEOPLE COUNT**: Number of visible individuals
    5. **INCAPACITATION**: Person lying motionless, unusual posture
    
    Return JSON with:
    - threat_level: "none", "low", "medium", "high", or "critical"
    - threats_detected: list of specific threats
    - weapon_type: specific weapon or "none"
    - people_count: integer count
    - unfamiliar_face: true/false
    - description: brief scene description
    """
    
    return Agent(
        name="vision_analysis_agent",
        model="gemini-2.5-flash",
        instruction=instruction,
        description="Analyzes camera frames for security threats",
        output_schema=VisionAnalysis,
        output_key="vision_analysis",
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True
    )