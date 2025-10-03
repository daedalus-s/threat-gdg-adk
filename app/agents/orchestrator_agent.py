"""Orchestrator agent for threat assessment."""

from google.adk.agents import Agent
from pydantic import BaseModel, Field


class ThreatDecision(BaseModel):
    """Structured output for final threat decision."""
    threat_level: str = Field(description="none, low, medium, high, or critical")
    action_required: str = Field(description="none, notify, check_in, or call_emergency")
    call_911: bool = Field(description="Whether to call 911")
    reasoning: str = Field(description="Explanation of the decision")
    evidence: list[str] = Field(description="List of supporting evidence")
    message_to_user: str = Field(description="Alert message for the user")


def create_orchestrator_agent() -> Agent:
    """Create orchestrator agent for final threat assessment."""
    
    instruction = """
    You are the THREAT ORCHESTRATOR. Make final decisions based on all data.
    
    **DECISION RULES:**
    1. **CRITICAL** (Call 911): 
       - Weapon + Unfamiliar person
       - Fire detected
       - Multiple critical threats
    
    2. **HIGH** (Notify Emergency Contact):
       - Fall + vital anomalies
       - Weapon detected (familiar person)
       - Multiple high threats
    
    3. **MEDIUM** (Check In):
       - Single vital anomaly
       - Suspicious behavior
       - Audio threat
    
    4. **LOW** (Monitor):
       - Minor anomalies
       - Single sensor alert
    
    5. **NONE**: No threats detected
    
    Return JSON with:
    - threat_level: severity level
    - action_required: what action to take
    - call_911: true/false
    - reasoning: why this decision was made
    - evidence: list of supporting facts
    - message_to_user: clear alert message
    """
    
    return Agent(
        name="threat_orchestrator",
        model="gemini-2.5-flash",
        instruction=instruction,
        description="Final threat assessment decision maker",
        output_schema=ThreatDecision,
        output_key="threat_decision",
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True
    )