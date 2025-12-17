"""
Responder Agent for generating context-aware responses.
Uses retrieved context and Gemini for response generation.
"""
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from src.config import GOOGLE_API_KEY, MODEL_ROUTING
from src.agents.state import AgentState, Message


class ResponderAgent:
    """
    Response generation agent that uses retrieved context
    to generate accurate, grounded responses.
    """
    
    def __init__(self):
        self.models = {
            tier: ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=GOOGLE_API_KEY,
                temperature=0.3
            )
            for tier, model_name in MODEL_TIERS.items()
        }
        
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
        model = self.models.get(state.complexity, self.models["standard"])
        state.model_used = MODEL_TIERS.get(state.complexity, MODEL_TIERS["standard"])
        
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
            print(f"Response generation failed: {e}")
            state.response = "I apologize, but I'm having trouble processing your request. Let me connect you with a support specialist."
            state.confidence = 0.0
            state.should_escalate = True
        
        return state
    
    def _calculate_confidence(self, state: AgentState, context: str) -> float:
        """Calculate response confidence using LLM."""
        try:
            prompt = self.confidence_prompt.format(
                query=state.current_query,
                response=state.response,
                context=context
            )
            
            # Use flash model for quick confidence check
            model = self.models["simple"]
            response = model.invoke(prompt)
            
            # Parse confidence score
            score_text = response.content.strip()
            score = float(score_text)
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            print(f"Confidence calculation failed: {e}")
            # Fallback: base confidence on retrieval scores
            if state.retrieval_results:
                return min(0.8, state.retrieval_results[0].score)
            return 0.5


# Agent instance
responder_agent = ResponderAgent()
