"""
LangGraph-based Multi-Agent Orchestration.
Defines the workflow graph with conditional routing.
"""
import time
import uuid
from typing import Dict, Any, Literal, Optional
from langgraph.graph import StateGraph, END

from src.agents.state import AgentState, create_initial_state
from src.agents.router import router_agent
from src.agents.retriever import retriever_agent
from src.agents.responder import responder_agent
from src.cache.semantic_cache import semantic_cache
from src.security.pii_detector import pii_detector
from src.security.injection_defense import injection_defense
from src.observability.metrics import MetricsContext, metrics_collector
from src.config import CONFIDENCE_THRESHOLD, ESCALATION_THRESHOLD, MAX_RETRIES


class SupportAgentGraph:
    """
    Multi-agent workflow orchestration using LangGraph.
    
    Flow:
    1. Security Check -> block if injection detected
    2. Cache Check -> return cached if similar query found
    3. Route -> classify intent and complexity
    4. Retrieve -> adaptive hybrid retrieval
    5. Respond -> generate grounded response
    6. Quality Check -> validate response quality
    7. Escalate (if needed) -> prepare for human handoff
    """
    
    def __init__(self):
        self.graph = self._build_graph()
        self.compiled = self.graph.compile()
    
    def _build_graph(self) -> StateGraph:
        """Build the agent workflow graph."""
        # Create state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("security_check", self._security_check)
        workflow.add_node("cache_check", self._cache_check)
        workflow.add_node("route", self._route)
        workflow.add_node("retrieve", self._retrieve)
        workflow.add_node("respond", self._respond)
        workflow.add_node("quality_check", self._quality_check)
        workflow.add_node("escalate", self._escalate)
        workflow.add_node("finalize", self._finalize)
        
        # Set entry point
        workflow.set_entry_point("security_check")
        
        # Add edges
        workflow.add_conditional_edges(
            "security_check",
            self._should_block,
            {
                "block": END,
                "continue": "cache_check"
            }
        )
        
        workflow.add_conditional_edges(
            "cache_check",
            self._has_cache_hit,
            {
                "hit": "finalize",
                "miss": "route"
            }
        )
        
        workflow.add_conditional_edges(
            "route",
            self._route_decision,
            {
                "immediate_escalate": "escalate",
                "retrieve": "retrieve"
            }
        )
        
        workflow.add_edge("retrieve", "respond")
        
        workflow.add_conditional_edges(
            "respond",
            self._quality_decision,
            {
                "good": "quality_check",
                "retry": "respond",
                "escalate": "escalate"
            }
        )
        
        workflow.add_conditional_edges(
            "quality_check",
            self._final_decision,
            {
                "complete": "finalize",
                "escalate": "escalate"
            }
        )
        
        workflow.add_edge("escalate", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow
    
    # Node implementations
    def _security_check(self, state: AgentState) -> AgentState:
        """Check for security issues (PII, injections)."""
        query = state.current_query
        
        # Check for prompt injection
        score, alerts = injection_defense.analyze(query)
        if score >= injection_defense.block_threshold:
            state.should_escalate = True
            state.escalation_reason = f"Security: Potential prompt injection detected (score: {score:.2f})"
            state.response = "I apologize, but I cannot process this request due to security concerns. Please contact support directly."
            return state
        
        # Detect and anonymize PII
        if pii_detector.has_pii(query):
            anonymized, token_map = pii_detector.anonymize(query)
            state.current_query = anonymized
            # Store mapping in metadata for later deanonymization
            if state.messages:
                state.messages[-1].metadata["pii_tokens"] = token_map
        
        return state
    
    def _cache_check(self, state: AgentState) -> AgentState:
        """Check semantic cache for similar queries."""
        cached = semantic_cache.get(state.current_query)
        
        if cached:
            response, metadata = cached
            state.response = response
            state.cache_hit = True
            state.confidence = metadata.get("confidence", 0.9)
            state.sources = metadata.get("sources", [])
        
        return state
    
    def _route(self, state: AgentState) -> AgentState:
        """Route query based on classification."""
        return router_agent.route(state)
    
    def _retrieve(self, state: AgentState) -> AgentState:
        """Perform adaptive retrieval."""
        return retriever_agent.retrieve(state)
    
    def _respond(self, state: AgentState) -> AgentState:
        """Generate response."""
        return responder_agent.respond(state)
    
    def _quality_check(self, state: AgentState) -> AgentState:
        """Validate response quality."""
        # Simple quality checks
        if len(state.response) < 20:
            state.confidence = min(state.confidence, 0.3)
        
        if not state.retrieval_results:
            state.confidence = min(state.confidence, 0.4)
        
        # Check if escalation needed
        if state.confidence < ESCALATION_THRESHOLD:
            state.should_escalate = True
            state.escalation_reason = f"Low confidence: {state.confidence:.2f}"
        
        return state
    
    def _escalate(self, state: AgentState) -> AgentState:
        """Prepare for human escalation."""
        from src.agents.escalation import prepare_escalation
        return prepare_escalation(state)
    
    def _finalize(self, state: AgentState) -> AgentState:
        """Finalize response and cache if appropriate."""
        # Cache successful responses
        if not state.cache_hit and state.confidence >= 0.7 and not state.should_escalate:
            semantic_cache.put(
                state.current_query,
                state.response,
                metadata={
                    "confidence": state.confidence,
                    "sources": state.sources,
                    "intent": state.intent,
                    "category": state.category
                }
            )
        
        # Deanonymize PII in response if needed
        if state.messages and "pii_tokens" in state.messages[-1].metadata:
            token_map = state.messages[-1].metadata["pii_tokens"]
            state.response = pii_detector.deanonymize(state.response, token_map)
        
        return state
    
    # Conditional edge functions
    def _should_block(self, state: AgentState) -> Literal["block", "continue"]:
        """Determine if request should be blocked."""
        if state.should_escalate and "Security" in state.escalation_reason:
            return "block"
        return "continue"
    
    def _has_cache_hit(self, state: AgentState) -> Literal["hit", "miss"]:
        """Check if cache hit occurred."""
        return "hit" if state.cache_hit else "miss"
    
    def _route_decision(self, state: AgentState) -> Literal["immediate_escalate", "retrieve"]:
        """Determine next step after routing."""
        if router_agent.should_escalate_immediately(state):
            state.should_escalate = True
            state.escalation_reason = "High urgency or negative sentiment detected"
            return "immediate_escalate"
        return "retrieve"
    
    def _quality_decision(self, state: AgentState) -> Literal["good", "retry", "escalate"]:
        """Determine quality of response."""
        if state.confidence >= CONFIDENCE_THRESHOLD:
            return "good"
        
        if state.retry_count < MAX_RETRIES and state.confidence > 0.3:
            state.retry_count += 1
            return "retry"
        
        return "escalate"
    
    def _final_decision(self, state: AgentState) -> Literal["complete", "escalate"]:
        """Final quality gate."""
        if state.should_escalate:
            return "escalate"
        return "complete"
    
    # Public API
    def process(
        self,
        query: str,
        user_id: str = None,
        ticket_id: str = None
    ) -> Dict[str, Any]:
        """
        Process a support query through the agent pipeline.
        
        Args:
            query: User query
            user_id: Optional user identifier
            ticket_id: Optional ticket identifier
            
        Returns:
            Response dictionary with answer, confidence, sources, etc.
        """
        request_id = str(uuid.uuid4())[:8]
        
        with MetricsContext(request_id, query) as metrics:
            start_time = time.time()
            
            # Create initial state
            state = create_initial_state(query, user_id, ticket_id)
            
            # Run the graph
            final_state = self.compiled.invoke(state)
            
            # Update metrics
            metrics.set_confidence(final_state.confidence)
            metrics.set_cache_hit(final_state.cache_hit)
            metrics.set_escalated(final_state.should_escalate)
            metrics.set_intent(final_state.intent)
            metrics.set_model(final_state.model_used)
            metrics.set_sources(len(final_state.sources))
            metrics.set_response_length(len(final_state.response))
            
            return {
                "response": final_state.response,
                "confidence": final_state.confidence,
                "sources": final_state.sources,
                "intent": final_state.intent,
                "category": final_state.category,
                "escalated": final_state.should_escalate,
                "escalation_reason": final_state.escalation_reason,
                "cache_hit": final_state.cache_hit,
                "latency_ms": (time.time() - start_time) * 1000,
                "model_used": final_state.model_used,
                "request_id": request_id
            }
    
    async def aprocess(
        self,
        query: str,
        user_id: str = None,
        ticket_id: str = None
    ) -> Dict[str, Any]:
        """Async version of process."""
        # Note: For full async support, agents would need async implementations
        # This provides a basic async wrapper
        return self.process(query, user_id, ticket_id)


# Lazy initialization to avoid slow startup
_support_agent_instance: Optional['SupportAgentGraph'] = None


def get_support_agent() -> 'SupportAgentGraph':
    """
    Get or create the support agent graph singleton.
    Uses lazy initialization to avoid slow model loading on import.
    """
    global _support_agent_instance
    if _support_agent_instance is None:
        _support_agent_instance = SupportAgentGraph()
    return _support_agent_instance


# Backwards compatibility
class _SupportAgentProxy:
    """Proxy to provide backward-compatible attribute access."""
    
    def __getattr__(self, name):
        return getattr(get_support_agent(), name)
    
    def __call__(self):
        return get_support_agent()


support_agent = _SupportAgentProxy()
