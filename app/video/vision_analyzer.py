"""Vision analysis using Google ADK agents."""

from typing import Any
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from ..agents.vision_agent import create_vision_agent


async def analyze_frame(
    camera_id: int,
    image_base64: str,
    scenario: str = "normal"
) -> dict[str, Any]:
    """
    Analyze a camera frame using the vision agent.
    
    Args:
        camera_id: Camera identifier
        image_base64: Base64 encoded image
        scenario: The scenario context for better analysis
        
    Returns:
        Dictionary containing vision analysis results
    """
    vision_agent = create_vision_agent()
    
    session_id = f"camera_{camera_id}_vision"
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="threat_detection",
        user_id="system",
        session_id=session_id
    )
    
    runner = Runner(
        agent=vision_agent,
        app_name="threat_detection",
        session_service=session_service
    )
    
    # Create multimodal content with image
    content = types.Content(
        role="user",
        parts=[
            types.Part(text=f"Analyze this frame from Camera {camera_id}. Context: {scenario} scenario."),
            types.Part(
                inline_data=types.Blob(
                    mime_type="image/jpeg",
                    data=image_base64
                )
            )
        ]
    )
    
    # Run analysis
    async for event in runner.run_async(
        user_id="system",
        session_id=session_id,
        new_message=content
    ):
        pass  # Process events
    
    # Retrieve analysis from session state
    session = await session_service.get_session(
        user_id="system",
        session_id=session_id,
        app_name="threat_detection"
    )
    
    analysis = session.state.get("vision_analysis", {})
    
    # Add camera metadata
    analysis["camera_id"] = camera_id
    analysis["scenario"] = scenario
    
    return analysis