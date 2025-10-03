"""Orchestrator agent for threat assessment and escalation."""

from google.adk.agents import Agent
from typing import Any


def create_orchestrator_agent() -> Agent:
    """Create orchestrator agent for final threat assessment."""
    
    instruction = """
    You are the THREAT ORCHESTRATOR. You receive:
    - Vision analysis from 5 cameras
    - Sensor analysis (vitals, audio, smoke, motion)
    
    **DECISION TREE:**
    
    1. **CRITICAL ALERT (Call 911):**
       - Weapon detected + Unfamiliar person
       - Fire detected (smoke >200ppm OR audio alarm + high temp)
       - Vital signs critical (O2 <85% + no response)
    
    2. **HIGH ALERT (Notify + Prepare to Call):**
       - Camera disconnected/covered + suspicious sensor activity
       - Fall detected + vital anomalies
       - Multiple unfamiliar faces
    
    3. **MEDIUM ALERT (Check-in Required):**
       - Fall detected alone
       - Vitals moderately abnormal
       - Single unfamiliar person
    
    4. **LOW ALERT (Log Only):**
       - Minor anomalies
       - Resolved situations
    
    **CAMERA FAILURE PROTOCOL:**
    If cameras offline:
    1. Attempt reconnection (Wi-Fi → Satellite → Starlink)
    2. Check smartwatch vitals
    3. Review last 30min of footage
    4. Enable phone microphone
    5. If danger signs → escalate
    
    **OUTPUT FORMAT (JSON):**
    {
        "threat_level": "none|low|medium|high|critical",
        "action_required": "none|notify|check_in|call_emergency",
        "call_911": false,
        "notify_contacts": false,
        "reasoning": "Why this decision was made",
        "evidence": ["weapon detected", "vitals critical"],
        "recommended_contacts": ["emergency", "family", "security"],
        "message_to_user": "Alert message for dashboard"
    }
    
    **COMPLIANCE NOTES:**
    - Log all decisions with timestamps
    - Maintain user privacy (no unnecessary data retention)
    - Allow user override of non-critical alerts
    """
    
    return Agent(
        name="threat_orchestrator",
        model="gemini-2.5-flash",
        instruction=instruction,
        description="Final threat assessment and escalation decision maker",
        output_key="threat_decision"
    )


def assess_threat(
    agent: Agent,
    vision_analyses: list[dict],
    sensor_analysis: dict
) -> dict:
    """Make final threat assessment."""
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    import asyncio
    import json
    
    async def run_assessment():
        session_service = InMemorySessionService()
        await session_service.create_session(
            app_name="orchestrator_app",
            user_id="system",
            session_id="threat_assessment"
        )
        
        runner = Runner(
            agent=agent,
            app_name="orchestrator_app",
            session_service=session_service
        )
        
        assessment_input = {
            "camera_analyses": vision_analyses,
            "sensor_analysis": sensor_analysis
        }
        
        content = types.Content(
            role="user",
            parts=[types.Part(
                text=f"Assess threat level:\n{json.dumps(assessment_input, indent=2)}"
            )]
        )
        
        events = []
        async for event in runner.run_async(
            user_id="system",
            session_id="threat_assessment",
            new_message=content
        ):
            events.append(event)
        
        for event in reversed(events):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        return {
                            "decision": part.text,
                            "input_data": assessment_input
                        }
        
        return {
            "decision": "No decision generated",
            "input_data": assessment_input
        }
    
    return asyncio.run(run_assessment())