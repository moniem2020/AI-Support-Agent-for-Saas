"""
Responder Agent for generating context-aware responses.
Uses retrieved context and Gemini for response generation.
Implements API key rotation for quota management.
"""
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from src.config import (
    GOOGLE_API_KEY, GOOGLE_API_KEY_FAST, GOOGLE_API_KEYS_POOL,
    MODEL_ROUTING, API_KEY_ROUTING
)
from src.agents.state import AgentState, Message


class ResponderAgent:
    """
    Response generation agent that uses retrieved context
    to generate accurate, grounded responses.
    Features API key rotation for quota management.
    """
    
    def __init__(self):
        # Track current key index for rotation
        self.current_key_index = 0
        self.api_keys_pool = GOOGLE_API_KEYS_POOL or [GOOGLE_API_KEY]
        
        # Create models with appropriate API keys based on tier
        self.models = {}
        self._create_models()
        
        # Response generation prompt
        self.response_prompt = PromptTemplate(
            input_variables=["query", "context", "history", "category"],
            template="""You are a helpful SaaS customer support agent. Answer the customer's question using ONLY the provided context.

RULES:
1. Base your answer ONLY on the provided context
2. If the context doesn't contain the answer, say so clearly
3. Be concise but thorough
4. Use a friendly, professional tone
5. Include specific steps if applicable
6. Cite sources when referencing specific information

Category: {category}

Previous conversation:
{history}

Relevant Documentation:
{context}

Customer Question: {query}

Provide a helpful response:"""
        )
    
    def _create_models(self):
        """Create LLM models for each tier with current API key."""
        for tier, model_name in MODEL_ROUTING.items():
            # Determine which API key to use for this tier
            key_type = API_KEY_ROUTING.get(tier, "main")
            
            if key_type == "fast":
                api_key = GOOGLE_API_KEY_FAST
            else:
                # Use current key from pool for main/complex queries
                api_key = self.api_keys_pool[self.current_key_index]
            
            self.models[tier] = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=0.3
            )
    
    def _rotate_key(self):
        """Rotate to next API key in pool."""
        old_index = self.current_key_index
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys_pool)
        print(f"[KEY ROTATION] Switched from key {old_index} to key {self.current_key_index}")
        # Recreate models with new key
        self._create_models()
        return self.current_key_index != old_index  # True if we have more keys to try
    
    def _invoke_with_rotation(self, model, prompt: str, tier: str, max_retries: int = 4):
        """
        Invoke model with automatic key rotation on quota errors.
        
        Args:
            model: The LangChain model to invoke
            prompt: The prompt to send
            tier: The complexity tier (for model selection after rotation)
            max_retries: Maximum number of keys to try
            
        Returns:
            Model response or raises exception if all keys exhausted
        """
        last_error = None
        keys_tried = 0
        
        while keys_tried < min(max_retries, len(self.api_keys_pool)):
            try:
                # Get current model for this tier
                current_model = self.models.get(tier, model)
                response = current_model.invoke(prompt)
                return response
            except Exception as e:
                error_str = str(e).lower()
                # Check if it's a quota error
                if "quota" in error_str or "429" in error_str or "rate" in error_str:
                    print(f"[QUOTA ERROR] Key {self.current_key_index} quota exceeded, rotating...")
                    last_error = e
                    keys_tried += 1
                    if self._rotate_key():
                        continue  # Try with next key
                    else:
                        break  # No more keys to try
                else:
                    # Non-quota error, don't rotate
                    raise e
        
        # All keys exhausted
        raise last_error or Exception("All API keys quota exceeded")
    
    def _build_context(self, state: AgentState) -> str:
        """Build context string from retrieval results."""
        if not state.retrieval_results:
            return "No relevant documentation found."
        
        context_parts = []
        for i, result in enumerate(state.retrieval_results[:5], 1):
            doc_id = result.metadata.get("doc_id", "unknown")
            context_parts.append(f"[Source {i} - {doc_id}]\n{result.content}\n")
        
        return "\n".join(context_parts)
    
    def _build_history(self, state: AgentState) -> str:
        """Build conversation history string."""
        history_parts = []
        for msg in state.messages[:-1]:  # Exclude current message
            role = "Customer" if msg.role == "user" else "Agent"
            history_parts.append(f"{role}: {msg.content}")
        
        return "\n".join(history_parts) if history_parts else "No previous conversation"
    
    def respond(self, state: AgentState) -> AgentState:
        """
        Generate a response using retrieved context.
        
        Args:
            state: Current agent state with retrieval results
            
        Returns:
            Updated state with response and confidence
        """
        # Select model based on complexity
        model = self.models.get(state.complexity, self.models["moderate"])
        state.model_used = MODEL_ROUTING.get(state.complexity, MODEL_ROUTING["moderate"])
        
        # Build prompt inputs
        context = self._build_context(state)
        history = self._build_history(state)
        
        prompt = self.response_prompt.format(
            query=state.current_query,
            context=context,
            history=history,
            category=state.category
        )
        
        try:
            # Generate response with automatic key rotation on quota errors
            tier = state.complexity or "moderate"
            response = self._invoke_with_rotation(model, prompt, tier)
            state.response = response.content
            
            # Extract sources
            state.sources = [
                r.metadata.get("doc_id", "unknown")
                for r in state.retrieval_results[:3]
            ]
            
            # Calculate confidence
            state.confidence = self._calculate_confidence(state, context)
            
            # Add to messages
            state.messages.append(Message(
                role="assistant",
                content=state.response,
                metadata={"confidence": state.confidence, "sources": state.sources}
            ))
            
        except Exception as e:
            import traceback
            print(f"Response generation failed: {type(e).__name__}: {e}")
            traceback.print_exc()
            state.response = "I apologize, but I'm having trouble processing your request. Let me connect you with a support specialist."
            state.confidence = 0.0
            state.should_escalate = True
        
        return state
    
    def _calculate_confidence(self, state: AgentState, context: str) -> float:
        """
        Calculate response confidence based on retrieval quality.
        Uses retrieval scores instead of LLM to avoid quota issues.
        """
        # Base confidence on retrieval results
        if not state.retrieval_results:
            return 0.4  # Low confidence without sources
        
        # Use top retrieval score as base
        top_score = state.retrieval_results[0].score if hasattr(state.retrieval_results[0], 'score') else 0.7
        
        # Boost confidence for more sources
        source_bonus = min(0.15, len(state.retrieval_results) * 0.03)
        
        # Check if context actually contains relevant info
        query_words = set(state.current_query.lower().split())
        context_words = set(context.lower().split())
        overlap = len(query_words & context_words) / max(len(query_words), 1)
        relevance_bonus = overlap * 0.1
        
        # Calculate final confidence (cap at 0.95)
        confidence = min(0.95, top_score + source_bonus + relevance_bonus)
        return max(0.5, confidence)  # Minimum 0.5 to avoid unnecessary escalation


# Agent instance
responder_agent = ResponderAgent()
