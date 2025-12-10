"""
Quality Agent - Response quality validation and improvement.
Ensures responses meet quality standards before delivery.
"""
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

from src.agents.state import AgentState
from src.config import CONFIDENCE_THRESHOLD


@dataclass
class QualityReport:
    """Quality assessment report for a response."""
    passed: bool
    overall_score: float
    issues: List[str]
    suggestions: List[str]
    needs_retry: bool
    needs_escalation: bool


class QualityAgent:
    """
    Validates and scores response quality.
    Determines if response should be delivered, retried, or escalated.
    """
    
    # Minimum requirements for quality
    MIN_RESPONSE_LENGTH = 30
    MIN_CONFIDENCE = 0.5
    MAX_RETRIES = 2
    
    def __init__(self):
        self._quality_patterns = {
            "generic_response": [
                "i don't know",
                "i'm not sure",
                "i cannot help",
                "i don't have information"
            ],
            "incomplete_response": [
                "please provide more",
                "i need more information",
                "could you clarify"
            ],
            "hallucination_indicators": [
                "as of my last update",
                "i believe",
                "probably",
                "might be"
            ]
        }
    
    def validate(self, state: AgentState) -> QualityReport:
        """
        Validate response quality.
        
        Args:
            state: Current agent state with response
            
        Returns:
            QualityReport with assessment details
        """
        issues = []
        suggestions = []
        scores = []
        
        # Check response length
        length_score = self._check_length(state.response, issues, suggestions)
        scores.append(length_score)
        
        # Check confidence
        confidence_score = self._check_confidence(state.confidence, issues, suggestions)
        scores.append(confidence_score)
        
        # Check for generic responses
        generic_score = self._check_generic_patterns(state.response, issues, suggestions)
        scores.append(generic_score)
        
        # Check source grounding
        grounding_score = self._check_grounding(state, issues, suggestions)
        scores.append(grounding_score)
        
        # Check relevance to query
        relevance_score = self._check_relevance(state, issues, suggestions)
        scores.append(relevance_score)
        
        # Calculate overall score
        overall_score = sum(scores) / len(scores) if scores else 0.0
        
        # Determine actions
        needs_retry = overall_score < 0.6 and state.retry_count < self.MAX_RETRIES
        needs_escalation = (
            overall_score < 0.4 or
            state.confidence < 0.3 or
            len(issues) > 3
        )
        passed = overall_score >= 0.6 and not needs_escalation
        
        return QualityReport(
            passed=passed,
            overall_score=overall_score,
            issues=issues,
            suggestions=suggestions,
            needs_retry=needs_retry,
            needs_escalation=needs_escalation
        )
    
    def _check_length(
        self,
        response: str,
        issues: List[str],
        suggestions: List[str]
    ) -> float:
        """Check response length."""
        length = len(response)
        
        if length < self.MIN_RESPONSE_LENGTH:
            issues.append("Response too short")
            suggestions.append("Provide more detailed information")
            return 0.3
        elif length < 100:
            return 0.6
        elif length < 500:
            return 1.0
        else:
            # Very long might indicate rambling
            return 0.8
    
    def _check_confidence(
        self,
        confidence: float,
        issues: List[str],
        suggestions: List[str]
    ) -> float:
        """Check confidence level."""
        if confidence < 0.3:
            issues.append("Very low confidence")
            suggestions.append("Consider escalating to human agent")
            return 0.2
        elif confidence < self.MIN_CONFIDENCE:
            issues.append("Low confidence")
            return 0.5
        elif confidence < CONFIDENCE_THRESHOLD:
            return 0.7
        else:
            return 1.0
    
    def _check_generic_patterns(
        self,
        response: str,
        issues: List[str],
        suggestions: List[str]
    ) -> float:
        """Check for generic/unhelpful patterns."""
        response_lower = response.lower()
        
        # Check for generic responses
        for pattern in self._quality_patterns["generic_response"]:
            if pattern in response_lower:
                issues.append("Response contains generic/unhelpful language")
                suggestions.append("Provide specific information from documentation")
                return 0.3
        
        # Check for incomplete responses
        for pattern in self._quality_patterns["incomplete_response"]:
            if pattern in response_lower:
                issues.append("Response indicates incomplete information")
                return 0.5
        
        return 1.0
    
    def _check_grounding(
        self,
        state: AgentState,
        issues: List[str],
        suggestions: List[str]
    ) -> float:
        """Check if response is grounded in retrieved sources."""
        if not state.retrieval_results:
            issues.append("No source documents to ground response")
            suggestions.append("Response may not be accurate without sources")
            return 0.4
        
        # Check if sources are cited
        has_sources = len(state.sources) > 0
        if not has_sources:
            suggestions.append("Consider citing source documents")
            return 0.7
        
        # Check top retrieval score
        top_score = state.retrieval_results[0].score
        if top_score < 0.3:
            issues.append("Retrieved documents have low relevance")
            return 0.5
        
        return 1.0
    
    def _check_relevance(
        self,
        state: AgentState,
        issues: List[str],
        suggestions: List[str]
    ) -> float:
        """Check if response is relevant to query."""
        query_words = set(state.current_query.lower().split())
        response_words = set(state.response.lower().split())
        
        # Remove common words
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "to", "of", "and", "in", "on", "for"}
        query_words = query_words - stop_words
        response_words = response_words - stop_words
        
        if not query_words:
            return 0.8
        
        overlap = len(query_words & response_words) / len(query_words)
        
        if overlap < 0.2:
            issues.append("Response may not address the query")
            suggestions.append("Ensure response directly answers the question")
            return 0.4
        elif overlap < 0.4:
            return 0.7
        else:
            return 1.0
    
    def improve_response(self, state: AgentState, report: QualityReport) -> AgentState:
        """
        Attempt to improve response based on quality report.
        Called when retry is triggered.
        """
        # Add improvement hints to state for responder
        hints = []
        
        for issue in report.issues:
            if "too short" in issue.lower():
                hints.append("Provide a more detailed response")
            if "low confidence" in issue.lower():
                hints.append("Focus on information directly from sources")
            if "generic" in issue.lower():
                hints.append("Be specific to the user's question")
            if "not address" in issue.lower():
                hints.append("Directly answer what was asked")
        
        # Store hints in metadata for next response attempt
        if state.messages:
            state.messages[-1].metadata["improvement_hints"] = hints
        
        return state


# Singleton instance
quality_agent = QualityAgent()


def validate_response_quality(state: AgentState) -> Tuple[bool, Optional[str]]:
    """
    Validate response quality and return pass/fail status.
    
    Returns:
        Tuple of (passed, reason) where reason is None if passed
    """
    report = quality_agent.validate(state)
    
    if report.passed:
        return True, None
    
    if report.needs_escalation:
        return False, f"Quality below threshold: {', '.join(report.issues)}"
    
    if report.needs_retry:
        return False, "Retry needed"
    
    return True, None
