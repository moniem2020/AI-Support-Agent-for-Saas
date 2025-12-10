"""
Cross-Encoder Reranker for refining retrieval results.
Uses a smaller model for efficient reranking.
"""
from typing import List, Dict, Any
from sentence_transformers import CrossEncoder

from src.config import RERANK_TOP_K


class Reranker:
    """
    Cross-encoder based reranker for improving retrieval precision.
    Re-scores document-query pairs for more accurate ranking.
    """
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        if self._model is None:
            self._model = CrossEncoder(model_name, max_length=512)
    
    def rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = RERANK_TOP_K
    ) -> List[Dict[str, Any]]:
        """
        Rerank results using cross-encoder scoring.
        
        Args:
            query: Original search query
            results: List of retrieval results to rerank
            top_k: Number of top results to return
            
        Returns:
            Reranked results with updated scores
        """
        if not results:
            return []
        
        # Prepare query-document pairs
        pairs = [(query, r["content"]) for r in results]
        
        # Get cross-encoder scores
        scores = self._model.predict(pairs)
        
        # Attach scores to results
        for result, score in zip(results, scores):
            result["rerank_score"] = float(score)
        
        # Sort by rerank score
        reranked = sorted(results, key=lambda x: x["rerank_score"], reverse=True)
        
        return reranked[:top_k]


# Singleton reranker instance
reranker = Reranker()
