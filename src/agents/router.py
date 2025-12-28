"""
Router Agent for intent classification and query routing.
Determines complexity, category, urgency, and sentiment.
"""
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import json
import re

from src.config import GOOGLE_API_KEY, GEMINI_MODEL
from src.agents.state import AgentState


class RouterAgent:
    """
    Routes queries by analyzing intent, complexity, and sentiment.
    Uses a smaller/faster model for quick classification.
    """
    
    def __init__(self):
        # Use flash model for fast routing
        self.llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.1  # Low temp for consistent classification
        )
        
        self.routing_prompt = PromptTemplate(
            input_variables=["query", "history"],
            template="""Analyze this customer support query and classify it.

Query: {query}

Previous conversation (if any):
{history}

Respond with a JSON object containing:
{{
    "intent": "question" | "complaint" | "request" | "feedback" | "greeting",
    "complexity": "simple" | "standard" | "complex" | "specialized",
    "category": "billing" | "technical" | "account" | "feature" | "integration" | "general",
    "urgency": 0.0 to 1.0 (0=low, 1=critical),
    "sentiment": 0.0 to 1.0 (0=very negative, 0.5=neutral, 1=very positive),
    "reasoning": "brief explanation"
}}

Classification rules:
- simple: FAQs, yes/no questions, basic lookups
- standard: Information retrieval, how-to questions
- complex: Multi-step issues, troubleshooting, requires reasoning
- specialized: Domain-specific, requires expert knowledge

Respond with ONLY the JSON object:"""
        )
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured classification."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        # Fallback defaults
        return {
            "intent": "question",
            "complexity": "standard",
            "category": "general",
            "urgency": 0.5,
            "sentiment": 0.5,
            "reasoning": "Failed to parse, using defaults"
        }
    
    def route(self, state: AgentState) -> AgentState:
        """
        Analyze and route the query.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with routing information
        """
        query_lower = state.current_query.lower().strip()
        
        # FAST PATH: Pattern-based greeting detection (no LLM needed!)
        greeting_patterns = [
            "hi", "hello", "hey", "greetings", "good morning", "good afternoon",
            "good evening", "howdy", "sup", "what's up", "yo", "hiya", "hola"
        ]
        
        # Check if query is a simple greeting
        if query_lower in greeting_patterns or len(query_lower) <= 3:
            state.intent = "greeting"
            state.complexity = "simple"  # Use simple tier with fast API key
            state.category = "general"
            state.urgency = 0.1
            state.sentiment = 0.8
            return state
        
        # Check for very short queries (likely simple)
        if len(query_lower.split()) <= 2:
            state.intent = "question"
            state.complexity = "simple"
            state.category = "general"
            state.urgency = 0.3
            state.sentiment = 0.5
            return state
        
        # Build conversation history
        history = ""
        for msg in state.messages[:-1]:  # Exclude current query
            history += f"{msg.role}: {msg.content}\n"
        
        if not history:
            history = "No previous conversation"
        
        # Get classification via LLM for complex queries
        prompt = self.routing_prompt.format(
            query=state.current_query,
            history=history
        )
        
        try:
            response = self.llm.invoke(prompt)
            classification = self._parse_response(response.content)
            
            # Update state
            state.intent = classification.get("intent", "question")
            
            # Map complexity to responder's expected values
            raw_complexity = classification.get("complexity", "standard")
            complexity_map = {
                "simple": "simple",
                "standard": "moderate",  # Map standard -> moderate
                "complex": "complex",
                "specialized": "complex"  # Map specialized -> complex
            }
            state.complexity = complexity_map.get(raw_complexity, "moderate")
            
            state.category = classification.get("category", "general")
            state.urgency = float(classification.get("urgency", 0.5))
            state.sentiment = float(classification.get("sentiment", 0.5))
            
        except Exception as e:
            print(f"Routing failed: {e}")
            # Use moderate (not simple) to avoid quota issues on retries
            state.complexity = "moderate"
            state.category = "general"
        
        return state
    
    def should_escalate_immediately(self, state: AgentState) -> bool:
        """Check if query should skip to escalation."""
        # Immediate escalation conditions
        if state.urgency > 0.9:
            return True
        if state.sentiment < 0.2:  # Very negative sentiment
            return True
        if "urgent" in state.current_query.lower() or "emergency" in state.current_query.lower():
            return True
        return False


# Agent instance
router_agent = RouterAgent()
