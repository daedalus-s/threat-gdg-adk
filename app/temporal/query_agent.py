"""Agent for querying temporal threat detection data."""

import re
import logging
from typing import Any
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from pydantic import BaseModel, Field

from app.temporal.vector_store import TemporalVectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TimeRange(BaseModel):
    """Extracted time range from query."""
    start_time: float = Field(description="Start time in seconds")
    end_time: float = Field(description="End time in seconds")
    camera_id: int = Field(description="Camera ID")


def parse_time_query(query: str) -> dict[str, Any]:
    """
    Parse natural language time queries.
    
    Examples:
    - "between 15 and 20 seconds" -> {"start": 15, "end": 20}
    - "first 30 seconds" -> {"start": 0, "end": 30}
    - "from 1:15 to 1:45" -> {"start": 75, "end": 105}
    - "at 2 minutes" -> {"start": 120, "end": 125}
    """
    query_lower = query.lower()
    
    # Extract camera ID
    camera_match = re.search(r'camera\s*(\d+)|cam\s*(\d+)|video\s*(\d+)', query_lower)
    camera_id = 1  # Default
    if camera_match:
        camera_id = int(camera_match.group(1) or camera_match.group(2) or camera_match.group(3))
    
    # Pattern: "between X and Y seconds"
    between_pattern = r'between\s+(\d+)\s+and\s+(\d+)\s+seconds?'
    match = re.search(between_pattern, query_lower)
    if match:
        return {
            "start_time": float(match.group(1)),
            "end_time": float(match.group(2)),
            "camera_id": camera_id
        }
    
    # Pattern: "first X seconds"
    first_pattern = r'first\s+(\d+)\s+seconds?'
    match = re.search(first_pattern, query_lower)
    if match:
        return {
            "start_time": 0.0,
            "end_time": float(match.group(1)),
            "camera_id": camera_id
        }
    
    # Pattern: "last X seconds"
    last_pattern = r'last\s+(\d+)\s+seconds?'
    match = re.search(last_pattern, query_lower)
    if match:
        duration = float(match.group(1))
        # Assume typical video length, adjust based on context
        return {
            "start_time": max(0, 60 - duration),  # Assume 60s video
            "end_time": 60.0,
            "camera_id": camera_id
        }
    
    # Pattern: "from X to Y" (seconds)
    from_to_pattern = r'from\s+(\d+)\s+to\s+(\d+)'
    match = re.search(from_to_pattern, query_lower)
    if match:
        return {
            "start_time": float(match.group(1)),
            "end_time": float(match.group(2)),
            "camera_id": camera_id
        }
    
    # Pattern: "at X seconds" (create 5-second window)
    at_pattern = r'at\s+(\d+)\s+seconds?'
    match = re.search(at_pattern, query_lower)
    if match:
        time = float(match.group(1))
        return {
            "start_time": max(0, time - 2.5),
            "end_time": time + 2.5,
            "camera_id": camera_id
        }
    
    # Pattern: "M:SS format" (e.g., "1:30 to 2:00")
    time_format_pattern = r'(\d+):(\d+)\s+to\s+(\d+):(\d+)'
    match = re.search(time_format_pattern, query_lower)
    if match:
        start_min, start_sec = int(match.group(1)), int(match.group(2))
        end_min, end_sec = int(match.group(3)), int(match.group(4))
        return {
            "start_time": float(start_min * 60 + start_sec),
            "end_time": float(end_min * 60 + end_sec),
            "camera_id": camera_id
        }
    
    # Default: return None if no pattern matched
    return None


