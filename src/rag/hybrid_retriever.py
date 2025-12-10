"""
Hybrid Retriever with Reciprocal Rank Fusion.
Combines dense (FAISS) and sparse (BM25) retrieval results.
"""
from typing import List, Dict, Any, Optional
from collections import defaultdict

from src.config import DENSE_TOP_K, SPARSE_TOP_K, RERANK_TOP_K
from src.rag.dense_retriever import DenseRetriever, dense_retriever
from src.rag.sparse_retriever import SparseRetriever, sparse_retriever
from src.rag.chunker import Chunk


class HybridRetriever:
    """
    Hybrid retriever combining dense and sparse search.
    Uses Reciprocal Rank Fusion (RRF) to merge results.
    """
    
    def __init__(
        self,
        dense: DenseRetriever = None,
        sparse: SparseRetriever = None,
        rrf_k: int = 60  # RRF constant
    ):
        self.dense = dense or dense_retriever
        self.sparse = sparse or sparse_retriever
        self.rrf_k = rrf_k
    
    def add_chunks(self, chunks: List[Chunk]):
        """Add chunks to both dense and sparse indexes."""
        self.dense.add_chunks(chunks)
        self.sparse.add_chunks(chunks)
    
    def _reciprocal_rank_fusion(
        self,
        result_lists: List[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Merge multiple result lists using Reciprocal Rank Fusion.
        
        RRF Score = Σ 1 / (k + rank_i) for each result list
        
        Args:
            result_lists: List of result lists from different retrievers
            
        Returns:
            Merged and re-ranked results
        """
        fused_scores = defaultdict(float)
        doc_data = {}
        
        for results in result_lists:
            for rank, result in enumerate(results):
                # Use chunk_id as unique identifier
                doc_id = result["metadata"].get("chunk_id", result["content"][:100])
                
                # RRF formula
                fused_scores[doc_id] += 1 / (self.rrf_k + rank + 1)
                
                # Store document data (keep the one with higher original score)
                if doc_id not in doc_data or result["score"] > doc_data[doc_id]["score"]:
                    doc_data[doc_id] = result
        
        # Sort by fused score
        sorted_docs = sorted(
            fused_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Build final results
        results = []
        for doc_id, fused_score in sorted_docs:
            result = doc_data[doc_id].copy()
            result["fused_score"] = fused_score
            results.append(result)
        
        return results
    
    def search(
        self,
        query: str,
        dense_top_k: int = DENSE_TOP_K,
        sparse_top_k: int = SPARSE_TOP_K,
        final_top_k: int = RERANK_TOP_K,
        filter_dict: Optional[Dict[str, Any]] = None,
        adaptive_k: bool = False,
        query_complexity: str = "standard"
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining dense and sparse results.
        
        Args:
            query: Search query
            dense_top_k: Number of dense results
            sparse_top_k: Number of sparse results
            final_top_k: Number of final results after fusion
            filter_dict: Optional metadata filters
            adaptive_k: Enable adaptive retrieval depth
            query_complexity: Query complexity level for adaptive retrieval
            
        Returns:
            Fused and ranked results
        """
        # Adaptive retrieval: adjust k based on query complexity
        if adaptive_k:
            complexity_multipliers = {
                "simple": 0.5,
                "standard": 1.0,
                "complex": 1.5,
                "specialized": 2.0
            }
            multiplier = complexity_multipliers.get(query_complexity, 1.0)
            dense_top_k = int(dense_top_k * multiplier)
            sparse_top_k = int(sparse_top_k * multiplier)
            final_top_k = int(final_top_k * multiplier)
        
        # Get results from both retrievers
        dense_results = self.dense.search(query, dense_top_k, filter_dict)
        sparse_results = self.sparse.search(query, sparse_top_k, filter_dict)
        
        # Fuse results using RRF
        fused_results = self._reciprocal_rank_fusion([dense_results, sparse_results])
        
        # Return top-k fused results
        return fused_results[:final_top_k]
    
    def get_document_count(self) -> int:
        """Get total number of indexed documents (from dense store)."""
        return self.dense.get_document_count()


# Default hybrid retriever instance
hybrid_retriever = HybridRetriever()
