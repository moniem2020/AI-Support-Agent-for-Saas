"""
Agent State Schema for LangGraph workflow.
Defines the shared state passed between agents.
"""
from typing import List, Dict, Any, Optional, Literal
from dataclasses import dataclass, field
from pydantic import BaseModel


class Message(BaseModel):
    """A conversation message."""
    role: Literal["user", "assistant", "system"]
    content: str
    metadata: Dict[str, Any] = {}


class RetrievalResult(BaseModel):
    """A single retrieval result."""
    content: str
    metadata: Dict[str, Any] = {}
    score: float = 0.0
    source: str = "unknown"


class AgentState(BaseModel):
    """
    Shared state for the multi-agent workflow.
    Passed between all agents in the LangGraph.
    """
    # Conversation
    messages: List[Message] = []
    current_query: str = ""
    
    # Routing
    intent: str = "general"
    complexity: Literal["simple", "standard", "complex", "specialized"] = "standard"
    category: str = "general"
    urgency: float = 0.5  # 0-1 scale
    sentiment: float = 0.5  # 0=negative, 0.5=neutral, 1=positive
    
    # Retrieval
    enhanced_queries: List[str] = []
    hyde_document: Optional[str] = None
    retrieval_results: List[RetrievalResult] = []
    
    # Response
    response: str = ""
    confidence: float = 0.0
    sources: List[str] = []
    
    # Quality & Escalation
    hallucination_detected: bool = False
    retry_count: int = 0
    should_escalate: bool = False
    escalation_reason: str = ""
    
    # Metrics (for observability)
    total_tokens: int = 0
    latency_ms: float = 0.0
    cache_hit: bool = False
    model_used: str = ""
    
    # Metadata
    ticket_id: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


def create_initial_state(
    query: str,
    user_id: str = None,
    ticket_id: str = None
) -> AgentState:
    """Create initial state for a new query."""
    from datetime import datetime
    
    return AgentState(
        messages=[Message(role="user", content=query)],
        current_query=query,
        user_id=user_id,
        ticket_id=ticket_id,
        timestamp=datetime.now().isoformat()
    )
