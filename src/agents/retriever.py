"""
Retriever Agent for adaptive hybrid retrieval.
Combines query enhancement with hybrid search.
"""
from typing import List, Dict, Any

from src.agents.state import AgentState, RetrievalResult
from src.rag.hybrid_retriever import hybrid_retriever
from src.rag.query_enhancer import query_enhancer
from src.rag.reranker import reranker
from src.config import RERANK_TOP_K


class RetrieverAgent:
    """
    Adaptive retrieval agent that adjusts search depth
    based on query complexity and uses hybrid retrieval.
    """
    
    def __init__(self):
        self.hybrid = hybrid_retriever
        self.enhancer = query_enhancer
        self.reranker = reranker
    
    def retrieve(self, state: AgentState) -> AgentState:
        """
        Perform adaptive hybrid retrieval.
        
        Args:
            state: Current agent state with query and complexity
            
        Returns:
            Updated state with retrieval results
        """
        query = state.current_query
        complexity = state.complexity
        
        # Query enhancement based on complexity
        use_hyde = complexity in ["complex", "specialized"]
        use_multi_query = complexity != "simple"
        
        enhanced = self.enhancer.enhance_query(
            query,
            use_hyde=use_hyde,
            use_multi_query=use_multi_query
        )
        
        state.enhanced_queries = enhanced["query_variations"]
        state.hyde_document = enhanced["hyde_document"]
        
        # Collect results from all query variations
        all_results = []
        
        for q in state.enhanced_queries:
            results = self.hybrid.search(
                query=q,
                adaptive_k=True,
                query_complexity=complexity
            )
            all_results.extend(results)
        
        # Also search with HyDE document if available
        if state.hyde_document:
            hyde_results = self.hybrid.search(
                query=state.hyde_document,
                adaptive_k=True,
                query_complexity=complexity
            )
            all_results.extend(hyde_results)
        
        # Deduplicate by chunk_id
        seen = set()
        unique_results = []
        for r in all_results:
            chunk_id = r["metadata"].get("chunk_id", r["content"][:50])
            if chunk_id not in seen:
                seen.add(chunk_id)
                unique_results.append(r)
        
        # Rerank if we have enough results
        if len(unique_results) > RERANK_TOP_K:
            reranked = self.reranker.rerank(
                query=query,
                results=unique_results,
                top_k=RERANK_TOP_K * 2  # Keep more for response generation
            )
        else:
            reranked = unique_results
        
        # Convert to RetrievalResult objects
        state.retrieval_results = [
            RetrievalResult(
                content=r["content"],
                metadata=r["metadata"],
                score=r.get("rerank_score", r.get("fused_score", r.get("score", 0))),
                source=r.get("source", "hybrid")
            )
            for r in reranked
        ]
        
        return state
    
    def has_relevant_results(self, state: AgentState, threshold: float = 0.3) -> bool:
        """Check if retrieval found relevant results."""
        if not state.retrieval_results:
            return False
        
        # Check if top result meets threshold
        top_score = state.retrieval_results[0].score
        return top_score >= threshold


# Agent instance
retriever_agent = RetrieverAgent()
