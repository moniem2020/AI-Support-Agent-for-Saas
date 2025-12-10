"""
Response Evaluator - Hallucination detection and quality scoring.
Uses LLM-based grounding checks and heuristic scoring.
"""
from typing import Dict, Any, List, Optional, Tuple
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.config import GOOGLE_API_KEY, GEMINI_MODEL


class ResponseEvaluator:
    """
    Evaluate response quality including hallucination detection.
    Uses LLM grounding checks and heuristic analysis.
    """
    
    def __init__(self):
        self._llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.0  # Deterministic for evaluation
        )
    
    async def check_hallucination(
        self,
        response: str,
        sources: List[str],
        query: str
    ) -> Tuple[bool, float, str]:
        """
        Check if response contains hallucinations.
        
        Args:
            response: The generated response
            sources: Source documents used
            query: Original query
            
        Returns:
            Tuple of (is_hallucinated, confidence, explanation)
        """
        if not sources:
            # No sources to ground against
            return True, 0.8, "No source documents to verify against"
        
        combined_sources = "\n\n---\n\n".join(sources[:5])  # Limit to 5 sources
        
        prompt = f"""Evaluate if the following response is grounded in the provided sources.

SOURCES:
{combined_sources}

QUERY: {query}

RESPONSE: {response}

Analyze whether the response:
1. Makes claims not supported by the sources
2. Contradicts information in the sources
3. Presents speculation as fact
4. Contains fabricated details

Respond in this exact format:
GROUNDED: [YES/NO]
CONFIDENCE: [0.0-1.0]
EXPLANATION: [Brief explanation]"""

        try:
            result = await self._llm.ainvoke([
                SystemMessage(content="You are a fact-checking assistant. Be strict about grounding."),
                HumanMessage(content=prompt)
            ])
            
            text = result.content
            
            # Parse response
            is_grounded = "GROUNDED: YES" in text.upper()
            
            confidence_match = re.search(r"CONFIDENCE:\s*([\d.]+)", text)
            confidence = float(confidence_match.group(1)) if confidence_match else 0.5
            
            explanation_match = re.search(r"EXPLANATION:\s*(.+)", text, re.DOTALL)
            explanation = explanation_match.group(1).strip() if explanation_match else "Unable to parse explanation"
            
            return not is_grounded, confidence, explanation
            
        except Exception as e:
            # Fallback to heuristic check
            return self._heuristic_hallucination_check(response, sources)
    
    def _heuristic_hallucination_check(
        self,
        response: str,
        sources: List[str]
    ) -> Tuple[bool, float, str]:
        """Fallback heuristic check for hallucinations."""
        combined_sources = " ".join(sources).lower()
        response_lower = response.lower()
        
        # Extract key noun phrases from response
        # Simple approach: look for capitalized words and numbers
        response_entities = set(re.findall(r'\b[A-Z][a-z]+\b|\b\d+(?:\.\d+)?\b', response))
        
        # Check if entities appear in sources
        missing_entities = []
        for entity in response_entities:
            if entity.lower() not in combined_sources:
                missing_entities.append(entity)
        
        # If many entities are missing, likely hallucination
        if len(missing_entities) > len(response_entities) * 0.5:
            return True, 0.6, f"Multiple entities not found in sources: {missing_entities[:5]}"
        
        return False, 0.7, "Response appears grounded in sources"
    
    def score_response(
        self,
        response: str,
        query: str,
        sources: List[str],
        confidence: float
    ) -> Dict[str, Any]:
        """
        Score response quality on multiple dimensions.
        
        Returns:
            Dictionary with quality scores
        """
        scores = {}
        
        # Relevance: Does response address the query?
        query_keywords = set(query.lower().split())
        response_lower = response.lower()
        keyword_coverage = sum(1 for kw in query_keywords if kw in response_lower) / max(len(query_keywords), 1)
        scores["relevance"] = min(keyword_coverage * 1.5, 1.0)
        
        # Completeness: Response length and structure
        word_count = len(response.split())
        if word_count < 20:
            scores["completeness"] = 0.4
        elif word_count < 50:
            scores["completeness"] = 0.6
        elif word_count < 200:
            scores["completeness"] = 0.8
        else:
            scores["completeness"] = 1.0
        
        # Formatting: Lists, structure, proper sentences
        has_list = bool(re.search(r'^\s*[-•*\d]+[.)]?\s', response, re.MULTILINE))
        has_multiple_sentences = len(re.findall(r'[.!?]\s+[A-Z]', response)) >= 2
        scores["formatting"] = (0.5 if has_list else 0) + (0.5 if has_multiple_sentences else 0.3)
        
        # Source attribution: Mentions sources
        mentions_sources = any(
            indicator in response.lower()
            for indicator in ["according to", "based on", "documentation", "as stated", "our guide"]
        )
        scores["attribution"] = 0.8 if mentions_sources else 0.5
        
        # Confidence alignment
        scores["confidence"] = confidence
        
        # Overall score (weighted average)
        weights = {
            "relevance": 0.3,
            "completeness": 0.2,
            "formatting": 0.1,
            "attribution": 0.1,
            "confidence": 0.3
        }
        
        overall = sum(scores[k] * weights[k] for k in weights)
        
        return {
            "overall": round(overall, 3),
            "dimensions": scores,
            "word_count": word_count,
            "needs_improvement": overall < 0.6
        }
    
    def get_improvement_suggestions(
        self,
        scores: Dict[str, Any],
        response: str
    ) -> List[str]:
        """Get suggestions for improving the response."""
        suggestions = []
        dims = scores.get("dimensions", {})
        
        if dims.get("relevance", 1) < 0.6:
            suggestions.append("Ensure response directly addresses the user's question")
        
        if dims.get("completeness", 1) < 0.6:
            suggestions.append("Provide more detailed information")
        
        if dims.get("formatting", 1) < 0.5:
            suggestions.append("Consider using bullet points or numbered lists for clarity")
        
        if dims.get("attribution", 1) < 0.6:
            suggestions.append("Reference the source documentation")
        
        if dims.get("confidence", 1) < 0.5:
            suggestions.append("Response may need verification or escalation")
        
        return suggestions


# Singleton instance
response_evaluator = ResponseEvaluator()