def query_temporal_events(
    query: str,
    tool_context: ToolContext
) -> dict[str, Any]:
    """
    Query threat detection events by time range and natural language.
    
    Args:
        query: Natural language query (e.g., "what happened between 15 and 20 seconds in camera 1?")
        tool_context: ADK tool context
    
    Returns:
        Dictionary containing matched events and summary
    """
    logger.info(f"Processing temporal query: {query}")
    
    # Initialize vector store
    vector_store = TemporalVectorStore()
    
    # Parse time-based query
    time_params = parse_time_query(query)
    
    if time_params:
        # Time-based query
        logger.info(f"Executing time-based query: {time_params}")
        
        insights = vector_store.query_by_time_range(
            camera_id=time_params['camera_id'],
            start_time=time_params['start_time'],
            end_time=time_params['end_time'],
            top_k=20
        )
        
        # Format results
        if not insights:
            return {
                "status": "success",
                "message": f"No events found in Camera {time_params['camera_id']} between {time_params['start_time']:.1f}s and {time_params['end_time']:.1f}s",
                "events": [],
                "summary": {
                    "time_range": f"{time_params['start_time']:.1f}s - {time_params['end_time']:.1f}s",
                    "camera_id": time_params['camera_id'],
                    "event_count": 0
                }
            }
        
        # Generate summary
        threat_counts = {}
        weapon_detected = False
        max_threat_level = "none"
        threat_levels = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
        
        for insight in insights:
            threat_level = insight.get('threat_level', 'none')
            threat_counts[threat_level] = threat_counts.get(threat_level, 0) + 1
            
            if threat_levels.get(threat_level, 0) > threat_levels.get(max_threat_level, 0):
                max_threat_level = threat_level
            
            if insight.get('weapon_type', 'none') != 'none':
                weapon_detected = True
        
        return {
            "status": "success",
            "message": f"Found {len(insights)} events in the specified time range",
            "events": insights,
            "summary": {
                "time_range": f"{time_params['start_time']:.1f}s - {time_params['end_time']:.1f}s",
                "camera_id": time_params['camera_id'],
                "event_count": len(insights),
                "max_threat_level": max_threat_level,
                "threat_distribution": threat_counts,
                "weapon_detected": weapon_detected
            }
        }
    
    else:
        # Semantic search query
        logger.info("Executing semantic search query")
        
        # Extract camera ID if mentioned
        camera_match = re.search(r'camera\s*(\d+)|cam\s*(\d+)|video\s*(\d+)', query.lower())
        camera_id = int(camera_match.group(1) or camera_match.group(2) or camera_match.group(3)) if camera_match else None
        
        insights = vector_store.query_by_semantic_search(
            query_text=query,
            camera_id=camera_id,
            top_k=10
        )
        
        if not insights:
            return {
                "status": "success",
                "message": "No relevant events found for your query",
                "events": [],
                "summary": {
                    "event_count": 0
                }
            }
        
        return {
            "status": "success",
            "message": f"Found {len(insights)} relevant events",
            "events": insights,
            "summary": {
                "event_count": len(insights),
                "query_type": "semantic_search",
                "camera_id": camera_id
            }
        }


def get_threat_timeline(
    camera_id: int,
    tool_context: ToolContext
) -> dict[str, Any]:
    """
    Get a complete timeline of threat events for a camera.
    
    Args:
        camera_id: Camera identifier
        tool_context: ADK tool context
    
    Returns:
        Chronological timeline of all events
    """
    logger.info(f"Fetching threat timeline for camera {camera_id}")
    
    vector_store = TemporalVectorStore()
    
    # Query all events for this camera (use large time range)
    insights = vector_store.query_by_time_range(
        camera_id=camera_id,
        start_time=0.0,
        end_time=999999.0,  # Large number to get all events
        top_k=100
    )
    
    # Group by threat level
    by_threat = {}
    for insight in insights:
        level = insight.get('threat_level', 'none')
        if level not in by_threat:
            by_threat[level] = []
        by_threat[level].append(insight)
    
    return {
        "status": "success",
        "camera_id": camera_id,
        "total_events": len(insights),
        "timeline": insights,
        "by_threat_level": by_threat,
        "summary": {
            "critical": len(by_threat.get('critical', [])),
            "high": len(by_threat.get('high', [])),
            "medium": len(by_threat.get('medium', [])),
            "low": len(by_threat.get('low', [])),
            "none": len(by_threat.get('none', []))
        }
    }


def create_temporal_query_agent() -> Agent:
    """Create an agent for querying temporal threat data."""
    
    instruction = """
    You are a temporal query assistant for a home threat detection system.
    
    Your job is to help users understand what happened in their cameras over time.
    
    **TOOLS AVAILABLE:**
    1. `query_temporal_events`: Query events by time range or natural language
       - Handles queries like "what happened between 15 and 20 seconds?"
       - Can do semantic search like "when was the weapon detected?"
    
    2. `get_threat_timeline`: Get complete chronological timeline for a camera
    
    **HOW TO RESPOND:**
    - Parse the user's query to understand the time range and camera
    - Use the appropriate tool to fetch events
    - Summarize the findings in clear, actionable language
    - Highlight critical threats first
    - Provide timestamps for specific events
    
    **EXAMPLE QUERIES:**
    - "What happened in camera 1 between 15 and 20 seconds?"
    - "Show me all weapon detections in the first 30 seconds"
    - "When did the person fall in camera 2?"
    - "Give me a timeline of all events in camera 3"
    """
    
    return Agent(
        name="temporal_query_agent",
        model="gemini-2.5-flash",
        instruction=instruction,
        description="Queries and explains temporal threat detection events",
        tools=[query_temporal_events, get_threat_timeline]
    )