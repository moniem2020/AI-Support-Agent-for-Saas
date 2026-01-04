"""
API Routes - Endpoint definitions for the support agent API.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List

from src.api.models import (
    ChatRequest, ChatResponse,
    IndexRequest, IndexResponse,
    MetricsResponse, HealthResponse,
    CacheStatsResponse, EscalationQueueResponse,
    FeedbackRequest
)
from src.agents.graph import support_agent
from src.cache.semantic_cache import semantic_cache
from src.observability.metrics import metrics_collector
from src.agents.escalation import escalation_handler

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint for customer support queries.
    
    Processes the query through the multi-agent pipeline:
    1. Security check
    2. Cache lookup
    3. Intent routing
    4. Hybrid retrieval
    5. Response generation
    6. Quality validation
    """
    try:
        result = support_agent.process(
            query=request.message,
            user_id=request.user_id,
            ticket_id=request.ticket_id
        )
        
        # Create ticket for tracking
        from src.tickets.ticket_store import ticket_store
        ticket_store.create(
            user_id=request.user_id or "anonymous",
            query=request.message,
            response=result["response"],
            ai_resolved=not result["escalated"],
            needs_escalation=result["escalated"],
            escalation_reason=result.get("escalation_reason", ""),
            confidence=result["confidence"]
        )
        
        return ChatResponse(
            response=result["response"],
            confidence=result["confidence"],
            sources=result["sources"],
            intent=result["intent"],
            category=result["category"],
            cache_hit=result["cache_hit"],
            escalated=result["escalated"],
            escalation_reason=result.get("escalation_reason"),
            latency_ms=result["latency_ms"],
            model_used=result["model_used"],
            request_id=result["request_id"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@router.post("/index", response_model=IndexResponse)
async def index_documents(request: IndexRequest) -> IndexResponse:
    """
    Index new documents into the knowledge base.
    
    Documents should have 'content' and optionally 'metadata' fields.
    """
    try:
        from src.rag.chunker import document_chunker
        from src.rag.dense_retriever import dense_retriever
        from src.rag.sparse_retriever import sparse_retriever
        
        indexed = 0
        errors = []
        
        for doc in request.documents:
            try:
                content = doc.get("content", "")
                metadata = doc.get("metadata", {})
                metadata["namespace"] = request.namespace
                
                # Chunk document
                chunks = document_chunker.chunk_text(content, metadata)
                
                # Index in both retrievers
                texts = [c["content"] for c in chunks]
                metadatas = [c["metadata"] for c in chunks]
                
                dense_retriever.add_documents(texts, metadatas)
                sparse_retriever.add_documents(texts, metadatas)
                
                indexed += 1
                
            except Exception as e:
                errors.append(f"Doc {indexed}: {str(e)}")
        
        return IndexResponse(
            success=len(errors) == 0,
            documents_indexed=indexed,
            errors=errors,
            namespace=request.namespace
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error indexing documents: {str(e)}"
        )


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    """Get aggregated performance metrics."""
    stats = metrics_collector.get_aggregated_stats()
    return MetricsResponse(**stats)


@router.get("/metrics/recent")
async def get_recent_metrics(count: int = 10):
    """Get recent request metrics."""
    return metrics_collector.get_recent(count)


@router.get("/cache/stats", response_model=CacheStatsResponse)
async def get_cache_stats() -> CacheStatsResponse:
    """Get cache statistics."""
    stats = semantic_cache.get_stats()
    return CacheStatsResponse(**stats)


@router.post("/cache/clear")
async def clear_cache():
    """Clear the semantic cache."""
    semantic_cache.clear()
    return {"message": "Cache cleared successfully"}


@router.get("/escalations", response_model=EscalationQueueResponse)
async def get_escalation_queue() -> EscalationQueueResponse:
    """Get escalation queue statistics."""
    stats = escalation_handler.get_queue_stats()
    return EscalationQueueResponse(**stats)


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback on a response."""
    # In production, this would store feedback for model improvement
    return {
        "message": "Feedback received",
        "request_id": request.request_id,
        "rating": request.rating
    }


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    components = {
        "api": "healthy",
        "cache": "healthy" if semantic_cache else "unavailable",
        "metrics": "healthy" if metrics_collector else "unavailable"
    }
    
    # Check if all components are healthy
    all_healthy = all(v == "healthy" for v in components.values())
    
    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        components=components
    )
