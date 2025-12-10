"""
Escalation Agent - Handles human handoff preparation.
Determines when and how to escalate to human agents.
"""
from typing import Dict, Any, List
from datetime import datetime

from src.agents.state import AgentState
from src.config import ESCALATION_THRESHOLD


class EscalationHandler:
    """
    Manages escalation to human support agents.
    Prepares context and documentation for handoff.
    """
    
    # Escalation reasons and priorities
    PRIORITY_MAP = {
        "security": "critical",
        "high_urgency": "high",
        "negative_sentiment": "high",
        "low_confidence": "medium",
        "no_results": "medium",
        "complex_query": "normal",
        "user_request": "normal"
    }
    
    def __init__(self):
        self.escalation_queue: List[Dict[str, Any]] = []
    
    def should_escalate(self, state: AgentState) -> bool:
        """
        Determine if query should be escalated.
        
        Escalation triggers:
        - Confidence below threshold
        - Very negative sentiment
        - High urgency
        - User explicitly requests human
        - Security concerns
        """
        # Already marked for escalation
        if state.should_escalate:
            return True
        
        # Confidence too low
        if state.confidence < ESCALATION_THRESHOLD:
            return True
        
        # Very negative sentiment
        if state.sentiment < 0.2:
            return True
        
        # High urgency
        if state.urgency > 0.9:
            return True
        
        # User requests human
        human_keywords = ["speak to human", "talk to agent", "real person", "human support", "escalate"]
        if any(kw in state.current_query.lower() for kw in human_keywords):
            return True
        
        return False
    
    def get_priority(self, state: AgentState) -> str:
        """Get escalation priority level."""
        if "security" in state.escalation_reason.lower():
            return "critical"
        if state.urgency > 0.9:
            return "high"
        if state.sentiment < 0.2:
            return "high"
        if state.confidence < 0.3:
            return "medium"
        return "normal"
    
    def prepare_handoff(self, state: AgentState) -> Dict[str, Any]:
        """
        Prepare escalation package for human agent.
        
        Returns:
            Dictionary with all context for human handoff
        """
        # Gather conversation history
        conversation = []
        for msg in state.messages:
            conversation.append({
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.metadata.get("timestamp", "")
            })
        
        # Gather retrieved context
        context_summary = []
        for result in state.retrieval_results[:5]:
            context_summary.append({
                "source": result.metadata.get("doc_id", "unknown"),
                "content_preview": result.content[:200] + "..." if len(result.content) > 200 else result.content,
                "relevance_score": result.score
            })
        
        # Build handoff package
        handoff = {
            "ticket_id": state.ticket_id or f"ESC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_id": state.user_id,
            "priority": self.get_priority(state),
            "created_at": datetime.now().isoformat(),
            
            # Query info
            "query": state.current_query,
            "intent": state.intent,
            "category": state.category,
            "complexity": state.complexity,
            
            # Sentiment/urgency
            "urgency": state.urgency,
            "sentiment": state.sentiment,
            
            # AI attempt summary
            "ai_response": state.response,
            "ai_confidence": state.confidence,
            "escalation_reason": state.escalation_reason,
            
            # Context
            "conversation_history": conversation,
            "relevant_docs": context_summary,
            
            # Agent notes
            "agent_notes": self._generate_agent_notes(state)
        }
        
        return handoff
    
    def _generate_agent_notes(self, state: AgentState) -> str:
        """Generate notes for human agent."""
        notes = []
        
        if state.confidence < 0.3:
            notes.append("⚠️ Very low confidence - AI response may be inaccurate")
        
        if state.sentiment < 0.3:
            notes.append("😠 Customer appears frustrated - handle with care")
        
        if state.urgency > 0.8:
            notes.append("🚨 High urgency - prioritize this ticket")
        
        if not state.retrieval_results:
            notes.append("📚 No relevant documentation found - may be a knowledge gap")
        
        if state.complexity == "specialized":
            notes.append("🔧 Specialized query - may need domain expert")
        
        if state.hallucination_detected:
            notes.append("⚠️ Possible hallucination detected in AI response")
        
        if "security" in state.escalation_reason.lower():
            notes.append("🔒 Security concern flagged - review carefully")
        
        return "\n".join(notes) if notes else "Standard escalation - no special notes"
    
    def queue_escalation(self, handoff: Dict[str, Any]) -> str:
        """Add to escalation queue and return ticket ID."""
        self.escalation_queue.append(handoff)
        return handoff["ticket_id"]
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get escalation queue statistics."""
        if not self.escalation_queue:
            return {"total": 0, "by_priority": {}}
        
        by_priority = {}
        for item in self.escalation_queue:
            priority = item.get("priority", "normal")
            by_priority[priority] = by_priority.get(priority, 0) + 1
        
        return {
            "total": len(self.escalation_queue),
            "by_priority": by_priority,
            "oldest": self.escalation_queue[0].get("created_at") if self.escalation_queue else None
        }


# Singleton instance
escalation_handler = EscalationHandler()


def prepare_escalation(state: AgentState) -> AgentState:
    """
    Prepare state for escalation.
    Called as a node in the agent graph.
    """
    if not state.should_escalate:
        state.should_escalate = True
        state.escalation_reason = state.escalation_reason or "Manual escalation"
    
    # Prepare handoff package
    handoff = escalation_handler.prepare_handoff(state)
    ticket_id = escalation_handler.queue_escalation(handoff)
    
    # Update response to inform user
    state.response = f"""I apologize, but I wasn't able to fully resolve your question. 
    
I've escalated this to our support team and they'll follow up with you shortly.

**Ticket ID**: {ticket_id}
**Priority**: {handoff['priority'].capitalize()}

In the meantime, here's what I found that might help:
{state.response if state.response else 'No relevant information found.'}

Our team will reach out to you soon. Is there anything else I can help with?"""
    
    return state
