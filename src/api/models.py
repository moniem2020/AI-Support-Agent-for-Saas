"""
Pydantic Models for API request/response schemas.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# Request Models
class ChatRequest(BaseModel):
    """Chat request from user."""
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    ticket_id: Optional[str] = Field(None, description="Optional ticket identifier")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")


class IndexRequest(BaseModel):
    """Request to index new documents."""
    documents: List[Dict[str, Any]] = Field(..., description="List of documents to index")
    namespace: Optional[str] = Field("default", description="Namespace for document grouping")


class FeedbackRequest(BaseModel):
    """User feedback on a response."""
    request_id: str = Field(..., description="ID of the request being rated")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    comment: Optional[str] = Field(None, description="Optional feedback comment")


# Response Models
class SourceInfo(BaseModel):
    """Information about a source document."""
    doc_id: str
    title: Optional[str] = None
    relevance_score: float = 0.0


class ChatResponse(BaseModel):
    """Response to chat request."""
    response: str = Field(..., description="AI-generated response")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    sources: List[str] = Field(default_factory=list, description="Source document IDs")
    
    # Metadata
    intent: str = Field("general", description="Detected intent")
    category: str = Field("general", description="Query category")
    cache_hit: bool = Field(False, description="Whether response was from cache")
    
    # Escalation
    escalated: bool = Field(False, description="Whether escalated to human")
    escalation_reason: Optional[str] = Field(None, description="Reason for escalation")
    ticket_id: Optional[str] = Field(None, description="Escalation ticket ID")
    
    # Performance
    latency_ms: float = Field(0.0, description="Response latency in milliseconds")
    model_used: str = Field("", description="Model used for response")
    request_id: str = Field("", description="Unique request identifier")


class IndexResponse(BaseModel):
    """Response to index request."""
    success: bool
    documents_indexed: int
    errors: List[str] = Field(default_factory=list)
    namespace: str = "default"


class MetricsResponse(BaseModel):
    """Aggregated metrics response."""
    total_requests: int = 0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    avg_tokens: float = 0.0
    total_cost_usd: float = 0.0
    avg_confidence: float = 0.0
    cache_hit_rate: float = 0.0
    escalation_rate: float = 0.0
    requests_per_model: Dict[str, int] = Field(default_factory=dict)
    requests_per_intent: Dict[str, int] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    components: Dict[str, str] = Field(default_factory=dict)


class CacheStatsResponse(BaseModel):
    """Cache statistics response."""
    total_entries: int = 0
    total_hits: int = 0
    total_misses: int = 0
    hit_rate: float = 0.0
    similarity_threshold: float = 0.0


class EscalationQueueResponse(BaseModel):
    """Escalation queue statistics."""
    total: int = 0
    by_priority: Dict[str, int] = Field(default_factory=dict)
    oldest: Optional[str] = None
