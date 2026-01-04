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
        Analyze and route the query using hybrid classification.
        
        Uses a combination of:
        1. Pattern matching for greetings/small-talk/chitchat (instant, no LLM)
        2. Heuristic scoring for product relevance detection
        3. LLM classification only for complex product queries
        
        Based on research: keyword-based methods are effective for simple queries,
        reducing LLM calls and improving response time.
        """
        query_lower = state.current_query.lower().strip()
        query_words = set(query_lower.split())
        
        # ============================================================
        # FAST PATH: Pattern-based classification (no LLM needed!)
        # Based on best practices for handling simple/casual queries
        # ============================================================
        
        # 1. GREETINGS - Common salutations
        greetings = {
            "hi", "hello", "hey", "hiya", "howdy", "greetings", "yo", "sup",
            "good morning", "good afternoon", "good evening", "good night",
            "morning", "afternoon", "evening", "hola", "bonjour", "ciao",
            "what's up", "whats up", "wassup", "wazzup", "g'day", "aloha"
        }
        
        # 2. FAREWELLS - Closing/goodbye phrases
        farewells = {
            "bye", "goodbye", "farewell", "see you", "see ya", "later",
            "take care", "have a nice day", "have a good one", "cya",
            "thanks bye", "thank you bye", "ok bye", "gtg", "gotta go",
            "talk later", "catch you later", "peace", "cheers"
        }
        
        # 3. APPRECIATION - Thank you phrases
        appreciation = {
            "thanks", "thank you", "thx", "ty", "thank u", "appreciate it",
            "thanks a lot", "thank you so much", "many thanks", "grateful",
            "much appreciated", "thanks for your help", "thanks for helping"
        }
        
        # 4. SMALL TALK - Casual conversation not about product
        small_talk = {
            "how are you", "how r u", "how are u", "hows it going",
            "how's it going", "what's new", "whats new", "how do you do",
            "nice to meet you", "pleasure", "how's your day", "hows your day",
            "are you a bot", "are you real", "are you human", "who are you",
            "what are you", "what's your name", "whats your name", "your name",
            "who made you", "who created you", "are you ai", "are you chatgpt",
            "can you help", "can you help me", "i need help", "help me",
            "help please", "please help", "need assistance", "assist me"
        }
        
        # 5. OFF-TOPIC / CHITCHAT - Non-product related
        off_topic = {
            "tell me a joke", "joke", "funny", "weather", "whats the weather",
            "what time is it", "time", "date", "what day is it", "today",
            "tell me something", "interesting", "fun fact", "bored", "boring",
            "random", "anything", "whatever", "idk", "i dont know", "dunno",
            "nothing", "nevermind", "nvm", "forget it", "ok", "okay", "k",
            "cool", "nice", "great", "awesome", "sure", "alright", "fine",
            "yes", "no", "yeah", "yep", "nope", "maybe", "perhaps", "lol",
            "haha", "hehe", "lmao", "rofl", "omg", "wow", "hmm", "umm", "uh"
        }
        
        # Check for exact matches or query contains the pattern
        # Use word boundary checking to avoid false matches (e.g., 'yo' in 'you')
        def matches_category(patterns: set) -> bool:
            if query_lower in patterns:
                return True
            # For multi-word patterns, check if they appear in the query
            for pattern in patterns:
                if ' ' in pattern and pattern in query_lower:
                    return True
            return False
        
        def matches_category_loose(patterns: set) -> bool:
            """Looser matching for simple single-word patterns."""
            if query_lower in patterns:
                return True
            for pattern in patterns:
                if pattern in query_lower:
                    return True
            return False
        
        def starts_with_any(patterns: set) -> bool:
            """Check if query starts with any of the patterns."""
            first_word = query_lower.split()[0] if query_lower.split() else ""
            return first_word in patterns
        
        # Single word greetings for starts_with check
        greeting_starters = {"hi", "hello", "hey", "hiya", "howdy", "yo", "sup"}
        
        # === SMALL TALK DETECTION (check BEFORE greetings to avoid false matches) ===
        if matches_category(small_talk):
            state.intent = "small_talk"
            state.complexity = "simple"
            state.category = "general"
            state.urgency = 0.2
            state.sentiment = 0.6
            return state
        
        # === GREETING DETECTION (including 'hey you', 'hello there', etc.) ===
        if (matches_category(greetings) or 
            starts_with_any(greeting_starters) or
            (len(query_lower) <= 3 and query_lower not in {"who", "why", "how", "what"})):
            state.intent = "greeting"
            state.complexity = "simple"
            state.category = "general"
            state.urgency = 0.1
            state.sentiment = 0.8
            return state
        
        # === FAREWELL DETECTION ===
        if matches_category_loose(farewells):
            state.intent = "farewell"
            state.complexity = "simple"
            state.category = "general"
            state.urgency = 0.1
            state.sentiment = 0.7
            return state
        
        # === APPRECIATION DETECTION ===
        if matches_category_loose(appreciation):
            state.intent = "appreciation"
            state.complexity = "simple"
            state.category = "general"
            state.urgency = 0.1
            state.sentiment = 0.9
            return state
        
        # === OFF-TOPIC / CHITCHAT DETECTION ===
        if matches_category_loose(off_topic) and len(query_words) <= 5:
            state.intent = "chitchat"
            state.complexity = "simple"
            state.category = "general"
            state.urgency = 0.1
            state.sentiment = 0.5
            return state
        
        # ============================================================
        # HEURISTIC: Check if query seems product-related
        # If very short and no product keywords, route to simple
        # ============================================================
        
        product_keywords = {
            "account", "billing", "subscription", "payment", "invoice", "plan",
            "feature", "integration", "api", "setup", "configure", "settings",
            "error", "issue", "problem", "bug", "broken", "not working", "fix",
            "how to", "how do i", "can i", "is it possible", "tutorial", "guide",
            "password", "login", "sign in", "sign up", "register", "upgrade",
            "cancel", "refund", "pricing", "cost", "charge", "trial", "demo",
            "workspace", "project", "task", "team", "member", "admin", "user",
            "notification", "email", "sync", "export", "import", "data", "backup"
        }
        
        has_product_keyword = any(kw in query_lower for kw in product_keywords)
        
        # Short queries without product keywords = simple (goes to hardcoded response)
        if len(query_words) <= 4 and not has_product_keyword:
            state.intent = "question"
            state.complexity = "simple"
            state.category = "general"
            state.urgency = 0.3
            state.sentiment = 0.5
            return state
        
        # =============================================================
        # HEURISTIC ROUTING: Skip LLM classification for common patterns
        # This saves API quota and reduces latency
        # =============================================================
        
        common_question_patterns = [
            "how to", "what is", "what are", "how do", "how can", 
            "where is", "where can", "when can", "can i", "can you",
            "tell me", "show me", "help me", "get started", "getting started"
        ]
        
        # If query starts with common question pattern, skip LLM classification
        if any(query_lower.startswith(p) or p in query_lower for p in common_question_patterns):
            state.intent = "question"
            state.complexity = "standard"  # Moderate to trigger retrieval
            state.category = "support"
            state.urgency = 0.4
            state.sentiment = 0.5
            return state  # Skip LLM classification!
        
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
                "standard": "standard",  # Map standard -> moderate
                "complex": "complex",
                "specialized": "complex"  # Map specialized -> complex
            }
            state.complexity = complexity_map.get(raw_complexity, "standard")
            
            state.category = classification.get("category", "general")
            state.urgency = float(classification.get("urgency", 0.5))
            state.sentiment = float(classification.get("sentiment", 0.5))
            
        except Exception as e:
            print(f"Routing failed: {e}")
            # Use moderate (not simple) to avoid quota issues on retries
            state.complexity = "standard"
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
