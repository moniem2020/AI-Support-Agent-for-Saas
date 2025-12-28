"""
Responder Agent for generating context-aware responses.
Uses retrieved context and Gemini for response generation.
"""
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from src.config import GOOGLE_API_KEY, GOOGLE_API_KEY_FAST, MODEL_ROUTING, API_KEY_ROUTING
from src.agents.state import AgentState, Message


class ResponderAgent:
    """
    Response generation agent that uses retrieved context
    to generate accurate, grounded responses.
    """
    
    def __init__(self):
        # Create models with appropriate API keys based on tier
        self.models = {}
        for tier, model_name in MODEL_ROUTING.items():
            # Determine which API key to use for this tier
            key_type = API_KEY_ROUTING.get(tier, "main")
            api_key = GOOGLE_API_KEY_FAST if key_type == "fast" else GOOGLE_API_KEY
            
            self.models[tier] = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=0.3
            )
        
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
        
        self.confidence_prompt = PromptTemplate(
            input_variables=["query", "response", "context"],
            template="""Rate how well this response is grounded in the provided context.

Question: {query}

Context:
{context}

Response: {response}

Rate from 0.0 to 1.0:
- 1.0: Response is fully supported by context
- 0.7-0.9: Mostly supported with minor inferences
- 0.4-0.6: Partially supported, some gaps
- 0.1-0.3: Poorly supported, significant gaps
- 0.0: Not supported or contradicts context

Respond with ONLY a number between 0.0 and 1.0:"""
        )
    
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
            # Generate response
            response = model.invoke(prompt)
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
