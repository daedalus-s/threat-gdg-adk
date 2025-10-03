"""Vision analysis agent for camera frame processing."""

from google.adk.agents import Agent


def create_vision_agent() -> Agent:
    """Create vision analysis agent for threat detection."""
    
    instruction = """
    You are a security vision analysis agent. Analyze camera frames for threats.
    
    **CRITICAL DETECTION PRIORITIES:**
    1. **WEAPONS**: Gun, knife, any weapon-like object â†’ IMMEDIATE CRITICAL ALERT
    2. **UNFAMILIAR FACES**: Unknown person â†’ CRITICAL if combined with weapon
    3. **SUSPICIOUS BEHAVIOR**: Camera tampering, forced entry, aggressive movements
    4. **PEOPLE COUNT**: Number of visible individuals
    5. **INCAPACITATION**: Person lying motionless, unusual posture
    
    **OUTPUT (JSON format):**
    {
        "threat_level": "none|low|medium|high|critical",
        "threats_detected": ["weapon", "unfamiliar_person"],
        "weapon_type": "none",
        "people_count": 0,
        "description": "Brief scene description"
    }
    """
    
    return Agent(
        name="vision_analysis_agent",
        model="gemini-2.5-flash",
        instruction=instruction,
        description="Analyzes camera frames for security threats",
        output_key="vision_analysis"
    )
