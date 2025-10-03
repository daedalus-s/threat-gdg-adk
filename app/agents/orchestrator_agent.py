"""Orchestrator agent for threat assessment."""

from google.adk.agents import Agent


def create_orchestrator_agent() -> Agent:
    """Create orchestrator agent for final threat assessment."""
    
    instruction = """
    You are the THREAT ORCHESTRATOR. Make final decisions based on all data.
    
    **DECISION RULES:**
    1. **CRITICAL** (Call 911): Weapon + Unfamiliar person, Fire detected
    2. **HIGH**: Fall + vital anomalies, Multiple threats
    3. **MEDIUM**: Single threat indicator
    4. **LOW**: Minor anomalies
    
    **OUTPUT (JSON format):**
    {
        "threat_level": "none|low|medium|high|critical",
        "action_required": "none|notify|check_in|call_emergency",
        "call_911": false,
        "reasoning": "Why this decision was made",
        "evidence": ["weapon detected"],
        "message_to_user": "Alert message"
    }
    """
    
    return Agent(
        name="threat_orchestrator",
        model="gemini-2.5-flash",
        instruction=instruction,
        description="Final threat assessment decision maker",
        output_key="threat_decision"
    )
