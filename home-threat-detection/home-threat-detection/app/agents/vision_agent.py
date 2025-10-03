"""Vision analysis agent for camera frame processing."""

from google.adk.agents import Agent
from google.genai import types


def create_vision_agent() -> Agent:
    """Create vision analysis agent for threat detection."""
    
    instruction = """
    You are a security vision analysis agent. Analyze camera frames for threats.
    
    **CRITICAL DETECTION PRIORITIES:**
    1. **WEAPONS**: Gun, knife, any weapon-like object → IMMEDIATE CRITICAL ALERT
    2. **UNFAMILIAR FACES**: Unknown person → CRITICAL if combined with weapon
    3. **SUSPICIOUS BEHAVIOR**: 
       - Attempting to cover/damage camera
       - Forced entry
       - Aggressive posture/movements
    4. **PEOPLE COUNT**: Number of visible individuals
    5. **INCAPACITATION SIGNS**: Person lying motionless, unusual posture
    
    **OUTPUT FORMAT (JSON):**
    {
        "threat_level": "none|low|medium|high|critical",
        "threats_detected": ["weapon", "unfamiliar_person", "suspicious_behavior"],
        "weapon_type": "gun|knife|blunt_object|none",
        "familiar_faces": ["name1", "name2"],
        "unfamiliar_faces_count": 0,
        "people_count": 0,
        "incapacitation_detected": false,
        "confidence": 0.95,
        "description": "Brief description of scene"
    }
    
    **ESCALATION RULES:**
    - Weapon + Unfamiliar Person = CRITICAL (call 911)
    - Camera covered/damaged = HIGH
    - Unfamiliar person alone = MEDIUM
    - Person lying motionless = MEDIUM (check vitals)
    """
    
    return Agent(
        name="vision_analysis_agent",
        model="gemini-2.5-flash",
        instruction=instruction,
        description="Analyzes camera frames for security threats",
        output_key="vision_analysis"
    )


def analyze_frame(agent: Agent, frame_base64: str, camera_id: int) -> dict:
    """Analyze a single camera frame."""
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    import asyncio
    
    async def run_analysis():
        session_service = InMemorySessionService()
        await session_service.create_session(
            app_name="vision_app",
            user_id="system",
            session_id=f"camera_{camera_id}"
        )
        
        runner = Runner(
            agent=agent,
            app_name="vision_app",
            session_service=session_service
        )
        
        # Create multimodal content with image
        content = types.Content(
            role="user",
            parts=[
                types.Part(text=f"Analyze this frame from Camera {camera_id} for threats:"),
                types.Part(inline_data=types.Blob(
                    mime_type="image/jpeg",
                    data=frame_base64
                ))
            ]
        )
        
        events = []
        async for event in runner.run_async(
            user_id="system",
            session_id=f"camera_{camera_id}",
            new_message=content
        ):
            events.append(event)
        
        # Extract response from final event
        for event in reversed(events):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        return {"camera_id": camera_id, "analysis": part.text}
        
        return {"camera_id": camera_id, "analysis": "No analysis generated"}
    
    return asyncio.run(run_analysis())