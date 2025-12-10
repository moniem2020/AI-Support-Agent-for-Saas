"""
Metrics Collector - Track latency, tokens, costs, and request metrics.
Provides in-memory aggregated statistics for observability dashboards.
"""
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from contextlib import contextmanager
import threading


@dataclass
class RequestMetrics:
    """Metrics for a single request."""
    request_id: str
    timestamp: str
    query: str = ""
    
    # Timing
    total_latency_ms: float = 0.0
    retrieval_latency_ms: float = 0.0
    llm_latency_ms: float = 0.0
    
    # Tokens
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    
    # Cost (estimated)
    estimated_cost_usd: float = 0.0
    
    # Quality
    confidence: float = 0.0
    cache_hit: bool = False
    escalated: bool = False
    hallucination_detected: bool = False
    
    # Model
    model_used: str = ""
    intent: str = ""
    
    # Results
    num_sources: int = 0
    response_length: int = 0


class MetricsContext:
    """Context manager for tracking request metrics."""
    
    def __init__(self, request_id: str, query: str = ""):
        self.metrics = RequestMetrics(
            request_id=request_id,
            timestamp=datetime.now().isoformat(),
            query=query[:100] if query else ""  # Truncate for storage
        )
        self._start_time: Optional[float] = None
        self._phase_start: Optional[float] = None
        self._current_phase: str = ""
    
    def __enter__(self):
        self._start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._start_time:
            self.metrics.total_latency_ms = (time.time() - self._start_time) * 1000
        metrics_collector.record(self.metrics)
    
    @contextmanager
    def phase(self, name: str):
        """Track a specific phase (retrieval, llm, etc.)."""
        start = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start) * 1000
            if name == "retrieval":
                self.metrics.retrieval_latency_ms = duration_ms
            elif name == "llm":
                self.metrics.llm_latency_ms = duration_ms
    
    def set_tokens(self, input_tokens: int, output_tokens: int):
        """Set token counts."""
        self.metrics.input_tokens = input_tokens
        self.metrics.output_tokens = output_tokens
        self.metrics.total_tokens = input_tokens + output_tokens
        
        # Estimate cost (Gemini 1.5 Flash pricing: $0.075/1M input, $0.30/1M output)
        self.metrics.estimated_cost_usd = (
            (input_tokens * 0.075 / 1_000_000) +
            (output_tokens * 0.30 / 1_000_000)
        )
    
    def set_model(self, model: str):
        self.metrics.model_used = model
    
    def set_confidence(self, confidence: float):
        self.metrics.confidence = confidence
    
    def set_cache_hit(self, hit: bool):
        self.metrics.cache_hit = hit
    
    def set_escalated(self, escalated: bool):
        self.metrics.escalated = escalated
    
    def set_hallucination(self, detected: bool):
        self.metrics.hallucination_detected = detected
    
    def set_intent(self, intent: str):
        self.metrics.intent = intent
    
    def set_sources(self, num_sources: int):
        self.metrics.num_sources = num_sources
    
    def set_response_length(self, length: int):
        self.metrics.response_length = length


class MetricsCollector:
    """
    Collects and aggregates metrics for observability.
    Thread-safe implementation for concurrent access.
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self._history: List[RequestMetrics] = []
        self._lock = threading.Lock()
        
        # Aggregated counters
        self._total_requests = 0
        self._total_tokens = 0
        self._total_cost = 0.0
        self._cache_hits = 0
        self._escalations = 0
        self._hallucinations = 0
    
    def record(self, metrics: RequestMetrics) -> None:
        """Record request metrics."""
        with self._lock:
            self._history.append(metrics)
            if len(self._history) > self.max_history:
                self._history.pop(0)
            
            # Update counters
            self._total_requests += 1
            self._total_tokens += metrics.total_tokens
            self._total_cost += metrics.estimated_cost_usd
            if metrics.cache_hit:
                self._cache_hits += 1
            if metrics.escalated:
                self._escalations += 1
            if metrics.hallucination_detected:
                self._hallucinations += 1
    
    def get_recent(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent request metrics."""
        with self._lock:
            recent = self._history[-count:]
            return [
                {
                    "request_id": m.request_id,
                    "timestamp": m.timestamp,
                    "latency_ms": m.total_latency_ms,
                    "tokens": m.total_tokens,
                    "confidence": m.confidence,
                    "cache_hit": m.cache_hit,
                    "model": m.model_used
                }
                for m in recent
            ]
    
    def get_aggregated_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics."""
        with self._lock:
            if not self._history:
                return {
                    "total_requests": 0,
                    "avg_latency_ms": 0,
                    "avg_tokens": 0,
                    "total_cost_usd": 0,
                    "cache_hit_rate": 0,
                    "escalation_rate": 0,
                    "hallucination_rate": 0
                }
            
            latencies = [m.total_latency_ms for m in self._history]
            tokens = [m.total_tokens for m in self._history]
            confidences = [m.confidence for m in self._history if m.confidence > 0]
            
            return {
                "total_requests": self._total_requests,
                "avg_latency_ms": sum(latencies) / len(latencies),
                "p95_latency_ms": sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) >= 20 else max(latencies),
                "avg_tokens": sum(tokens) / len(tokens),
                "total_tokens": self._total_tokens,
                "total_cost_usd": round(self._total_cost, 6),
                "avg_confidence": sum(confidences) / len(confidences) if confidences else 0,
                "cache_hit_rate": self._cache_hits / self._total_requests if self._total_requests > 0 else 0,
                "escalation_rate": self._escalations / self._total_requests if self._total_requests > 0 else 0,
                "hallucination_rate": self._hallucinations / self._total_requests if self._total_requests > 0 else 0,
                "requests_per_model": self._get_model_breakdown(),
                "requests_per_intent": self._get_intent_breakdown()
            }
    
    def _get_model_breakdown(self) -> Dict[str, int]:
        """Get request counts per model."""
        breakdown = {}
        for m in self._history:
            if m.model_used:
                breakdown[m.model_used] = breakdown.get(m.model_used, 0) + 1
        return breakdown
    
    def _get_intent_breakdown(self) -> Dict[str, int]:
        """Get request counts per intent."""
        breakdown = {}
        for m in self._history:
            if m.intent:
                breakdown[m.intent] = breakdown.get(m.intent, 0) + 1
        return breakdown
    
    def get_latency_stats(self) -> Dict[str, float]:
        """Get detailed latency statistics."""
        with self._lock:
            if not self._history:
                return {}
            
            total = [m.total_latency_ms for m in self._history]
            retrieval = [m.retrieval_latency_ms for m in self._history if m.retrieval_latency_ms > 0]
            llm = [m.llm_latency_ms for m in self._history if m.llm_latency_ms > 0]
            
            return {
                "total_avg": sum(total) / len(total),
                "total_min": min(total),
                "total_max": max(total),
                "retrieval_avg": sum(retrieval) / len(retrieval) if retrieval else 0,
                "llm_avg": sum(llm) / len(llm) if llm else 0
            }
    
    def clear(self) -> None:
        """Clear all metrics."""
        with self._lock:
            self._history.clear()
            self._total_requests = 0
            self._total_tokens = 0
            self._total_cost = 0.0
            self._cache_hits = 0
            self._escalations = 0
            self._hallucinations = 0


# Singleton instance
metrics_collector = MetricsCollector()
